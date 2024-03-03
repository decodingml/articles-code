from sagemaker.enums import EndpointType
from sagemaker.huggingface import get_huggingface_llm_image_uri

from src.aws_auth import authenticate_with_aws_vault
from src.service import DeploymentService
from src.settings import settings
from src.strategy import SagemakerHuggingfaceStrategy
from src.utils import ResourceManager


def create_huggingface_endpoint(task_name, endpoint_type=EndpointType.INFERENCE_COMPONENT_BASED):

    gpu_instance_type = settings.GPU_INSTANCE_TYPE

    if task_name == "summarization":
        endpoint_name = settings.SAGEMAKER_ENDPOINT_SUMMARIZATION
        endpoint_config_name = settings.SAGEMAKER_ENDPOINT_CONFIG_SUMMARIZATION

    else:
        raise ValueError("Invalid task name")

    role_arn = settings.ARN_ROLE
    llm_image = get_huggingface_llm_image_uri("huggingface", version="1.1.0")

    resource_manager = ResourceManager()
    deployment_service = DeploymentService(resource_manager=resource_manager)

    """
    Deploy endpoint without inference component EndpointType.MODEL_BASED
    """
    SagemakerHuggingfaceStrategy(deployment_service).deploy(
        role_arn=role_arn,
        llm_image=llm_image,
        config=settings.hugging_face_deploy_config,
        endpoint_name=endpoint_name,
        endpoint_config_name=endpoint_config_name,
        gpu_instance_type=gpu_instance_type,
        resources=settings.model_resource_config,
        endpoint_type=endpoint_type,
    )


if __name__ == "__main__":
    authenticate_with_aws_vault("your-profile")
    task_name = "summarization"
    create_huggingface_endpoint(task_name, endpoint_type=EndpointType.MODEL_BASED)
