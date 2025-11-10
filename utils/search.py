"""Universal search utility for Notion Master Inbox."""

import os
from typing import List, Dict, Any, Optional
from notion.client import NotionClient
from config import Config


def search_notion_inbox(
    query: Optional[str] = None,
    tags: Optional[List[str]] = None,
    para_type: Optional[str] = None,
    item_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search Master Inbox database in Notion.

    Args:
        query: Search query string
        tags: Filter by tags
        para_type: Filter by P.A.R.A. type (Project, Area, Resource, Archive)
        item_type: Filter by item type (File, Email, Calendar, Contact, Other)

    Returns:
        List of matching page objects
    """
    config = Config()
    client = NotionClient(config.notion_api_key)

    inbox_id = config.notion_inbox_db_id
    if not inbox_id:
        raise ValueError("NOTION_INBOX_DB_ID must be set")

    # Build filter
    filters = []

    if para_type:
        filters.append({"property": "para_type", "select": {"equals": para_type}})

    if item_type:
        filters.append({"property": "type", "select": {"equals": item_type}})

    if tags:
        for tag in tags:
            filters.append({"property": "tags", "multi_select": {"contains": tag}})

    filter_dict = None
    if len(filters) == 1:
        filter_dict = filters[0]
    elif len(filters) > 1:
        filter_dict = {"and": filters}

    # Query database
    results = client.query_database(inbox_id, filter_dict=filter_dict)

    # Filter by query string if provided
    if query:
        query_lower = query.lower()
        filtered_results = []
        for page in results:
            # Search in title, summary, and content
            title = _extract_text_property(page, "name")
            summary = _extract_text_property(page, "summary")
            content = _extract_text_property(page, "content")

            if (
                query_lower in title.lower()
                or query_lower in summary.lower()
                or query_lower in content.lower()
            ):
                filtered_results.append(page)
        results = filtered_results

    return results


def _extract_text_property(page: Dict[str, Any], property_name: str) -> str:
    """Extract text from Notion page property.

    Args:
        page: Notion page object
        property_name: Property name

    Returns:
        Extracted text
    """
    prop = page.get("properties", {}).get(property_name, {})
    if prop.get("title"):
        return "".join([t.get("plain_text", "") for t in prop["title"]])
    elif prop.get("rich_text"):
        return "".join([t.get("plain_text", "") for t in prop["rich_text"]])
    return ""


def format_search_result(page: Dict[str, Any]) -> str:
    """Format search result for display.

    Args:
        page: Notion page object

    Returns:
        Formatted string
    """
    title = _extract_text_property(page, "name")
    summary = _extract_text_property(page, "summary")
    page_id = page.get("id", "")
    notion_url = f"https://www.notion.so/{page_id.replace('-', '')}"

    return f"{title}\n{summary}\n{notion_url}"

