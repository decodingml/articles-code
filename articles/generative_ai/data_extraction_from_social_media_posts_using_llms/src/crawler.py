import instaloader

from itertools import takewhile, dropwhile
from typing import List, Dict, Any
from datetime import datetime, timedelta


class InstagramCrawler:
    def __init__(self):
        self.loader = instaloader.Instaloader()
        self._until = datetime.now()
        self._since = self._until - timedelta(days=7)

    def crawl(self, page_name) -> List[Dict[str, str | Any]]:
        profile = instaloader.Profile.from_username(self.loader.context, page_name)
        posts = takewhile(lambda p: p.date > self._since,
                          dropwhile(lambda p: p.date > self._until, profile.get_posts()))

        return [
            {'content': post.caption, 'date': post.date, 'link': f"https://www.instagram.com/{page_name}"}
            for post in posts
        ]

    def get_posts(self, profiles_to_scrap: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        all_posts = []
        for restaurant_name, profile_info in profiles_to_scrap.items():
            try:
                posts = self.crawl(profile_info['page_name'])
                for post in posts:
                    post['restaurant_name'] = restaurant_name
                    post['city'] = profile_info['city']
                    all_posts.append(post)
                print(f"Scraped {len(posts)} posts for {restaurant_name}")
            except Exception as e:
                print(f"Error scraping {restaurant_name}: {str(e)}")
        return all_posts


