"""Functions for creating and managing Notion P.A.R.A. databases."""

import os
from typing import Dict, Any, Optional
from notion.client import NotionClient
from notion.schemas import (
    MASTER_INBOX_SCHEMA,
    PROJECTS_SCHEMA,
    AREAS_SCHEMA,
    RESOURCES_SCHEMA,
)


def get_parent_page_id() -> str:
    """Get parent page ID from environment or use workspace root.

    Returns:
        Parent page ID string
    """
    parent_id = os.getenv("NOTION_PARENT_PAGE_ID")
    if not parent_id:
        raise ValueError(
            "NOTION_PARENT_PAGE_ID must be set in environment. "
            "Create a page in Notion and use its ID."
        )
    return parent_id


def create_para_databases(client: NotionClient) -> Dict[str, str]:
    """Create all P.A.R.A. databases in Notion.

    Args:
        client: NotionClient instance

    Returns:
        Dictionary mapping database names to their IDs
    """
    parent_id = get_parent_page_id()
    database_ids = {}

    # Create Projects database
    projects_db = client.create_database(parent_id, PROJECTS_SCHEMA)
    database_ids["projects"] = projects_db["id"]
    print(f"Created Projects database: {projects_db['id']}")

    # Create Areas database
    areas_db = client.create_database(parent_id, AREAS_SCHEMA)
    database_ids["areas"] = areas_db["id"]
    print(f"Created Areas database: {areas_db['id']}")

    # Create Resources database
    resources_db = client.create_database(parent_id, RESOURCES_SCHEMA)
    database_ids["resources"] = resources_db["id"]
    print(f"Created Resources database: {resources_db['id']}")

    # Create Master Inbox database
    # Update relations to point to created databases
    inbox_schema = MASTER_INBOX_SCHEMA.copy()
    inbox_schema["properties"]["project_relation"]["relation"] = {
        "database_id": database_ids["projects"]
    }
    inbox_schema["properties"]["area_relation"]["relation"] = {
        "database_id": database_ids["areas"]
    }
    inbox_schema["properties"]["resource_relation"]["relation"] = {
        "database_id": database_ids["resources"]
    }

    inbox_db = client.create_database(parent_id, inbox_schema)
    database_ids["inbox"] = inbox_db["id"]
    print(f"Created Master Inbox database: {inbox_db['id']}")

    return database_ids


def ensure_databases_exist(client: NotionClient) -> Dict[str, str]:
    """Ensure all required databases exist, create if missing.

    Args:
        client: NotionClient instance

    Returns:
        Dictionary mapping database names to their IDs
    """
    database_ids = {}

    # Check if databases exist via environment variables
    inbox_id = os.getenv("NOTION_INBOX_DB_ID")
    projects_id = os.getenv("NOTION_PROJECTS_DB_ID")
    areas_id = os.getenv("NOTION_AREAS_DB_ID")
    resources_id = os.getenv("NOTION_RESOURCES_DB_ID")

    if all([inbox_id, projects_id, areas_id, resources_id]):
        # Verify databases exist
        try:
            client.get_database(inbox_id)
            client.get_database(projects_id)
            client.get_database(areas_id)
            client.get_database(resources_id)
            database_ids = {
                "inbox": inbox_id,
                "projects": projects_id,
                "areas": areas_id,
                "resources": resources_id,
            }
            print("All databases verified and exist")
            return database_ids
        except Exception as e:
            print(f"Error verifying databases: {e}")
            print("Creating new databases...")

    # Create databases if they don't exist
    return create_para_databases(client)


def get_para_categories(client: NotionClient) -> Dict[str, List[str]]:
    """Fetch current Projects, Areas, and Resources from Notion.

    Args:
        client: NotionClient instance

    Returns:
        Dictionary with 'projects', 'areas', 'resources' lists of names
    """
    categories = {"projects": [], "areas": [], "resources": []}

    projects_id = os.getenv("NOTION_PROJECTS_DB_ID")
    areas_id = os.getenv("NOTION_AREAS_DB_ID")
    resources_id = os.getenv("NOTION_RESOURCES_DB_ID")

    if projects_id:
        try:
            projects = client.query_database(
                projects_id,
                filter_dict={"property": "status", "select": {"equals": "Active"}},
            )
            categories["projects"] = [
                _extract_title(p) for p in projects
            ]
        except Exception as e:
            print(f"Error fetching projects: {e}")

    if areas_id:
        try:
            areas = client.query_database(
                areas_id,
                filter_dict={"property": "status", "select": {"equals": "Active"}},
            )
            categories["areas"] = [
                _extract_title(a) for a in areas
            ]
        except Exception as e:
            print(f"Error fetching areas: {e}")

    if resources_id:
        try:
            resources = client.query_database(
                resources_id,
                filter_dict={"property": "status", "select": {"equals": "Active"}},
            )
            categories["resources"] = [
                _extract_title(r) for r in resources
            ]
        except Exception as e:
            print(f"Error fetching resources: {e}")

    return categories


def _extract_title(page: Dict[str, Any]) -> str:
    """Extract title from Notion page object.

    Args:
        page: Notion page object

    Returns:
        Title string
    """
    title_prop = page.get("properties", {}).get("name", {})
    if title_prop.get("title"):
        return "".join(
            [t.get("plain_text", "") for t in title_prop["title"]]
        )
    return ""

