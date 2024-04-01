"""
    This script defines the ByteWax dataflow implementation for the Upstash use case. 
    The dataflow contains these steps:
        1. Input: Read data from a Kafka stream.
        2. Refine: Transform the input data into a common format.
        3. Chunkenize: Split the input data into smaller chunks.
        4. Embed: Generate embeddings for the input data.
        5. Output: Write the output data to the Upstash vector database.
"""

from pathlib import Path
from typing import Optional

import bytewax.operators as op
from vector import UpstashVectorOutput
from consumer import process_message, build_kafka_stream_client
from bytewax.connectors.kafka import KafkaSource
from bytewax.dataflow import Dataflow
from bytewax.outputs import DynamicSink
from embeddings import TextEmbedder
from models import ChunkedDocument, EmbeddedDocument, RefinedDocument
from logger import get_logger

logger = get_logger(__name__)


def build(
    model_cache_dir: Optional[Path] = None,
) -> Dataflow:
    """
    Build the ByteWax dataflow for the Upstash use case.
    Follows this dataflow:
        * 1. Tag: ['kafka_input']   = The input data is read from a KafkaSource
        * 2. Tag: ['map_kinp']      = Process message from KafkaSource to CommonDocument
            * 2.1 [Optional] Tag ['dbg_map_kinp'] = Debugging after ['map_kinp']
        * 3. Tag: ['refine']        = Convert the message to a refined document format
            * 3.1 [Optional] Tag ['dbg_refine'] = Debugging after ['refine']
        * 4. Tag: ['chunkenize']    = Split the refined document into smaller chunks
            * 4.1 [Optional] Tag ['dbg_chunkenize'] = Debugging after ['chunkenize']
        * 5. Tag: ['embed']         = Generate embeddings for the chunks
            * 5.1 [Optional] Tag ['dbg_embed'] = Debugging after ['embed']
        * 6. Tag: ['output']        = Write the embeddings to the Upstash vector database
    Note:
        Each Optional Tag is a debugging step that can be enabled for troubleshooting.
    """
    model = TextEmbedder(cache_dir=model_cache_dir)

    dataflow = Dataflow(flow_id="news-to-upstash")
    stream = op.input(
        step_id="kafka_input",
        flow=dataflow,
        source=_build_input(),
    )
    stream = op.flat_map("map_kinp", stream, process_message)
    # _ = op.inspect("dbg_map_kinp", stream)
    stream = op.map("refine", stream, RefinedDocument.from_common)
    # _ = op.inspect("dbg_refine", stream)
    stream = op.flat_map(
        "chunkenize",
        stream,
        lambda refined_doc: ChunkedDocument.from_refined(refined_doc, model),
    )
    # _ = op.inspect("dbg_chunkenize", stream)
    stream = op.map(
        "embed",
        stream,
        lambda chunked_doc: EmbeddedDocument.from_chunked(chunked_doc, model),
    )
    # _ = op.inspect("dbg_embed", stream)
    stream = op.output("output", stream, _build_output())
    logger.info("Successfully created bytewax dataflow.")
    logger.info(
        "\tStages: Kafka Input -> Map -> Refine -> Chunkenize -> Embed -> Upsert"
    )
    return dataflow


def _build_input() -> KafkaSource:
    return build_kafka_stream_client()


def _build_output() -> DynamicSink:
    return UpstashVectorOutput()
