"""P.A.R.A. classifier that combines file processing and AI categorization."""

from typing import Dict, Any, Optional
from processors.file_processor import FileProcessor
from processors.ai_processor import ClaudeProcessor
from notion.client import NotionClient
from notion.databases import get_para_categories


class PARAClassifier:
    """Classify content into P.A.R.A. system using AI."""

    def __init__(
        self,
        notion_client: NotionClient,
        claude_api_key: Optional[str] = None,
    ) -> None:
        """Initialize P.A.R.A. classifier.

        Args:
            notion_client: NotionClient instance
            claude_api_key: Optional Claude API key (reads from env if not provided)
        """
        self.notion_client = notion_client
        self.file_processor = FileProcessor()
        self.ai_processor = ClaudeProcessor(api_key=claude_api_key)

    def classify_file(self, file_path: str) -> Dict[str, Any]:
        """Classify a file into P.A.R.A. system.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with classification results and file metadata
        """
        # Extract file content
        file_data = self.file_processor.extract_content(file_path)

        if file_data.get("error"):
            return {
                "success": False,
                "error": file_data["error"],
                "file_path": file_path,
                "file_type": file_data.get("file_type", "unknown"),
            }

        # Get current P.A.R.A. categories
        para_categories = get_para_categories(self.notion_client)

        # Process with AI
        ai_result = self.ai_processor.process_content(
            content=file_data["content"],
            source_path=file_path,
            para_categories=para_categories,
        )

        return {
            "success": True,
            "file_path": file_path,
            "file_type": file_data["file_type"],
            "file_size": file_data["file_size"],
            "title": ai_result.get("title", ""),
            "summary": ai_result.get("summary", ""),
            "tags": ai_result.get("tags", []),
            "para_type": ai_result.get("para_type", "Archive"),
            "para_link": ai_result.get("para_link"),
            "priority": ai_result.get("priority", "Low"),
            "content": file_data["content"],
        }

    def classify_text(
        self, text: str, source_identifier: str, source_type: str = "Other"
    ) -> Dict[str, Any]:
        """Classify text content (e.g., from email, calendar event).

        Args:
            text: Text content to classify
            source_identifier: Identifier for the source (e.g., email subject, event title)
            source_type: Type of source (Email, Calendar, Contact, Other)

        Returns:
            Dictionary with classification results
        """
        # Get current P.A.R.A. categories
        para_categories = get_para_categories(self.notion_client)

        # Process with AI
        ai_result = self.ai_processor.process_content(
            content=text,
            source_path=source_identifier,
            para_categories=para_categories,
        )

        return {
            "success": True,
            "source_identifier": source_identifier,
            "source_type": source_type,
            "title": ai_result.get("title", ""),
            "summary": ai_result.get("summary", ""),
            "tags": ai_result.get("tags", []),
            "para_type": ai_result.get("para_type", "Archive"),
            "para_link": ai_result.get("para_link"),
            "priority": ai_result.get("priority", "Low"),
            "content": text,
        }

