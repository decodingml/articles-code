import os

import wandb
from dotenv import load_dotenv

from config import TrainingConfig
from data.data_handler import DataHandler
from training.trainer import Trainer


def run_train():

    # Load Env Variables from .env file
    load_dotenv()

    # Load Training Config from config.yaml file
    config = TrainingConfig.load_from_yaml("config.yaml")

    # Initialize WandB project
    wandb.init(project=config.project_name, config=config)

    # Prepare data
    data_handler = DataHandler(config.dataset_name, config.train_batch_size, config.image_size)
    data_handler.load_data()

    # Save reference images for FID computation
    reference_images_dir = os.path.join(config.output_dir, "reference_images")
    os.makedirs(reference_images_dir, exist_ok=True)
    data_handler.save_reference_images(output_dir=reference_images_dir)

    # Initialize Trainer with DataLoader and Configurations
    trainer = Trainer(dataloader=data_handler.get_dataloader(), config=config)

    # Start Training
    trainer.train()

    # Finalize WandB session
    wandb.finish()


run_train()
