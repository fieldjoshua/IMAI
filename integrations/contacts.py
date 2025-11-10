"""Google Contacts integration for contact processing."""

import os
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from integrations.base import BaseIntegration
from config import Config


class ContactsIntegration(BaseIntegration):
    """Google Contacts integration for fetching contacts."""

    SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]

    def __init__(self, config: Config) -> None:
        """Initialize Contacts integration.

        Args:
            config: Config instance
        """
        super().__init__("Contacts")
        self.config = config
        self.service = None
        self.credentials: Optional[Credentials] = None
        self.token_file = ".contacts_token.json"

    def authenticate(self) -> bool:
        """Authenticate with Google Contacts API.

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
            self.service = build("people", "v1", credentials=self.credentials)
            self.reset_error_count()
            return True

        except Exception as e:
            self.handle_error(e)
            return False

    def sync(self) -> Dict[str, Any]:
        """Sync contacts from Google Contacts.

        Returns:
            Dictionary with sync results
        """
        if not self.service:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        try:
            # Get contacts
            results = (
                self.service.people()
                .connections()
                .list(
                    resourceName="people/me",
                    pageSize=100,
                    personFields="names,emailAddresses,phoneNumbers,organizations,biographies",
                )
                .execute()
            )

            connections = results.get("connections", [])

            contacts = []
            for person in connections:
                contact_data = self._format_contact(person)
                if contact_data:
                    contacts.append(contact_data)

            self.reset_error_count()
            return {
                "success": True,
                "contacts": contacts,
                "count": len(contacts),
            }

        except HttpError as e:
            self.handle_error(e)
            return {"success": False, "error": str(e)}

    def _format_contact(self, person: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format contact for processing.

        Args:
            person: Google Contacts person object

        Returns:
            Formatted contact dictionary
        """
        names = person.get("names", [])
        if not names:
            return None

        name = names[0].get("displayName", "")
        emails = [e.get("value", "") for e in person.get("emailAddresses", [])]
        phones = [p.get("value", "") for p in person.get("phoneNumbers", [])]
        orgs = person.get("organizations", [])
        organization = orgs[0].get("name", "") if orgs else ""
        biographies = person.get("biographies", [])
        notes = biographies[0].get("value", "") if biographies else ""

        return {
            "id": person.get("resourceName", ""),
            "name": name,
            "emails": emails,
            "phones": phones,
            "organization": organization,
            "notes": notes,
        }

