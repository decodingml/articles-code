import os
import pymongo.errors

from aws_lambda_powertools import Logger
from pymongo import MongoClient

logger = Logger(service="marketing-reports/news", child=True)


class DatabaseConnection:

    _client: MongoClient = None

    @classmethod
    def connect(cls):
        if cls._client is None:
            try:
                cls._client = MongoClient(os.getenv('DATABASE_URI'))
            except pymongo.errors.ConnectionFailure as exc:
                logger.error(f"Database failed connection: {exc}")
                raise
            logger.debug("Created connection to database")

    @classmethod
    def get_database(cls, name: str):
        if cls._client is None:
            cls.connect()
        return cls._client[name]

    @classmethod
    def close(cls):
        if cls._client is not None:
            cls._client.close()
            cls._client = None

        logger.debug("Closed connection to database")


database = DatabaseConnection.get_database(os.getenv('DATABASE_NAME'))
