class AnyType(str):
    """A ComfyUI type that matches every other type, so it can connect to any socket."""

    __slots__ = ()

    def __ne__(self, other: object) -> bool:
        """Never report a mismatch, since ComfyUI rejects a connection when the socket types differ."""
        return False


ANY_TYPE = AnyType("*")
