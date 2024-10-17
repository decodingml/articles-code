import os

from datasets import load_dataset
from torch.utils.data import DataLoader
from torchvision import transforms
from utils import save_grid_image


class DataHandler:
    def __init__(self, dataset_name: str, batch_size: int, image_size: int):
        self.train_dataloader = None
        self.dataset = None
        self.dataset_name = dataset_name
        self.batch_size = batch_size
        self.image_size = image_size
        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])
        self.load_data()

    def load_data(self):
        """
        Loads the dataset from Huggingface
        """

        self.dataset = load_dataset(self.dataset_name, split="train")

    def get_dataloader(self) -> DataLoader:
        """
        Returns the DataLoader for the dataset. Ensures that the DataLoader is created if not already done.

        Returns:
            DataLoader: The DataLoader for the training dataset.
        """

        if self.train_dataloader is None:
            self.create_dataloader()
        return self.train_dataloader

    def save_reference_images(self, output_dir: str, n_images: int = 16) -> None:
        """
        Saves a subset of the dataset as individual images and as a grid.

        Args:
            output_dir (str): Directory to save images.
            n_images (int): Number of images to save.
        """

        if self.dataset is None:
            self.load_data()

        os.makedirs(output_dir, exist_ok=True)
        images = []
        reference_images = self.dataset.select(range(n_images))  # Select the first n_images

        for idx, example in enumerate(reference_images):
            image = example['image'].convert("RGB")
            image = self.transform(image)
            image = transforms.ToPILImage()(image)
            images.append(image)
            image.save(os.path.join(output_dir, f"{idx}.png"))

        # Save as grid for visualization
        save_grid_image(images, rows=4, cols=4, output_path=os.path.join(output_dir, "reference_image_grid.png"))

    def create_dataloader(self):
        """
        Preprocesses the loaded dataset and creates a DataLoader with the specified batch size.
        """

        if self.dataset is None:
            self.load_data()

        self._preprocess_data()
        self.train_dataloader = DataLoader(
            self.dataset,
            batch_size=self.batch_size,
            shuffle=True
        )

    def _preprocess_data(self):
        """
        # Apply transformation to each image in the dataset
        """

        self.dataset.set_transform(self._apply_transform)
        
    def _apply_transform(self, examples):
        """
        Internal method to apply transformation to each image in the dataset.
        """

        images = [self.transform(image.convert("RGB")) for image in examples["image"]]
        return {"images": images}
