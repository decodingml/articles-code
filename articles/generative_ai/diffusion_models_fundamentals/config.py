import os

import yaml
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class TrainingConfig:
    project_name: str = "diffusion-butterflies"  # The name of the project, used for logging and tracking
    logger_name: Optional[str] = None  # The logger used by accelerate; can be None if logging is not required
    image_size: int = 128  # The generated image resolution (e.g., 128 for 128x128 images)
    train_batch_size: int = 16  # The batch size used during training
    eval_batch_size: int = 16  # The number of images to sample during evaluation
    num_epochs: int = 50  # Total number of training epochs
    dataset_name: str = "huggan/smithsonian_butterflies_subset"  # The name of the Hugging Face dataset repository
    gradient_accumulation_steps: int = 1  # Number of steps to accumulate gradients before an optimizer step
    learning_rate: float = 1e-4  # The initial learning rate for the optimizer
    lr_warmup_steps: int = 500  # Number of steps to warm up the learning rate from 0 to the initial learning rate
    save_image_epochs: int = 5  # Interval (in epochs) at which generated images are saved
    save_model_epochs: int = 5  # Interval (in epochs) at which the model is saved
    num_train_timesteps: int = 1000  # The number of steps for which noise is added to the image
    mixed_precision: str = "no"  # Precision type for training; "no" for float32, "fp16" for mixed precision
    output_dir: str = "ddpm-butterflies-128"  # The directory where model outputs (images, checkpoints) are saved
    overwrite_output_dir: bool = True  # Overwrite the output directory if it already exists
    seed: int = 0  # Seed for random number generation to ensure reproducibility
    logger_name: str = "wandb"
    wandb_api_key: str = os.getenv("WANDB_API_KEY", "")
    wandb_init_timeout: str = os.getenv("WANDB_INIT_TIMEOUT", "300")

    @classmethod
    def load_from_yaml(cls, file_path: Optional[str] = None) -> 'TrainingConfig':
        """
        Loads the training configuration from a YAML file, if provided.
        Otherwise, uses default values specified in the dataclass.

        Args:
            file_path (Optional[str]): Path to the YAML configuration file. If None, defaults are used.

        Returns:
            TrainingConfig: An instance of TrainingConfig initialized with values from the YAML file or defaults.
        """
        if file_path:
            with open(file_path, "r") as file:
                config_dict = yaml.safe_load(file)
            return cls(**config_dict)
        else:
            return cls()


config = TrainingConfig.load_from_yaml("config.yaml")
