import re

from src.crawlers.base import BaseAbstractCrawler
from src.crawlers.instagram import InstagramCrawler


class CrawlerDispatcher:

    def __init__(self) -> None:
        self._crawlers = {}

    def register(self, domain: str, crawler: type[BaseAbstractCrawler]) -> None:
        self._crawlers[r"https://(www\.)?{}.com/*".format(re.escape(domain))] = crawler

    def get_crawler(self, url: str) -> BaseAbstractCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler(url)
        else:
            raise ValueError("No crawler found for the provided link")


dispatcher = CrawlerDispatcher()
dispatcher.register('instagram', InstagramCrawler)
