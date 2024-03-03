import logging
import time

import boto3

from src.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def delete_endpoint(endpoint_name: str, inference_component_name: str) -> None:

    sagemaker_client = boto3.client("sagemaker")

    logging.info(f"Deleting inference components for: {endpoint_name}")

    sagemaker_client.delete_inference_component(InferenceComponentName=inference_component_name)

    time.sleep(120)

    sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
    logging.info(f"Deleting endpoint : {endpoint_name}")


def delete_sagemaker_resources(endpoint_name: str, model_name: str, endpoint_config_name: str) -> None:
    """Deletes the SageMaker resources for a given endpoint name."""
    sagemaker_client = boto3.client("sagemaker")
    logging.info(f"Delete Initialized for: {endpoint_name}")

    try:

        try:
            inference_components = sagemaker_client.list_inference_components(EndpointNameEquals=endpoint_name)
            for component in inference_components["InferenceComponents"]:
                inference_component_name = component["InferenceComponentName"]
                # if component["InferenceComponentStatus"] == "InService":
                sagemaker_client.delete_inference_component(InferenceComponentName=inference_component_name)
                logging.info(f"Deleting inference components for: {endpoint_name}")
                time.sleep(120)
                logging.info(f"Deleted inference components for: {endpoint_name}")

        except sagemaker_client.exceptions.ClientError as e:
            logging.error(f"Error listing inference components: {e}")
            raise

        # Delete the endpoint
        try:
            sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        except sagemaker_client.exceptions.ClientError as e:
            logging.error(f"Error deleting endpoint: {e}")

        # Delete the endpoint configuration
        try:
            sagemaker_client.delete_endpoint_config(EndpointConfigName=endpoint_config_name)
            logging.info(f"Deleted endpoint configuration: {endpoint_config_name}")
        except sagemaker_client.exceptions.ClientError as e:
            logging.error(f"Error deleting endpoint configuration: {e}")

        # Delete the model
        try:
            sagemaker_client.delete_model(ModelName=model_name)
            logging.info(f"Deleted model: {model_name}")
        except sagemaker_client.exceptions.ClientError as e:
            logging.error(f"Error deleting model: {e}")

    except Exception as e:
        logging.error(f"Error in deleting SageMaker resources: {e}")
        raise


def perform_delete_sagemaker_resources(task_name):
    """Performs the deletion of SageMaker resources for a given task name."""

    if task_name == "summarization":
        endpoint_name = settings.SAGEMAKER_ENDPOINT_SUMMARIZATION
        model_name = settings.SAGEMAKER_MODEL_SUMMARIZATION
        endpoint_config_name = settings.SAGEMAKER_ENDPOINT_CONFIG_SUMMARIZATION

    else:
        raise ValueError("Invalid task name")

    delete_sagemaker_resources(
        endpoint_name=endpoint_name,
        model_name=model_name,
        endpoint_config_name=endpoint_config_name,
    )


if __name__ == "__main__":
    from ai_document_tasks.core.aws.utils import authenticate_with_aws_vault

    authenticate_with_aws_vault("epostbox.development")
    task_name = "evaluation"
    perform_delete_sagemaker_resources(task_name=task_name)

    # delete_endpoint(
    #     endpoint_name=settings.SAGEMAKER_ENDPOINT_SUMMARIZATION,
    #     inference_component_name="huggingface-pytorch-tgi-inference-2024-02-23-15-1708702416-73ac",
    # )
