"""Notion API integration module for P.A.R.A. Life OS."""

from notion.client import NotionClient
from notion.databases import create_para_databases, ensure_databases_exist
from notion.schemas import (
    MASTER_INBOX_SCHEMA,
    PROJECTS_SCHEMA,
    AREAS_SCHEMA,
    RESOURCES_SCHEMA,
)

__all__ = [
    "NotionClient",
    "create_para_databases",
    "ensure_databases_exist",
    "MASTER_INBOX_SCHEMA",
    "PROJECTS_SCHEMA",
    "AREAS_SCHEMA",
    "RESOURCES_SCHEMA",
]

