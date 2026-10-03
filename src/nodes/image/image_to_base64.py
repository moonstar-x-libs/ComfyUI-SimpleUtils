from ...utils.tensor import img_tensor_to_base64
from .common import NODE_CATEGORY
from inspect import cleandoc
from torch import Tensor


class ImageToBase64:
    """
    Transform an image to a base64 encoded string.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "The image to transform."
                })
            }
        }

    CATEGORY = NODE_CATEGORY
    DESCRIPTION = cleandoc(__doc__)

    FUNCTION = "transform"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("BASE64",)
    OUTPUT_NODE = True

    def transform(self, image: Tensor) -> tuple[str]:
        return (img_tensor_to_base64(image[0]),)
