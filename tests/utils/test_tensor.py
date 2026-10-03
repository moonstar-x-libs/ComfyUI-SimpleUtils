import base64
import binascii
import io
from typing import Callable

import numpy as np
import pytest
import torch
from PIL import Image, UnidentifiedImageError
from src.utils.tensor import base64_to_img_tensor, img_tensor_to_base64

IMAGE_HEIGHT = 4
IMAGE_WIDTH = 6


@pytest.fixture
def decode_to_pil_image() -> Callable[[str], Image.Image]:
    def _decode(img_base64: str) -> Image.Image:
        return Image.open(io.BytesIO(base64.b64decode(img_base64)))

    return _decode


@pytest.fixture
def encode_pil_image() -> Callable[..., str]:
    def _encode(img: Image.Image, img_format: str = "PNG") -> str:
        buffer = io.BytesIO()
        img.save(buffer, format=img_format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    return _encode


@pytest.fixture
def rgb_array() -> np.ndarray:
    rng = np.random.default_rng(seed=1234)
    return rng.integers(0, 256, size=(IMAGE_HEIGHT, IMAGE_WIDTH, 3), dtype=np.uint8)


@pytest.fixture
def rgb_base64(rgb_array: np.ndarray, encode_pil_image: Callable[..., str]) -> str:
    return encode_pil_image(Image.fromarray(rgb_array, mode="RGB"))


@pytest.fixture
def img_tensor(rgb_array: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(rgb_array.astype(np.float32) / 255.0)


class TestImgTensorToBase64:
    def test_returns_valid_base64_string(self, img_tensor):
        result = img_tensor_to_base64(img_tensor)

        assert isinstance(result, str)
        base64.b64decode(result, validate=True)

    def test_encodes_as_png(self, img_tensor, decode_to_pil_image):
        img = decode_to_pil_image(img_tensor_to_base64(img_tensor))

        assert img.format == "PNG"
        assert img.mode == "RGB"

    def test_preserves_dimensions(self, img_tensor, decode_to_pil_image):
        height, width, _ = img_tensor.shape
        img = decode_to_pil_image(img_tensor_to_base64(img_tensor))

        assert img.size == (width, height)

    def test_preserves_pixel_values(self, img_tensor, rgb_array, decode_to_pil_image):
        img = decode_to_pil_image(img_tensor_to_base64(img_tensor))

        np.testing.assert_allclose(np.array(img).astype(np.int16), rgb_array.astype(np.int16), atol=1)

    def test_maps_extremes_to_black_and_white(self, decode_to_pil_image):
        black = torch.zeros((2, 2, 3))
        white = torch.ones((2, 2, 3))

        assert np.all(np.array(decode_to_pil_image(img_tensor_to_base64(black))) == 0)
        assert np.all(np.array(decode_to_pil_image(img_tensor_to_base64(white))) == 255)

    def test_encodes_rgba_tensor(self, decode_to_pil_image):
        rgba = torch.ones((2, 3, 4))
        img = decode_to_pil_image(img_tensor_to_base64(rgba))

        assert img.mode == "RGBA"
        assert img.size == (3, 2)

    def test_does_not_mutate_input(self, img_tensor):
        original = img_tensor.clone()
        img_tensor_to_base64(img_tensor)

        assert torch.equal(img_tensor, original)


class TestBase64ToImgTensor:
    def test_returns_batched_float_tensor(self, rgb_base64, rgb_array):
        height, width, _ = rgb_array.shape
        result = base64_to_img_tensor(rgb_base64)

        assert isinstance(result, torch.Tensor)
        assert result.dtype == torch.float32
        assert result.shape == (1, height, width, 3)

    def test_values_are_normalized(self, rgb_base64, rgb_array):
        result = base64_to_img_tensor(rgb_base64)

        assert result.min() >= 0.0
        assert result.max() <= 1.0
        expected = torch.from_numpy(rgb_array.astype(np.float32) / 255.0)
        torch.testing.assert_close(result[0], expected)

    @pytest.mark.parametrize("mode", ["RGBA", "L", "P", "LA"])
    def test_converts_other_modes_to_rgb(self, mode, encode_pil_image):
        img = Image.new("RGB", (5, 3), color=(10, 120, 240)).convert(mode)
        result = base64_to_img_tensor(encode_pil_image(img))

        assert result.shape == (1, 3, 5, 3)

    def test_rgba_drops_alpha_channel(self, encode_pil_image):
        img = Image.new("RGBA", (2, 2), color=(255, 0, 0, 0))
        result = base64_to_img_tensor(encode_pil_image(img))

        torch.testing.assert_close(result[0, 0, 0], torch.tensor([1.0, 0.0, 0.0]))

    def test_decodes_jpeg(self, encode_pil_image):
        img = Image.new("RGB", (8, 8), color=(0, 0, 0))
        result = base64_to_img_tensor(encode_pil_image(img, "JPEG"))

        assert result.shape == (1, 8, 8, 3)

    def test_invalid_base64_raises(self):
        with pytest.raises(binascii.Error):
            base64_to_img_tensor("not-valid-base64!")

    def test_non_image_data_raises(self):
        not_an_image = base64.b64encode(b"definitely not an image").decode("utf-8")

        with pytest.raises(UnidentifiedImageError):
            base64_to_img_tensor(not_an_image)
