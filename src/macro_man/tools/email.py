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


def _read_email_via_service(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Read emails via the external email service using provided filters.

    Args:
        payload: Dictionary containing filter parameters

    Returns:
        Dictionary with read email results as provided by the service
    """

    settings = get_settings()
    read_service_url = f"{settings.email_service_url}/read-email"

    try:
        response = httpx.post(
            read_service_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Email read service returned status {response.status_code}"
            try:
                error_detail = response.json()
                if "message" in error_detail:
                    error_msg += f": {error_detail['message']}"
            except (ValueError, KeyError):
                error_msg += f": {response.text}"

            raise MacroManError(error_msg)

    except httpx.TimeoutException:
        raise MacroManError("Email read service request timed out")
    except httpx.ConnectError:
        raise MacroManError("Could not connect to email service at localhost:3000")
    except httpx.RequestError as e:
        raise MacroManError(f"Email read service request failed: {e!s}")
    except Exception as e:
        raise MacroManError(f"Unexpected error calling email read service: {e!s}")


def read_email(
    fromName: str | None = None,
    subjectContains: str | None = None,
    threadContains: str | None = None,
    after: str | None = None,
    maxResults: int | None = None,
    includeBody: bool | None = None,
) -> dict[str, Any]:
    """
    Read emails using optional filters via the external email service.

    Filters:
        fromName: Filter by sender display name
        subjectContains: Filter emails whose subject contains this text
        threadContains: Filter anywhere in thread content contains this text
        after: ISO date string YYYY-MM-DD to filter emails after this date
        maxResults: Maximum number of emails to return
        includeBody: Whether to include full body content in results
    """

    # Validate simple types
    if maxResults is not None and (not isinstance(maxResults, int) or maxResults <= 0):
        raise ValidationError(
            "maxResults must be a positive integer", field="maxResults"
        )

    if after is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", after.strip()):
        # Basic YYYY-MM-DD validation
        raise ValidationError(
            "after must be a date string in format YYYY-MM-DD", field="after"
        )

    # Build payload with only provided keys
    payload: dict[str, Any] = {}
    if fromName is not None and fromName.strip():
        payload["fromName"] = fromName.strip()
    if subjectContains is not None and subjectContains.strip():
        payload["subjectContains"] = subjectContains.strip()
    if threadContains is not None and threadContains.strip():
        payload["threadContains"] = threadContains.strip()
    if after is not None and after.strip():
        payload["after"] = after.strip()
    if maxResults is not None:
        payload["maxResults"] = maxResults
    if includeBody is not None:
        payload["includeBody"] = bool(includeBody)

    try:
        result = _read_email_via_service(payload)
        return result
    except Exception as e:
        raise MacroManError(f"Failed to read emails: {e!s}")


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

    @mcp_server.tool()
    def _read_email(
        fromName: str | None = None,
        subjectContains: str | None = None,
        threadContains: str | None = None,
        after: str | None = None,
        maxResults: int | None = None,
        includeBody: bool | None = None,
    ) -> str:
        """
        Read emails from the external email service using optional filters.

        Returns:
            JSON string with read email results
        """
        try:
            result = read_email(
                fromName=fromName,
                subjectContains=subjectContains,
                threadContains=threadContains,
                after=after,
                maxResults=maxResults,
                includeBody=includeBody,
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(
                {"success": False, "error": str(e), "message": "Failed to read emails"},
                indent=2,
            )
