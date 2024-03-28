import pytest
from unittest.mock import patch
from src.tools import NewsFetcher


def mocked_newsapi_article():
    return {
        "article_id": "0b09d2891dcb9085f2d5201249356458",
        "title": "Top events of the day: From PM Modi's Kerala visit to Russian presidential elections, track top news on March 15 here",
        "link": "https://www.livemint.com/news/india/top-events-of-the-day-from-pm-modis-kerala-visit-to-russian-presidential-elections-track-top-news-on-march-15-here-11710464847509.html",
        "keywords": None,
        "creator": None,
        "video_url": None,
        "description": "Top news of the day: PM Modi's Lok Sabha poll campaign in Kerala, Rahul Gandhi to address a public rally in Bhiwandi, deadline of advance tax payment, Russia's presidential elections, and more",
        "content": "ONLY AVAILABLE IN PAID PLANS",
        "pubDate": "2024-03-15 01:42:57",
        "image_url": "https://www.livemint.com/lm-img/img/2024/03/15/1600x900/Modi-16_1710466650723_1710466677228.jpg",
        "source_id": "livemint",
        "source_url": "https://www.livemint.com",
        "source_icon": "https://i.bytvi.com/domain_icons/livemint.png",
        "source_priority": 7134,
        "country": ["india"],
        "category": ["top"],
        "language": "english",
        "ai_tag": "ONLY AVAILABLE IN PROFESSIONAL AND CORPORATE PLANS",
        "sentiment": "ONLY AVAILABLE IN PROFESSIONAL AND CORPORATE PLANS",
        "sentiment_stats": "ONLY AVAILABLE IN PROFESSIONAL AND CORPORATE PLANS",
        "ai_region": "ONLY AVAILABLE IN CORPORATE PLANS",
    }


def mocked_newsdata_article():
    return {
        "source": {"id": None, "name": "News18"},
        "author": "News18",
        "title": "Still Using Paytm FASTag? Here Is A Step-by-Step Guide To Port To A New FASTag - News18",
        "description": "NHAI suggests users acquire FASTags from the 32 banks that are now on the authorised list for FASTag issuing",
        "url": "https://www.news18.com/business/still-using-paytm-fastag-here-is-a-step-by-step-guide-to-port-to-a-new-fastag-8814964.html",
        "urlToImage": "https://images.news18.com/ibnlive/uploads/2024/02/untitled-design-2024-02-12t023732.441-2024-02-d1cbfb73a1fd442b891b3917ea3d4de1-16x9.jpg?impolicy=website&width=1200&height=675",
        "publishedAt": "2024-03-14T12:18:27Z",
        "content": "In a recent move, the Reserve Bank of India (RBI) ordered Paytm Payments Bank Ltd. (PPBL) to cease taking deposits or top-ups in any client accounts including wallets and FASTags after February 29, 2\u2026 [+3529 chars]",
    }


@pytest.fixture
def mock_news_fetcher():
    with patch.object(
        NewsFetcher, "fetch_from_newsapi"
    ) as mock_fetch_from_newsapi, patch.object(
        NewsFetcher, "fetch_from_newsdataapi"
    ) as mock_fetch_from_newsdataapi:

        mock_fetch_from_newsapi.return_value = [
            {
                "article_id": "0b09d2891dcb9085f2d5201249356458",
                "pubDate": "2024-03-15 01:42:57",
            }
        ]
        mock_fetch_from_newsdataapi.return_value = [
            {
                "source": {"id": None, "name": "News18"},
                "author": "News18",
            }
        ]

        yield NewsFetcher()


def test_news_fetch(mock_news_fetcher):
    news_api_articles = mock_news_fetcher.fetch_from_newsapi()
    newsdata_api_articles = mock_news_fetcher.fetch_from_newsdataapi()

    assert len(news_api_articles) > 0
    assert len(newsdata_api_articles) > 0
    assert news_api_articles[0]["article_id"] == "0b09d2891dcb9085f2d5201249356458"
    assert news_api_articles[0]["pubDate"] == "2024-03-15 01:42:57"

    assert newsdata_api_articles[0]["source"] == {"id": None, "name": "News18"}
    assert newsdata_api_articles[0]["author"] == "News18"
