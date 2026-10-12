import base64
import io
import wave

import av
import numpy as np
import pytest
import torch
from src.nodes.audio.audio_to_base64 import AudioToBase64
from src.nodes.audio.common import NODE_CATEGORY

SAMPLE_RATE = 8000
CHANNELS = 2
SAMPLES = 32


@pytest.fixture
def node() -> AudioToBase64:
    return AudioToBase64()


@pytest.fixture
def waveform() -> torch.Tensor:
    rng = np.random.default_rng(seed=1234)
    return torch.from_numpy(rng.uniform(-1.0, 1.0, size=(1, CHANNELS, SAMPLES)).astype(np.float32))


@pytest.fixture
def audio(waveform: torch.Tensor) -> dict:
    return {"waveform": waveform, "sample_rate": SAMPLE_RATE}


def read_wav(audio_base64: str) -> tuple[wave.Wave_read, np.ndarray]:
    wav_file = wave.open(io.BytesIO(base64.b64decode(audio_base64)), "rb")  # noqa: SIM115
    frames = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype="<i2")
    return wav_file, frames.reshape(-1, wav_file.getnchannels()).T


class TestAudioToBase64Definition:
    def test_input_types(self):
        input_types = AudioToBase64.INPUT_TYPES()

        assert list(input_types) == ["required"]
        assert list(input_types["required"]) == ["audio", "format"]

        input_type, options = input_types["required"]["audio"]
        assert input_type == "AUDIO"
        assert "tooltip" in options

        formats, options = input_types["required"]["format"]
        assert formats == ["wav", "flac", "mp3", "opus"]
        assert options["default"] == "wav"
        assert "tooltip" in options

    def test_node_metadata(self):
        assert AudioToBase64.CATEGORY == NODE_CATEGORY
        assert AudioToBase64.DESCRIPTION == "Transform an audio to a base64 encoded string."
        assert AudioToBase64.FUNCTION == "transform"
        assert AudioToBase64.RETURN_TYPES == ("STRING",)
        assert AudioToBase64.RETURN_NAMES == ("BASE64",)
        assert AudioToBase64.OUTPUT_NODE is True

    def test_function_points_to_existing_method(self, node):
        assert callable(getattr(node, AudioToBase64.FUNCTION))


class TestAudioToBase64Transform:
    def test_returns_single_element_tuple(self, node, audio):
        result = node.transform(audio)

        assert isinstance(result, tuple)
        assert len(result) == len(AudioToBase64.RETURN_TYPES)

    def test_returns_valid_base64_string(self, node, audio):
        (result,) = node.transform(audio)

        assert isinstance(result, str)
        base64.b64decode(result, validate=True)

    def test_encodes_as_16_bit_wav_by_default(self, node, audio):
        (result,) = node.transform(audio)
        wav_file, _ = read_wav(result)

        assert wav_file.getnchannels() == CHANNELS
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == SAMPLE_RATE
        assert wav_file.getnframes() == SAMPLES

    @pytest.mark.parametrize(
        ("audio_format", "container_format"),
        [("wav", "wav"), ("flac", "flac"), ("mp3", "mp3"), ("opus", "ogg")],
    )
    def test_encodes_in_selected_format(self, node, audio, audio_format, container_format):
        (result,) = node.transform(audio, audio_format)

        with av.open(io.BytesIO(base64.b64decode(result))) as container:
            assert container.format.name == container_format
            assert container.streams.audio[0].channels == CHANNELS

    def test_preserves_sample_values(self, node, audio, waveform):
        (result,) = node.transform(audio)
        _, frames = read_wav(result)

        np.testing.assert_allclose(frames / 32768.0, waveform[0].numpy(), atol=1 / 32768.0)

    def test_only_encodes_first_audio_of_batch(self, node):
        batch = torch.stack([torch.zeros((CHANNELS, SAMPLES)), torch.ones((CHANNELS, SAMPLES))])
        (result,) = node.transform({"waveform": batch, "sample_rate": SAMPLE_RATE})
        _, frames = read_wav(result)

        assert np.all(frames == 0)

    def test_does_not_mutate_input(self, node, audio, waveform):
        original = waveform.clone()
        node.transform(audio)

        assert torch.equal(waveform, original)
