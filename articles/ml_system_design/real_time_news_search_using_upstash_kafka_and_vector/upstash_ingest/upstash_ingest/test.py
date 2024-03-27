from typing import List
from embeddings import TextEmbedder
from settings import settings
from models import CommonDocument, RefinedDocument, ChunkedDocument, EmbeddedDocument
from .tools import NewsFetcher
from .logger import get_logger
import pytest

logger = get_logger(__name__)


def _test_news_fetch():
    fetcher = NewsFetcher()
    news_api_articles = fetcher.fetch_from_newsapi()
    newsdata_api_articles = fetcher.fetch_from_newsdataapi()
    logger.info("[TEST] Fetching articles from NewsAPI and NewsDataAPI.")
    logger.info(f"Fetched {len(news_api_articles)} articles from NewsAPI.")
    logger.info(f"Fetched {len(newsdata_api_articles)} articles from NewsDataAPI.")


def _test_news_embed(articles: List[CommonDocument]):
    model = TextEmbedder(
        model_id=settings.EMBEDDING_MODEL_ID,
        max_input_length=settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
        device=settings.EMBEDDING_MODEL_DEVICE,
    )
    for doc in articles:
        refined: RefinedDocument = RefinedDocument.from_common(doc)
        chunks: List[ChunkedDocument] = ChunkedDocument.from_refined(refined, model)
        for chunk in chunks:
            embedded: EmbeddedDocument = EmbeddedDocument.from_chunked(chunk, model)
            print(embedded.to_payload())
