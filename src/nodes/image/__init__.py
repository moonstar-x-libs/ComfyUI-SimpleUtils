from .base64_to_image import Base64ToImage
from .image_to_base64 import ImageToBase64

NODE_CLASS_MAPPINGS = {
    "SimpleUtilsBase64ToImage": Base64ToImage,
    "SimpleUtilsImageToBase64": ImageToBase64,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUtilsBase64ToImage": "Image > Base64ToImage",
    "SimpleUtilsImageToBase64": "Image > ImageToBase64",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "Base64ToImage",
    "ImageToBase64",
]
