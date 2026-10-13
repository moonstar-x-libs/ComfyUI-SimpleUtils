from inspect import cleandoc
from typing import Any

from ...utils.any_type import ANY_TYPE
from ...utils.filesystem import resolve_input_file
from .common import NODE_CATEGORY


class DeleteInputFile:
    """Delete a file from ComfyUI's input directory.

    The optional passthrough is returned unchanged, so it can be used to control when the file is deleted.
    """

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "filename": (
                    "STRING",
                    {"tooltip": "The name of the file to delete, relative to the input directory."},
                )
            },
            "optional": {
                "passthrough": (
                    ANY_TYPE,
                    {"tooltip": "Any value, returned unchanged. The file is only deleted once this value is available."},
                )
            },
        }

    CATEGORY = NODE_CATEGORY
    DESCRIPTION = cleandoc(__doc__)

    FUNCTION = "delete"
    RETURN_TYPES = (ANY_TYPE,)
    RETURN_NAMES = ("PASSTHROUGH",)
    OUTPUT_NODE = True

    def delete(self, filename: str, passthrough: Any = None) -> tuple[Any]:  # noqa: ANN401
        path = resolve_input_file(filename)

        if not path.is_file():
            msg = f"The file {filename!r} does not exist in the input directory."
            raise FileNotFoundError(msg)

        path.unlink()
        return (passthrough,)
