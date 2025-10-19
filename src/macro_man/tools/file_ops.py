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

    @mcp_server.tool()
    def _read_file(file_path: str) -> str:
        return read_file(file_path)

    @mcp_server.tool()
    def _write_file(
        file_path: str, content: str, overwrite: bool = False
    ) -> dict[str, Any]:
        return write_file(file_path, content, overwrite)

    @mcp_server.tool()
    def _list_directory(
        directory_path: str = ".", include_hidden: bool = False
    ) -> list[dict[str, Any]]:
        return list_directory(directory_path, include_hidden)

    @mcp_server.tool()
    def _read_json_file(file_path: str) -> dict[str, Any]:
        return read_json_file(file_path)

    @mcp_server.tool()
    def _write_json_file(
        file_path: str, data: dict[str, Any], indent: int = 2, overwrite: bool = False
    ) -> dict[str, Any]:
        return write_json_file(file_path, data, indent, overwrite)
