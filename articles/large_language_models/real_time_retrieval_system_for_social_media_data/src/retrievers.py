from io import BytesIO
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import requests
import umap
from IPython.display import HTML, display
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.http import models
from tqdm import tqdm

from src import settings
from src.embeddings import CrossEncoderModelSingleton, EmbeddingModelSingleton
from src.models import ChunkedPost, CleanedPost, EmbeddedChunkedPost


class QdrantVectorDBRetriever:
    def __init__(
        self,
        embedding_model: EmbeddingModelSingleton,
        vector_db_client: QdrantClient,
        cross_encoder_model: Optional[CrossEncoderModelSingleton] = None,
        vector_db_collection: str = settings.VECTOR_DB_OUTPUT_COLLECTION_NAME,
    ):
        self._embedding_model = embedding_model
        self._vector_db_client = vector_db_client
        self._cross_encoder_model = cross_encoder_model
        self._vector_db_collection = vector_db_collection

    def search(
        self, query: str, limit: int = 3, return_all: bool = False
    ) -> Union[list[EmbeddedChunkedPost], dict[str, list]]:
        embdedded_queries = self.embed_query(query)

        if self._cross_encoder_model:
            original_limit = limit
            limit = limit * 10
        else:
            original_limit = limit

        search_queries = [
            models.SearchRequest(
                vector=embedded_query, limit=limit, with_payload=True, with_vector=True
            )
            for embedded_query in embdedded_queries
        ]
        retrieved_points = self._vector_db_client.search_batch(
            collection_name=self._vector_db_collection,
            requests=search_queries,
        )

        posts = set()
        for chunk_retrieved_points in retrieved_points:
            posts.update(
                {
                    EmbeddedChunkedPost.from_retrieved_point(point)
                    for point in chunk_retrieved_points
                }
            )
        posts = list(posts)

        if self._cross_encoder_model:
            posts = self.rerank(query, posts)
        else:
            posts = sorted(posts, key=lambda x: x.score, reverse=True)

        posts = posts[:original_limit]

        if return_all:
            return {
                "posts": posts,
                "query": query,
                "embdedded_queries": embdedded_queries,
            }

        return posts

    def embed_query(self, query: str) -> list[list[float]]:
        cleaned_query = CleanedPost.clean(query)
        chunks = ChunkedPost.chunk(cleaned_query, self._embedding_model)
        embdedded_queries = [
            self._embedding_model(chunk, to_list=True) for chunk in chunks
        ]

        return embdedded_queries

    def rerank(
        self, query: str, posts: list[EmbeddedChunkedPost]
    ) -> list[EmbeddedChunkedPost]:
        pairs = [[query, f"{post.text}"] for post in posts]
        cross_encoder_scores = self._cross_encoder_model(pairs)
        ranked_posts = sorted(
            zip(posts, cross_encoder_scores), key=lambda x: x[1], reverse=True
        )

        reranked_posts = []
        for post, rerank_score in ranked_posts:
            post.rerank_score = rerank_score

            reranked_posts.append(post)

        return reranked_posts

    def scroll(self, limit: Optional[int] = None) -> list[EmbeddedChunkedPost]:
        if limit is None:
            collection_stats = self._vector_db_client.get_collection(
                collection_name=self._vector_db_collection
            )
            limit = collection_stats.points_count

        retrieved_points = self._vector_db_client.scroll(
            collection_name=self._vector_db_collection,
            limit=limit,
            with_payload=True,
            with_vectors=True,
        )
        retrieved_points = retrieved_points[0]
        posts = [
            EmbeddedChunkedPost.from_retrieved_point(point)
            for point in retrieved_points
        ]

        return posts

    def render_as_text(self, post: EmbeddedChunkedPost) -> None:
        print("#" * 80)
        print()
        print(f"Post ID: {post.post_id}")
        print(f"Chunk ID: {post.chunk_id}")
        if post.score is not None:
            print(f"Score: {post.score}")
        if post.rerank_score is not None:
            print(f"Rerank Score: {post.rerank_score}")
        print(f"Text Embedding Length: {len(post.text_embedding)}")
        print()
        print("#" * 80)
        print()
        print(f"Full Raw Text:\n\n{post.full_raw_text}")
        print()
        print("#" * 80)
        print()
        print(f"Text:\n\n{post.text}")
        print()
        print("#" * 80)
        print("\n\n\n")

        if post.image:
            response = requests.get(post.image)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.show()

    def render_as_html(self, post: EmbeddedChunkedPost) -> None:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; color: black; margin: 10px; padding: 20px; border-radius: 10px; background-color: #f3f3f3; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h2 style="color: #333;">Post ID: {post.post_id}</h2>
            <h3 style="color: #555;">Chunk ID: {post.chunk_id}</h3>
            <p><strong>Embedding Length:</strong> {len(post.text_embedding)}</p>
        """

        if post.score is not None:
            html_content += f"<p><strong>Score:</strong> {post.score}</p>"
        if post.rerank_score is not None:
            html_content += f"<p><strong>Rerank Score:</strong> {post.rerank_score}</p>"

        html_content += f"""
            <p><strong>Chunked Text:</strong> " {post.text} "</p>
            <p><strong>Full Raw Text:</strong> " {post.full_raw_text} "</p>
            
        """

        if post.image and False:
            response = requests.head(post.image)
            if response.status_code == 200:
                html_content += f'<img src="{post.image}" alt="Post Image" style="max-width: 500px; height: auto; border-radius: 5px; margin-top: 10px;">'

        html_content += "</div>"

        display(HTML(html_content))


class RetrievalVisualizer:
    def __init__(self, posts: list[EmbeddedChunkedPost]):
        self._posts = posts

        self._umap_transform = self._fit_model(self._posts)
        self._projected_post_embeddings = self.project_posts(self._posts)

    def _fit_model(self, posts: list[EmbeddedChunkedPost]) -> umap.UMAP:
        embeddings = np.array([post.text_embedding for post in posts])

        umap_transform = umap.UMAP(random_state=0, transform_seed=0)
        umap_transform = umap_transform.fit(embeddings)

        return umap_transform

    def project_posts(self, posts: list[EmbeddedChunkedPost]) -> np.ndarray:
        embeddings = np.array([post.text_embedding for post in posts])

        return self._project(embeddings=embeddings)

    def _project(self, embeddings: np.ndarray) -> np.ndarray:
        umap_embeddings = np.empty((len(embeddings), 2))

        for i, embedding in enumerate(tqdm(embeddings)):
            umap_embeddings[i] = self._umap_transform.transform([embedding])

        return umap_embeddings

    def render(
        self,
        embedded_queries: list[list[float]],
        retrieved_posts: list[EmbeddedChunkedPost],
    ) -> None:
        assert (
            self._umap_transform is not None
        ), "Must call `compute_projected_embeddings` first."

        embedded_queries = np.array(embedded_queries)
        projected_query_embeddings = self._project(embedded_queries)

        projected_retrieved_embeddings = self.project_posts(retrieved_posts)

        plt.figure(figsize=(10, 6))
        plt.scatter(
            self._projected_post_embeddings[:, 0],
            self._projected_post_embeddings[:, 1],
            s=10,
            color="gray",
            label="All Posts Embeddings",
        )
        plt.scatter(
            projected_query_embeddings[:, 0],
            projected_query_embeddings[:, 1],
            s=100,
            marker="x",
            color="k",
            label="Query Embeddings",
        )
        plt.scatter(
            projected_retrieved_embeddings[:, 0],
            projected_retrieved_embeddings[:, 1],
            s=100,
            facecolors="none",
            edgecolors="tab:orange",
            label="Retrieved Posts Embeddings",
        )

        plt.gca().set_aspect("equal", "datalim")
        plt.axis("off")
        plt.title("Visualization of Retrieved Embeddings")
        plt.legend(loc="best")
        plt.show()
