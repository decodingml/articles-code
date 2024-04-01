"""Application Settings"""

from pydantic_settings import SettingsConfigDict, BaseSettings
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(dir_path, "..", "./.env"), env_file_encoding="utf-8"
    )

    UPSTASH_KAFKA_UNAME: str
    UPSTASH_KAFKA_PASS: str
    UPSTASH_KAFKA_ENDPOINT: str
    UPSTASH_KAFKA_TOPIC: str
    UPSTASH_VECTOR_ENDPOINT: str
    UPSTASH_VECTOR_TOPIC: str
    UPSTASH_VECTOR_KEY: str
    UPSTASH_VECTOR_RETRIES: int = 5
    UPSTASH_VECTOR_WAIT_INTERVAL: float = 0.1
    UPSTASH_VECTOR_UPSERT_BATCH_SIZE: int = 2
    UPSTASH_KAFKA_SECURITY_PROTOCOL: str = "SASL_SSL"
    UPSTASH_KAFKA_SASL_MECHANISM: str = "SCRAM-SHA-256"

    NEWSAPI_KEY: str
    NEWSDATAIO_KEY: str
    NEWS_TOPIC: str
    ARTICLES_BATCH_SIZE: int = 5

    FETCH_WAIT_WINDOW: int = 1800  # seconds (30 minutes)

    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 384
    EMBEDDING_MODEL_DEVICE: str = "cpu"


settings = AppSettings()
