import os
from datetime import datetime, timedelta
from itertools import takewhile, dropwhile
from typing import List, Dict, Any
from urllib.parse import urlparse

import instaloader

from src.crawlers.base import BaseAbstractCrawler


class InstagramCrawler(BaseAbstractCrawler):

    def __init__(self, link: str, proxy=None):
        self.link = link
        self.loader = instaloader.Instaloader()
        self._until = datetime.now()
        self._since = self._until - timedelta(days=7)
        self._proxy = proxy

    def extract(self, **kwargs) -> List[Dict[str, str | Any]]:
        parsed_url = urlparse(self.link)

        if self._proxy:
            os.environ['https_proxy'] = self._proxy.__dict__().get('http')
        profile = instaloader.Profile.from_username(self.loader.context, parsed_url.path.strip('/').split('/')[0])
        posts = takewhile(lambda p: p.date > self._since, dropwhile(lambda p: p.date > self._until, profile.get_posts()))

        return [
            {'content': post.caption, 'date': post.date, 'link': self.link}
            for post in posts
        ]
