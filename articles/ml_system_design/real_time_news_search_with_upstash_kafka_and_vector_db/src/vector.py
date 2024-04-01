from typing import Optional, List

from bytewax.outputs import DynamicSink, StatelessSinkPartition
from upstash_vector import Index, Vector
from models import EmbeddedDocument
from settings import settings
from logger import get_logger


logger = get_logger(__name__)


class UpstashVectorOutput(DynamicSink):
    """A class representing a Upstash vector output.

    This class is used to create a Upstash vector output, which is a type of dynamic output that supports
    at-least-once processing. Messages from the resume epoch will be duplicated right after resume.

    Args:
        vector_size (int): The size of the vector.
        collection_name (str, optional): The name of the collection.
            Defaults to constants.VECTOR_DB_OUTPUT_COLLECTION_NAME.
        client (Optional[UpstashClient], optional): The Upstash client. Defaults to None.
    """

    def __init__(
        self,
        vector_size: int = settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
        collection_name: str = settings.UPSTASH_VECTOR_TOPIC,
        client: Optional[Index] = None,
    ):
        self._collection_name = collection_name
        self._vector_size = vector_size

        if client:
            self.client = client
        else:
            self.client = Index(
                url=settings.UPSTASH_VECTOR_ENDPOINT,
                token=settings.UPSTASH_VECTOR_KEY,
                retries=settings.UPSTASH_VECTOR_RETRIES,
                retry_interval=settings.UPSTASH_VECTOR_WAIT_INTERVAL,
            )

    def build(
        self, step_id: str, worker_index: int, worker_count: int
    ) -> StatelessSinkPartition:
        return UpstashVectorSink(self.client, self._collection_name)


class UpstashVectorSink(StatelessSinkPartition):
    """
    A sink that writes document embeddings to an Upstash Vector database collection.
    This implementation enhances error handling and logging, utilizes batch upserts for efficiency,
    and follows Pythonic best practices for readability and maintainability.

    Args:
        client (Index): The Upstash Vector client to use for writing.
        collection_name (str, optional): The name of the collection to write to.
            Defaults to the value of the UPSTASH_VECTOR_TOPIC environment variable.
    """

    def __init__(
        self,
        client: Index,
        collection_name: str = None,
    ):
        self._client = client
        self._collection_name = collection_name
        self._upsert_batch_size = settings.UPSTASH_VECTOR_UPSERT_BATCH_SIZE

    def write_batch(self, documents: List[EmbeddedDocument]):
        """
        Writes a batch of document embeddings to the configured Upstash Vector database collection.

        Args:
            documents (List[EmbeddedDocument]): The documents to write.
        """
        vectors = [
            Vector(id=doc.doc_id, vector=doc.embeddings, metadata=doc.metadata)
            for doc in documents
        ]

        # Batch upsert for efficiency
        for i in range(0, len(vectors), self._upsert_batch_size):
            batch_vectors = vectors[i : i + self._upsert_batch_size]
            try:
                self._client.upsert(vectors=batch_vectors)
            except Exception as e:
                logger.error(f"Caught an exception during batch upsert {e}")
