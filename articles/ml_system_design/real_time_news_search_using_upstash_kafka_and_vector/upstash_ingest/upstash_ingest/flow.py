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
from bytewax.dataflow import Dataflow
from bytewax.inputs import DynamicSource
from consumer import UpstashKafkaStreamSource
from embeddings import TextEmbedder
from models import ChunkedDocument, EmbeddedDocument, RefinedDocument
from vector import UpstashVectorOutput


def build(
    model_cache_dir: Optional[Path] = None,
) -> Dataflow:
    model = TextEmbedder(cache_dir=model_cache_dir)

    dataflow = Dataflow(flow_id="news-to-upstash")
    stream = op.input(
        step_id="input",
        flow=dataflow,
        source=_build_input(),
    )
    stream = op.map("refine", stream, RefinedDocument.from_common)
    stream = op.flat_map(
        "chunkenize",
        stream,
        lambda refined_doc: ChunkedDocument.from_refined(refined_doc, model),
    )
    stream = op.map(
        "embed",
        stream,
        lambda chunked_doc: EmbeddedDocument.from_chunked(chunked_doc, model),
    )
    stream = op.output("output", stream, _build_output())
    return dataflow


def _build_input() -> DynamicSource:
    return UpstashKafkaStreamSource()


def _build_output():
    return UpstashVectorOutput()
