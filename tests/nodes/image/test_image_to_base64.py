import base64
import io
from typing import Callable

import numpy as np
import pytest
import torch
from PIL import Image
from src.nodes.image.common import NODE_CATEGORY
from src.nodes.image.image_to_base64 import ImageToBase64

IMAGE_HEIGHT = 4
IMAGE_WIDTH = 6


@pytest.fixture
def node() -> ImageToBase64:
    return ImageToBase64()


@pytest.fixture
def rgb_array() -> np.ndarray:
    rng = np.random.default_rng(seed=1234)
    return rng.integers(0, 256, size=(IMAGE_HEIGHT, IMAGE_WIDTH, 3), dtype=np.uint8)


@pytest.fixture
def image_batch(rgb_array: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(rgb_array.astype(np.float32) / 255.0).unsqueeze(0)


@pytest.fixture
def decode_to_pil_image() -> Callable[[str], Image.Image]:
    def _decode(img_base64: str) -> Image.Image:
        return Image.open(io.BytesIO(base64.b64decode(img_base64)))

    return _decode


class TestImageToBase64Definition:
    def test_input_types(self):
        input_types = ImageToBase64.INPUT_TYPES()

        assert list(input_types) == ["required"]
        assert list(input_types["required"]) == ["image"]

        input_type, options = input_types["required"]["image"]
        assert input_type == "IMAGE"
        assert "tooltip" in options

    def test_node_metadata(self):
        assert ImageToBase64.CATEGORY == NODE_CATEGORY
        assert ImageToBase64.DESCRIPTION == "Transform an image to a base64 encoded string."
        assert ImageToBase64.FUNCTION == "transform"
        assert ImageToBase64.RETURN_TYPES == ("STRING",)
        assert ImageToBase64.RETURN_NAMES == ("BASE64",)
        assert ImageToBase64.OUTPUT_NODE is True

    def test_function_points_to_existing_method(self, node):
        assert callable(getattr(node, ImageToBase64.FUNCTION))


class TestImageToBase64Transform:
    def test_returns_single_element_tuple(self, node, image_batch):
        result = node.transform(image_batch)

        assert isinstance(result, tuple)
        assert len(result) == len(ImageToBase64.RETURN_TYPES)

    def test_returns_valid_base64_string(self, node, image_batch):
        (result,) = node.transform(image_batch)

        assert isinstance(result, str)
        base64.b64decode(result, validate=True)

    def test_encodes_as_png(self, node, image_batch, decode_to_pil_image):
        (result,) = node.transform(image_batch)
        img = decode_to_pil_image(result)

        assert img.format == "PNG"
        assert img.mode == "RGB"
        assert img.size == (IMAGE_WIDTH, IMAGE_HEIGHT)

    def test_preserves_pixel_values(self, node, image_batch, rgb_array, decode_to_pil_image):
        (result,) = node.transform(image_batch)
        img = decode_to_pil_image(result)

        np.testing.assert_allclose(np.array(img).astype(np.int16), rgb_array.astype(np.int16), atol=1)

    def test_only_encodes_first_image_of_batch(self, node, decode_to_pil_image):
        batch = torch.stack([torch.zeros((2, 2, 3)), torch.ones((2, 2, 3))])
        (result,) = node.transform(batch)

        assert np.all(np.array(decode_to_pil_image(result)) == 0)

    def test_does_not_mutate_input(self, node, image_batch):
        original = image_batch.clone()
        node.transform(image_batch)

        assert torch.equal(image_batch, original)
