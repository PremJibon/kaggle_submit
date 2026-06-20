from typing import Any, Dict, List, Optional
import logging
import asyncio
from datetime import datetime

from .google_keep_connector import GoogleKeepConnector
from .gdrive_connector import GoogleDriveConnector
from .browser_connector import BrowserConnector

logger = logging.getLogger(__name__)


class KnowledgeMCPServer:
    """Main MCP server that coordinates all connectors."""

    def __init__(self, google_keep_api_key: str = None, google_drive_api_key: str = None):
        self.connectors = {
            "google_keep": GoogleKeepConnector(api_key=google_keep_api_key),
            "google_drive": GoogleDriveConnector(api_key=google_drive_api_key),
            "browser": BrowserConnector(),
        }
        self.sync_history = []
        self.is_initialized = False
        self.logger = logging.getLogger(__name__)

    async def initialize(self) -> None:
        """Initialize all connectors."""
        self.logger.info("Initializing Knowledge MCP Server")
        self.is_initialized = True

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up Knowledge MCP Server")
        self.is_initialized = False

    async def fetch_content(self, source_type: str, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Fetch content from a specific source."""
        if source_type not in self.connectors:
            raise ValueError(f"Unknown source type: {source_type}")
        
        connector = self.connectors[source_type]
        
        try:
            if source_type == "google_keep":
                return await connector.fetch_notes(query)
            elif source_type == "google_drive":
                return await connector.fetch_files(query, **kwargs)
            elif source_type == "browser":
                return await connector.fetch_bookmarks()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error fetching from {source_type}: {e}")
            return []

    async def sync_all(self) -> Dict[str, Any]:
        """Sync content from all sources."""
        self.logger.info("Syncing content from all sources")
        
        sync_result = {
            "started_at": datetime.now().isoformat(),
            "sources": {},
            "total_items": 0,
            "errors": []
        }
        
        # Sync from each source
        for source_name, connector in self.connectors.items():
            try:
                if source_name == "google_keep":
                    items = await connector.fetch_notes()
                elif source_name == "google_drive":
                    items = await connector.fetch_files()
                elif source_name == "browser":
                    items = await connector.fetch_bookmarks()
                else:
                    items = []
                
                sync_result["sources"][source_name] = {
                    "item_count": len(items),
                    "items": items
                }
                sync_result["total_items"] += len(items)
                
            except Exception as e:
                sync_result["errors"].append({
                    "source": source_name,
                    "error": str(e)
                })
                self.logger.error(f"Error syncing {source_name}: {e}")
        
        sync_result["completed_at"] = datetime.now().isoformat()
        self.sync_history.append(sync_result)
        
        return sync_result

    async def search_all(self, query: str) -> Dict[str, Any]:
        """Search across all sources."""
        self.logger.info(f"Searching all sources for: {query}")
        
        results = {
            "query": query,
            "sources": {},
            "total_results": 0
        }
        
        for source_name, connector in self.connectors.items():
            try:
                if source_name == "google_keep":
                    items = await connector.search_notes(query)
                elif source_name == "google_drive":
                    items = await connector.search_files(query)
                elif source_name == "browser":
                    items = await connector.search_bookmarks(query)
                else:
                    items = []
                
                results["sources"][source_name] = {
                    "result_count": len(items),
                    "items": items
                }
                results["total_results"] += len(items)
                
            except Exception as e:
                self.logger.error(f"Error searching {source_name}: {e}")
        
        return results

    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sync history."""
        return self.sync_history[-limit:]

    def get_source_status(self) -> Dict[str, Any]:
        """Get status of all sources."""
        return {
            "sources": list(self.connectors.keys()),
            "is_initialized": self.is_initialized,
            "sync_count": len(self.sync_history)
        }