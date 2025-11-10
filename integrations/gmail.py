"""Gmail integration for email processing."""

import os
import base64
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from integrations.base import BaseIntegration
from config import Config


class GmailIntegration(BaseIntegration):
    """Gmail integration for fetching and processing emails."""

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, config: Config) -> None:
        """Initialize Gmail integration.

        Args:
            config: Config instance
        """
        super().__init__("Gmail")
        self.config = config
        self.service = None
        self.credentials: Optional[Credentials] = None
        self.token_file = ".gmail_token.json"

    def authenticate(self) -> bool:
        """Authenticate with Gmail API.

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
                if (
                    self.credentials
                    and self.credentials.expired
                    and self.credentials.refresh_token
                ):
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
            self.service = build("gmail", "v1", credentials=self.credentials)
            self.reset_error_count()
            return True

        except Exception as e:
            self.handle_error(e)
            return False

    def sync(self) -> Dict[str, Any]:
        """Sync emails from Gmail.

        Returns:
            Dictionary with sync results
        """
        if not self.service:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        try:
            # Get recent messages
            results = (
                self.service.users()
                .messages()
                .list(userId="me", maxResults=10, q="is:unread")
                .execute()
            )
            messages = results.get("messages", [])

            emails = []
            for msg in messages:
                email_data = self._get_email_details(msg["id"])
                if email_data:
                    emails.append(email_data)

            self.reset_error_count()
            return {
                "success": True,
                "emails": emails,
                "count": len(emails),
            }

        except HttpError as e:
            self.handle_error(e)
            return {"success": False, "error": str(e)}

    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed email information.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with email details
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            headers = message["payload"].get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "")

            # Extract body
            body = self._extract_body(message["payload"])

            return {
                "id": message_id,
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": body,
                "snippet": message.get("snippet", ""),
            }

        except Exception as e:
            print(f"Error getting email details: {e}")
            return None

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload.

        Args:
            payload: Email payload

        Returns:
            Email body text
        """
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data")
                    if data:
                        body += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                elif part["mimeType"] == "text/html":
                    data = part["body"].get("data")
                    if data:
                        html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                        # Simple HTML stripping (could use BeautifulSoup for better extraction)
                        body += html.replace("<br>", "\n").replace("</p>", "\n")
        else:
            if payload["mimeType"] == "text/plain":
                data = payload["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        return body

