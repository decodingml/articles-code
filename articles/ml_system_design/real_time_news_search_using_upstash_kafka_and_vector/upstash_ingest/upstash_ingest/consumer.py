import json
from typing import Iterable, List
from kafka import KafkaConsumer

from bytewax.inputs import DynamicSource, StatelessSourcePartition
from models import CommonDocument
from settings import settings

from logger import get_logger

logger = get_logger(__name__)


class UpstashKafkaStreamSource(DynamicSource):
    """Builds a KafkaStreamClient instance as a DynamicSource for Bytewax."""

    def __init__(self):
        self._consumer = KafkaStreamClient(
            kafka_topic=settings.UPSTASH_KAFKA_TOPIC,
            kafka_endpoint=settings.UPSTASH_KAFKA_ENDPOINT,
        )

    def build(
        self, step_id: str, worker_index: int, worker_count: int
    ) -> "KafkaStreamClient":
        return KafkaStreamClient()


class KafkaStreamClient(StatelessSourcePartition):
    def __init__(
        self,
        kafka_topic: str = settings.UPSTASH_KAFKA_TOPIC,
        kafka_endpoint: str = settings.UPSTASH_KAFKA_ENDPOINT,
    ):
        """
        Initializes the KafkaStream consumer with the given topic and endpoint.
        """
        self._client = KafkaConsumer(
            kafka_topic,
            bootstrap_servers=kafka_endpoint,
            sasl_mechanism="SCRAM-SHA-256",
            security_protocol="SASL_SSL",
            sasl_plain_username=settings.UPSTASH_KAFKA_UNAME,
            sasl_plain_password=settings.UPSTASH_KAFKA_PASS,
            auto_offset_reset="earliest",
        )

    def next_batch(self) -> Iterable:
        """
        Retrieves the next batch of documents from the client.

        Returns:
            An iterable of CommonDocument instances containing the retrieved documents.
        Raises:
            JSONDecodeError: If there is an error in decoding the JSON message.
            Other potential exceptions should be documented here.
        """
        documents: List[CommonDocument] = []
        try:
            message = next(self._client)
            json_str = message.value.decode("utf-8")
            data = json.loads(json_str)
            documents = [CommonDocument.from_json(obj) for obj in data]
            return documents
        except StopIteration:
            logger.info("No more documents to fetch from the client.")
        except KeyError as e:
            logger.error(f"Key error in processing document batch: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from message: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in next_batch: {e}")
