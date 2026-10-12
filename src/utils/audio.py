from __future__ import annotations

import base64
import io
from typing import NamedTuple, TypedDict, cast

import av
import numpy as np
import torch


class ComfyAudio(TypedDict):
    """The structure ComfyUI uses for the AUDIO type."""

    waveform: torch.Tensor
    sample_rate: int


class AudioFormat(NamedTuple):
    """The container and codec used to encode an audio format."""

    container: str
    codec: str
    sample_rate: int | None = None


AUDIO_FORMATS = {
    "wav": AudioFormat("wav", "pcm_s16le"),
    "flac": AudioFormat("flac", "flac"),
    "mp3": AudioFormat("mp3", "libmp3lame"),
    "opus": AudioFormat("ogg", "libopus", sample_rate=48000),
}


def audio_tensor_to_base64(waveform: torch.Tensor, sample_rate: int, audio_format: str = "wav") -> str:
    """Convert a waveform tensor of shape (channels, samples) to a base64 encoded string in the given audio format."""
    container_format, codec, codec_sample_rate = AUDIO_FORMATS[audio_format]
    samples = np.ascontiguousarray(waveform.detach().cpu().float().clamp(-1.0, 1.0).numpy())
    layout = av.AudioLayout(f"{samples.shape[0]}c")

    frame = av.AudioFrame.from_ndarray(samples, format="fltp", layout=layout.name)
    frame.sample_rate = sample_rate

    audio_buffer = io.BytesIO()
    with av.open(audio_buffer, mode="w", format=container_format) as container:
        stream = cast("av.AudioStream", container.add_stream(codec, rate=codec_sample_rate or sample_rate, layout=layout.name))
        container.mux(stream.encode(frame))
        container.mux(stream.encode(None))

    return base64.b64encode(audio_buffer.getvalue()).decode("utf-8")


def base64_to_audio_tensor(audio_base64: str) -> tuple[torch.Tensor, int]:
    """Convert a base64 encoded audio string to a waveform tensor of shape (1, channels, samples) and its sample rate."""
    audio_bytes = base64.b64decode(audio_base64)

    with av.open(io.BytesIO(audio_bytes), mode="r") as container:
        if not container.streams.audio:
            msg = "The provided data does not contain an audio stream."
            raise ValueError(msg)

        stream = container.streams.audio[0]
        sample_rate = stream.rate
        resampler = av.AudioResampler(format="fltp", layout=stream.layout, rate=sample_rate)

        chunks = [resampled.to_ndarray() for frame in container.decode(stream) for resampled in resampler.resample(frame)]
        chunks.extend(resampled.to_ndarray() for resampled in resampler.resample(None))

    waveform = torch.from_numpy(np.concatenate(chunks, axis=1))

    return waveform.unsqueeze(0), sample_rate
