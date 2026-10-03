from inspect import cleandoc

from torch import Tensor

from ...utils.tensor import base64_to_img_tensor
from .common import NODE_CATEGORY


class Base64ToImage:
    """Transform a base64 encoded string into an image."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "base64": (
                    "STRING",
                    {"tooltip": "The base64 string to transform.", "multiline": True},
                )
            }
        }

    CATEGORY = NODE_CATEGORY
    DESCRIPTION = cleandoc(__doc__)

    FUNCTION = "transform"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    OUTPUT_NODE = True

    def transform(self, base64: str) -> tuple[Tensor]:
        return (base64_to_img_tensor(base64),)
