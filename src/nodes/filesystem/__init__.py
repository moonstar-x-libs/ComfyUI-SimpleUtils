from .delete_input_file import DeleteInputFile

NODE_CLASS_MAPPINGS = {
    "SimpleUtilsDeleteInputFile": DeleteInputFile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUtilsDeleteInputFile": "Filesystem > DeleteInputFile",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "DeleteInputFile",
]
