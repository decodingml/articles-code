from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.prod"))

    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 256
    EMBEDDING_SIZE: int = 384
    EMBEDDING_MODEL_DEVICE: str = "cpu"
    VECTOR_DB_OUTPUT_COLLECTION_NAME: str = "linkedin_posts"

    # Variables loaded from .env file
    QDRANT_URL: str = "localhost:6333"
    QDRANT_API_KEY: Optional[str] = None


settings = AppSettings()
