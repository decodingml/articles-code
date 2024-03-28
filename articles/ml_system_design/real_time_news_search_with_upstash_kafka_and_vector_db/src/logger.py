"""
    Common logger definition for all modules. 
    Logger format will look like this:
        [01/01/2021 00:00:00.000][INFO][upstash.logger] : This is an info message.
"""

import logging

logger_config = {
    "format": ("[%(asctime)s.%(msecs)03d][%(levelname)s][%(name)s] : %(message)s"),
    "level": logging.INFO,
    "datefmt": "%d/%m/%Y %H:%M:%S",
    "force": True,
}


def get_logger(name: str) -> logging.Logger:
    """Create a logger with the specified name."""
    logging.basicConfig(**logger_config)
    logger = logging.getLogger(name)
    return logger
