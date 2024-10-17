import os
from PIL import Image
from typing import List
from diffusers.utils import make_image_grid

def save_grid_image(images: List[Image.Image], rows: int, cols: int, output_path: str) -> None:
    """
    Creates a grid of images, resizes the grid, and saves it to the specified output path.
    """
    grid = make_image_grid(images, rows=rows, cols=cols)
    new_width = grid.width // 2
    new_height = grid.height // 2
    grid = grid.resize((new_width, new_height), Image.LANCZOS)
    grid.save(output_path)

def save_individual_images(images: List[Image.Image], directory: str) -> None:
    """
    Saves a list of PIL images to the specified directory.
    """
    os.makedirs(directory, exist_ok=True)
    for idx, image in enumerate(images):
        image.save(os.path.join(directory, f"{idx}.png"))
