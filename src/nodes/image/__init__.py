from .image_to_base64 import ImageToBase64

NODE_CLASS_MAPPINGS = {
    "SimpleUtilsImageToBase64": ImageToBase64
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUtilsImageToBase64": "Image > ImageToBase64"
}

__all__ = [
    "ImageToBase64",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]
