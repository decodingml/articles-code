from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from articles.generative_ai.data_extraction_from_social_media_posts_using_llms.src.config import settings


class DatabaseConnection:
    _client: MongoClient = None

    @classmethod
    def connect(cls):
        if cls._client is None:
            try:
                cls._client = MongoClient(f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}")
            except ConnectionFailure as exc:
                print(f'Exception while connecting to database: {exc}')
                raise

    @classmethod
    def get_database(cls, name: str):
        if cls._client is None:
            cls.connect()
        return cls._client[name]

    @classmethod
    def close(cls):
        if cls._client is not None:
            cls._client.close()


database = DatabaseConnection.get_database(settings.MONGO_DATABASE)
