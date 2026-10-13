import pytest
from src.nodes.filesystem.common import NODE_CATEGORY
from src.nodes.filesystem.delete_input_file import DeleteInputFile
from src.utils.any_type import ANY_TYPE


@pytest.fixture
def input_directory(tmp_path, monkeypatch):
    directory = (tmp_path / "input").resolve()
    directory.mkdir()
    monkeypatch.setattr("src.utils.filesystem.get_input_directory", lambda: directory)
    return directory


@pytest.fixture
def node() -> DeleteInputFile:
    return DeleteInputFile()


class TestDeleteInputFileDefinition:
    def test_input_types(self, input_directory):
        (input_directory / "image.png").write_bytes(b"data")
        input_types = DeleteInputFile.INPUT_TYPES()

        assert list(input_types) == ["required", "optional"]
        assert list(input_types["required"]) == ["filename"]
        assert list(input_types["optional"]) == ["passthrough"]

        input_type, options = input_types["required"]["filename"]
        assert input_type == ["image.png"]
        assert "tooltip" in options

        input_type, options = input_types["optional"]["passthrough"]
        assert input_type is ANY_TYPE
        assert "tooltip" in options

    def test_filename_options_reflect_input_directory(self, input_directory):
        assert DeleteInputFile.INPUT_TYPES()["required"]["filename"][0] == []

        (input_directory / "b.png").write_bytes(b"data")
        (input_directory / "nested").mkdir()
        (input_directory / "nested" / "a.png").write_bytes(b"data")

        assert DeleteInputFile.INPUT_TYPES()["required"]["filename"][0] == ["b.png", "nested/a.png"]

    def test_node_metadata(self):
        assert DeleteInputFile.CATEGORY == NODE_CATEGORY
        assert DeleteInputFile.DESCRIPTION.startswith("Delete a file from ComfyUI's input directory.")
        assert DeleteInputFile.FUNCTION == "delete"
        assert DeleteInputFile.RETURN_TYPES == (ANY_TYPE,)
        assert DeleteInputFile.RETURN_NAMES == ("PASSTHROUGH",)
        assert DeleteInputFile.OUTPUT_NODE is True

    def test_function_points_to_existing_method(self, node):
        assert callable(getattr(node, DeleteInputFile.FUNCTION))


class TestDeleteInputFileDelete:
    def test_deletes_file(self, node, input_directory):
        file = input_directory / "image.png"
        file.write_bytes(b"data")

        node.delete("image.png")

        assert not file.exists()

    def test_returns_none_without_passthrough(self, node, input_directory):
        (input_directory / "image.png").write_bytes(b"data")

        assert node.delete("image.png") == (None,)

    @pytest.mark.parametrize("value", ["text", 42, {"waveform": None, "sample_rate": 8000}])
    def test_returns_passthrough_unchanged(self, node, input_directory, value):
        (input_directory / "image.png").write_bytes(b"data")

        (result,) = node.delete("image.png", value)

        assert result is value

    def test_deletes_file_in_subdirectory(self, node, input_directory):
        (input_directory / "nested").mkdir()
        file = input_directory / "nested" / "image.png"
        file.write_bytes(b"data")

        node.delete("nested/image.png")

        assert not file.exists()

    def test_missing_file_raises(self, node, input_directory):  # noqa: ARG002
        with pytest.raises(FileNotFoundError):
            node.delete("missing.png")

    def test_directory_raises(self, node, input_directory):
        (input_directory / "nested").mkdir()

        with pytest.raises(FileNotFoundError):
            node.delete("nested")

        assert (input_directory / "nested").is_dir()

    @pytest.mark.parametrize("filename", ["", "   ", ".", "./"])
    def test_empty_or_input_directory_raises(self, node, input_directory, filename):
        with pytest.raises(ValueError, match=r"empty|not inside"):
            node.delete(filename)

        assert input_directory.is_dir()

    def test_path_traversal_raises(self, node, input_directory):
        outside = input_directory.parent / "outside.txt"
        outside.write_bytes(b"data")

        with pytest.raises(ValueError, match="not inside"):
            node.delete("../outside.txt")

        assert outside.exists()

    def test_absolute_path_outside_raises(self, node, input_directory):
        outside = input_directory.parent / "outside.txt"
        outside.write_bytes(b"data")

        with pytest.raises(ValueError, match="not inside"):
            node.delete(str(outside))

        assert outside.exists()

    def test_symlink_escaping_input_directory_raises(self, node, input_directory):
        outside = input_directory.parent / "outside.txt"
        outside.write_bytes(b"data")
        (input_directory / "link.txt").symlink_to(outside)

        with pytest.raises(ValueError, match="not inside"):
            node.delete("link.txt")

        assert outside.exists()
