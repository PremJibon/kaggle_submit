from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base_agent import BaseAgent


class IngestionAgent(BaseAgent):
    """Agent responsible for processing and ingesting information from various sources."""

    def __init__(self):
        super().__init__(
            name="ingestion",
            description="Processes incoming information from various sources, extracts metadata, and normalizes content."
        )
        self.supported_formats = ["text", "markdown", "html", "json"]
        self.metadata_extractors = {
            "dates": self._extract_dates,
            "tags": self._extract_tags,
            "sources": self._extract_sources,
        }

    async def initialize(self) -> None:
        """Initialize the ingestion agent."""
        self.logger.info("Initializing Ingestion Agent")
        self.is_initialized = True

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming information and extract metadata."""
        if not await self.validate_input(input_data):
            return {"error": "Invalid input data"}

        content = input_data.get("content", "")
        source_type = input_data.get("source_type", "unknown")
        source_url = input_data.get("source_url", "")

        # Extract metadata
        metadata = await self._extract_metadata(content, source_type, source_url)

        # Normalize content
        normalized_content = await self._normalize_content(content, input_data.get("format", "text"))

        return {
            "content": normalized_content,
            "metadata": metadata,
            "source_type": source_type,
            "source_url": source_url,
            "ingested_at": datetime.now().isoformat(),
            "agent": self.name,
        }

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up Ingestion Agent")
        self.is_initialized = False

    async def _extract_metadata(self, content: str, source_type: str, source_url: str) -> Dict[str, Any]:
        """Extract metadata from content."""
        metadata = {
            "source_type": source_type,
            "source_url": source_url,
            "content_length": len(content),
            "extracted_at": datetime.now().isoformat(),
        }

        # Extract dates
        dates = self._extract_dates(content)
        if dates:
            metadata["dates"] = dates

        # Extract potential tags
        tags = self._extract_tags(content)
        if tags:
            metadata["tags"] = tags

        return metadata

    async def _normalize_content(self, content: str, format_type: str) -> str:
        """Normalize content to a standard format."""
        if format_type == "html":
            # Simple HTML to text conversion
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
        elif format_type == "markdown":
            # Keep markdown as-is for now
            pass
        elif format_type == "json":
            # Try to extract text from JSON
            try:
                import json
                data = json.loads(content)
                if isinstance(data, dict) and "text" in data:
                    content = data["text"]
            except json.JSONDecodeError:
                pass

        return content.strip()

    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)

        return list(set(dates))

    def _extract_tags(self, content: str) -> List[str]:
        """Extract potential tags from content."""
        # Simple tag extraction - look for #hashtags or common keywords
        hashtags = re.findall(r'#(\w+)', content)
        
        # Common keywords that might be tags
        common_tags = [
            "important", "todo", "meeting", "project", "idea",
            "question", "research", "reference", "note", "reminder"
        ]
        
        tags = []
        for tag in common_tags:
            if tag.lower() in content.lower():
                tags.append(tag)
        
        return list(set(hashtags + tags))

    def _extract_sources(self, content: str) -> List[str]:
        """Extract source references from content."""
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, content)
        return urls