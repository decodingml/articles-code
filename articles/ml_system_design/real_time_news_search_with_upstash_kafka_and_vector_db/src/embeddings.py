"""
    This module contains the `TextEmbedder` class, which is a Singleton class.
    The `TextEmbedder` class is responsible for tokenizing and generating embeddings
    based on a given input text using a pre-trained transformer model that is defined in settings.py.
"""

import traceback
from pathlib import Path
from threading import Lock
from typing import Optional, Union

import numpy as np
from transformers import AutoModel, AutoTokenizer

from settings import settings
from logger import get_logger

logger = get_logger(__name__)


class SingletonMeta(type):
    """
    A thread-safe implementation of the Singleton pattern.
    Utilizes a class-level lock to ensure that only one instance
    of the Singleton class can be created across threads.
    """

    _instances = {}
    _lock = (
        Lock()
    )  # A lock object to synchronize threads during the first instantiation.

    def __call__(cls, *args, **kwargs):
        """
        Overrides the default __call__ method. Ensures that only one instance
        of the Singleton class can be created (per subclass), regardless of
        how many times it is called, and ensures thread safety.
        """
        if cls not in cls._instances:
            with cls._lock:
                # Double-check if the instance was created while this thread was waiting
                # on the lock to ensure it doesn't create another Singleton instance.
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class TextEmbedder(metaclass=SingletonMeta):
    def __init__(
        self,
        model_id: str = settings.EMBEDDING_MODEL_ID,
        max_input_length: int = settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
        device: str = settings.EMBEDDING_MODEL_DEVICE,
        cache_dir: Optional[Path] = None,
        token_limit: int = 256,
    ):
        self._model_id = model_id
        self._device = device
        self._max_input_length = int(max_input_length)
        self._token_limit = token_limit

        self._tokenizer = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModel.from_pretrained(
            model_id,
            cache_dir=str(cache_dir) if cache_dir else None,
        ).to(self._device)
        self._model.eval()

    @property
    def token_limit(self) -> str:
        return self._token_limit

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def max_input_length(self) -> int:
        return int(self._max_input_length)

    @property
    def tokenizer(self) -> AutoTokenizer:
        return self._tokenizer

    def __call__(
        self, input_text: str, to_list: bool = True
    ) -> Union[np.ndarray, list]:
        try:
            tokenized_text = self._tokenizer(
                input_text,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=self._max_input_length,
            ).to(self._device)
        except Exception:
            logger.error(traceback.format_exc())
            logger.error(f"Error tokenizing the following input text: {input_text}")

            return [] if to_list else np.array([])

        try:
            result = self._model(**tokenized_text)
        except Exception:
            logger.error(traceback.format_exc())
            logger.error(
                f"Error generating embeddings for the following model_id: {self._model_id} and input text: {input_text}"
            )

            return [] if to_list else np.array([])

        embeddings = result.last_hidden_state[:, 0, :].cpu().detach().numpy()
        if to_list:
            embeddings = embeddings.flatten().tolist()

        return embeddings
