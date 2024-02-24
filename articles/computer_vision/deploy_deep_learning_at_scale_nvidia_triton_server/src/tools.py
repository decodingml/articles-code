from typing import List

import numpy as np
from PIL import Image


def resize_image(image: Image, min_length: float = 1.0) -> np.array:
    """
    Resize an image to a specified minimum length while maintaining the aspect ratio.

    Args:
        image_path (PIL.Image): The image file.
        min_length (float, optional): The minimum length of the resized image. Defaults to 1.0.

    Returns:
        np.array: The resized image as a NumPy array.
    """
    scale_ratio = min_length / min(image.size)
    new_size = tuple(int(round(dim * scale_ratio)) for dim in image.size)
    resized_image = image.resize(new_size, Image.BILINEAR)
    return np.array(resized_image)


def crop_center(image_array: np.array, crop_width: int, crop_height: int) -> np.array:
    """
    Crop the center region of an image array.

    Args:
        image_array (numpy.ndarray): The input image array.
        crop_width (int): The width of the cropped region.
        crop_height (int): The height of the cropped region.

    Returns:
        numpy.ndarray: The cropped image array.
    """
    height, width, _ = image_array.shape
    start_x = (width - crop_width) // 2
    start_y = (height - crop_height) // 2
    return image_array[start_y : start_y + crop_height, start_x : start_x + crop_width]


def load_image(image_path: str) -> Image:
    """
    Load an image from a file.

    Args:
        image_path (str): The path to the input image.

    Returns:
        PIL.Image: The loaded image.
    """
    return Image.open(image_path).convert("RGB")


def normalize_image(image_array: np.array) -> np.array:
    """
    Normalize the input image array.

    Args:
        image_array (numpy.ndarray): The input image array.

    Returns:
        numpy.ndarray: The normalized image array.

    """
    image_array = image_array.transpose(2, 0, 1)
    image_array = np.ascontiguousarray(image_array, dtype=np.float32)
    mean_vec = np.array([0.485, 0.456, 0.406], np.float32)
    stddev_vec = np.array([0.229, 0.224, 0.225], np.float32)
    normalized_image = (image_array / 255 - mean_vec[:, None, None]) / stddev_vec[
        :, None, None
    ]
    normalized_image = normalized_image.reshape(1, 3, 224, 224)
    return normalized_image


def load_classes(filename: str) -> List[str]:
    with open(filename, "r") as f:
        return f.read().splitlines()
