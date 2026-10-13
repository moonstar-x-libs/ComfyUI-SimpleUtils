import pytest
from src.utils.filesystem import list_input_files


@pytest.fixture
def input_directory(tmp_path, monkeypatch):
    directory = (tmp_path / "input").resolve()
    directory.mkdir()
    monkeypatch.setattr("src.utils.filesystem.get_input_directory", lambda: directory)
    return directory


class TestListInputFiles:
    def test_empty_directory(self, input_directory):  # noqa: ARG002
        assert list_input_files() == []

    def test_lists_files_sorted(self, input_directory):
        for name in ["c.png", "a.wav", "b.txt"]:
            (input_directory / name).write_bytes(b"data")

        assert list_input_files() == ["a.wav", "b.txt", "c.png"]

    def test_includes_subdirectories_with_forward_slashes(self, input_directory):
        (input_directory / "nested" / "deeper").mkdir(parents=True)
        (input_directory / "nested" / "deeper" / "image.png").write_bytes(b"data")
        (input_directory / "root.png").write_bytes(b"data")

        assert list_input_files() == ["nested/deeper/image.png", "root.png"]

    def test_excludes_directories(self, input_directory):
        (input_directory / "empty").mkdir()

        assert list_input_files() == []

    def test_includes_symlink_inside_input_directory(self, input_directory):
        (input_directory / "image.png").write_bytes(b"data")
        (input_directory / "link.png").symlink_to(input_directory / "image.png")

        assert list_input_files() == ["image.png", "link.png"]

    def test_excludes_symlink_escaping_input_directory(self, input_directory):
        outside = input_directory.parent / "outside.txt"
        outside.write_bytes(b"data")
        (input_directory / "link.txt").symlink_to(outside)

        assert list_input_files() == []
