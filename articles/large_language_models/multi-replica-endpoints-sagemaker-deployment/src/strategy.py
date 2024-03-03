import enum
import logging
from typing import Optional

from sagemaker.enums import EndpointType

from src.interfaces import DeploymentStrategy
from src.settings import settings


class SagemakerHuggingfaceStrategy(DeploymentStrategy):
    def __init__(self, deployment_service):
        """
        Initializes the deployment strategy with the necessary services.

        :param deployment_service: The service handling the deployment details.
        :param logger: Logger for logging information and errors.
        """
        self.deployment_service = deployment_service

    def deploy(
        self,
        role_arn: str,
        llm_image: str,
        config: dict,
        endpoint_name: str,
        endpoint_config_name: str,
        gpu_instance_type: str,
        resources: Optional[dict] = None,
        endpoint_type: enum.Enum = EndpointType.MODEL_BASED,
    ) -> None:
        """
        Initiates the deployment process for a HuggingFace model on AWS SageMaker.

        :param role_arn: AWS role ARN with permissions for SageMaker deployment.
        :param llm_image: URI for the HuggingFace model Docker image.
        :param config: Configuration settings for the model environment.
        :param endpoint_name: Name of the SageMaker endpoint.
        :param endpoint_config_name: Name of the SageMaker endpoint configuration.
        :param resources: Optional resources for the model deployment(used for multi model endpoints)
        :param endpoint_type: can be EndpointType.MODEL_BASED (without inference component)
                or EndpointType.INFERENCE_COMPONENT (with inference component)

        """
        logging.info("Starting deployment using Sagemaker Huggingface Strategy...")
        logging.info(
            f"Deployment parameters: nb of replicas: {settings.COPIES}, nb of gpus:{settings.GPUS}, instance_type:{settings.GPU_INSTANCE_TYPE}"
        )
        try:
            # Delegate to the deployment service to handle the actual deployment details
            self.deployment_service.deploy(
                role_arn=role_arn,
                llm_image=llm_image,
                config=config,
                endpoint_name=endpoint_name,
                endpoint_config_name=endpoint_config_name,
                gpu_instance_type=gpu_instance_type,
                resources=resources,
                endpoint_type=endpoint_type,
            )
            logging.info("Deployment completed successfully.")
        except Exception as e:
            logging.error(f"Error during deployment: {e}")
            raise
