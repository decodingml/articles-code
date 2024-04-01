"""
    Pydantic models definition used within the news data pipeline.
    Implementation contains models for different NewsArticle formats:
    - NewsDataIOModel: Model for NewsDataIO API response.
    - NewsAPIModel: Model for NewsAPI response.
    
    Rest of the models are used for data processing and exchange within the pipeline:
    - CommonDocument: Common representation of a news article.
    - RefinedDocument: Refined version of a CommonDocument.
    - ChunkedDocument: Chunked version of a RefinedDocument.
    - EmbeddedDocument: Embedded version of a ChunkedDocument.
     
"""

import datetime
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from dateutil import parser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field, field_validator
from unstructured.staging.huggingface import chunk_by_attention_window

from cleaners import clean_full, normalize_whitespace, remove_html_tags
from embeddings import TextEmbedder

logger = logging.getLogger(__name__)

RECURSIVE_SPLITTER = RecursiveCharacterTextSplitter()


class DocumentSource(BaseModel):
    id: Optional[str]
    name: str


class RefinedDocument(BaseModel):
    doc_id: str
    full_text: str = ""
    metadata: dict = {}

    @classmethod
    def from_common(cls, common: "CommonDocument") -> "RefinedDocument":
        """Converts a CommonDocument to refined document format."""
        refined = RefinedDocument(doc_id=str(common.article_id))
        refined.metadata = {
            "title": common.title,
            "url": common.url,
            "published_at": common.published_at,
            "source_name": common.source_name,
            "author": common.author,
            "image_url": common.image_url,
        }
        refined.full_text = ".".join([common.title, common.description])
        return refined


class ChunkedDocument(BaseModel):
    doc_id: str
    chunk_id: str
    full_raw_text: str
    text: str
    metadata: Dict[str, Union[str, Any]]

    @classmethod
    def from_refined(
        cls, refined_doc: RefinedDocument, embedding_model: TextEmbedder
    ) -> list["ChunkedDocument"]:
        chunks = ChunkedDocument.chunkenize(refined_doc.full_text, embedding_model)

        return [
            cls(
                doc_id=refined_doc.doc_id,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                full_raw_text=refined_doc.full_text,
                text=chunk,
                metadata=refined_doc.metadata,
            )
            for chunk in chunks
        ]

    @staticmethod
    def chunkenize(text: str, embedding_model: TextEmbedder) -> list[str]:
        text_sections = RECURSIVE_SPLITTER.split_text(text=text)
        chunks = []
        for text_section in text_sections:
            chunks.extend(
                chunk_by_attention_window(text_section, embedding_model.tokenizer)
            )

        return chunks


class EmbeddedDocument(BaseModel):
    doc_id: str
    chunk_id: str
    full_raw_text: str
    text: str
    embeddings: List[float]
    metadata: Dict[str, Union[str, Any]] = {}

    @classmethod
    def from_chunked(
        cls, chunked_doc: ChunkedDocument, embedding_model: TextEmbedder
    ) -> "EmbeddedDocument":
        return cls(
            doc_id=chunked_doc.doc_id,
            chunk_id=chunked_doc.chunk_id,
            full_raw_text=chunked_doc.full_raw_text,
            text=chunked_doc.text,
            embeddings=embedding_model(chunked_doc.text, to_list=True),
            metadata=chunked_doc.metadata,
        )

    def to_payload(self) -> tuple[str, List[float], dict]:
        return (self.chunk_id, self.embeddings, self.metadata)

    def __repr__(self) -> str:
        return f"EmbeddedDocument(doc_id={self.doc_id}, chunk_id={self.chunk_id})"


class CommonDocument(BaseModel):
    article_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(default_factory=lambda: "N/A")
    url: str = Field(default_factory=lambda: "N/A")
    published_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    source_name: str = Field(default_factory=lambda: "Unknown")
    image_url: Optional[str] = Field(default_factory=lambda: None)
    author: Optional[str] = Field(default_factory=lambda: "Unknown")
    description: Optional[str] = Field(default_factory=lambda: None)
    content: Optional[str] = Field(default_factory=lambda: None)

    @field_validator("title", "description", "content")
    def clean_text_fields(cls, v):
        if v is None or v == "":
            return "N/A"
        return clean_full(v)

    @field_validator("url", "image_url")
    def clean_url_fields(cls, v):
        if v is None:
            return "N/A"
        v = remove_html_tags(v)
        v = normalize_whitespace(v)
        return v

    @field_validator("published_at")
    def clean_date_field(cls, v):
        try:
            parsed_date = parser.parse(v)
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            logger.error(f"Error parsing date: {v}, using current date instead.")

    @classmethod
    def from_json(cls, data: dict) -> "CommonDocument":
        """Create a CommonDocument from a JSON object."""
        return cls(**data)

    def to_kafka_payload(self) -> dict:
        """Prepare the common representation for Kafka payload."""
        return self.model_dump(exclude_none=False)


class NewsDataIOModel(BaseModel):
    article_id: str
    title: str
    link: str
    description: Optional[str]
    pubDate: str
    source_id: Optional[str]
    source_url: Optional[str]
    source_icon: Optional[str]
    creator: Optional[List[str]]
    image_url: Optional[str]
    content: Optional[str]

    def to_common(self) -> CommonDocument:
        """Convert to common news article format."""
        return CommonDocument(
            article_id=self.article_id,
            title=self.title,
            description=self.description,
            url=self.link,
            published_at=self.pubDate,
            source_name=self.source_id or "Unknown",
            image_url=self.image_url,
            author=", ".join(self.creator) if self.creator else None,
            content=self.content,
        )


class NewsAPIModel(BaseModel):
    source: DocumentSource
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    urlToImage: Optional[str]
    publishedAt: str
    content: Optional[str]

    def to_common(self) -> CommonDocument:
        """Convert to common news article format."""
        return CommonDocument(
            title=self.title,
            description=self.description,
            url=self.url,
            published_at=self.publishedAt,
            source_name=self.source.name,
            source_id=self.source.id,
            author=self.author,
            image_url=self.urlToImage,
            content=self.content,
        )
