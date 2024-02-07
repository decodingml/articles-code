import os
from typing import Optional

from bytewax.outputs import DynamicSink, StatelessSinkPartition
from qdrant_client import QdrantClient
from qdrant_client.http.api_client import UnexpectedResponse
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import Batch

from src import settings
from src.models import EmbeddedChunkedPost


class QdrantVectorOutput(DynamicSink):
    """A class representing a Qdrant vector output.

    This class is used to create a Qdrant vector output, which is a type of dynamic output that supports
    at-least-once processing. Messages from the resume epoch will be duplicated right after resume.

    Args:
        vector_size (int): The size of the vector.
        collection_name (str, optional): The name of the collection.
            Defaults to settings.VECTOR_DB_OUTPUT_COLLECTION_NAME.
        client (Optional[QdrantClient], optional): The Qdrant client. Defaults to None.
    """

    def __init__(
        self,
        vector_size: int,
        collection_name: str = settings.VECTOR_DB_OUTPUT_COLLECTION_NAME,
        client: Optional[QdrantClient] = None,
    ):
        self._collection_name = collection_name
        self._vector_size = vector_size

        if client:
            self.client = client
        else:
            self.client = build_qdrant_client()

        try:
            self.client.get_collection(collection_name=self._collection_name)
        except (UnexpectedResponse, ValueError):
            self.client.recreate_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=self._vector_size, distance=Distance.COSINE
                ),
            )

    def build(self, worker_index, worker_count) -> "QdrantVectorSink":
        """Builds a QdrantVectorSink object.

        Args:
            worker_index (int): The index of the worker.
            worker_count (int): The total number of workers.

        Returns:
            QdrantVectorSink: A QdrantVectorSink object.
        """

        return QdrantVectorSink(self.client, self._collection_name)


def build_qdrant_client(url: Optional[str] = None, api_key: Optional[str] = None):
    """
    Builds a QdrantClient object with the given URL and API key.

    Args:
        url (Optional[str]): The URL of the Qdrant server. If not provided,
            it will be read from the QDRANT_URL environment variable.
        api_key (Optional[str]): The API key to use for authentication. If not provided,
            it will be read from the QDRANT_API_KEY environment variable.

    Raises:
        KeyError: If the QDRANT_URL or QDRANT_API_KEY environment variables are not set
            and no values are provided as arguments.

    Returns:
        QdrantClient: A QdrantClient object connected to the specified Qdrant server.
    """

    client_kwargs = {}
    if url is None:
        try:
            url = os.environ["QDRANT_URL"]
        except KeyError:
            raise KeyError(
                "QDRANT_URL must be set as environment variable or manually passed as an argument."
            )
    client_kwargs["url"] = url

    if api_key is None:
        api_key = os.environ.get("QDRANT_API_KEY")
    if api_key:
        client_kwargs["url"] = url

    client = QdrantClient(**client_kwargs)

    return client


class QdrantVectorSink(StatelessSinkPartition):
    """
    A sink that writes document embeddings to a Qdrant collection.

    Args:
        client (QdrantClient): The Qdrant client to use for writing.
        collection_name (str, optional): The name of the collection to write to.
            Defaults to settings.VECTOR_DB_OUTPUT_COLLECTION_NAME.
    """

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = settings.VECTOR_DB_OUTPUT_COLLECTION_NAME,
    ):
        self._client = client
        self._collection_name = collection_name

    def write_batch(self, chunks: list[EmbeddedChunkedPost]):
        ids = []
        embeddings = []
        metadata = []
        for chunk in chunks:
            chunk_id, text_embedding, chunk_metadata = chunk.to_payload()

            ids.append(chunk_id)
            embeddings.append(text_embedding)
            metadata.append(chunk_metadata)

        self._client.upsert(
            collection_name=self._collection_name,
            points=Batch(
                ids=ids,
                vectors=embeddings,
                payloads=metadata,
            ),
        )
