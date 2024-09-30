import datetime
import io
import json

import pandas as pd

from typing import List, Dict, Any
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from articles.generative_ai.data_extraction_from_social_media_posts_using_llms.src.config import settings
from articles.generative_ai.data_extraction_from_social_media_posts_using_llms.src.crawler import InstagramCrawler
from articles.generative_ai.data_extraction_from_social_media_posts_using_llms.src.db import database
from articles.generative_ai.data_extraction_from_social_media_posts_using_llms.src.llm import get_chain
from schemas import ReportProfiles
from templates import PROFILES_REPORT_TEMPLATE, PROFILES_TEMPLATE_REFINE


class ReportGenerator:
    def __init__(self):
        self.crawler = InstagramCrawler()
        self.database = database
        self.llm = ChatOpenAI(model_name=settings.OPENAI_MODEl, api_key=settings.OPENAI_API_KEY)

    def crawl_and_store_posts(self):
        posts = self.crawler.get_posts(settings.PROFILES_TO_SCRAP)
        posts_collection = self.database['instagram_posts']
        for post in posts:
            posts_collection.update_one(
                {'link': post['link']},
                {'$set': post},
                upsert=True
            )
        return len(posts)

    def get_posts_from_db(self) -> List[Dict[str, Any]]:
        posts_collection = self.database['instagram_posts']
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=7)
        return list(posts_collection.find({
            'date': {'$gte': start_date, '$lte': end_date}
        }))

    @staticmethod
    def get_posts_text(posts: List[Dict[str, Any]]) -> List[str]:
        unique_posts = set()
        for post in posts:
            post_text = post.get("content", "")
            page_text = post.get("restaurant_name", "")
            link_text = post.get("link", "")
            city_text = post.get("city", "")

            if post_text:
                unique_posts.add(f"{post_text} | {page_text} | {link_text} | {city_text}\n")

        return list(unique_posts)

    def create_report(self, posts: List[str]) -> str:
        chain_1 = get_chain(
            self.llm,
            PROFILES_REPORT_TEMPLATE,
            input_variables=["input_var"],
            output_key="report",
        )

        result_1 = chain_1.invoke({"input_var": posts})
        report = result_1["report"]

        output_parser = PydanticOutputParser(pydantic_object=ReportProfiles)
        format_output = {"format_instructions": output_parser.get_format_instructions()}

        chain_2 = get_chain(
            self.llm,
            PROFILES_TEMPLATE_REFINE,
            input_variables=["raport", "format_instructions"],
            output_key="formatted_report",
        )

        result_2 = chain_2.invoke({"raport": report, "format_instructions": format_output})

        return result_2["formatted_report"]

    @staticmethod
    def create_excel_file(data: Dict[str, Any]):
        rows = []
        excel_filename = f"Profiles_report_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"

        report_name = data.get("name", "Unknown Report")
        for field in data.get("fields", []):
            field_name = field.get("name", "Unknown Field")
            for key in field.get("keys", []):
                rows.append({
                    "Type of Report": report_name,
                    "Type of Information": field_name,
                    "Source": key.get("name", "no name"),
                    "Information": key.get("information", "no information"),
                    "Link": key.get("link", "no link"),
                    "City": key.get("city", "no city"),
                })

        df = pd.DataFrame(rows)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        return buffer, excel_filename

    def generate_report(self):
        # Step 1: Crawl and store Instagram posts
        posts_count = self.crawl_and_store_posts()
        print(f"Crawled and stored {posts_count} posts.")

        # Step 2: Retrieve posts from the database
        db_posts = self.get_posts_from_db()
        print(f"Retrieved {len(db_posts)} posts from the database.")

        # Step 3: Process posts and create report
        posts_text = self.get_posts_text(db_posts)
        report_data_str = self.create_report(posts_text)
        print(f"Generated report from posts: {report_data_str}")

        # Parse the JSON string
        try:
            report_data = json.loads(report_data_str)
        except json.JSONDecodeError:
            print("Error: Unable to parse the report data as JSON.")
            return None

        # Step 4: Create Excel file
        excel_buffer, excel_filename = self.create_excel_file(report_data)

        # Step 5: Save Excel file
        with open(excel_filename, 'wb') as f:
            f.write(excel_buffer.getvalue())

        print(f"Excel file '{excel_filename}' has been created successfully.")
        return excel_filename
