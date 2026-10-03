import base64
import io
import numpy as np
from torch import Tensor
from PIL import Image


def img_tensor_to_base64(img_tensor: Tensor) -> str:
    """
    Convert an image tensor to a base64 encoded string.
    """
    img_array = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
    img_pil = Image.fromarray(img_array)

    img_buffer = io.BytesIO()
    img_pil.save(img_buffer, format='PNG')

    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
