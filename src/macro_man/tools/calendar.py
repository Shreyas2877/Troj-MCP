"""
Calendar tools for scheduling Google Meet invites via external service.
"""

import json
import re
from collections.abc import Iterable
from typing import Any

import httpx

from macro_man.config.settings import get_settings
from macro_man.utils.exceptions import MacroManError, ValidationError


def _schedule_meet_via_service(payload: dict[str, Any]) -> dict[str, Any]:
    """Call external service to schedule a meeting."""
    settings = get_settings()
    service_url = f"{settings.email_service_url}/schedule-meet"

    try:
        response = httpx.post(
            service_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

        if response.status_code == 200:
            return response.json()

        error_msg = f"Calendar service returned status {response.status_code}"
        try:
            detail = response.json()
            if "message" in detail:
                error_msg += f": {detail['message']}"
        except (ValueError, KeyError):
            error_msg += f": {response.text}"

        raise MacroManError(error_msg)

    except httpx.TimeoutException:
        raise MacroManError("Calendar service request timed out")
    except httpx.ConnectError:
        raise MacroManError("Could not connect to calendar service at localhost:3000")
    except httpx.RequestError as e:
        raise MacroManError(f"Calendar service request failed: {e!s}")
    except Exception as e:
        raise MacroManError(f"Unexpected error calling calendar service: {e!s}")


def _validate_emails(attendees: Iterable[str]) -> list[str]:
    """Validate attendee emails and return cleaned list."""
    cleaned: list[str] = []
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    for email in attendees:
        if not isinstance(email, str) or not email.strip():
            raise ValidationError(
                "Attendee email must be a non-empty string", field="attendees"
            )
        email_clean = email.strip()
        if not re.match(email_pattern, email_clean):
            raise ValidationError("Invalid attendee email format", field="attendees")
        cleaned.append(email_clean)
    return cleaned


def schedule_meet(
    title: str,
    description: str | None,
    start: str,
    end: str,
    timeZone: str | None = None,
    attendees: list[str] | None = None,
    sendUpdates: str | None = None,
) -> dict[str, Any]:
    """
    Schedule a Google Meet calendar invite via external service.
    """

    if not title or not title.strip():
        raise ValidationError("Title is required", field="title")
    if not start or not start.strip():
        raise ValidationError("Start datetime is required", field="start")
    if not end or not end.strip():
        raise ValidationError("End datetime is required", field="end")

    # Basic ISO8601-like validation for datetime strings
    iso_like = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$"
    if not re.match(iso_like, start.strip()):
        raise ValidationError(
            "start must be ISO8601 like 2025-10-21T10:00:00Z", field="start"
        )
    if not re.match(iso_like, end.strip()):
        raise ValidationError(
            "end must be ISO8601 like 2025-10-21T10:30:00Z", field="end"
        )

    if sendUpdates is not None and sendUpdates not in {"all", "externalOnly", "none"}:
        raise ValidationError(
            "sendUpdates must be one of: all, externalOnly, none",
            field="sendUpdates",
        )

    cleaned_attendees: list[str] | None = None
    if attendees is not None:
        if not isinstance(attendees, (list, tuple)) or len(attendees) == 0:
            raise ValidationError(
                "attendees must be a non-empty list of emails", field="attendees"
            )
        cleaned_attendees = _validate_emails(attendees)

    payload: dict[str, Any] = {
        "title": title.strip(),
        "start": start.strip(),
        "end": end.strip(),
    }
    if description is not None and description.strip():
        payload["description"] = description.strip()
    if timeZone is not None and timeZone.strip():
        payload["timeZone"] = timeZone.strip()
    if cleaned_attendees is not None:
        payload["attendees"] = cleaned_attendees
    if sendUpdates is not None:
        payload["sendUpdates"] = sendUpdates

    try:
        return _schedule_meet_via_service(payload)
    except Exception as e:
        raise MacroManError(f"Failed to schedule meeting: {e!s}")


def _list_events_via_service(payload: dict[str, Any]) -> dict[str, Any]:
    """Call external service to list calendar events."""
    settings = get_settings()
    service_url = f"{settings.email_service_url}/list-events"

    try:
        response = httpx.post(
            service_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

        if response.status_code == 200:
            return response.json()

        error_msg = f"Calendar list service returned status {response.status_code}"
        try:
            detail = response.json()
            if "message" in detail:
                error_msg += f": {detail['message']}"
        except (ValueError, KeyError):
            error_msg += f": {response.text}"

        raise MacroManError(error_msg)

    except httpx.TimeoutException:
        raise MacroManError("Calendar list service request timed out")
    except httpx.ConnectError:
        raise MacroManError("Could not connect to calendar service at localhost:3000")
    except httpx.RequestError as e:
        raise MacroManError(f"Calendar list service request failed: {e!s}")
    except Exception as e:
        raise MacroManError(f"Unexpected error calling calendar list service: {e!s}")


def list_events(
    timeMin: str,
    timeMax: str,
    maxResults: int | None = None,
    q: str | None = None,
) -> dict[str, Any]:
    """
    List calendar events via external service.

    Args:
        timeMin: Start time for event search (ISO8601 format)
        timeMax: End time for event search (ISO8601 format)
        maxResults: Maximum number of events to return
        q: Search query string

    Returns:
        Dictionary with list of events as provided by the service
    """
    if not timeMin or not timeMin.strip():
        raise ValidationError("timeMin is required", field="timeMin")
    if not timeMax or not timeMax.strip():
        raise ValidationError("timeMax is required", field="timeMax")

    # Basic ISO8601-like validation for datetime strings
    iso_like = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$"
    if not re.match(iso_like, timeMin.strip()):
        raise ValidationError(
            "timeMin must be ISO8601 like 2025-10-20T00:00:00Z", field="timeMin"
        )
    if not re.match(iso_like, timeMax.strip()):
        raise ValidationError(
            "timeMax must be ISO8601 like 2025-10-27T23:59:59Z", field="timeMax"
        )

    if maxResults is not None and (not isinstance(maxResults, int) or maxResults <= 0):
        raise ValidationError(
            "maxResults must be a positive integer", field="maxResults"
        )

    payload: dict[str, Any] = {
        "timeMin": timeMin.strip(),
        "timeMax": timeMax.strip(),
    }
    if maxResults is not None:
        payload["maxResults"] = maxResults
    if q is not None and q.strip():
        payload["q"] = q.strip()

    try:
        return _list_events_via_service(payload)
    except Exception as e:
        raise MacroManError(f"Failed to list events: {e!s}")


def register_calendar_tools(mcp_server) -> None:
    """Register calendar scheduling tools."""

    # Store references to implementation functions from module globals
    # to avoid shadowing issues when defining wrapper functions with same names
    _impl_schedule_meet = globals()["schedule_meet"]
    _impl_list_events = globals()["list_events"]

    @mcp_server.tool()
    def schedule_meet(
        title: str,
        description: str | None,
        start: str,
        end: str,
        timeZone: str | None = None,
        attendees: list[str] | None = None,
        sendUpdates: str | None = None,
    ) -> str:
        """Schedule a Google Meet calendar event via external service.

        Creates a calendar event with Google Meet link and sends invitations
        to specified attendees. Supports timezone-aware scheduling and
        configurable update notifications. Useful for automating meeting
        scheduling, coordinating team events, or managing calendars.

        Args:
            title: Meeting title (required)
            description: Meeting description or agenda (optional)
            start: Start time in ISO8601 format (e.g., "2025-10-21T10:00:00Z") (required)
            end: End time in ISO8601 format (e.g., "2025-10-21T11:00:00Z") (required)
            timeZone: Timezone identifier (e.g., "America/New_York") (optional)
            attendees: List of attendee email addresses (optional)
            sendUpdates: Who should receive updates - "all", "externalOnly", or "none" (optional)

        Returns:
            JSON string containing:
            - success: Whether the meeting was scheduled successfully
            - meetLink: Google Meet URL for the meeting
            - eventId: Calendar event identifier
            - start: Confirmed start time
            - end: Confirmed end time
            - attendees: List of invited attendees

        Raises:
            ValidationError: If required fields are missing, datetime format is invalid,
                           or attendee emails are invalid
        """
        try:
            result = _impl_schedule_meet(
                title=title,
                description=description,
                start=start,
                end=end,
                timeZone=timeZone,
                attendees=attendees,
                sendUpdates=sendUpdates,
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to schedule meeting",
                },
                indent=2,
            )

    @mcp_server.tool()
    def list_events(
        timeMin: str,
        timeMax: str,
        maxResults: int | None = None,
        q: str | None = None,
    ) -> str:
        """List calendar events from the external service within a time range.

        Retrieves calendar events from the configured calendar service within
        the specified time range. Supports optional search queries and result
        limiting. Useful for checking availability, viewing schedules, or
        finding specific events.

        Args:
            timeMin: Start of time range in ISO8601 format (e.g., "2025-10-20T00:00:00Z") (required)
            timeMax: End of time range in ISO8601 format (e.g., "2025-10-27T23:59:59Z") (required)
            maxResults: Maximum number of events to return (optional, must be positive)
            q: Search query string to filter events by title or description (optional)

        Returns:
            JSON string containing:
            - success: Whether the operation succeeded
            - events: List of event objects
            - count: Number of events returned
            Each event includes:
            - id: Event identifier
            - title: Event title
            - start: Start time
            - end: End time
            - description: Event description
            - attendees: List of attendees

        Raises:
            ValidationError: If time format is invalid or maxResults is not positive
        """
        try:
            result = _impl_list_events(
                timeMin=timeMin,
                timeMax=timeMax,
                maxResults=maxResults,
                q=q,
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to list events",
                },
                indent=2,
            )
