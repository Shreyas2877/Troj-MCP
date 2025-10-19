"""Tests for email tools functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.config.settings import get_settings
from macro_man.tools.email import (
    _send_email_via_service,
    send_email,
)
from macro_man.utils.exceptions import MacroManError, ValidationError


class TestSendEmailViaService:
    """Test email sending via actual service."""

    @patch("macro_man.tools.email.httpx.post")
    def test_send_email_via_service_success(self, mock_post):
        """Test successful email sending via service."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Email sent successfully",
            "messageId": "<test-message-id@gmail.com>",
        }
        mock_post.return_value = mock_response

        result = _send_email_via_service(
            "test@example.com", "Test Subject", "Test Body"
        )

        assert result["success"] is True
        assert result["message"] == "Email sent successfully"
        assert result["messageId"] == "<test-message-id@gmail.com>"

        # Verify the HTTP call was made correctly
        settings = get_settings()
        expected_url = f"{settings.email_service_url}/send-email"
        mock_post.assert_called_once_with(
            expected_url,
            json={
                "to": "test@example.com",
                "subject": "Test Subject",
                "body": "Test Body",
            },
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    @patch("macro_man.tools.email.httpx.post")
    def test_send_email_via_service_http_error(self, mock_post):
        """Test email service HTTP error handling."""
        # Mock HTTP error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_post.return_value = mock_response

        with pytest.raises(MacroManError) as exc_info:
            _send_email_via_service("test@example.com", "Test", "Body")

        assert "Email service returned status 500" in str(exc_info.value)
        assert "Internal server error" in str(exc_info.value)

    @patch("macro_man.tools.email.httpx.post")
    def test_send_email_via_service_connection_error(self, mock_post):
        """Test email service connection error handling."""
        # Mock connection error
        import httpx

        mock_post.side_effect = httpx.ConnectError("Connection failed")

        with pytest.raises(MacroManError) as exc_info:
            _send_email_via_service("test@example.com", "Test", "Body")

        assert "Could not connect to email service" in str(exc_info.value)

    @patch("macro_man.tools.email.httpx.post")
    def test_send_email_via_service_timeout(self, mock_post):
        """Test email service timeout handling."""
        # Mock timeout error
        import httpx

        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        with pytest.raises(MacroManError) as exc_info:
            _send_email_via_service("test@example.com", "Test", "Body")

        assert "Email service request timed out" in str(exc_info.value)

    @patch("macro_man.tools.email.httpx.post")
    def test_send_email_via_service_request_error(self, mock_post):
        """Test email service request error handling."""
        # Mock request error
        import httpx

        mock_post.side_effect = httpx.RequestError("Request failed")

        with pytest.raises(MacroManError) as exc_info:
            _send_email_via_service("test@example.com", "Test", "Body")

        assert "Email service request failed" in str(exc_info.value)


class TestSendEmail:
    """Test email sending functionality."""

    @patch("macro_man.tools.email._send_email_via_service")
    def test_send_email_success(self, mock_send_service):
        """Test successful email sending."""
        # Mock successful email service response
        mock_send_service.return_value = {
            "success": True,
            "message": "Email sent successfully",
            "messageId": "<test-message-id@gmail.com>",
        }

        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Test body content",
        )

        assert result["success"] is True
        assert result["message"] == "Email sent successfully"
        assert result["messageId"] == "<test-message-id@gmail.com>"
        assert result["recipient"] == "test@example.com"
        assert result["subject"] == "Test Subject"
        assert result["body_length"] == len("Test body content")

        # Verify the service was called with correct parameters
        mock_send_service.assert_called_once_with(
            "test@example.com", "Test Subject", "Test body content"
        )

    @patch("macro_man.tools.email._send_email_via_service")
    def test_send_email_service_error(self, mock_send_service):
        """Test email sending when service returns error."""
        # Mock service error
        mock_send_service.side_effect = MacroManError("Service unavailable")

        with pytest.raises(MacroManError) as exc_info:
            send_email(
                to="test@example.com",
                subject="Test Subject",
                body="Test body",
            )

        assert "Service unavailable" in str(exc_info.value)

    def test_send_email_invalid_recipient(self):
        """Test email sending with invalid recipient."""
        with pytest.raises(ValidationError) as exc_info:
            send_email("", "Subject", "Body")

        assert "Recipient email address is required" in str(exc_info.value)
        assert exc_info.value.field == "to"

    def test_send_email_invalid_subject(self):
        """Test email sending with invalid subject."""
        with pytest.raises(ValidationError) as exc_info:
            send_email("test@example.com", "", "Body")

        assert "Email subject is required" in str(exc_info.value)
        assert exc_info.value.field == "subject"

    def test_send_email_invalid_body(self):
        """Test email sending with invalid body."""
        with pytest.raises(ValidationError) as exc_info:
            send_email("test@example.com", "Subject", "")

        assert "Email body is required" in str(exc_info.value)
        assert exc_info.value.field == "body"

    def test_send_email_invalid_email_format(self):
        """Test email sending with invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            send_email("invalid-email", "Subject", "Body")

        assert "Invalid email address format" in str(exc_info.value)
        assert exc_info.value.field == "to"

    @patch("macro_man.tools.email._send_email_via_service")
    def test_send_email_whitespace_handling(self, mock_send_service):
        """Test email sending with whitespace in inputs."""
        # Mock successful email service response
        mock_send_service.return_value = {
            "success": True,
            "message": "Email sent successfully",
            "messageId": "<test-message-id@gmail.com>",
        }

        result = send_email(
            to="  test@example.com  ",
            subject="  Test Subject  ",
            body="  Test body  ",
        )

        assert result["success"] is True
        assert result["recipient"] == "test@example.com"  # Whitespace trimmed
        assert result["subject"] == "Test Subject"  # Whitespace trimmed

        # Verify the service was called with trimmed values
        mock_send_service.assert_called_once_with(
            "test@example.com", "Test Subject", "Test body"
        )


class TestEmailToolsIntegration:
    """Integration tests for email tools."""

    @patch("macro_man.tools.email._send_email_via_service")
    def test_complete_email_workflow(self, mock_send_service):
        """Test complete email workflow."""
        # Mock successful email service response
        mock_send_service.return_value = {
            "success": True,
            "message": "Email sent successfully",
            "messageId": "<test-message-id@gmail.com>",
        }

        # Test sending
        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Hello, this is a test email.",
        )

        assert result["success"] is True
        assert result["recipient"] == "test@example.com"
        assert result["subject"] == "Test Subject"
        assert result["body_length"] == len("Hello, this is a test email.")

    def test_email_tools_error_handling(self):
        """Test error handling in email tools."""
        # Test invalid inputs
        with pytest.raises(ValidationError):
            send_email("", "Subject", "Body")

        with pytest.raises(ValidationError):
            send_email("test@example.com", "", "Body")

        with pytest.raises(ValidationError):
            send_email("test@example.com", "Subject", "")

        with pytest.raises(ValidationError):
            send_email("invalid-email", "Subject", "Body")
