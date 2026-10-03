from .example_node import Example

NODE_CLASS_MAPPINGS = {
    "ExampleNode": Example
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExampleNode": "Image - ExampleNode"
}

__all__ = [
    "Example",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]
