import base64
import io
import wave
from typing import TypedDict

import numpy as np
import torch

PCM_16_MAX = 32767
_PCM_FULL_SCALE = {1: 128.0, 2: 32768.0, 3: 8388608.0, 4: 2147483648.0}


class ComfyAudio(TypedDict):
    """The structure ComfyUI uses for the AUDIO type."""

    waveform: torch.Tensor
    sample_rate: int


def audio_tensor_to_base64(waveform: torch.Tensor, sample_rate: int) -> str:
    """Convert a waveform tensor of shape (channels, samples) to a base64 encoded 16-bit PCM WAV string."""
    samples = waveform.detach().cpu().float().clamp(-1.0, 1.0).numpy()
    pcm = np.round(samples.T * PCM_16_MAX).astype("<i2")

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(samples.shape[0])
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())

    return base64.b64encode(wav_buffer.getvalue()).decode("utf-8")


def base64_to_audio_tensor(audio_base64: str) -> tuple[torch.Tensor, int]:
    """Convert a base64 encoded PCM WAV string to a waveform tensor of shape (1, channels, samples) and its sample rate."""
    wav_bytes = base64.b64decode(audio_base64)

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())

    if sample_width == 1:
        pcm = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0
    elif sample_width == 2:  # noqa: PLR2004
        pcm = np.frombuffer(frames, dtype="<i2").astype(np.float32)
    elif sample_width == 3:  # noqa: PLR2004
        raw = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        pcm = (raw[:, 0] | (raw[:, 1] << 8) | (raw[:, 2] << 16)).astype(np.int32)
        pcm = np.where(pcm >= 1 << 23, pcm - (1 << 24), pcm).astype(np.float32)
    elif sample_width == 4:  # noqa: PLR2004
        pcm = np.frombuffer(frames, dtype="<i4").astype(np.float32)
    else:
        msg = f"Unsupported WAV sample width: {sample_width} bytes."
        raise ValueError(msg)

    samples = (pcm / _PCM_FULL_SCALE[sample_width]).reshape(-1, channels).T
    waveform = torch.from_numpy(np.ascontiguousarray(samples))

    return waveform.unsqueeze(0), sample_rate
