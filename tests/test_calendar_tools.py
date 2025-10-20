"""Tests for calendar scheduling tool."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.config.settings import get_settings
from macro_man.tools.calendar import (
    _list_events_via_service,
    _schedule_meet_via_service,
    list_events,
    schedule_meet,
)
from macro_man.utils.exceptions import MacroManError, ValidationError


class TestScheduleMeetViaService:
    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "id": "abc",
            "status": "confirmed",
            "meetLink": "https://meet.google.com/xyz",
        }
        mock_post.return_value = mock_response

        payload = {
            "title": "Design sync",
            "start": "2025-10-21T10:00:00Z",
            "end": "2025-10-21T10:30:00Z",
            "attendees": ["user@example.com"],
        }

        result = _schedule_meet_via_service(payload)
        assert result["success"] is True
        assert result["id"] == "abc"

        settings = get_settings()
        expected_url = f"{settings.email_service_url}/schedule-meet"
        mock_post.assert_called_once_with(
            expected_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_http_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal error"}
        mock_post.return_value = mock_response

        with pytest.raises(MacroManError) as exc:
            _schedule_meet_via_service(
                {
                    "title": "X",
                    "start": "2025-01-01T00:00:00Z",
                    "end": "2025-01-01T00:30:00Z",
                }
            )

        assert "returned status 500" in str(exc.value)
        assert "Internal error" in str(exc.value)

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_timeout(self, mock_post):
        import httpx

        mock_post.side_effect = httpx.TimeoutException("timeout")
        with pytest.raises(MacroManError) as exc:
            _schedule_meet_via_service({})
        assert "timed out" in str(exc.value).lower()

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_connect_error(self, mock_post):
        import httpx

        mock_post.side_effect = httpx.ConnectError("connect")
        with pytest.raises(MacroManError) as exc:
            _schedule_meet_via_service({})
        assert "could not connect" in str(exc.value).lower()

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_request_error(self, mock_post):
        import httpx

        mock_post.side_effect = httpx.RequestError("boom")
        with pytest.raises(MacroManError) as exc:
            _schedule_meet_via_service({})
        assert "request failed" in str(exc.value).lower()


class TestScheduleMeet:
    @patch("macro_man.tools.calendar._schedule_meet_via_service")
    def test_schedule_meet_success(self, mock_service):
        mock_service.return_value = {
            "success": True,
            "id": "abc",
            "status": "confirmed",
            "meetLink": "https://meet.google.com/xyz",
        }

        result = schedule_meet(
            title="  Design sync  ",
            description="  Review MCP server changes  ",
            start="2025-10-21T10:00:00Z",
            end="2025-10-21T10:30:00Z",
            timeZone="UTC",
            attendees=[" user@example.com "],
            sendUpdates="all",
        )

        assert result["success"] is True
        mock_service.assert_called_once()
        called_payload = mock_service.call_args.args[0]
        assert called_payload["title"] == "Design sync"
        assert called_payload["description"] == "Review MCP server changes"
        assert called_payload["start"] == "2025-10-21T10:00:00Z"
        assert called_payload["end"] == "2025-10-21T10:30:00Z"
        assert called_payload["timeZone"] == "UTC"
        assert called_payload["attendees"] == ["user@example.com"]
        assert called_payload["sendUpdates"] == "all"

    def test_schedule_meet_missing_title(self):
        with pytest.raises(ValidationError) as exc:
            schedule_meet(
                title="",
                description=None,
                start="2025-10-21T10:00:00Z",
                end="2025-10-21T10:30:00Z",
            )
        assert exc.value.field == "title"

    def test_schedule_meet_invalid_datetime_format(self):
        with pytest.raises(ValidationError) as exc:
            schedule_meet(
                title="Design",
                description=None,
                start="2025-10-21 10:00:00",  # missing TZ
                end="2025-10-21T10:30:00Z",
            )
        assert exc.value.field == "start"

        with pytest.raises(ValidationError) as exc2:
            schedule_meet(
                title="Design",
                description=None,
                start="2025-10-21T10:00:00Z",
                end="2025-10-21 10:30:00",
            )
        assert exc2.value.field == "end"

    def test_schedule_meet_invalid_attendees(self):
        with pytest.raises(ValidationError) as exc:
            schedule_meet(
                title="Design",
                description=None,
                start="2025-10-21T10:00:00Z",
                end="2025-10-21T10:30:00Z",
                attendees=[],
            )
        assert exc.value.field == "attendees"

        with pytest.raises(ValidationError) as exc2:
            schedule_meet(
                title="Design",
                description=None,
                start="2025-10-21T10:00:00Z",
                end="2025-10-21T10:30:00Z",
                attendees=["invalid"],
            )
        assert exc2.value.field == "attendees"

    def test_schedule_meet_invalid_send_updates(self):
        with pytest.raises(ValidationError) as exc:
            schedule_meet(
                title="Design",
                description=None,
                start="2025-10-21T10:00:00Z",
                end="2025-10-21T10:30:00Z",
                sendUpdates="everyone",
            )
        assert exc.value.field == "sendUpdates"


class TestListEventsViaService:
    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "events": [
                {
                    "id": "event1",
                    "summary": "Team Meeting",
                    "start": {"dateTime": "2025-10-21T10:00:00Z"},
                    "end": {"dateTime": "2025-10-21T11:00:00Z"},
                }
            ],
            "total": 1,
        }
        mock_post.return_value = mock_response

        payload = {
            "timeMin": "2025-10-20T00:00:00Z",
            "timeMax": "2025-10-27T23:59:59Z",
            "maxResults": 10,
            "q": "meeting",
        }

        result = _list_events_via_service(payload)
        assert result["success"] is True
        assert result["total"] == 1
        assert len(result["events"]) == 1

        settings = get_settings()
        expected_url = f"{settings.email_service_url}/list-events"
        mock_post.assert_called_once_with(
            expected_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_http_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid time range"}
        mock_post.return_value = mock_response

        with pytest.raises(MacroManError) as exc:
            _list_events_via_service(
                {
                    "timeMin": "2025-10-20T00:00:00Z",
                    "timeMax": "2025-10-27T23:59:59Z",
                }
            )

        assert "returned status 400" in str(exc.value)
        assert "Invalid time range" in str(exc.value)

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_timeout(self, mock_post):
        import httpx

        mock_post.side_effect = httpx.TimeoutException("timeout")
        with pytest.raises(MacroManError) as exc:
            _list_events_via_service({})
        assert "timed out" in str(exc.value).lower()

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_connect_error(self, mock_post):
        import httpx

        mock_post.side_effect = httpx.ConnectError("connect")
        with pytest.raises(MacroManError) as exc:
            _list_events_via_service({})
        assert "could not connect" in str(exc.value).lower()

    @patch("macro_man.tools.calendar.httpx.post")
    def test_service_request_error(self, mock_post):
        import httpx

        mock_post.side_effect = httpx.RequestError("boom")
        with pytest.raises(MacroManError) as exc:
            _list_events_via_service({})
        assert "request failed" in str(exc.value).lower()


class TestListEvents:
    @patch("macro_man.tools.calendar._list_events_via_service")
    def test_list_events_success(self, mock_service):
        mock_service.return_value = {
            "success": True,
            "events": [
                {
                    "id": "event1",
                    "summary": "Team Meeting",
                    "start": {"dateTime": "2025-10-21T10:00:00Z"},
                    "end": {"dateTime": "2025-10-21T11:00:00Z"},
                }
            ],
            "total": 1,
        }

        result = list_events(
            timeMin="  2025-10-20T00:00:00Z  ",
            timeMax="  2025-10-27T23:59:59Z  ",
            maxResults=10,
            q="  meeting  ",
        )

        assert result["success"] is True
        mock_service.assert_called_once()
        called_payload = mock_service.call_args.args[0]
        assert called_payload["timeMin"] == "2025-10-20T00:00:00Z"
        assert called_payload["timeMax"] == "2025-10-27T23:59:59Z"
        assert called_payload["maxResults"] == 10
        assert called_payload["q"] == "meeting"

    @patch("macro_man.tools.calendar._list_events_via_service")
    def test_list_events_minimal_params(self, mock_service):
        mock_service.return_value = {"success": True, "events": [], "total": 0}

        result = list_events(
            timeMin="2025-10-20T00:00:00Z",
            timeMax="2025-10-27T23:59:59Z",
        )

        assert result["success"] is True
        called_payload = mock_service.call_args.args[0]
        assert "timeMin" in called_payload
        assert "timeMax" in called_payload
        assert "maxResults" not in called_payload
        assert "q" not in called_payload

    def test_list_events_missing_time_min(self):
        with pytest.raises(ValidationError) as exc:
            list_events(
                timeMin="",
                timeMax="2025-10-27T23:59:59Z",
            )
        assert exc.value.field == "timeMin"

    def test_list_events_missing_time_max(self):
        with pytest.raises(ValidationError) as exc:
            list_events(
                timeMin="2025-10-20T00:00:00Z",
                timeMax="",
            )
        assert exc.value.field == "timeMax"

    def test_list_events_invalid_time_format(self):
        with pytest.raises(ValidationError) as exc:
            list_events(
                timeMin="2025-10-20 00:00:00",  # missing TZ
                timeMax="2025-10-27T23:59:59Z",
            )
        assert exc.value.field == "timeMin"

        with pytest.raises(ValidationError) as exc2:
            list_events(
                timeMin="2025-10-20T00:00:00Z",
                timeMax="2025-10-27 23:59:59",  # missing TZ
            )
        assert exc2.value.field == "timeMax"

    def test_list_events_invalid_max_results(self):
        with pytest.raises(ValidationError) as exc:
            list_events(
                timeMin="2025-10-20T00:00:00Z",
                timeMax="2025-10-27T23:59:59Z",
                maxResults=0,  # invalid
            )
        assert exc.value.field == "maxResults"

        with pytest.raises(ValidationError) as exc2:
            list_events(
                timeMin="2025-10-20T00:00:00Z",
                timeMax="2025-10-27T23:59:59Z",
                maxResults="10",  # type: ignore[arg-type]
            )
        assert exc2.value.field == "maxResults"

    @patch("macro_man.tools.calendar._list_events_via_service")
    def test_list_events_empty_query_ignored(self, mock_service):
        mock_service.return_value = {"success": True, "events": [], "total": 0}

        list_events(
            timeMin="2025-10-20T00:00:00Z",
            timeMax="2025-10-27T23:59:59Z",
            q="   ",  # whitespace only
        )

        called_payload = mock_service.call_args.args[0]
        assert "q" not in called_payload
