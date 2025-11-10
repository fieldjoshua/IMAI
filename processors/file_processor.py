"""File content extraction for multiple file formats."""

import os
import json
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
import PyPDF2
from docx import Document
from PIL import Image
import pytesseract


class FileProcessor:
    """Extract text content from various file formats."""

    MAX_CONTENT_LENGTH = 50000  # Truncate to ~50K characters for API efficiency

    def __init__(self) -> None:
        """Initialize file processor."""
        self.supported_extensions = {
            ".pdf": self._extract_pdf,
            ".docx": self._extract_docx,
            ".txt": self._extract_text,
            ".md": self._extract_text,
            ".csv": self._extract_csv,
            ".json": self._extract_json,
            ".xml": self._extract_text,
            ".jpg": self._extract_image,
            ".jpeg": self._extract_image,
            ".png": self._extract_image,
            ".zip": self._extract_zip,
        }

    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """Extract content from a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with 'content', 'file_type', 'file_size', 'error' keys
        """
        path = Path(file_path)
        if not path.exists():
            return {
                "content": "",
                "file_type": "unknown",
                "file_size": 0,
                "error": f"File not found: {file_path}",
            }

        extension = path.suffix.lower()
        file_size = path.stat().st_size

        if extension not in self.supported_extensions:
            return {
                "content": "",
                "file_type": extension[1:] if extension else "unknown",
                "file_size": file_size,
                "error": f"Unsupported file type: {extension}",
            }

        try:
            extractor = self.supported_extensions[extension]
            content = extractor(str(path))
            content = self._truncate_content(content)

            return {
                "content": content,
                "file_type": extension[1:] if extension else "unknown",
                "file_size": file_size,
                "error": None,
            }
        except Exception as e:
            return {
                "content": "",
                "file_type": extension[1:] if extension else "unknown",
                "file_size": file_size,
                "error": f"Error extracting content: {str(e)}",
            }

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        content = []
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                content.append(page.extract_text())
        return "\n".join(content)

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content
        """
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs)

    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text file.

        Args:
            file_path: Path to text file

        Returns:
            File content as string
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _extract_csv(self, file_path: str) -> str:
        """Extract content from CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            CSV content as formatted string
        """
        import csv

        content = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                content.append(",".join(row))
        return "\n".join(content)

    def _extract_json(self, file_path: str) -> str:
        """Extract content from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            JSON content as formatted string
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            return json.dumps(data, indent=2)

    def _extract_image(self, file_path: str) -> str:
        """Extract text from image using OCR.

        Args:
            file_path: Path to image file

        Returns:
            Extracted text from OCR
        """
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"[OCR Error: {str(e)}]"

    def _extract_zip(self, file_path: str) -> str:
        """Extract and process contents of ZIP archive.

        Args:
            file_path: Path to ZIP file

        Returns:
            Combined content from all files in archive
        """
        content_parts = []
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            for file_info in zip_ref.namelist():
                if not file_info.endswith("/"):  # Skip directories
                    try:
                        file_content = zip_ref.read(file_info)
                        # Try to decode as text
                        try:
                            text_content = file_content.decode("utf-8")
                            content_parts.append(f"--- {file_info} ---\n{text_content}")
                        except UnicodeDecodeError:
                            content_parts.append(f"--- {file_info} ---\n[Binary file]")
                    except Exception as e:
                        content_parts.append(f"--- {file_info} ---\n[Error: {str(e)}]")
        return "\n\n".join(content_parts)

    def _truncate_content(self, content: str) -> str:
        """Truncate content to maximum length.

        Args:
            content: Content string

        Returns:
            Truncated content with indicator if truncated
        """
        if len(content) <= self.MAX_CONTENT_LENGTH:
            return content
        truncated = content[: self.MAX_CONTENT_LENGTH]
        return truncated + "\n\n[Content truncated for API efficiency]"

