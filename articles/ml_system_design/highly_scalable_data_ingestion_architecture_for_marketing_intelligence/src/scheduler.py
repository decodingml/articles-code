import json
import os
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import backoff
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
import openai
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from openai import OpenAI

from src.constants import PAGE_LINK
from src.db import database
from src.schemas import ReportProfiles
from src.utils import monitor
from src.templates import PROFILES_REPORT_TEMPLATE, PROFILES_TEMPLATE_REFINE

logger = Logger(service="decodingml/scheduler")

_client = boto3.client("lambda")


def get_chain(llm, template: str, input_variables=None, verbose=True, output_key=""):
    return LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=input_variables, template=template, verbose=verbose
        ),
        output_key=output_key,
        verbose=verbose,
    )


@backoff.on_exception(backoff.expo, openai.RateLimitError)
def completion_with_backoff(llm, **kwargs):
    return llm.chat.completions.create(**kwargs)


def create_report_for_batch(batch):
    logger.info("Starting report creation for batch.")

    llm = OpenAI()
    model = os.getenv('OPENAI_MODEL', default='gpt-4-1106-preview')
    logger.debug(f"Requesting initial completion with batch data: {batch}")

    try:
        chain_profiles = completion_with_backoff(
            llm=llm,
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": PROFILES_REPORT_TEMPLATE.format(input_var=batch),
                },
            ],
        )
    except Exception as e:
        logger.error("Failed during initial completion request", exc_info=True)
        raise e

    report = chain_profiles.choices[0].message.content
    logger.debug("Received initial completion results.")

    output_parser = PydanticOutputParser(pydantic_object=ReportProfiles)
    logger.debug("Parsing output with Pydantic.")

    try:
        format_output = {"format_instructions": output_parser.get_format_instructions()}
    except Exception as e:
        logger.error("Failed during output parsing", exc_info=True)
        raise e

    logger.info("Requesting refinement of the initial report.")

    try:
        chain_refine = completion_with_backoff(
            llm=llm,
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": PROFILES_TEMPLATE_REFINE.format(
                        raport=report, format_instructions=format_output
                    ),
                },
            ],
        )
        print("CHAIN REFINE", chain_refine)
    except Exception as e:
        logger.error("Failed during report refinement request", exc_info=True)
        raise e

    logger.info("Report refinement completed.")

    return chain_refine.choices[0].message.content


def generate_profiles_report(posts: list[dict]) -> list[str]:
    """
    Method that creates a chain to output a profile report based on the scraped data.
    :returns: list of reports
    """

    responses = []
    input_var = [f"{p.get('content')} {p.get('link')} {p.get('name')} \n" for p in posts]

    batch_size = 50

    # create batches
    batches = [
        input_var[i: i + batch_size] for i in range(0, len(input_var), batch_size)
    ]

    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_batch = {
            executor.submit(create_report_for_batch, batch): batch
            for batch in batches
        }
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_result = future.result()
            responses.append(batch_result)

    return responses


def lambda_handler(event, context: LambdaContext):
    correlation_ids = []

    for link in PAGE_LINK:
        response = _client.invoke(
            FunctionName="pi-prod-profiles-crawler",
            InvocationType="Event",
            Payload=json.dumps({"link": link}),
        )
        logger.info(f"Triggered crawler for: {link}")

        correlation_ids.append(response["ResponseMetadata"]["RequestId"])

    logger.info(f"Monitoring: {len(correlation_ids)} crawler processes")

    while True:
        time.sleep(15)
        completed = monitor(correlation_ids)

        correlation_ids = [c for c in correlation_ids if c not in completed]

        if not correlation_ids:
            break

        logger.info(f"Still waiting for {len(correlation_ids)} crawlers to complete")

    now = datetime.now()
    posts = list(
        database.profiles.find(
            {
                "date": {"$gte": (now - timedelta(days=7)), "$lte": now},
            }
        )
    )

    logger.info(f"Gathered {len(posts)} posts")

    if not posts:
        logger.info("Cannot generate report, no new posts available")
        return

    reports = generate_profiles_report(posts)

    logger.info("Generated new report!")
