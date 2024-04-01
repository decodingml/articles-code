import json
from typing import List

from bytewax.connectors.kafka import KafkaSinkMessage, KafkaSource

from logger import get_logger
from models import CommonDocument
from settings import settings

logger = get_logger(__name__)


def build_kafka_stream_client():
    """
    Build a Kafka stream client to read messages from the Upstash Kafka topic using the ByteWax KafkaSource connector.
    """
    kafka_config = {
        "bootstrap.servers": settings.UPSTASH_KAFKA_ENDPOINT,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "SCRAM-SHA-256",
        "sasl.username": settings.UPSTASH_KAFKA_UNAME,
        "sasl.password": settings.UPSTASH_KAFKA_PASS,
        "auto.offset.reset": "earliest",  # Start reading at the earliest message
    }
    kafka_input = KafkaSource(
        topics=[settings.UPSTASH_KAFKA_TOPIC],
        brokers=[settings.UPSTASH_KAFKA_ENDPOINT],
        add_config=kafka_config,
    )
    logger.info("KafkaSource client created successfully.")
    return kafka_input


def process_message(message: KafkaSinkMessage):
    """
    On a Kafka message, process the message and return a list of CommonDocuments.
    - message: KafkaSinkMessage(key, value) where value is the message payload.
    """
    documents: List[CommonDocument] = []
    try:
        json_str = message.value.decode("utf-8")
        data = json.loads(json_str)
        documents = [CommonDocument.from_json(obj) for obj in data]
        logger.info(f"Decoded into {len(documents)} CommonDocuments")
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
