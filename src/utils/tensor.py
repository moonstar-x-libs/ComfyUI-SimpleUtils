import base64
import io
import numpy as np
import torch
from PIL import Image


def img_tensor_to_base64(img_tensor: torch.Tensor) -> str:
    """
    Convert an image tensor to a base64 encoded string.
    """
    img_array = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
    img_pil = Image.fromarray(img_array)

    img_buffer = io.BytesIO()
    img_pil.save(img_buffer, format='PNG')

    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')


def base64_to_img_tensor(img_base64: str) -> torch.Tensor:
    """
    Convert a base64 encoded string to an image tensor.
    """
    img_bytes = base64.b64decode(img_base64)
    img_buffer = io.BytesIO(img_bytes)
    img_pil = Image.open(img_buffer)

    if img_pil.mode != "RGB":
        img_pil = img_pil.convert("RGB")

    img_array = np.array(img_pil).astype(np.float32) / 255.0
    img_tensor = torch.from_numpy(img_array)

    return img_tensor.unsqueeze(0)
