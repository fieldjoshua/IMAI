"""Integration modules for external services."""

from integrations.base import BaseIntegration
from integrations.file_watcher import FileWatcher, NewFileHandler
from integrations.gmail import GmailIntegration
from integrations.calendar import CalendarIntegration
from integrations.contacts import ContactsIntegration

__all__ = [
    "BaseIntegration",
    "FileWatcher",
    "NewFileHandler",
    "GmailIntegration",
    "CalendarIntegration",
    "ContactsIntegration",
]

