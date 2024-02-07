import hashlib
from typing import Optional, Tuple, Union

import numpy as np
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)
from pydantic import BaseModel
from qdrant_client.models import ScoredPoint, Record
from unstructured.cleaners.core import (
    clean,
    clean_non_ascii_chars,
    replace_unicode_quotes,
)

from src.cleaning import (
    remove_emojis_and_symbols,
    replace_urls_with_placeholder,
    unbold_text,
    unitalic_text,
)
from src.embeddings import EmbeddingModelSingleton


class RawPost(BaseModel):
    post_id: str
    text: str
    image: Optional[str]

    @classmethod
    def from_source(cls, k_v: Tuple[str, dict]) -> "RawPost":
        k, v = k_v

        return cls(post_id=k, text=v["text"], image=v.get("image", None))


class CleanedPost(BaseModel):
    post_id: str
    raw_text: str
    text: str
    image: Optional[str]

    @classmethod
    def from_raw_post(cls, raw_post: RawPost) -> "CleanedPost":
        cleaned_text = CleanedPost.clean(raw_post.text)

        return cls(
            post_id=raw_post.post_id,
            raw_text=raw_post.text,
            text=cleaned_text,
            image=raw_post.image,
        )
        
    @staticmethod
    def clean(text: str) -> str:
        cleaned_text = unbold_text(text)
        cleaned_text = unitalic_text(cleaned_text)
        cleaned_text = remove_emojis_and_symbols(cleaned_text)
        cleaned_text = clean(cleaned_text)
        cleaned_text = replace_unicode_quotes(cleaned_text)
        cleaned_text = clean_non_ascii_chars(cleaned_text)
        cleaned_text = replace_urls_with_placeholder(cleaned_text)
        
        return cleaned_text


class ChunkedPost(BaseModel):
    post_id: str
    chunk_id: str
    full_raw_text: str
    text: str
    image: Optional[str]

    @classmethod
    def from_cleaned_post(
        cls, cleaned_post: CleanedPost, embedding_model: EmbeddingModelSingleton
    ) -> list["ChunkedPost"]:
        chunks = ChunkedPost.chunk(cleaned_post.text, embedding_model)

        return [
            cls(
                post_id=cleaned_post.post_id,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                full_raw_text=cleaned_post.raw_text,
                text=chunk,
                image=cleaned_post.image,
            )
            for chunk in chunks
        ]
        
    @staticmethod
    def chunk(text: str, embedding_model: EmbeddingModelSingleton) -> list[str]:
        character_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n"], chunk_size=500, chunk_overlap=0
        )
        text_sections = character_splitter.split_text(text)

        token_splitter = SentenceTransformersTokenTextSplitter(
            chunk_overlap=50,
            tokens_per_chunk=embedding_model.max_input_length,
            model_name=embedding_model.model_id,
        )

        chunks = []
        for text_section in text_sections:
            chunks.extend(token_splitter.split_text(text_section))
            
        return chunks


class EmbeddedChunkedPost(BaseModel):
    post_id: str
    chunk_id: str
    full_raw_text: str
    text: str
    text_embedding: list
    image: Optional[str] = None
    score: Optional[float] = None
    rerank_score: Optional[float] = None

    @classmethod
    def from_chunked_post(
        cls, chunked_post: ChunkedPost, embedding_model: EmbeddingModelSingleton
    ) -> "EmbeddedChunkedPost":
        return cls(
            post_id=chunked_post.post_id,
            chunk_id=chunked_post.chunk_id,
            full_raw_text=chunked_post.full_raw_text,
            text=chunked_post.text,
            text_embedding=embedding_model(chunked_post.text, to_list=True),
            image=chunked_post.image,
        )

    @classmethod
    def from_retrieved_point(cls, point: Union[ScoredPoint, Record]) -> "EmbeddedChunkedPost":
        return cls(
            post_id=point.payload["post_id"],
            chunk_id=point.id,
            full_raw_text=point.payload["full_raw_text"],
            text=point.payload["text"],
            text_embedding=point.vector,
            image=point.payload["image"],
            score=point.score if hasattr(point, "score") else None
        )

    def to_payload(self) -> tuple[str, np.ndarray, dict]:
        return (
            self.chunk_id,
            self.text_embedding,
            {
                "post_id": self.post_id,
                "text": self.text,
                "image": self.image,
                "full_raw_text": self.full_raw_text,
            },
        )

    def __str__(self) -> str:
        return f"EmbeddedChunkedPost(post_id={self.post_id}, chunk_id={self.chunk_id}, has_image={bool(self.image)}, text_embedding_length={len(self.text_embedding)})"

    def __hash__(self) -> int:
        return hash(self.chunk_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, EmbeddedChunkedPost):
            return False
        
        return self.chunk_id == other.chunk_id
