"""Claude AI processor for content categorization."""

import os
import json
from typing import Dict, Any, List, Optional
from anthropic import Anthropic


class ClaudeProcessor:
    """Process content using Claude AI for P.A.R.A. categorization."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022") -> None:
        """Initialize Claude processor.

        Args:
            api_key: Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var.
            model: Claude model to use. Defaults to claude-3-5-sonnet-20241022.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = 4096

    def process_content(
        self,
        content: str,
        source_path: str,
        para_categories: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Process content with Claude AI to categorize into P.A.R.A. system.

        Args:
            content: Content to process
            source_path: Source file path or identifier
            para_categories: Dictionary with 'projects', 'areas', 'resources' lists

        Returns:
            Dictionary with 'title', 'summary', 'tags', 'para_type', 'para_link', 'priority'
        """
        prompt = self._build_prompt(content, source_path, para_categories)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract text from response
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text

            # Parse JSON response
            result = self._parse_response(response_text)
            return result

        except Exception as e:
            return {
                "title": os.path.basename(source_path),
                "summary": f"Error processing with AI: {str(e)}",
                "tags": [],
                "para_type": "Archive",
                "para_link": None,
                "priority": "Low",
            }

    def _build_prompt(
        self, content: str, source_path: str, para_categories: Dict[str, List[str]]
    ) -> str:
        """Build prompt for Claude AI.

        Args:
            content: Content to analyze
            source_path: Source path
            para_categories: Current P.A.R.A. categories

        Returns:
            Formatted prompt string
        """
        projects_list = ", ".join(para_categories.get("projects", [])) or "None"
        areas_list = ", ".join(para_categories.get("areas", [])) or "None"
        resources_list = ", ".join(para_categories.get("resources", [])) or "None"

        prompt = f"""You are an AI assistant helping organize information into the P.A.R.A. methodology system.

P.A.R.A. Categories:
- **Projects**: Goals with defined end dates (e.g., "Launch New Website", "Complete Tax Filing")
- **Areas**: Broad responsibilities to maintain (e.g., "Finances", "Health", "Career")
- **Resources**: Topics of ongoing interest (e.g., "AI Development", "Photography")
- **Archive**: Inactive items from Projects, Areas, or Resources

Current Active Items:
- Projects: {projects_list}
- Areas: {areas_list}
- Resources: {resources_list}

Source: {source_path}

Content:
{content[:20000]}  # Limit content to avoid token limits

Analyze this content and return a JSON object with the following structure:
{{
    "title": "A concise, descriptive title (max 100 chars)",
    "summary": "A 2-3 sentence summary of the content",
    "tags": ["tag1", "tag2", "tag3"],
    "para_type": "Project|Area|Resource|Archive",
    "para_link": "Specific project/area/resource name to link to (or null if none match)",
    "priority": "High|Medium|Low"
}}

Rules:
1. If the content matches an existing Project, Area, or Resource, set para_link to that exact name
2. Choose para_type based on the content's nature:
   - Project: Has a clear goal with an end date/deadline
   - Area: Ongoing responsibility or maintenance task
   - Resource: Reference material or learning resource
   - Archive: Completed or inactive content
3. Generate 3-5 relevant tags
4. Set priority based on urgency and importance

Return ONLY valid JSON, no additional text."""

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response.

        Args:
            response_text: Response text from Claude

        Returns:
            Parsed dictionary
        """
        # Try to extract JSON from response
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text

        try:
            result = json.loads(response_text)
            # Validate required fields
            required_fields = ["title", "summary", "tags", "para_type", "para_link", "priority"]
            for field in required_fields:
                if field not in result:
                    result[field] = None if field == "para_link" else ""
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "title": "Uncategorized",
                "summary": response_text[:500],
                "tags": [],
                "para_type": "Archive",
                "para_link": None,
                "priority": "Low",
            }

