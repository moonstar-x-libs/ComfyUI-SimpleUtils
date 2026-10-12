from .audio_to_base64 import AudioToBase64
from .base64_to_audio import Base64ToAudio

NODE_CLASS_MAPPINGS = {
    "SimpleUtilsBase64ToAudio": Base64ToAudio,
    "SimpleUtilsAudioToBase64": AudioToBase64,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUtilsBase64ToAudio": "Audio > Base64ToAudio",
    "SimpleUtilsAudioToBase64": "Audio > AudioToBase64",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "AudioToBase64",
    "Base64ToAudio",
]
