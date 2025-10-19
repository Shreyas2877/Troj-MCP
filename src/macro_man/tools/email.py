"""
Email tools for sending emails with AI-powered content elaboration.
"""

import json
import re
from typing import Any

import httpx

from macro_man.config.settings import get_settings
from macro_man.utils.exceptions import MacroManError, ValidationError


def elaborate_email_body(brief_text: str, subject: str = "") -> str:
    """
    Elaborate a brief email body into comprehensive content.

    Args:
        brief_text: The brief text provided by the user
        subject: Optional email subject for context

    Returns:
        Elaborated email body content

    Raises:
        ValidationError: If brief_text is empty or invalid
        MacroManError: If elaboration fails
    """
    if not brief_text or not brief_text.strip():
        raise ValidationError("Brief text cannot be empty", field="brief_text")

    # Clean the input
    brief_text = brief_text.strip()

    # Simple AI-like elaboration using patterns and templates
    # In a real implementation, you'd use an actual AI service like OpenAI

    # Detect the type of email based on keywords
    email_type = _detect_email_type(brief_text, subject)

    # Generate elaborated content based on type
    elaborated_content = _generate_elaborated_content(brief_text, email_type, subject)

    return elaborated_content


def _detect_email_type(text: str, subject: str = "") -> str:
    """Detect the type of email based on content and subject."""
    text_lower = text.lower()
    subject_lower = subject.lower()
    combined = f"{text_lower} {subject_lower}"

    # Greeting patterns
    if any(
        word in combined
        for word in [
            "hello",
            "hi",
            "hey",
            "greetings",
            "good morning",
            "good afternoon",
        ]
    ):
        return "greeting"

    # Meeting patterns
    if any(
        word in combined
        for word in ["meeting", "schedule", "appointment", "call", "discuss"]
    ):
        return "meeting"

    # Thank you patterns
    if any(word in combined for word in ["thank", "thanks", "appreciate", "grateful"]):
        return "thanks"

    # Question patterns
    if any(
        word in combined
        for word in [
            "question",
            "ask",
            "wonder",
            "?",
            "how",
            "what",
            "when",
            "where",
            "why",
        ]
    ):
        return "question"

    # Update patterns
    if any(
        word in combined
        for word in ["update", "status", "progress", "report", "inform"]
    ):
        return "update"

    # Request patterns
    if any(
        word in combined
        for word in ["request", "need", "please", "could you", "would you"]
    ):
        return "request"

    # Default to general
    return "general"


def _generate_elaborated_content(
    brief_text: str, email_type: str, subject: str = ""
) -> str:
    """Generate elaborated content based on email type."""

    # Use subject for additional context if provided
    if subject:
        brief_text = f"{brief_text} (Subject: {subject})"

    templates = {
        "greeting": {
            "opening": "I hope this email finds you well.",
            "closing": "I look forward to hearing from you soon.\n\nBest regards",
        },
        "meeting": {
            "opening": "I hope you're doing well.",
            "closing": "Please let me know if this time works for you, or if you'd prefer an alternative time.\n\nBest regards",
        },
        "thanks": {
            "opening": "I hope this message finds you in good spirits.",
            "closing": "Once again, thank you for your time and consideration.\n\nWarm regards",
        },
        "question": {
            "opening": "I hope you're doing well.",
            "closing": "I appreciate your time and look forward to your response.\n\nBest regards",
        },
        "update": {
            "opening": "I hope this email finds you well.",
            "closing": "Please let me know if you need any additional information or have any questions.\n\nBest regards",
        },
        "request": {
            "opening": "I hope you're doing well.",
            "closing": "I understand this may require some time, and I appreciate your consideration.\n\nThank you for your time and assistance.\n\nBest regards",
        },
        "general": {
            "opening": "I hope this email finds you well.",
            "closing": "I look forward to hearing from you.\n\nBest regards",
        },
    }

    template = templates.get(email_type, templates["general"])

    # Build the elaborated content
    content_parts = []

    # Opening
    content_parts.append(template["opening"])
    content_parts.append("")

    # Main content - expand the brief text
    expanded_content = _expand_brief_text(brief_text, email_type)
    content_parts.append(expanded_content)
    content_parts.append("")

    # Closing
    content_parts.append(template["closing"])

    return "\n".join(content_parts)


def _expand_brief_text(text: str, email_type: str) -> str:
    """Expand brief text into more comprehensive content."""

    # Add context based on email type
    expansions = {
        "greeting": "I wanted to reach out and connect with you. ",
        "meeting": "I'd like to schedule a meeting to discuss this further. ",
        "thanks": "I wanted to express my sincere gratitude. ",
        "question": "I have a question that I hope you can help me with. ",
        "update": "I wanted to provide you with an update on this matter. ",
        "request": "I have a request that I hope you can assist me with. ",
        "general": "I wanted to share some information with you. ",
    }

    expansion = expansions.get(email_type, expansions["general"])

    # Capitalize the first letter of the original text
    if text:
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

    # Combine expansion with original text
    expanded = expansion + text

    # Add additional context if the text is very short
    if len(text) < 20:
        additional_context = _add_additional_context(email_type)
        expanded += additional_context

    return expanded


def _add_additional_context(email_type: str) -> str:
    """Add additional context for very brief messages."""

    contexts = {
        "greeting": " I hope we can connect and discuss potential opportunities for collaboration.",
        "meeting": " Please let me know your availability and I'll send over a calendar invite.",
        "thanks": " Your assistance has been invaluable, and I truly appreciate your time and effort.",
        "question": " I believe your expertise in this area would be very helpful.",
        "update": " I'll continue to keep you informed as more information becomes available.",
        "request": " I understand this may require some time, and I'm happy to provide any additional information you might need.",
        "general": " Please let me know if you have any questions or need any clarification.",
    }

    return contexts.get(email_type, contexts["general"])


def send_email(
    to: str, subject: str, body: str, elaborate: bool = True
) -> dict[str, Any]:
    """
    Send an email with optional AI-powered body elaboration.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (will be elaborated if elaborate=True)
        elaborate: Whether to elaborate the body content

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

    # Elaborate body if requested
    if elaborate:
        try:
            elaborated_body = elaborate_email_body(body, subject)
        except Exception as e:
            raise MacroManError(f"Failed to elaborate email body: {e!s}")
    else:
        elaborated_body = body

    # Send email via the actual email service
    try:
        # Call the real email service
        email_result = _send_email_via_service(to, subject, elaborated_body)

        return {
            "success": email_result.get("success", False),
            "message": email_result.get("message", "Email sending completed"),
            "messageId": email_result.get("messageId"),
            "recipient": to,
            "subject": subject,
            "body_length": len(elaborated_body),
            "elaborated": elaborate,
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
    def _send_email(to: str, subject: str, body: str, elaborate: bool = True) -> str:
        """
        Send an email with optional AI-powered body elaboration.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (will be elaborated if elaborate=True)
            elaborate: Whether to elaborate the body content (default: True)

        Returns:
            JSON string with email sending result
        """
        try:
            result = send_email(to, subject, body, elaborate)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(
                {"success": False, "error": str(e), "message": "Failed to send email"},
                indent=2,
            )

    @mcp_server.tool()
    def _elaborate_email_body(brief_text: str, subject: str = "") -> str:
        """
        Elaborate a brief email body into comprehensive content.

        Args:
            brief_text: The brief text to elaborate
            subject: Optional email subject for context

        Returns:
            Elaborated email body content
        """
        try:
            elaborated = elaborate_email_body(brief_text, subject)
            return elaborated
        except Exception as e:
            return f"Error elaborating email body: {e!s}"
