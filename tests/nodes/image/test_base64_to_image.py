import base64
import binascii
import io

import numpy as np
import pytest
import torch
from PIL import Image, UnidentifiedImageError
from src.nodes.image.base64_to_image import Base64ToImage
from src.nodes.image.common import NODE_CATEGORY

IMAGE_HEIGHT = 4
IMAGE_WIDTH = 6


@pytest.fixture
def node() -> Base64ToImage:
    return Base64ToImage()


@pytest.fixture
def rgb_array() -> np.ndarray:
    rng = np.random.default_rng(seed=1234)
    return rng.integers(0, 256, size=(IMAGE_HEIGHT, IMAGE_WIDTH, 3), dtype=np.uint8)


@pytest.fixture
def rgb_base64(rgb_array: np.ndarray) -> str:
    buffer = io.BytesIO()
    Image.fromarray(rgb_array, mode="RGB").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class TestBase64ToImageDefinition:
    def test_input_types(self):
        input_types = Base64ToImage.INPUT_TYPES()

        assert list(input_types) == ["required"]
        assert list(input_types["required"]) == ["base64"]

        input_type, options = input_types["required"]["base64"]
        assert input_type == "STRING"
        assert options["multiline"] is True
        assert "tooltip" in options

    def test_node_metadata(self):
        assert Base64ToImage.CATEGORY == NODE_CATEGORY
        assert Base64ToImage.DESCRIPTION == "Transform a base64 encoded string into an image."
        assert Base64ToImage.FUNCTION == "transform"
        assert Base64ToImage.RETURN_TYPES == ("IMAGE",)
        assert Base64ToImage.RETURN_NAMES == ("IMAGE",)
        assert Base64ToImage.OUTPUT_NODE is True

    def test_function_points_to_existing_method(self, node):
        assert callable(getattr(node, Base64ToImage.FUNCTION))


class TestBase64ToImageTransform:
    def test_returns_single_element_tuple(self, node, rgb_base64):
        result = node.transform(rgb_base64)

        assert isinstance(result, tuple)
        assert len(result) == len(Base64ToImage.RETURN_TYPES)

    def test_returns_batched_float_tensor(self, node, rgb_base64):
        (image,) = node.transform(rgb_base64)

        assert isinstance(image, torch.Tensor)
        assert image.dtype == torch.float32
        assert image.shape == (1, IMAGE_HEIGHT, IMAGE_WIDTH, 3)

    def test_preserves_pixel_values(self, node, rgb_base64, rgb_array):
        (image,) = node.transform(rgb_base64)

        expected = torch.from_numpy(rgb_array.astype(np.float32) / 255.0)
        torch.testing.assert_close(image[0], expected)

    def test_invalid_base64_raises(self, node):
        with pytest.raises(binascii.Error):
            node.transform("not-valid-base64!")

    def test_non_image_data_raises(self, node):
        not_an_image = base64.b64encode(b"definitely not an image").decode("utf-8")

        with pytest.raises(UnidentifiedImageError):
            node.transform(not_an_image)
