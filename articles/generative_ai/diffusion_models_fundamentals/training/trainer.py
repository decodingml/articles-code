# trainer.py
import os
import torch
import torch.nn.functional as F
import wandb
from accelerate import Accelerator
from diffusers import DDPMScheduler, DDPMPipeline
from diffusers.optimization import get_cosine_schedule_with_warmup
from pytorch_fid import fid_score
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from typing import Tuple

from config import TrainingConfig
from model import DiffusionUNet
from utils import save_grid_image


class Trainer:
    def __init__(self, dataloader: DataLoader, config: TrainingConfig):
        self.config = config
        self.dataloader = dataloader
        self.diffusion_unet = DiffusionUNet(config)
        self.model = self.diffusion_unet.get_model()
        self.noise_scheduler = DDPMScheduler(num_train_timesteps=config.num_train_timesteps)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=config.learning_rate)
        self.lr_scheduler = get_cosine_schedule_with_warmup(
            optimizer=self.optimizer,
            num_warmup_steps=config.lr_warmup_steps,
            num_training_steps=len(dataloader) * config.num_epochs
        )

        self.accelerator = Accelerator(
            mixed_precision=config.mixed_precision,
            gradient_accumulation_steps=config.gradient_accumulation_steps,
            log_with=config.logger_name,
            project_dir=os.path.join(config.output_dir, "logs"),
        )

        if self.accelerator.is_main_process:
            if config.output_dir is not None:
                os.makedirs(config.output_dir, exist_ok=True)
            self.accelerator.init_trackers(config.project_name)

        # Prepare model, optimizer, dataloader, and lr_scheduler for accelerated training
        self.model, self.optimizer, self.dataloader, self.lr_scheduler = self.accelerator.prepare(
            self.model, self.optimizer, self.dataloader, self.lr_scheduler
        )

    def add_noise(self, images: torch.Tensor, timesteps: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Adds noise to images according to specified timesteps.

        Args:
            images (torch.Tensor): The batch of images to add noise to.
            timesteps (torch.Tensor): The timesteps determining the noise level.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: The noisy images and the noise added.
        """
        noise = torch.randn(images.shape, device=images.device, dtype=images.dtype)
        noisy_images = self.noise_scheduler.add_noise(images, noise, timesteps)
        return noisy_images, noise

    def calculate_fid(self, reference_images_dir: str, generated_image_dir: str) -> float:
        """
        Calculates the Fréchet Inception Distance (FID) between reference and generated images.

        Args:
            reference_images_dir (str): Path to the directory containing reference images.
            generated_image_dir (str): Path to the directory containing generated images.

        Returns:
            float: The calculated FID score.
        """
        fid_value = fid_score.calculate_fid_given_paths(
            [reference_images_dir, generated_image_dir],
            batch_size=self.config.eval_batch_size,
            device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            dims=2048,
        )
        return fid_value

    def evaluate(self, epoch: int, pipeline: DDPMPipeline) -> None:
        """
        Generates images using the model pipeline, saves them, and logs the FID score.

        Args:
            epoch (int): The current epoch number during training.
            pipeline (DDPMPipeline): The image generation pipeline (the diffusion model).
        """
        generated_images = pipeline(
            batch_size=self.config.eval_batch_size,
            generator=torch.Generator(device='cpu').manual_seed(self.config.seed),
        ).images

        generated_image_dir = os.path.join(self.config.output_dir, f"generated_epoch_{epoch}")
        os.makedirs(generated_image_dir, exist_ok=True)
        for idx, img in enumerate(generated_images):
            img.save(os.path.join(generated_image_dir, f"{idx}.png"))

        generated_grid_path = os.path.join(self.config.output_dir, f"{epoch:04d}.png")
        save_grid_image(generated_images, rows=4, cols=4, output_path=generated_grid_path)

        reference_images_dir = os.path.join(self.config.output_dir, "reference_images")
        fid_value = self.calculate_fid(reference_images_dir, generated_image_dir)
        wandb.log({"fid": fid_value, "epoch": epoch})

    def train(self) -> None:
        """
        Main training loop that iterates over epochs and batches, performing model updates
        and logging metrics at each step.
        """
        global_step = 0
        wandb.define_metric("epoch")
        wandb.define_metric("fid", step_metric="epoch")

        for epoch in range(self.config.num_epochs):
            progress_bar = tqdm(total=len(self.dataloader), disable=not self.accelerator.is_local_main_process)
            progress_bar.set_description(f"Epoch {epoch}")

            for step, batch in enumerate(self.dataloader):
                clean_images = batch["images"].to(self.accelerator.device)
                bs = clean_images.shape[0]
                timesteps = torch.randint(0, self.config.num_train_timesteps, (bs,), device=clean_images.device)

                noisy_images, noise = self.add_noise(clean_images, timesteps)

                with self.accelerator.accumulate(self.model):
                    noise_pred = self.model(noisy_images, timesteps, return_dict=False)[0]
                    loss = F.mse_loss(noise_pred, noise)
                    self.accelerator.backward(loss)
                    self.accelerator.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.optimizer.step()
                    self.lr_scheduler.step()
                    self.optimizer.zero_grad()

                metrics = {"loss": loss.detach().item(), "lr": self.lr_scheduler.get_last_lr()[0]}
                wandb.log(metrics, step=global_step)
                progress_bar.update(1)
                progress_bar.set_postfix(**metrics)
                global_step += 1

            if self.accelerator.is_main_process:
                pipeline = DDPMPipeline(unet=self.accelerator.unwrap_model(self.model), scheduler=self.noise_scheduler)
                if (epoch + 1) % self.config.save_image_epochs == 0 or epoch == self.config.num_epochs - 1:
                    self.evaluate(epoch, pipeline)
                if (epoch + 1) % self.config.save_model_epochs == 0 or epoch == self.config.num_epochs - 1:
                    pipeline.save_pretrained(self.config.output_dir)
