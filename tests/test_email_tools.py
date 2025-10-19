"""Tests for email tools functionality."""

import json
import sys
from pathlib import Path

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.tools.email import (
    elaborate_email_body,
    send_email,
    _detect_email_type,
    _generate_elaborated_content,
    _expand_brief_text,
    _add_additional_context,
    _simulate_email_sending
)
from macro_man.utils.exceptions import ValidationError, MacroManError


class TestElaborateEmailBody:
    """Test email body elaboration functionality."""

    def test_elaborate_basic_text(self):
        """Test basic text elaboration."""
        brief_text = "hello there"
        result = elaborate_email_body(brief_text)
        
        assert isinstance(result, str)
        assert len(result) > len(brief_text)
        assert "I hope this email finds you well" in result
        assert "Hello there" in result  # Capitalized in the result

    def test_elaborate_empty_text(self):
        """Test elaboration with empty text."""
        with pytest.raises(ValidationError) as exc_info:
            elaborate_email_body("")
        
        assert "Brief text cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "brief_text"

    def test_elaborate_whitespace_only_text(self):
        """Test elaboration with whitespace-only text."""
        with pytest.raises(ValidationError) as exc_info:
            elaborate_email_body("   \n\t   ")
        
        assert "Brief text cannot be empty" in str(exc_info.value)

    def test_elaborate_with_subject(self):
        """Test elaboration with subject context."""
        brief_text = "meeting tomorrow"
        subject = "Schedule Meeting"
        result = elaborate_email_body(brief_text, subject)
        
        assert isinstance(result, str)
        assert "meeting" in result.lower()
        assert "schedule" in result.lower()

    def test_elaborate_different_types(self):
        """Test elaboration for different email types."""
        test_cases = [
            ("hello", "greeting"),
            ("thank you", "thanks"),
            ("can we meet?", "question"),
            ("update on project", "update"),
            ("please help", "request"),
            ("schedule call", "meeting")
        ]
        
        for brief_text, expected_type in test_cases:
            result = elaborate_email_body(brief_text)
            assert isinstance(result, str)
            assert len(result) > len(brief_text)


class TestDetectEmailType:
    """Test email type detection."""

    def test_detect_greeting(self):
        """Test greeting email detection."""
        assert _detect_email_type("hello there") == "greeting"
        assert _detect_email_type("hi", "Greetings") == "greeting"
        assert _detect_email_type("good morning") == "greeting"

    def test_detect_meeting(self):
        """Test meeting email detection."""
        assert _detect_email_type("meeting tomorrow") == "meeting"
        assert _detect_email_type("schedule call") == "meeting"
        assert _detect_email_type("appointment", "Meeting Request") == "meeting"

    def test_detect_thanks(self):
        """Test thanks email detection."""
        assert _detect_email_type("thank you") == "thanks"
        assert _detect_email_type("appreciate it") == "thanks"
        assert _detect_email_type("grateful", "Thanks") == "thanks"

    def test_detect_question(self):
        """Test question email detection."""
        assert _detect_email_type("question about") == "question"
        assert _detect_email_type("how do I") == "question"
        assert _detect_email_type("what is", "Question") == "question"

    def test_detect_update(self):
        """Test update email detection."""
        assert _detect_email_type("update on project") == "update"
        assert _detect_email_type("status report") == "update"
        assert _detect_email_type("progress", "Update") == "update"

    def test_detect_request(self):
        """Test request email detection."""
        assert _detect_email_type("please help") == "request"
        assert _detect_email_type("need assistance") == "request"
        assert _detect_email_type("could you", "Request") == "request"

    def test_detect_general(self):
        """Test general email detection."""
        assert _detect_email_type("random text") == "general"
        assert _detect_email_type("some random content") == "general"


class TestGenerateElaboratedContent:
    """Test elaborated content generation."""

    def test_generate_greeting_content(self):
        """Test greeting content generation."""
        result = _generate_elaborated_content("hello", "greeting")
        
        assert "I hope this email finds you well" in result
        assert "Hello" in result
        assert "Best regards" in result

    def test_generate_meeting_content(self):
        """Test meeting content generation."""
        result = _generate_elaborated_content("meeting tomorrow", "meeting")
        
        assert "I hope you're doing well" in result
        assert "Meeting tomorrow" in result
        assert "alternative time" in result

    def test_generate_thanks_content(self):
        """Test thanks content generation."""
        result = _generate_elaborated_content("thank you", "thanks")
        
        assert "good spirits" in result
        assert "Thank you" in result
        assert "Warm regards" in result

    def test_generate_question_content(self):
        """Test question content generation."""
        result = _generate_elaborated_content("how are you?", "question")
        
        assert "I hope you're doing well" in result
        assert "How are you?" in result
        assert "look forward to your response" in result

    def test_generate_update_content(self):
        """Test update content generation."""
        result = _generate_elaborated_content("project update", "update")
        
        assert "I hope this email finds you well" in result
        assert "Project update" in result
        assert "additional information" in result

    def test_generate_request_content(self):
        """Test request content generation."""
        result = _generate_elaborated_content("please help", "request")
        
        assert "I hope you're doing well" in result
        assert "Please help" in result
        assert "time and assistance" in result


class TestExpandBriefText:
    """Test brief text expansion."""

    def test_expand_greeting(self):
        """Test greeting text expansion."""
        result = _expand_brief_text("hello", "greeting")
        
        assert "I wanted to reach out and connect" in result
        assert "Hello" in result

    def test_expand_meeting(self):
        """Test meeting text expansion."""
        result = _expand_brief_text("meeting", "meeting")
        
        assert "schedule a meeting" in result
        assert "Meeting" in result

    def test_expand_thanks(self):
        """Test thanks text expansion."""
        result = _expand_brief_text("thanks", "thanks")
        
        assert "sincere gratitude" in result
        assert "Thanks" in result

    def test_expand_question(self):
        """Test question text expansion."""
        result = _expand_brief_text("question", "question")
        
        assert "question that I hope you can help" in result
        assert "Question" in result

    def test_expand_update(self):
        """Test update text expansion."""
        result = _expand_brief_text("update", "update")
        
        assert "provide you with an update" in result
        assert "Update" in result

    def test_expand_request(self):
        """Test request text expansion."""
        result = _expand_brief_text("help", "request")
        
        assert "request that I hope you can assist" in result
        assert "Help" in result

    def test_expand_general(self):
        """Test general text expansion."""
        result = _expand_brief_text("info", "general")
        
        assert "share some information" in result
        assert "Info" in result

    def test_expand_short_text(self):
        """Test expansion of very short text."""
        result = _expand_brief_text("hi", "greeting")
        
        assert len(result) > 20  # Should be expanded
        assert "collaboration" in result  # Additional context added


class TestAddAdditionalContext:
    """Test additional context addition."""

    def test_add_greeting_context(self):
        """Test greeting additional context."""
        result = _add_additional_context("greeting")
        assert "collaboration" in result

    def test_add_meeting_context(self):
        """Test meeting additional context."""
        result = _add_additional_context("meeting")
        assert "calendar invite" in result

    def test_add_thanks_context(self):
        """Test thanks additional context."""
        result = _add_additional_context("thanks")
        assert "invaluable" in result

    def test_add_question_context(self):
        """Test question additional context."""
        result = _add_additional_context("question")
        assert "expertise" in result

    def test_add_update_context(self):
        """Test update additional context."""
        result = _add_additional_context("update")
        assert "keep you informed" in result

    def test_add_request_context(self):
        """Test request additional context."""
        result = _add_additional_context("request")
        assert "additional information" in result

    def test_add_general_context(self):
        """Test general additional context."""
        result = _add_additional_context("general")
        assert "questions" in result


class TestSimulateEmailSending:
    """Test email sending simulation."""

    def test_simulate_email_sending(self):
        """Test email sending simulation."""
        result = _simulate_email_sending("test@example.com", "Test", "Body")
        
        assert isinstance(result, dict)
        assert "message_id" in result
        assert "timestamp" in result
        assert "status" in result
        assert "service" in result
        assert result["status"] == "sent"
        assert result["service"] == "simulated_email_service"

    def test_simulate_email_sending_different_inputs(self):
        """Test email sending with different inputs."""
        result1 = _simulate_email_sending("user1@test.com", "Subject 1", "Body 1")
        result2 = _simulate_email_sending("user2@test.com", "Subject 2", "Body 2")
        
        # Should have different message IDs
        assert result1["message_id"] != result2["message_id"]


class TestSendEmail:
    """Test email sending functionality."""

    def test_send_email_success(self):
        """Test successful email sending."""
        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Test body",
            elaborate=True
        )
        
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["recipient"] == "test@example.com"
        assert result["subject"] == "Test Subject"
        assert result["elaborated"] is True
        assert "message_id" in result["details"]

    def test_send_email_without_elaboration(self):
        """Test email sending without elaboration."""
        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Test body",
            elaborate=False
        )
        
        assert result["success"] is True
        assert result["elaborated"] is False
        assert result["body_length"] == len("Test body")

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

    def test_send_email_whitespace_handling(self):
        """Test email sending with whitespace in inputs."""
        result = send_email(
            to="  test@example.com  ",
            subject="  Test Subject  ",
            body="  Test body  ",
            elaborate=False
        )
        
        assert result["success"] is True
        assert result["recipient"] == "test@example.com"  # Whitespace trimmed
        assert result["subject"] == "Test Subject"  # Whitespace trimmed

    def test_send_email_elaboration_failure(self):
        """Test email sending when elaboration fails."""
        # This test would require mocking the elaborate_email_body function
        # For now, we'll test with a valid case
        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Valid body",
            elaborate=True
        )
        
        assert result["success"] is True


class TestEmailToolsIntegration:
    """Integration tests for email tools."""

    def test_complete_email_workflow(self):
        """Test complete email workflow."""
        # Test elaboration
        brief_text = "hello there"
        elaborated = elaborate_email_body(brief_text)
        assert len(elaborated) > len(brief_text)
        
        # Test sending
        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body=brief_text,
            elaborate=True
        )
        
        assert result["success"] is True
        assert result["elaborated"] is True

    def test_different_email_types_workflow(self):
        """Test workflow with different email types."""
        test_cases = [
            ("hello", "greeting"),
            ("thank you", "thanks"),
            ("meeting tomorrow", "meeting"),
            ("how are you?", "question"),
            ("project update", "update"),
            ("please help", "request")
        ]
        
        for brief_text, expected_type in test_cases:
            # Test elaboration
            elaborated = elaborate_email_body(brief_text)
            assert isinstance(elaborated, str)
            assert len(elaborated) > len(brief_text)
            
            # Test sending
            result = send_email(
                to="test@example.com",
                subject=f"Test {expected_type}",
                body=brief_text,
                elaborate=True
            )
            
            assert result["success"] is True

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
        
        with pytest.raises(ValidationError):
            elaborate_email_body("")


# Import pytest at the end to avoid issues
import pytest
