"""
    Helper methods to interact witth VectorDB
"""

import fire
from .settings import settings
from .logger import get_logger
from upstash_vector import Index

logger = get_logger("[DEV][Helpers]")


class VectorDBHelper:
    def clean_vectordb(self):
        """
        Cleans the VectorDB by fetching 10 samples and then resetting the index.
        """
        index = Index(
            url=settings.UPSTASH_VECTOR_ENDPOINT, token=settings.UPSTASH_VECTOR_KEY
        )
        logger.info("Fetching 10 samples from VectorDB")
        _samples = index.range(limit=10, include_vectors=False, include_metadata=True)
        logger.info("10 samples: OK")
        logger.info(f"{_samples}")
        logger.info("CAUTION!!: Cleaning VectorDB")
        index.reset()
        logger.info("Cleaning VectorDB: OK")


def main():
    fire.Fire(VectorDBHelper)


if __name__ == "__main__":
    main()
