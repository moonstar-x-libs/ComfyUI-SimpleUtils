import base64
import io
import wave

import numpy as np
import pytest
import torch
from PIL import Image
from src.utils.audio import AUDIO_FORMATS, audio_tensor_to_base64, base64_to_audio_tensor

SAMPLE_RATE = 8000
CHANNELS = 2
SAMPLES = 32


def encode_wav(frames: bytes, sample_width: int, channels: int = CHANNELS) -> str:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(frames)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@pytest.fixture
def waveform() -> torch.Tensor:
    rng = np.random.default_rng(seed=1234)
    return torch.from_numpy(rng.uniform(-1.0, 1.0, size=(CHANNELS, SAMPLES)).astype(np.float32))


class TestAudioTensorToBase64:
    def test_returns_valid_base64_string(self, waveform):
        result = audio_tensor_to_base64(waveform, SAMPLE_RATE)

        assert isinstance(result, str)
        base64.b64decode(result, validate=True)

    def test_defaults_to_wav(self, waveform):
        assert audio_tensor_to_base64(waveform, SAMPLE_RATE) == audio_tensor_to_base64(waveform, SAMPLE_RATE, "wav")

    def test_clamps_out_of_range_samples(self):
        waveform = torch.tensor([[2.0, -2.0]])
        waveform_out, _ = base64_to_audio_tensor(audio_tensor_to_base64(waveform, SAMPLE_RATE))

        torch.testing.assert_close(waveform_out[0], torch.tensor([[32767 / 32768, -1.0]]))

    def test_handles_mono(self):
        waveform = torch.zeros((1, SAMPLES))
        waveform_out, _ = base64_to_audio_tensor(audio_tensor_to_base64(waveform, SAMPLE_RATE))

        assert waveform_out.shape == (1, 1, SAMPLES)

    def test_unknown_format_raises(self, waveform):
        with pytest.raises(KeyError):
            audio_tensor_to_base64(waveform, SAMPLE_RATE, "not-a-format")


class TestBase64ToAudioTensor:
    @pytest.mark.parametrize("audio_format", ["wav", "flac"])
    def test_lossless_round_trip(self, waveform, audio_format):
        waveform_out, sample_rate = base64_to_audio_tensor(audio_tensor_to_base64(waveform, SAMPLE_RATE, audio_format))

        assert sample_rate == SAMPLE_RATE
        assert waveform_out.shape == (1, CHANNELS, SAMPLES)
        torch.testing.assert_close(waveform_out[0], waveform, atol=1 / 16384, rtol=0)

    @pytest.mark.parametrize("audio_format", ["mp3", "opus"])
    def test_lossy_round_trip(self, audio_format):
        sample_rate = 16000
        waveform = torch.zeros((CHANNELS, sample_rate))
        waveform_out, sample_rate_out = base64_to_audio_tensor(audio_tensor_to_base64(waveform, sample_rate, audio_format))

        assert sample_rate_out == AUDIO_FORMATS[audio_format].sample_rate or sample_rate
        assert waveform_out.dtype == torch.float32
        assert waveform_out.shape[:2] == (1, CHANNELS)

    @pytest.mark.parametrize(
        ("sample_width", "frames", "expected"),
        [
            (1, bytes([0, 128, 255, 64]), [-1.0, 0.0, 127 / 128, -0.5]),
            (2, np.array([-32768, 0, 16384, -16384], dtype="<i2").tobytes(), [-1.0, 0.0, 0.5, -0.5]),
            (3, bytes([0, 0, 0x80, 0, 0, 0, 0, 0, 0x40, 0, 0, 0xC0]), [-1.0, 0.0, 0.5, -0.5]),
            (4, np.array([-(2**31), 0, 2**30, -(2**30)], dtype="<i4").tobytes(), [-1.0, 0.0, 0.5, -0.5]),
        ],
    )
    def test_decodes_pcm_sample_widths(self, sample_width, frames, expected):
        waveform, _ = base64_to_audio_tensor(encode_wav(frames, sample_width, channels=1))

        torch.testing.assert_close(waveform[0, 0], torch.tensor(expected))

    def test_deinterleaves_channels(self):
        frames = np.array([16384, -16384, 16384, -16384], dtype="<i2").tobytes()
        waveform, _ = base64_to_audio_tensor(encode_wav(frames, 2, channels=2))

        torch.testing.assert_close(waveform[0], torch.tensor([[0.5, 0.5], [-0.5, -0.5]]))

    def test_data_without_audio_stream_raises(self):
        buffer = io.BytesIO()
        Image.new("RGB", (2, 2)).save(buffer, format="PNG")

        with pytest.raises(ValueError, match="does not contain an audio stream"):
            base64_to_audio_tensor(base64.b64encode(buffer.getvalue()).decode("utf-8"))
