# main.py
import os

import wandb

from config import config
from data.data_handler import DataHandler
from training.trainer import Trainer


def main():
    # Initialize WandB project
    wandb.init(project=config.project_name, config=config)

    # Prepare data
    data_handler = DataHandler(config.dataset_name, config.train_batch_size, config.image_size)
    data_handler.load_data()

    # Save reference images (optional, done before training)
    reference_images_dir = os.path.join(config.output_dir, "reference_images")
    os.makedirs(reference_images_dir, exist_ok=True)
    data_handler.save_reference_images(output_dir=reference_images_dir)

    data_handler.preprocess_data()
    # Initialize Trainer with DataLoader and Configurations
    trainer = Trainer(dataloader=data_handler.get_dataloader(), config=config)

    # Start Training
    trainer.train()

    # Finalize WandB session
    wandb.finish()


if __name__ == "__main__":
    main()
