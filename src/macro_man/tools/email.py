"""
Email tools for sending emails via external email service.
"""

import json
import re
from typing import Any

import httpx

from macro_man.config.settings import get_settings
from macro_man.utils.exceptions import MacroManError, ValidationError


def send_email(to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Send an email via the external email service.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content

    Returns:
        Dictionary with email sending result

    Raises:
        ValidationError: If required parameters are invalid
        MacroManError: If email sending fails
    """
    # Validate inputs
    if not to or not to.strip():
        raise ValidationError("Recipient email address is required", field="to")

    if not subject or not subject.strip():
        raise ValidationError("Email subject is required", field="subject")

    if not body or not body.strip():
        raise ValidationError("Email body is required", field="body")

    # Clean inputs
    to = to.strip()
    subject = subject.strip()
    body = body.strip()

    # Validate email format (basic validation)
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, to):
        raise ValidationError("Invalid email address format", field="to")

    # Send email via the actual email service
    try:
        email_result = _send_email_via_service(to, subject, body)

        return {
            "success": email_result.get("success", False),
            "message": email_result.get("message", "Email sent successfully"),
            "messageId": email_result.get("messageId"),
            "recipient": to,
            "subject": subject,
            "body_length": len(body),
            "details": email_result,
        }

    except Exception as e:
        raise MacroManError(f"Failed to send email: {e!s}")


def _send_email_via_service(to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Send email via the actual email service.
    """

    # Get email service URL from settings
    settings = get_settings()
    email_service_url = f"{settings.email_service_url}/send-email"

    # Prepare the request payload
    payload = {"to": to, "subject": subject, "body": body}

    try:
        # Make HTTP request to the email service
        response = httpx.post(
            email_service_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            # Handle HTTP errors
            error_msg = f"Email service returned status {response.status_code}"
            try:
                error_detail = response.json()
                if "message" in error_detail:
                    error_msg += f": {error_detail['message']}"
            except (ValueError, KeyError):
                error_msg += f": {response.text}"

            raise MacroManError(error_msg)

    except httpx.TimeoutException:
        raise MacroManError("Email service request timed out")
    except httpx.ConnectError:
        raise MacroManError("Could not connect to email service at localhost:3000")
    except httpx.RequestError as e:
        raise MacroManError(f"Email service request failed: {e!s}")
    except Exception as e:
        raise MacroManError(f"Unexpected error calling email service: {e!s}")


def register_email_tools(mcp_server):
    """Register email tools with the MCP server."""

    @mcp_server.tool()
    def _send_email(to: str, subject: str, body: str) -> str:
        """
        Send an email via the external email service.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content

        Returns:
            JSON string with email sending result
        """
        try:
            result = send_email(to, subject, body)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(
                {"success": False, "error": str(e), "message": "Failed to send email"},
                indent=2,
            )
