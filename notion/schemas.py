"""Notion database schema definitions for IMAI."""

from typing import Dict, Any

# Master Inbox Database Schema
MASTER_INBOX_SCHEMA: Dict[str, Any] = {
    "name": "Master Inbox",
    "properties": {
        "name": {"title": {}},
        "status": {
            "select": {
                "options": [
                    {"name": "New", "color": "blue"},
                    {"name": "Processing", "color": "yellow"},
                    {"name": "Categorized", "color": "green"},
                    {"name": "Archived", "color": "gray"},
                ]
            }
        },
        "type": {
            "select": {
                "options": [
                    {"name": "File", "color": "blue"},
                    {"name": "Email", "color": "green"},
                    {"name": "Calendar", "color": "orange"},
                    {"name": "Contact", "color": "purple"},
                    {"name": "Other", "color": "gray"},
                ]
            }
        },
        "source_path": {"url": {}},
        "content": {"rich_text": {}},
        "summary": {"rich_text": {}},
        "tags": {"multi_select": {"options": []}},
        "para_type": {
            "select": {
                "options": [
                    {"name": "Project", "color": "red"},
                    {"name": "Area", "color": "blue"},
                    {"name": "Resource", "color": "green"},
                    {"name": "Archive", "color": "gray"},
                ]
            }
        },
        "project_relation": {"relation": {}},
        "area_relation": {"relation": {}},
        "resource_relation": {"relation": {}},
        "created_date": {"created_time": {}},
        "processed_date": {"date": {}},
    },
}

# Projects Database Schema
PROJECTS_SCHEMA: Dict[str, Any] = {
    "name": "Projects",
    "properties": {
        "name": {"title": {}},
        "status": {
            "select": {
                "options": [
                    {"name": "Active", "color": "green"},
                    {"name": "On Hold", "color": "yellow"},
                    {"name": "Completed", "color": "blue"},
                    {"name": "Cancelled", "color": "red"},
                ]
            }
        },
        "start_date": {"date": {}},
        "end_date": {"date": {}},
        "tags": {"multi_select": {"options": []}},
    },
}

# Areas Database Schema
AREAS_SCHEMA: Dict[str, Any] = {
    "name": "Areas",
    "properties": {
        "name": {"title": {}},
        "status": {
            "select": {
                "options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Inactive", "color": "gray"},
                ]
            }
        },
        "tags": {"multi_select": {"options": []}},
        "description": {"rich_text": {}},
    },
}

# Resources Database Schema
RESOURCES_SCHEMA: Dict[str, Any] = {
    "name": "Resources",
    "properties": {
        "name": {"title": {}},
        "status": {
            "select": {
                "options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Inactive", "color": "gray"},
                ]
            }
        },
        "tags": {"multi_select": {"options": []}},
        "description": {"rich_text": {}},
    },
}

