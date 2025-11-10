"""Configuration management for IMAI."""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Centralized configuration management."""

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        # API Keys
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.notion_api_key = os.getenv("NOTION_API_KEY")

        # Notion Database IDs
        self.notion_inbox_db_id = os.getenv("NOTION_INBOX_DB_ID")
        self.notion_projects_db_id = os.getenv("NOTION_PROJECTS_DB_ID")
        self.notion_areas_db_id = os.getenv("NOTION_AREAS_DB_ID")
        self.notion_resources_db_id = os.getenv("NOTION_RESOURCES_DB_ID")
        self.notion_parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")

        # Google OAuth
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/callback")

        # Watch Directories
        watch_dirs_str = os.getenv("WATCH_DIRECTORIES", "[]")
        try:
            if isinstance(watch_dirs_str, str):
                self.watch_directories = json.loads(watch_dirs_str)
            else:
                self.watch_directories = watch_dirs_str
        except json.JSONDecodeError:
            # Fallback to comma-separated list
            self.watch_directories = [
                d.strip() for d in watch_dirs_str.split(",") if d.strip()
            ]

        # Obsidian
        self.obsidian_vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "")

        # Processing Intervals (seconds)
        self.gmail_sync_interval = int(os.getenv("GMAIL_SYNC_INTERVAL", "300"))
        self.calendar_sync_interval = int(os.getenv("CALENDAR_SYNC_INTERVAL", "300"))
        self.contacts_sync_interval = int(os.getenv("CONTACTS_SYNC_INTERVAL", "600"))

        # Token Usage Warning Threshold
        self.token_usage_warning_threshold = int(
            os.getenv("TOKEN_USAGE_WARNING_THRESHOLD", "80")
        )

        # Integration Flags
        self.enable_gmail = os.getenv("ENABLE_GMAIL", "true").lower() == "true"
        self.enable_calendar = os.getenv("ENABLE_CALENDAR", "true").lower() == "true"
        self.enable_contacts = os.getenv("ENABLE_CONTACTS", "true").lower() == "true"
        self.enable_file_watcher = (
            os.getenv("ENABLE_FILE_WATCHER", "true").lower() == "true"
        )

    def validate(self) -> List[str]:
        """Validate configuration and return list of missing required fields.

        Returns:
            List of missing required field names
        """
        missing = []

        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.notion_api_key:
            missing.append("NOTION_API_KEY")

        # Notion databases can be created if missing, but parent page is required
        if not self.notion_parent_page_id and not all(
            [
                self.notion_inbox_db_id,
                self.notion_projects_db_id,
                self.notion_areas_db_id,
                self.notion_resources_db_id,
            ]
        ):
            missing.append("NOTION_PARENT_PAGE_ID or all database IDs")

        if self.enable_gmail and not (self.google_client_id and self.google_client_secret):
            missing.append("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (if Gmail enabled)")

        if self.enable_calendar and not (self.google_client_id and self.google_client_secret):
            missing.append("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (if Calendar enabled)")

        if self.enable_contacts and not (self.google_client_id and self.google_client_secret):
            missing.append("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (if Contacts enabled)")

        return missing

    def get_notion_db_ids(self) -> Dict[str, str]:
        """Get dictionary of Notion database IDs.

        Returns:
            Dictionary mapping database names to IDs
        """
        return {
            "inbox": self.notion_inbox_db_id,
            "projects": self.notion_projects_db_id,
            "areas": self.notion_areas_db_id,
            "resources": self.notion_resources_db_id,
        }

