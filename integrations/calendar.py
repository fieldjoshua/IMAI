"""Google Calendar integration for event processing."""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from integrations.base import BaseIntegration
from config import Config


class CalendarIntegration(BaseIntegration):
    """Google Calendar integration for fetching events."""

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    def __init__(self, config: Config) -> None:
        """Initialize Calendar integration.

        Args:
            config: Config instance
        """
        super().__init__("Calendar")
        self.config = config
        self.service = None
        self.credentials: Optional[Credentials] = None
        self.token_file = ".calendar_token.json"

    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API.

        Returns:
            True if authentication successful
        """
        try:
            # Check for existing token
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_file, self.SCOPES
                )

            # If no valid credentials, start OAuth flow
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    from google.auth.transport.requests import Request

                    self.credentials.refresh(Request())
                else:
                    flow = Flow.from_client_config(
                        {
                            "web": {
                                "client_id": self.config.google_client_id,
                                "client_secret": self.config.google_client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": [self.config.google_redirect_uri],
                            }
                        },
                        self.SCOPES,
                    )
                    flow.redirect_uri = self.config.google_redirect_uri
                    auth_url, _ = flow.authorization_url(prompt="consent")
                    print(f"Please visit this URL to authorize: {auth_url}")
                    code = input("Enter the authorization code: ")
                    flow.fetch_token(code=code)
                    self.credentials = flow.credentials

                    # Save credentials
                    with open(self.token_file, "w") as token:
                        token.write(self.credentials.to_json())

            # Build service
            self.service = build("calendar", "v3", credentials=self.credentials)
            self.reset_error_count()
            return True

        except Exception as e:
            self.handle_error(e)
            return False

    def sync(self) -> Dict[str, Any]:
        """Sync events from Google Calendar.

        Returns:
            Dictionary with sync results
        """
        if not self.service:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        try:
            # Get events from now to 30 days ahead
            now = datetime.utcnow().isoformat() + "Z"
            future = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    timeMax=future,
                    maxResults=50,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            event_data = []
            for event in events:
                event_data.append(self._format_event(event))

            self.reset_error_count()
            return {
                "success": True,
                "events": event_data,
                "count": len(event_data),
            }

        except HttpError as e:
            self.handle_error(e)
            return {"success": False, "error": str(e)}

    def _format_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format calendar event for processing.

        Args:
            event: Google Calendar event object

        Returns:
            Formatted event dictionary
        """
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")

        return {
            "id": event.get("id", ""),
            "title": event.get("summary", "No Title"),
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "start": start,
            "end": end,
            "attendees": [a.get("email", "") for a in event.get("attendees", [])],
            "organizer": event.get("organizer", {}).get("email", ""),
            "status": event.get("status", ""),
        }

