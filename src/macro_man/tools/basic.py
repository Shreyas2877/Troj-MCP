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

    # Store references to implementation functions from module globals
    # to avoid shadowing issues when defining wrapper functions with same names
    _impl_add_numbers = globals()["add_numbers"]
    _impl_multiply_numbers = globals()["multiply_numbers"]
    _impl_greet_user = globals()["greet_user"]
    _impl_get_system_info = globals()["get_system_info"]
    _impl_echo_message = globals()["echo_message"]

    @mcp_server.tool()
    def add_numbers(a: float, b: float) -> float:
        """Add two numbers together and return the sum.

        This tool performs basic arithmetic addition. Useful for calculations,
        aggregations, or any scenario where you need to sum numeric values.

        Args:
            a: First number to add
            b: Second number to add

        Returns:
            The sum of a and b as a float
        """
        return _impl_add_numbers(a, b)

    @mcp_server.tool()
    def multiply_numbers(a: float, b: float) -> float:
        """Multiply two numbers together and return the product.

        This tool performs basic arithmetic multiplication. Useful for calculations,
        scaling values, or computing areas/volumes.

        Args:
            a: First number to multiply
            b: Second number to multiply

        Returns:
            The product of a and b as a float
        """
        return _impl_multiply_numbers(a, b)

    @mcp_server.tool()
    def greet_user(name: str) -> str:
        """Greet a user with a personalized message.

        Creates a friendly greeting message using the provided name. Useful for
        personalizing interactions and creating welcoming experiences.

        Args:
            name: The name of the user to greet (must be non-empty)

        Returns:
            A personalized greeting message
        """
        return _impl_greet_user(name)

    @mcp_server.tool()
    def get_system_info() -> dict[str, Any]:
        """Get basic system information about the host machine.

        Retrieves fundamental system details including platform, Python version,
        architecture, processor type, and current timestamp. Useful for
        diagnostics, compatibility checks, or system identification.

        Returns:
            Dictionary containing:
            - platform: Operating system platform string
            - python_version: Python interpreter version
            - architecture: System architecture (e.g., 64bit)
            - processor: Processor type
            - timestamp: Current UTC timestamp in ISO format
        """
        return _impl_get_system_info()

    @mcp_server.tool()
    def echo_message(message: str) -> str:
        """Echo back a message (useful for testing and debugging).

        Returns the input message prefixed with "Echo: ". This tool is primarily
        useful for testing connectivity, debugging communication, or verifying
        that the MCP server is responding correctly.

        Args:
            message: The message to echo back (must be non-empty)

        Returns:
            The echoed message with "Echo: " prefix
        """
        return _impl_echo_message(message)
