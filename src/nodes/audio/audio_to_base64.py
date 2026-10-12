from inspect import cleandoc

from ...utils.audio import AUDIO_FORMATS, ComfyAudio, audio_tensor_to_base64
from .common import NODE_CATEGORY


class AudioToBase64:
    """Transform an audio to a base64 encoded string."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The audio to transform."}),
                "format": (list(AUDIO_FORMATS), {"default": "wav", "tooltip": "The format to encode the audio as."}),
            }
        }

    CATEGORY = NODE_CATEGORY
    DESCRIPTION = cleandoc(__doc__)

    FUNCTION = "transform"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("BASE64",)
    OUTPUT_NODE = True

    def transform(self, audio: ComfyAudio, format: str = "wav") -> tuple[str]:  # noqa: A002
        return (audio_tensor_to_base64(audio["waveform"][0], audio["sample_rate"], format),)
