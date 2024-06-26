from datetime import datetime, timedelta

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.crawlers import dispatcher
from src.db import database

logger = Logger(service="decodingml/crawler")


def lambda_handler(event, context: LambdaContext):

    link = event.get('link')

    logger.info(f"Start extracting posts for {link}")

    crawler = dispatcher.get_crawler(event.get('link'))

    posts = [{**page, 'correlation_id': context.aws_request_id} for page in crawler.extract()]

    now = datetime.now()
    existing_posts = database.profiles.find({
        "date": {"$gte": (now - timedelta(days=7)), "$lte": now},
        "name": link
    }, projection={'date': 1})

    existing_posts = [post.get('date') for post in list(existing_posts)]

    posts = [post for post in posts if post.get('date') not in existing_posts]

    if not posts:
        logger.info("No new posts on page")
        return

    logger.info(f"Successfully extracted {len(posts)} posts")
    database.profiles.insert_many(posts)
    logger.info(f"Successfully inserted data in db")
