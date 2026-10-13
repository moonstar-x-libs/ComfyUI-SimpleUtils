from pathlib import Path


def get_input_directory() -> Path:
    """Get ComfyUI's input directory.

    ``folder_paths`` is only importable inside a running ComfyUI instance, so it is imported lazily.
    """
    import folder_paths  # noqa: PLC0415

    return Path(folder_paths.get_input_directory()).resolve()


def resolve_input_file(filename: str) -> Path:
    """Resolve a filename relative to ComfyUI's input directory.

    Raises:
        ValueError: If the filename is empty or resolves to a path outside the input directory.

    """
    if not filename.strip():
        msg = "The filename must not be empty."
        raise ValueError(msg)

    input_directory = get_input_directory()
    path = (input_directory / filename).resolve()

    if path == input_directory or not path.is_relative_to(input_directory):
        msg = f"The file {filename!r} is not inside the input directory."
        raise ValueError(msg)

    return path


def list_input_files() -> list[str]:
    """List the files inside ComfyUI's input directory, including subdirectories.

    Paths are returned sorted, relative to the input directory and with forward slashes.
    Files whose resolved path is outside the input directory (e.g. symlinks pointing elsewhere) are skipped.
    """
    input_directory = get_input_directory()

    return sorted(
        path.relative_to(input_directory).as_posix()
        for path in input_directory.rglob("*")
        if path.is_file() and path.resolve().is_relative_to(input_directory)
    )
