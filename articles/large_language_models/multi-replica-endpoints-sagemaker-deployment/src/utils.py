import logging

import boto3
from botocore.exceptions import ClientError


class ResourceManager:
    def __init__(self):
        self.sagemaker_client = boto3.client("sagemaker")
        self.logger = logging.getLogger(__name__)

    def endpoint_config_exists(self, endpoint_config_name: str) -> bool:
        """Check if the SageMaker endpoint configuration exists."""
        try:
            self.sagemaker_client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
            self.logger.info(f"Endpoint configuration '{endpoint_config_name}' exists.")
            return True
        except ClientError:
            self.logger.info(f"Endpoint configuration '{endpoint_config_name}' does not exist.")
            return False

    def endpoint_exists(self, endpoint_name: str) -> bool:
        """Check if the SageMaker endpoint exists."""
        try:
            self.sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            self.logger.info(f"Endpoint '{endpoint_name}' exists.")
            return True
        except self.sagemaker_client.exceptions.ResourceNotFoundException:
            self.logger.info(f"Endpoint '{endpoint_name}' does not exist.")
            return False


def get_role_arn(role_name: str):
    """
    The get_role_arn function takes a role name as input and returns the ARN for that role.

    :param role_name: str: Specify the name of the role that we want to retrieve
    :return: The arn of the role
    """
    iam = boto3.client("iam")

    try:
        role_details = iam.get_role(RoleName=role_name)
        logging.info(f"Retrieved role ARN for {role_name}")
        return role_details["Role"]["Arn"]
    except Exception as e:
        logging.error(f"Error obtaining role ARN: {e}")
        raise
