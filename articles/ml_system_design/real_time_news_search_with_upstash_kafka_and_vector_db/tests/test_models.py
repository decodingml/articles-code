"""
    This module contains tests for the pydantic models defined in upstash_ingest.models.
    Using pytest for testing flow and faker for generating fake data.
"""

from datetime import datetime
from src.models import CommonDocument, RefinedDocument
from src.cleaners import clean_full, remove_html_tags
from faker import Faker

fake = Faker()


def test_common_document_creation():
    title = fake.sentence()
    url = fake.url()
    published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    description = fake.paragraph()

    doc = CommonDocument(
        title=title,
        url=url,
        published_at=published_at,
        description=description,
    )

    assert doc.title == clean_full(title)
    assert doc.url == remove_html_tags(url)
    assert doc.published_at == published_at
    assert doc.description == clean_full(description)


def test_common_document_to_kafka_payload():
    doc = CommonDocument(
        title=fake.sentence(),
        url=fake.url(),
        published_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description=fake.paragraph(),
    )

    payload = doc.to_kafka_payload()
    assert isinstance(payload, dict)
    assert payload["title"] == doc.title
    assert payload["url"] == doc.url


def test_refined_document_from_common():
    common_doc = CommonDocument(
        title=fake.sentence(),
        url=fake.url(),
        published_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description=fake.paragraph(),
    )

    refined_doc = RefinedDocument.from_common(common_doc)

    assert refined_doc.doc_id == str(common_doc.article_id)
    assert refined_doc.metadata["title"] == common_doc.title
    assert refined_doc.metadata["url"] == common_doc.url
