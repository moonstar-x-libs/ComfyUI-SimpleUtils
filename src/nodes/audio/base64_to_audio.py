from inspect import cleandoc

from ...utils.audio import ComfyAudio, base64_to_audio_tensor
from .common import NODE_CATEGORY


class Base64ToAudio:
    """Transform a base64 encoded string into an audio."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "base64": (
                    "STRING",
                    {"tooltip": "The base64 string to transform.", "multiline": True},
                )
            }
        }

    CATEGORY = NODE_CATEGORY
    DESCRIPTION = cleandoc(__doc__)

    FUNCTION = "transform"
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("AUDIO",)
    OUTPUT_NODE = True

    def transform(self, base64: str) -> tuple[ComfyAudio]:
        waveform, sample_rate = base64_to_audio_tensor(base64)
        result: ComfyAudio = {"waveform": waveform, "sample_rate": sample_rate}
        return (result,)
