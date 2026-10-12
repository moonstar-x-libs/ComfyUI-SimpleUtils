import base64
import binascii
import io
import wave

import av
import numpy as np
import pytest
import torch
from src.nodes.audio.base64_to_audio import Base64ToAudio
from src.nodes.audio.common import NODE_CATEGORY
from src.utils.audio import AUDIO_FORMATS, audio_tensor_to_base64

SAMPLE_RATE = 8000
CHANNELS = 2
SAMPLES = 32


@pytest.fixture
def node() -> Base64ToAudio:
    return Base64ToAudio()


@pytest.fixture
def pcm_array() -> np.ndarray:
    rng = np.random.default_rng(seed=1234)
    return rng.integers(-32768, 32768, size=(SAMPLES, CHANNELS), dtype=np.int16)


@pytest.fixture
def wav_base64(pcm_array: np.ndarray) -> str:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_array.astype("<i2").tobytes())
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class TestBase64ToAudioDefinition:
    def test_input_types(self):
        input_types = Base64ToAudio.INPUT_TYPES()

        assert list(input_types) == ["required"]
        assert list(input_types["required"]) == ["base64"]

        input_type, options = input_types["required"]["base64"]
        assert input_type == "STRING"
        assert options["multiline"] is True
        assert "tooltip" in options

    def test_node_metadata(self):
        assert Base64ToAudio.CATEGORY == NODE_CATEGORY
        assert Base64ToAudio.DESCRIPTION == "Transform a base64 encoded string into an audio."
        assert Base64ToAudio.FUNCTION == "transform"
        assert Base64ToAudio.RETURN_TYPES == ("AUDIO",)
        assert Base64ToAudio.RETURN_NAMES == ("AUDIO",)
        assert Base64ToAudio.OUTPUT_NODE is True

    def test_function_points_to_existing_method(self, node):
        assert callable(getattr(node, Base64ToAudio.FUNCTION))


class TestBase64ToAudioTransform:
    def test_returns_single_element_tuple(self, node, wav_base64):
        result = node.transform(wav_base64)

        assert isinstance(result, tuple)
        assert len(result) == len(Base64ToAudio.RETURN_TYPES)

    def test_returns_comfy_audio_dict(self, node, wav_base64):
        (audio,) = node.transform(wav_base64)

        assert set(audio) == {"waveform", "sample_rate"}
        assert audio["sample_rate"] == SAMPLE_RATE
        assert isinstance(audio["waveform"], torch.Tensor)
        assert audio["waveform"].dtype == torch.float32
        assert audio["waveform"].shape == (1, CHANNELS, SAMPLES)

    def test_preserves_sample_values(self, node, wav_base64, pcm_array):
        (audio,) = node.transform(wav_base64)

        expected = torch.from_numpy((pcm_array.astype(np.float32) / 32768.0).T.copy())
        torch.testing.assert_close(audio["waveform"][0], expected)

    @pytest.mark.parametrize("audio_format", list(AUDIO_FORMATS))
    def test_decodes_supported_formats(self, node, audio_format):
        waveform = torch.zeros((CHANNELS, 16000))
        (audio,) = node.transform(audio_tensor_to_base64(waveform, 16000, audio_format))

        assert audio["waveform"].dtype == torch.float32
        assert audio["waveform"].shape[:2] == (1, CHANNELS)
        assert audio["sample_rate"] == AUDIO_FORMATS[audio_format].sample_rate or 16000

    def test_invalid_base64_raises(self, node):
        with pytest.raises(binascii.Error):
            node.transform("not-valid-base64!")

    def test_non_audio_data_raises(self, node):
        not_audio = base64.b64encode(b"definitely not an audio file").decode("utf-8")

        with pytest.raises(av.error.InvalidDataError):
            node.transform(not_audio)
