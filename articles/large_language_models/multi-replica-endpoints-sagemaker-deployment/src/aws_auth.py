import logging
import os
import platform
import subprocess

import py_aws_vault_auth

from src.settings import settings


def authenticate_with_aws_vault(profile_name: str):

    current_platform = platform.system()

    if current_platform == "Darwin":  # Darwin is the system name for macOS
        authenticate_with_aws_vault_mac(profile_name)
    elif current_platform == "Linux":
        authenticate_with_aws_vault_wsl(profile_name, aws_vault_file_passphrase=settings.PASSPHRASE_AWS_VAULT)


def authenticate_with_aws_vault_mac(profile_name: str):
    """Authenticates with AWS Vault for a given profile name."""
    environ_auth = py_aws_vault_auth.authenticate(profile_name, return_as="environ")
    os.environ.update(environ_auth)
    logging.info(f"Authenticated with AWS Vault for profile: {profile_name}")


def authenticate_with_aws_vault_wsl(profile: str, aws_vault_file_passphrase: str = "my_pass"):
    """Shell out to aws-vault, set AWS_VAULT_FILE_PASSPHRASE, and update AWS credentials in environment"""
    os.environ["AWS_VAULT_BACKEND"] = "file"
    cmd = ["aws-vault", "exec", profile]
    cmd.extend(["--", "env"])

    # Prepare the environment with AWS_VAULT_FILE_PASSPHRASE
    env = os.environ.copy()
    env["AWS_VAULT_FILE_PASSPHRASE"] = aws_vault_file_passphrase
    # Execute the command and capture the output
    envvars = subprocess.check_output(cmd, env=env).decode()
    # Update the current process's environment variables with the ones from aws-vault
    for envline in envvars.splitlines():
        if not envline.startswith("AWS_"):
            continue
        k, v = envline.split("=", 1)
        os.environ[k] = v
