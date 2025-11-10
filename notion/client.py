"""Notion API client wrapper with error handling and retry logic."""

import os
import time
from typing import Dict, Any, Optional, List
from notion_client import Client
from notion_client.errors import APIResponseError


class NotionClient:
    """Wrapper around Notion API client with error handling and retry logic."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize Notion client.

        Args:
            api_key: Notion API key. If not provided, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        if not self.api_key:
            raise ValueError("NOTION_API_KEY must be provided or set in environment")
        self.client = Client(auth=self.api_key)
        self.max_retries = 3
        self.retry_delay = 1.0

    def _retry_request(self, func, *args, **kwargs) -> Any:
        """Execute request with exponential backoff retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            APIResponseError: If all retries fail
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except APIResponseError as e:
                last_error = e
                if e.code == "rate_limited":
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                elif e.code in ["object_not_found", "validation_error"]:
                    raise
                else:
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
            except Exception as e:
                last_error = e
                wait_time = self.retry_delay * (2 ** attempt)
                time.sleep(wait_time)

        raise last_error or Exception("Unknown error occurred")

    def create_database(
        self, parent_page_id: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new database in Notion.

        Args:
            parent_page_id: ID of parent page
            schema: Database schema definition

        Returns:
            Created database object
        """
        return self._retry_request(
            self.client.databases.create,
            parent_id=parent_page_id,
            title=[{"type": "text", "text": {"content": schema["name"]}}],
            properties=schema["properties"],
        )

    def get_database(self, database_id: str) -> Dict[str, Any]:
        """Retrieve a database by ID.

        Args:
            database_id: Database ID

        Returns:
            Database object
        """
        return self._retry_request(self.client.databases.retrieve, database_id=database_id)

    def query_database(
        self, database_id: str, filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query a database.

        Args:
            database_id: Database ID
            filter_dict: Optional filter criteria

        Returns:
            List of page objects
        """
        results = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self._retry_request(
                self.client.databases.query,
                database_id=database_id,
                filter=filter_dict,
                start_cursor=start_cursor,
            )
            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return results

    def create_page(
        self, database_id: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new page in a database.

        Args:
            database_id: Database ID
            properties: Page properties

        Returns:
            Created page object
        """
        return self._retry_request(
            self.client.pages.create,
            parent={"database_id": database_id},
            properties=properties,
        )

    def update_page(
        self, page_id: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing page.

        Args:
            page_id: Page ID
            properties: Updated properties

        Returns:
            Updated page object
        """
        return self._retry_request(
            self.client.pages.update, page_id=page_id, properties=properties
        )

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Retrieve a page by ID.

        Args:
            page_id: Page ID

        Returns:
            Page object
        """
        return self._retry_request(self.client.pages.retrieve, page_id=page_id)

    def search(
        self, query: Optional[str] = None, filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search Notion workspace.

        Args:
            query: Optional search query string
            filter_dict: Optional filter criteria

        Returns:
            List of matching objects
        """
        results = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self._retry_request(
                self.client.search,
                query=query,
                filter=filter_dict,
                start_cursor=start_cursor,
            )
            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return results

