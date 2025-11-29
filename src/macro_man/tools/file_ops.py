"""File operation tools for the MCP server."""

import json
from pathlib import Path
from typing import Any

import structlog

from ..utils.exceptions import MacroManError, ValidationError

logger = structlog.get_logger(__name__)


def read_file(file_path: str) -> str:
    """Read the contents of a text file.

    Args:
        file_path: Path to the file to read

    Returns:
        The contents of the file
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(
                f"File does not exist: {file_path}", field="file_path"
            )

        if not path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}", field="file_path")

        with open(path, encoding="utf-8") as f:
            content = f.read()

        logger.info("File read", file_path=file_path, size=len(content))
        return content

    except (ValidationError, FileNotFoundError, PermissionError):
        # Re-raise validation errors and common file errors as-is
        raise
    except Exception as e:
        logger.error("Error reading file", file_path=file_path, error=str(e))
        raise MacroManError(f"Failed to read file: {e!s}")


def write_file(file_path: str, content: str, overwrite: bool = False) -> dict[str, Any]:
    """Write content to a text file.

    Args:
        file_path: Path where to write the file
        content: Content to write to the file
        overwrite: Whether to overwrite existing files

    Returns:
        Dictionary with operation result
    """
    try:
        path = Path(file_path)

        if path.exists() and not overwrite:
            raise ValidationError(
                f"File already exists: {file_path}. Use overwrite=True to replace it.",
                field="file_path",
            )

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        result = {
            "success": True,
            "file_path": str(path.absolute()),
            "size": len(content),
            "overwritten": path.exists() and overwrite,
        }

        logger.info("File written", **result)
        return result

    except (ValidationError, PermissionError, OSError):
        # Re-raise validation errors and common file errors as-is
        raise
    except Exception as e:
        logger.error("Error writing file", file_path=file_path, error=str(e))
        raise MacroManError(f"Failed to write file: {e!s}")


def list_directory(
    directory_path: str = ".", include_hidden: bool = False
) -> list[dict[str, Any]]:
    """List files and directories in a given path.

    Args:
        directory_path: Path to the directory to list
        include_hidden: Whether to include hidden files/directories

    Returns:
        List of dictionaries with file/directory information
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            raise ValidationError(
                f"Directory does not exist: {directory_path}", field="directory_path"
            )

        if not path.is_dir():
            raise ValidationError(
                f"Path is not a directory: {directory_path}", field="directory_path"
            )

        items = []
        for item in path.iterdir():
            if not include_hidden and item.name.startswith("."):
                continue

            items.append(
                {
                    "name": item.name,
                    "path": str(item),
                    "is_file": item.is_file(),
                    "is_directory": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime,
                }
            )

        # Sort by name
        items.sort(key=lambda x: str(x["name"]))

        logger.info("Directory listed", directory_path=directory_path, count=len(items))
        return items

    except (ValidationError, PermissionError, OSError):
        # Re-raise validation errors and common file errors as-is
        raise
    except Exception as e:
        logger.error(
            "Error listing directory", directory_path=directory_path, error=str(e)
        )
        raise MacroManError(f"Failed to list directory: {e!s}")


def read_json_file(file_path: str) -> dict[str, Any]:
    """Read and parse a JSON file.

    Args:
        file_path: Path to the JSON file to read

    Returns:
        Parsed JSON data as a dictionary
    """
    try:
        content = read_file(file_path)
        data = json.loads(content)

        logger.info("JSON file read", file_path=file_path)
        return data

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON", file_path=file_path, error=str(e))
        raise ValidationError(f"Invalid JSON in file: {e!s}", field="file_path")
    except Exception as e:
        logger.error("Error reading JSON file", file_path=file_path, error=str(e))
        raise MacroManError(f"Failed to read JSON file: {e!s}")


def write_json_file(
    file_path: str, data: dict[str, Any], indent: int = 2, overwrite: bool = False
) -> dict[str, Any]:
    """Write data to a JSON file.

    Args:
        file_path: Path where to write the JSON file
        data: Data to write as JSON
        indent: JSON indentation level
        overwrite: Whether to overwrite existing files

    Returns:
        Dictionary with operation result
    """
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        result = write_file(file_path, content, overwrite=overwrite)

        logger.info("JSON file written", file_path=file_path)
        return result

    except (ValidationError, PermissionError, OSError):
        # Re-raise validation errors and common file errors as-is
        raise
    except Exception as e:
        logger.error("Error writing JSON file", file_path=file_path, error=str(e))
        raise MacroManError(f"Failed to write JSON file: {e!s}")


def register_file_tools(mcp_server) -> None:
    """Register file operation tools."""

    # Store references to implementation functions from module globals
    # to avoid shadowing issues when defining wrapper functions with same names
    _impl_read_file = globals()["read_file"]
    _impl_write_file = globals()["write_file"]
    _impl_list_directory = globals()["list_directory"]
    _impl_read_json_file = globals()["read_json_file"]
    _impl_write_json_file = globals()["write_json_file"]

    @mcp_server.tool()
    def read_file(file_path: str) -> str:
        """Read the contents of a text file.

        Reads and returns the entire contents of a text file as a string.
        Supports UTF-8 encoding. Useful for reading configuration files,
        documentation, logs, or any text-based content.

        Args:
            file_path: Path to the file to read (relative or absolute)

        Returns:
            The file contents as a string

        Raises:
            ValidationError: If file doesn't exist or path is not a file
        """
        return _impl_read_file(file_path)

    @mcp_server.tool()
    def write_file(
        file_path: str, content: str, overwrite: bool = False
    ) -> dict[str, Any]:
        """Write content to a text file.

        Creates or updates a text file with the provided content. Automatically
        creates parent directories if they don't exist. By default, prevents
        overwriting existing files unless explicitly allowed.

        Args:
            file_path: Path where to write the file (relative or absolute)
            content: Text content to write to the file
            overwrite: If True, overwrites existing files. If False, raises
                      error if file exists (default: False)

        Returns:
            Dictionary containing:
            - success: Whether the operation succeeded
            - file_path: Absolute path of the written file
            - size: Size of the written content in bytes
            - overwritten: Whether an existing file was overwritten

        Raises:
            ValidationError: If file exists and overwrite is False
        """
        return _impl_write_file(file_path, content, overwrite)

    @mcp_server.tool()
    def list_directory(
        directory_path: str = ".", include_hidden: bool = False
    ) -> list[dict[str, Any]]:
        """List files and directories in a given path.

        Returns a list of all items (files and directories) in the specified
        directory. Each item includes metadata like name, path, type, size,
        and modification time. Can optionally include hidden files/directories.

        Args:
            directory_path: Path to the directory to list (default: current directory)
            include_hidden: If True, includes files/directories starting with '.'
                          (default: False)

        Returns:
            List of dictionaries, each containing:
            - name: Item name
            - path: Full path to the item
            - is_file: Whether the item is a file
            - is_directory: Whether the item is a directory
            - size: File size in bytes (None for directories)
            - modified: Modification timestamp

        Raises:
            ValidationError: If directory doesn't exist or path is not a directory
        """
        return _impl_list_directory(directory_path, include_hidden)

    @mcp_server.tool()
    def read_json_file(file_path: str) -> dict[str, Any]:
        """Read and parse a JSON file.

        Reads a JSON file and parses it into a Python dictionary. Validates
        that the file contains valid JSON syntax. Useful for reading configuration
        files, data files, or any structured JSON data.

        Args:
            file_path: Path to the JSON file to read

        Returns:
            Parsed JSON data as a dictionary

        Raises:
            ValidationError: If file doesn't exist or contains invalid JSON
        """
        return _impl_read_json_file(file_path)

    @mcp_server.tool()
    def write_json_file(
        file_path: str, data: dict[str, Any], indent: int = 2, overwrite: bool = False
    ) -> dict[str, Any]:
        """Write data to a JSON file with formatting.

        Serializes a Python dictionary to JSON format and writes it to a file.
        Automatically formats the JSON with indentation for readability.
        Creates parent directories if needed. Prevents overwriting by default.

        Args:
            file_path: Path where to write the JSON file
            data: Dictionary or JSON-serializable data to write
            indent: Number of spaces for JSON indentation (default: 2)
            overwrite: If True, overwrites existing files (default: False)

        Returns:
            Dictionary containing:
            - success: Whether the operation succeeded
            - file_path: Absolute path of the written file
            - size: Size of the written content in bytes
            - overwritten: Whether an existing file was overwritten

        Raises:
            ValidationError: If file exists and overwrite is False
        """
        return _impl_write_json_file(file_path, data, indent, overwrite)
