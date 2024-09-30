from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8', extra='ignore')

    # OPENAI
    OPENAI_API_KEY: str
    OPENAI_MODEl: str = "gpt-4o-mini"

    # DB
    MONGO_HOST: str = 'localhost'
    MONGO_PORT: int = 27017
    MONGO_USER: str = None
    MONGO_PASSWORD: str = None
    MONGO_DATABASE: str = 'restaurants'
    MONGO_URI: str = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}"

    # PROFILES TO CRAWL
    PROFILES_TO_SCRAP: dict = {
        "KFC": {"page_name": "kfc", "city": "Salt Lake"},
        "MC": {"page_name": "mcdonalds", "city": "San Bernardino"},
        "In-N-Out Burger": {"page_name": "innout", "city": "Baldwin Park"},
        "Taco Bell": {"page_name": "tacobell", "city": "Downey"},
        "Wendy's": {"page_name": "wendys", "city": "Columbus"},
    }


settings = Settings()
