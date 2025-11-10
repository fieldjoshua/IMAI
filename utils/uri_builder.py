"""URI builder for various applications and file systems."""

import os
from pathlib import Path
from typing import Optional
from config import Config


def build_obsidian_uri(file_path: str, vault_path: Optional[str] = None) -> str:
    """Build Obsidian URI for a file.

    Args:
        file_path: Path to file
        vault_path: Optional vault path (reads from config if not provided)

    Returns:
        Obsidian URI string
    """
    config = Config()
    vault = vault_path or config.obsidian_vault_path

    if not vault:
        return build_file_uri(file_path)

    # Get relative path from vault
    try:
        vault_path_obj = Path(vault).resolve()
        file_path_obj = Path(file_path).resolve()
        relative_path = file_path_obj.relative_to(vault_path_obj)
        file_name = relative_path.as_posix()

        return f"obsidian://open?vault={Path(vault).name}&file={file_name}"
    except ValueError:
        # File not in vault, return file URI
        return build_file_uri(file_path)


def build_file_uri(file_path: str) -> str:
    """Build file:// URI for a local file.

    Args:
        file_path: Path to file

    Returns:
        file:// URI string
    """
    abs_path = Path(file_path).resolve()
    return f"file://{abs_path.as_posix()}"


def build_notion_uri(page_id: str) -> str:
    """Build Notion page URL.

    Args:
        page_id: Notion page ID

    Returns:
        Notion URL string
    """
    return f"https://www.notion.so/{page_id.replace('-', '')}"


def build_google_drive_uri(file_id: str) -> str:
    """Build Google Drive file URL.

    Args:
        file_id: Google Drive file ID

    Returns:
        Google Drive URL string
    """
    return f"https://drive.google.com/file/d/{file_id}/view"

