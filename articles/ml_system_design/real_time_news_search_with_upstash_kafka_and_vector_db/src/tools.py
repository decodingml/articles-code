import datetime
import functools
import logging
from typing import Callable, Dict, List

from newsapi import NewsApiClient
from newsdataapi import NewsDataApiClient
from pydantic import ValidationError

from models import NewsAPIModel, NewsDataIOModel
from settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handle_article_fetching(func: Callable) -> Callable:
    """
    Decorator to handle exceptions for article fetching functions.

    This decorator wraps article fetching functions to catch and log any exceptions
    that occur during the fetching process. If an error occurs, it logs the error
    and returns an empty list.

    Args:
        func (Callable): The article fetching function to wrap.

    Returns:
        Callable: The wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error while processing articles: {e}")
        except Exception as e:
            logger.error(f"Error fetching data from source: {e}")
            logger.exception(e)
        return []

    return wrapper


def time_window(hours: int) -> str:
    """
    Generate the datetime pairs for the specified time window.
    Args:
        hours (int): The length of the time window in hours.

    Returns:
        Tuple[str, str]: A tuple containing the start and end times of the window in ISO format.

    Note:
        Batch fetching feature is available only with pro plan.

    """
    current_datetime = datetime.datetime.now()
    end_datetime = current_datetime + datetime.timedelta(hours=hours)
    return current_datetime.strftime("%Y-%m-%dT%H:%M:%S"), end_datetime.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )


class NewsFetcher:
    """
    A class for fetching news articles from various APIs.

    Attributes:
        _newsapi (NewsApiClient): Client for the NewsAPI.
        _newsdataapi (NewsDataApiClient): Client for the NewsDataAPI.
        _time_window_h (int): The time window for fetching articles, in hours.

    Methods:
        fetch_from_newsapi(): Fetches articles from NewsAPI.
        fetch_from_newsdataapi(): Fetches articles from NewsDataAPI.
        sources: Returns a list of callable fetch functions.
    """

    def __init__(self):
        self._newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        self._newsdataapi = NewsDataApiClient(apikey=settings.NEWSDATAIO_KEY)
        self._time_window_h = 24  # Fetch news once a day

    @handle_article_fetching
    def fetch_from_newsapi(self) -> List[Dict]:
        """Fetch top headlines from NewsAPI."""
        response = self._newsapi.get_everything(
            q=settings.NEWS_TOPIC,
            language="en",
            page=settings.ARTICLES_BATCH_SIZE,
            page_size=settings.ARTICLES_BATCH_SIZE,
        )
        return [
            NewsAPIModel(**article).to_common()
            for article in response.get("articles", [])
        ]

    @handle_article_fetching
    def fetch_from_newsdataapi(self) -> List[Dict]:
        """Fetch news data from NewsDataAPI."""
        response = self._newsdataapi.news_api(
            q=settings.NEWS_TOPIC,
            language="en",
            size=settings.ARTICLES_BATCH_SIZE,
        )
        return [
            NewsDataIOModel(**article).to_common()
            for article in response.get("results", [])
        ]

    @property
    def sources(self) -> List[callable]:
        """List of news fetching functions."""
        return [self.fetch_from_newsapi, self.fetch_from_newsdataapi]
