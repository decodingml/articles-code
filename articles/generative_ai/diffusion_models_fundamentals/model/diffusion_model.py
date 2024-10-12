# diffusion_model.py
from diffusers import UNet2DModel


class DiffusionUNet:
    def __init__(self, config):
        """
        Initializes the DiffusionUNet with the specified configuration parameters.

        Args:
            config: Configuration dictionary containing model parameters.
        """
        self.config = config
        self.model = UNet2DModel(
            sample_size=config.image_size,  # the target image resolution
            in_channels=3,  # the number of input channels, 3 for RGB images
            out_channels=3,  # the number of output channels
            layers_per_block=2,  # how many ResNet layers to use per UNet block
            block_out_channels=(128, 128, 256, 256, 512, 512),  # the number of output channels for each UNet block
            down_block_types=(
                "DownBlock2D", "DownBlock2D", "DownBlock2D",
                "DownBlock2D", "AttnDownBlock2D", "DownBlock2D"
            ),
            up_block_types=(
                "UpBlock2D", "AttnUpBlock2D", "UpBlock2D",
                "UpBlock2D", "UpBlock2D", "UpBlock2D"
            ),
        )

    def get_model(self):
        """
        Returns the underlying UNet2DModel instance.

        Returns:
            UNet2DModel: The initialized UNet2DModel.
        """
        return self.model

    def to(self, device):
        """
        Moves the model to the specified device.

        Args:
            device (str): The device to move the model to ('cpu' or 'cuda').
        """
        self.model.to(device)

    def save_model(self, save_path):
        """
        Saves the model to the specified path.

        Args:
            save_path (str): The file path where the model should be saved.
        """
        self.model.save_pretrained(save_path)

    def load_model(self, load_path):
        """
        Loads the model from the specified path.

        Args:
            load_path (str): The file path from which to load the model.
        """
        self.model = UNet2DModel.from_pretrained(load_path)
