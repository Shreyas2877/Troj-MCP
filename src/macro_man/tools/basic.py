"""Basic utility tools for the MCP server."""

from typing import Any

import structlog

from ..utils.exceptions import ValidationError

logger = structlog.get_logger(__name__)


def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    try:
        result = a + b
        logger.info("Numbers added", a=a, b=b, result=result)
        return result
    except Exception as e:
        logger.error("Error adding numbers", error=str(e))
        raise ValidationError(f"Failed to add numbers: {e!s}")


def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The product of a and b
    """
    try:
        result = a * b
        logger.info("Numbers multiplied", a=a, b=b, result=result)
        return result
    except Exception as e:
        logger.error("Error multiplying numbers", error=str(e))
        raise ValidationError(f"Failed to multiply numbers: {e!s}")


def greet_user(name: str) -> str:
    """Greet a user by name.

    Args:
        name: The name of the user to greet

    Returns:
        A personalized greeting message
    """
    if not name or not name.strip():
        raise ValidationError("Name cannot be empty", field="name")

    greeting = f"Hello, {name.strip()}! Nice to meet you."
    logger.info("User greeted", name=name)
    return greeting


def get_system_info() -> dict[str, Any]:
    """Get basic system information.

    Returns:
        Dictionary containing system information
    """
    import platform
    import sys
    from datetime import datetime

    info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info("System info requested")
    return info


def echo_message(message: str) -> str:
    """Echo back a message (useful for testing).

    Args:
        message: The message to echo back

    Returns:
        The same message that was sent
    """
    if not message:
        raise ValidationError("Message cannot be empty", field="message")

    logger.info("Message echoed", message=message)
    return f"Echo: {message}"


def register_basic_tools(mcp_server) -> None:
    """Register basic utility tools."""

    @mcp_server.tool()
    def _add_numbers(a: float, b: float) -> float:
        return add_numbers(a, b)

    @mcp_server.tool()
    def _multiply_numbers(a: float, b: float) -> float:
        return multiply_numbers(a, b)

    @mcp_server.tool()
    def _greet_user(name: str) -> str:
        return greet_user(name)

    @mcp_server.tool()
    def _get_system_info() -> dict[str, Any]:
        return get_system_info()

    @mcp_server.tool()
    def _echo_message(message: str) -> str:
        return echo_message(message)
