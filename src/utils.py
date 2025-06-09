from io import BytesIO
from typing import Union

import numpy as np
from PIL import Image
from viam.logging import getLogger
from viam.media.video import CameraMimeType, ViamImage

LOGGER = getLogger(__name__)

SUPPORTED_IMAGE_TYPE = [
    CameraMimeType.JPEG,
    CameraMimeType.PNG,
    CameraMimeType.VIAM_RGBA,
]

LIBRARY_SUPPORTED_FORMATS = ["JPEG", "PNG", "VIAM_RGBA"]

def create_empty_rgb_image(height: int, width: int) -> np.ndarray:
    """
    Create an empty RGB image with the specified height and width
    Args:
        height (int): Height of the image
        width (int): Width of the image
    Returns:
        np.ndarray: An empty RGB image of the specified size
    """
    return np.zeros((height, width, 3), dtype=np.uint8)

def decode_image(image: Union[Image.Image, ViamImage, np.ndarray]) -> np.ndarray:
    """
    Decode image to BGR numpy array.
    Args:
        raw_image (Union[Image.Image, RawImage])
    Returns:
        np.ndarray: BGR numpy array
    """
    if isinstance(image, ViamImage):
        if image.mime_type not in SUPPORTED_IMAGE_TYPE:
            LOGGER.error(
                "Unsupported image type: %s. Supported types are %s.",
                image.mime_type,
                SUPPORTED_IMAGE_TYPE,
            )

            raise ValueError(f"Unsupported image type: {image.mime_type}.")

        pil_img = Image.open(BytesIO(image.data), formats=LIBRARY_SUPPORTED_FORMATS).convert("RGB")
    else:
        pil_img = image

    res = pil_img.convert("RGB") # type: ignore
    rgb = np.array(res)
    return rgb
