"""Tests for file operation tools."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.tools.file_ops import (
    list_directory,
    read_file,
    read_json_file,
    write_file,
    write_json_file,
)
from macro_man.utils.exceptions import MacroManError, ValidationError


class TestReadFile:
    """Test read_file function."""

    def test_read_existing_file(self):
        """Test reading an existing file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            test_content = "Hello, World!\nThis is a test file."
            f.write(test_content)
            temp_path = f.name

        try:
            result = read_file(temp_path)
            assert result == test_content
        finally:
            os.unlink(temp_path)

    def test_read_nonexistent_file(self):
        """Test reading a non-existent file raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            read_file("/nonexistent/file.txt")

        assert "File does not exist" in str(exc_info.value)
        assert exc_info.value.field == "file_path"

    def test_read_directory_as_file(self):
        """Test reading a directory as file raises ValidationError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError) as exc_info:
                read_file(temp_dir)

            assert "Path is not a file" in str(exc_info.value)
            assert exc_info.value.field == "file_path"

    def test_read_file_with_unicode(self):
        """Test reading a file with unicode content."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt", encoding="utf-8"
        ) as f:
            test_content = "Hello, 世界! 🌍\nThis is a test with unicode."
            f.write(test_content)
            temp_path = f.name

        try:
            result = read_file(temp_path)
            assert result == test_content
        finally:
            os.unlink(temp_path)


class TestWriteFile:
    """Test write_file function."""

    def test_write_new_file(self):
        """Test writing to a new file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "new_file.txt")
            test_content = "This is test content for a new file."

            result = write_file(temp_path, test_content)

            assert result["success"] is True
            assert result["size"] == len(test_content)
            assert result["overwritten"] is False
            assert "file_path" in result

            # Verify file was created and contains correct content
            with open(temp_path) as f:
                assert f.read() == test_content

    def test_write_file_with_overwrite(self):
        """Test writing to an existing file with overwrite=True."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Original content")
            temp_path = f.name

        try:
            new_content = "New content that overwrites the original."
            result = write_file(temp_path, new_content, overwrite=True)

            assert result["success"] is True
            assert result["size"] == len(new_content)
            assert result["overwritten"] is True

            # Verify file was overwritten
            with open(temp_path) as f:
                assert f.read() == new_content
        finally:
            os.unlink(temp_path)

    def test_write_file_without_overwrite_existing(self):
        """Test writing to existing file without overwrite raises ValidationError."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Original content")
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                write_file(temp_path, "New content", overwrite=False)

            assert "File already exists" in str(exc_info.value)
            assert "Use overwrite=True" in str(exc_info.value)
            assert exc_info.value.field == "file_path"
        finally:
            os.unlink(temp_path)

    def test_write_file_creates_directories(self):
        """Test that write_file creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "nested", "subdir", "test.txt")
            test_content = "Content in nested directory"

            result = write_file(nested_path, test_content)

            assert result["success"] is True
            assert os.path.exists(nested_path)

            with open(nested_path) as f:
                assert f.read() == test_content


class TestListDirectory:
    """Test list_directory function."""

    def test_list_existing_directory(self):
        """Test listing an existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files and directories
            test_files = ["file1.txt", "file2.txt", "subdir"]
            for item in test_files:
                item_path = os.path.join(temp_dir, item)
                if item.endswith(".txt"):
                    with open(item_path, "w") as f:
                        f.write(f"Content of {item}")
                else:
                    os.makedirs(item_path)

            result = list_directory(temp_dir)

            assert len(result) == 3
            result_names = [item["name"] for item in result]
            assert "file1.txt" in result_names
            assert "file2.txt" in result_names
            assert "subdir" in result_names

            # Check structure of returned items
            for item in result:
                assert "name" in item
                assert "path" in item
                assert "is_file" in item
                assert "is_directory" in item
                assert "size" in item
                assert "modified" in item

                if item["name"].endswith(".txt"):
                    assert item["is_file"] is True
                    assert item["is_directory"] is False
                    assert item["size"] is not None
                else:
                    assert item["is_file"] is False
                    assert item["is_directory"] is True
                    assert item["size"] is None

    def test_list_nonexistent_directory(self):
        """Test listing a non-existent directory raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            list_directory("/nonexistent/directory")

        assert "Directory does not exist" in str(exc_info.value)
        assert exc_info.value.field == "directory_path"

    def test_list_file_as_directory(self):
        """Test listing a file as directory raises ValidationError."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                list_directory(temp_path)

            assert "Path is not a directory" in str(exc_info.value)
            assert exc_info.value.field == "directory_path"
        finally:
            os.unlink(temp_path)

    def test_list_directory_with_hidden_files(self):
        """Test listing directory with and without hidden files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create visible and hidden files
            visible_file = os.path.join(temp_dir, "visible.txt")
            hidden_file = os.path.join(temp_dir, ".hidden.txt")

            with open(visible_file, "w") as f:
                f.write("visible content")
            with open(hidden_file, "w") as f:
                f.write("hidden content")

            # Test without hidden files
            result_no_hidden = list_directory(temp_dir, include_hidden=False)
            assert len(result_no_hidden) == 1
            assert result_no_hidden[0]["name"] == "visible.txt"

            # Test with hidden files
            result_with_hidden = list_directory(temp_dir, include_hidden=True)
            assert len(result_with_hidden) == 2
            result_names = [item["name"] for item in result_with_hidden]
            assert "visible.txt" in result_names
            assert ".hidden.txt" in result_names

    def test_list_directory_default_path(self):
        """Test listing directory with default path (current directory)."""
        result = list_directory()
        assert isinstance(result, list)
        # Should contain at least some files from the current directory
        assert len(result) >= 0


class TestReadJsonFile:
    """Test read_json_file function."""

    def test_read_valid_json_file(self):
        """Test reading a valid JSON file."""
        test_data = {"name": "test", "value": 42, "nested": {"key": "value"}}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = read_json_file(temp_path)
            assert result == test_data
        finally:
            os.unlink(temp_path)

    def test_read_invalid_json_file(self):
        """Test reading an invalid JSON file raises ValidationError."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write("{ invalid json content")
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                read_json_file(temp_path)

            assert "Invalid JSON" in str(exc_info.value)
            assert exc_info.value.field == "file_path"
        finally:
            os.unlink(temp_path)

    def test_read_nonexistent_json_file(self):
        """Test reading a non-existent JSON file raises MacroManError."""
        with pytest.raises(MacroManError) as exc_info:
            read_json_file("/nonexistent/file.json")

        assert "Failed to read JSON file" in str(exc_info.value)


class TestWriteJsonFile:
    """Test write_json_file function."""

    def test_write_json_file(self):
        """Test writing data to a JSON file."""
        test_data = {"name": "test", "value": 42, "nested": {"key": "value"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "test.json")

            result = write_json_file(temp_path, test_data)

            assert result["success"] is True
            assert "file_path" in result

            # Verify file was created and contains correct JSON
            with open(temp_path) as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data

    def test_write_json_file_with_custom_indent(self):
        """Test writing JSON file with custom indentation."""
        test_data = {"name": "test", "value": 42}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "test.json")

            result = write_json_file(temp_path, test_data, indent=4)

            assert result["success"] is True

            # Verify file was created with proper indentation
            with open(temp_path) as f:
                content = f.read()
                # Should have 4-space indentation
                assert '    "name"' in content
                assert '    "value"' in content

    def test_write_json_file_with_unicode(self):
        """Test writing JSON file with unicode content."""
        test_data = {"message": "Hello, 世界! 🌍", "emoji": "🚀"}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "test.json")

            result = write_json_file(temp_path, test_data)

            assert result["success"] is True

            # Verify file was created and contains correct unicode
            with open(temp_path, encoding="utf-8") as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data

    def test_write_json_file_existing_without_overwrite(self):
        """Test writing JSON file to existing file without overwrite raises ValidationError."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump({"original": "data"}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                write_json_file(temp_path, {"new": "data"}, overwrite=False)

            assert "File already exists" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
