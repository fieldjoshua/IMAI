"""Main orchestrator for P.A.R.A. Life OS."""

import os
import time
import signal
import sys
from typing import Dict, Any, List
from config import Config
from notion.client import NotionClient
from notion.databases import ensure_databases_exist
from processors.para_classifier import PARAClassifier
from integrations.file_watcher import FileWatcher
from integrations.gmail import GmailIntegration
from integrations.calendar import CalendarIntegration
from integrations.contacts import ContactsIntegration
from utils.uri_builder import build_obsidian_uri, build_file_uri


class PARAOrchestrator:
    """Main orchestrator for P.A.R.A. Life OS."""

    def __init__(self) -> None:
        """Initialize orchestrator."""
        self.config = Config()
        self.running = False
        self.notion_client: NotionClient = None
        self.classifier: PARAClassifier = None
        self.file_watcher: FileWatcher = None
        self.integrations: List = []

    def initialize(self) -> bool:
        """Initialize all components.

        Returns:
            True if initialization successful
        """
        # Validate configuration
        missing = self.config.validate()
        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            return False

        # Initialize Notion client
        try:
            self.notion_client = NotionClient(self.config.notion_api_key)
            # Ensure databases exist
            ensure_databases_exist(self.notion_client)
        except Exception as e:
            print(f"Error initializing Notion: {e}")
            return False

        # Initialize classifier
        try:
            self.classifier = PARAClassifier(
                self.notion_client, self.config.anthropic_api_key
            )
        except Exception as e:
            print(f"Error initializing classifier: {e}")
            return False

        # Initialize file watcher
        if self.config.enable_file_watcher:
            self.file_watcher = FileWatcher(
                self.config.watch_directories, self._handle_new_file
            )
            self.integrations.append(self.file_watcher)

        # Initialize Google integrations
        if self.config.enable_gmail:
            gmail = GmailIntegration(self.config)
            self.integrations.append(gmail)

        if self.config.enable_calendar:
            calendar = CalendarIntegration(self.config)
            self.integrations.append(calendar)

        if self.config.enable_contacts:
            contacts = ContactsIntegration(self.config)
            self.integrations.append(contacts)

        return True

    def start(self) -> None:
        """Start the orchestrator."""
        if not self.initialize():
            print("Initialization failed. Exiting.")
            sys.exit(1)

        print("Starting P.A.R.A. Life OS...")
        self.running = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start file watcher
        if self.file_watcher:
            result = self.file_watcher.sync()
            if not result.get("success"):
                print(f"File watcher failed to start: {result.get('error')}")

        # Main loop
        try:
            while self.running:
                # Process queued files
                if self.file_watcher:
                    queued_files = self.file_watcher.get_queued_files()
                    for file_path in queued_files:
                        self._process_file(file_path)

                # Sync integrations periodically
                self._sync_integrations()

                # Sleep before next iteration
                time.sleep(10)  # Check every 10 seconds

        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop()

    def _handle_new_file(self, file_path: str) -> None:
        """Handle new file detected by watcher.

        Args:
            file_path: Path to new file
        """
        print(f"New file detected: {file_path}")
        # File will be processed in main loop from queue

    def _process_file(self, file_path: str) -> None:
        """Process a file and add to Notion.

        Args:
            file_path: Path to file
        """
        try:
            # Classify file
            result = self.classifier.classify_file(file_path)

            if not result.get("success"):
                print(f"Error processing {file_path}: {result.get('error')}")
                return

            # Add to Notion
            self._add_to_notion(result, file_path)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    def _add_to_notion(self, classification: Dict[str, Any], source_path: str) -> None:
        """Add classified item to Notion Master Inbox.

        Args:
            classification: Classification result from classifier
            source_path: Source file path
        """
        inbox_id = self.config.notion_inbox_db_id

        # Build properties
        properties = {
            "name": {"title": [{"text": {"content": classification.get("title", "")}}]},
            "status": {"select": {"name": "New"}},
            "type": {"select": {"name": "File"}},
            "source_path": {"url": build_file_uri(source_path)},
            "content": {
                "rich_text": [
                    {"text": {"content": classification.get("content", "")[:2000]}}
                ]
            },
            "summary": {
                "rich_text": [{"text": {"content": classification.get("summary", "")}}]
            },
            "tags": {
                "multi_select": [
                    {"name": tag} for tag in classification.get("tags", [])
                ]
            },
            "para_type": {"select": {"name": classification.get("para_type", "Archive")}},
        }

        # Add relations if para_link exists
        para_link = classification.get("para_link")
        para_type = classification.get("para_type")

        if para_link:
            if para_type == "Project":
                # Find project and add relation
                projects = self.notion_client.query_database(
                    self.config.notion_projects_db_id,
                    filter_dict={"property": "name", "title": {"equals": para_link}},
                )
                if projects:
                    properties["project_relation"] = {
                        "relation": [{"id": projects[0]["id"]}]
                    }
            elif para_type == "Area":
                areas = self.notion_client.query_database(
                    self.config.notion_areas_db_id,
                    filter_dict={"property": "name", "title": {"equals": para_link}},
                )
                if areas:
                    properties["area_relation"] = {"relation": [{"id": areas[0]["id"]}]}
            elif para_type == "Resource":
                resources = self.notion_client.query_database(
                    self.config.notion_resources_db_id,
                    filter_dict={"property": "name", "title": {"equals": para_link}},
                )
                if resources:
                    properties["resource_relation"] = {
                        "relation": [{"id": resources[0]["id"]}]
                    }

        # Create page
        try:
            page = self.notion_client.create_page(inbox_id, properties)
            print(f"Added to Notion: {classification.get('title')}")
        except Exception as e:
            print(f"Error adding to Notion: {e}")

    def _sync_integrations(self) -> None:
        """Sync all enabled integrations."""
        for integration in self.integrations:
            if integration.is_healthy() and hasattr(integration, "sync"):
                try:
                    result = integration.sync()
                    if result.get("success"):
                        # Process results
                        if "emails" in result:
                            self._process_emails(result["emails"])
                        if "events" in result:
                            self._process_events(result["events"])
                        if "contacts" in result:
                            self._process_contacts(result["contacts"])
                except Exception as e:
                    print(f"Error syncing {integration.name}: {e}")

    def _process_emails(self, emails: List[Dict[str, Any]]) -> None:
        """Process emails and add to Notion.

        Args:
            emails: List of email dictionaries
        """
        for email in emails:
            text_content = f"From: {email.get('sender')}\nSubject: {email.get('subject')}\n\n{email.get('body', '')}"
            result = self.classifier.classify_text(
                text_content, email.get("subject", ""), "Email"
            )
            # Add to Notion (similar to _add_to_notion but for emails)

    def _process_events(self, events: List[Dict[str, Any]]) -> None:
        """Process calendar events and add to Notion.

        Args:
            events: List of event dictionaries
        """
        for event in events:
            text_content = f"Title: {event.get('title')}\nDescription: {event.get('description', '')}\nLocation: {event.get('location', '')}"
            result = self.classifier.classify_text(
                text_content, event.get("title", ""), "Calendar"
            )
            # Add to Notion

    def _process_contacts(self, contacts: List[Dict[str, Any]]) -> None:
        """Process contacts and add to Notion.

        Args:
            contacts: List of contact dictionaries
        """
        for contact in contacts:
            text_content = f"Name: {contact.get('name')}\nOrganization: {contact.get('organization', '')}\nNotes: {contact.get('notes', '')}"
            result = self.classifier.classify_text(
                text_content, contact.get("name", ""), "Contact"
            )
            # Add to Notion

    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        print("\nReceived shutdown signal...")
        self.stop()

    def stop(self) -> None:
        """Stop the orchestrator."""
        self.running = False
        if self.file_watcher:
            self.file_watcher.stop()
        print("P.A.R.A. Life OS stopped.")


def main() -> None:
    """Main entry point."""
    orchestrator = PARAOrchestrator()
    orchestrator.start()


if __name__ == "__main__":
    main()

