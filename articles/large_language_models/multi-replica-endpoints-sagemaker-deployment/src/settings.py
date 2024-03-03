import json
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sagemaker.compute_resource_requirements.resource_requirements import (
    ResourceRequirements,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "../.env"))


class CommonSettings(BaseSettings):
    ARN_ROLE: str = "str"
    HUGGING_FACE_HUB_TOKEN: str = "str"


class ModelDeploySettings(CommonSettings):
    HF_MODEL_ID: str = "test"
    GPU_INSTANCE_TYPE: str = "test"
    SM_NUM_GPUS: int = 1
    MAX_INPUT_LENGTH: int = 4095
    MAX_TOTAL_TOKENS: int = 4096
    MAX_BATCH_TOTAL_TOKENS: int = 8192
    COPIES: int = 4  # Number of replicas
    GPUS: int = 1  # Number of GPUs
    CPUS: int = 8  # Number of CPU cores  96 // num_replica - more for management
    RETURN_FULL_TEXT: bool = False


class SummarizationSettings(CommonSettings):
    SAGEMAKER_ENDPOINT_CONFIG_SUMMARIZATION: str = "test"
    SAGEMAKER_INFERENCE_COMPONENT_SUMMARIZATION: str = "test"
    SAGEMAKER_ENDPOINT_SUMMARIZATION: str = "test"
    SAGEMAKER_MODEL_SUMMARIZATION: str = "test"
    TEMPERATURE_SUMMARY: float = 0.8
    TOP_P_SUMMARY: float = 0.9
    MAX_NEW_TOKENS_SUMMARY: int = 150


class Settings(ModelDeploySettings, SummarizationSettings):

    @property
    def model_resource_config(self):
        return ResourceRequirements(
            requests={
                "copies": self.COPIES,
                "num_accelerators": self.GPUS,
                "num_cpus": self.CPUS,
                "memory": 5 * 1024,  # Example value, adjust based on your needs
            },
        )

    @property
    def hugging_face_deploy_config(self):
        return {
            "HF_MODEL_ID": self.HF_MODEL_ID,
            "SM_NUM_GPUS": json.dumps(self.SM_NUM_GPUS),
            "MAX_INPUT_LENGTH": json.dumps(self.MAX_INPUT_LENGTH),
            "MAX_TOTAL_TOKENS": json.dumps(self.MAX_TOTAL_TOKENS),
            "MAX_BATCH_TOTAL_TOKENS": json.dumps(self.MAX_BATCH_TOTAL_TOKENS),
            "HUGGING_FACE_HUB_TOKEN": self.HUGGING_FACE_HUB_TOKEN,
        }

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../.env")


settings = Settings()
