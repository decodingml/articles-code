import torch
from diffusers import DDPMPipeline


class DiffusionInference:
    def __init__(self, repo_name, device=None):
        """
        Initializes the DiffusionInference class with a pipeline loaded from the Hugging Face Hub.

        Args:
            repo_name (str): The repository name on the Hugging Face Hub.
            device (str, optional): The device to load the model on ('cpu' or 'cuda'). Defaults to auto-detect.
        """
        self.repo_name = repo_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipeline = self.load_unconditioned_pipeline()

    def load_unconditioned_pipeline(self):
        """
        Loads the unconditioned diffusion pipeline from the Hugging Face Hub.

        Returns:
            DDPMPipeline: The loaded diffusion pipeline for unconditioned image generation.
        """
        pipeline = DDPMPipeline.from_pretrained(self.repo_name)
        pipeline.to(self.device)
        return pipeline

    def generate_unconditioned_image(self):
        """
        Generates an unconditioned image using the loaded diffusion model.

        Returns:
            PIL.Image: The generated image.
        """
        image = self.pipeline().images[0]
        return image
