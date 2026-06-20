from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base_agent import BaseAgent


class RetrievalAgent(BaseAgent):
    """Agent responsible for finding and ranking relevant information based on queries."""

    def __init__(self):
        super().__init__(
            name="retrieval",
            description="Finds relevant information based on user queries using semantic search and keyword matching."
        )
        self.search_strategies = {
            "keyword": self._keyword_search,
            "semantic": self._semantic_search,
            "combined": self._combined_search,
        }
        self.knowledge_base = []  # In-memory knowledge base for demo

    async def initialize(self) -> None:
        """Initialize the retrieval agent."""
        self.logger.info("Initializing Retrieval Agent")
        self.is_initialized = True

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a search query and return ranked results."""
        if not await self.validate_input(input_data):
            return {"error": "Invalid input data"}

        query = input_data.get("query", "")
        search_strategy = input_data.get("strategy", "combined")
        max_results = input_data.get("max_results", 10)

        if not query:
            return {"error": "Query is required"}

        # Perform search
        results = await self._search(query, search_strategy, max_results)

        return {
            "query": query,
            "strategy": search_strategy,
            "results": results,
            "total_results": len(results),
            "searched_at": datetime.now().isoformat(),
            "agent": self.name,
        }

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up Retrieval Agent")
        self.is_initialized = False

    async def _search(self, query: str, strategy: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform search using the specified strategy."""
        if strategy in self.search_strategies:
            return await self.search_strategies[strategy](query, max_results)
        else:
            self.logger.warning(f"Unknown search strategy: {strategy}, using combined")
            return await self._combined_search(query, max_results)

    async def _keyword_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Simple keyword-based search."""
        results = []
        query_lower = query.lower()
        
        for item in self.knowledge_base:
            content = item.get("content", "").lower()
            if query_lower in content:
                # Calculate relevance score based on keyword frequency
                score = content.count(query_lower)
                results.append({
                    "id": item.get("id"),
                    "content": item.get("content"),
                    "metadata": item.get("metadata", {}),
                    "score": score,
                    "match_type": "keyword"
                })
        
        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    async def _semantic_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Semantic search using embeddings (simplified for demo)."""
        # In a real implementation, this would use sentence-transformers
        # For now, we'll use a simplified approach
        results = []
        
        # Simple semantic similarity based on word overlap
        query_words = set(query.lower().split())
        
        for item in self.knowledge_base:
            content_words = set(item.get("content", "").lower().split())
            overlap = len(query_words.intersection(content_words))
            
            if overlap > 0:
                results.append({
                    "id": item.get("id"),
                    "content": item.get("content"),
                    "metadata": item.get("metadata", {}),
                    "score": overlap,
                    "match_type": "semantic"
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    async def _combined_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Combine keyword and semantic search results."""
        keyword_results = await self._keyword_search(query, max_results)
        semantic_results = await self._semantic_search(query, max_results)
        
        # Merge results, removing duplicates
        seen_ids = set()
        combined = []
        
        for result in keyword_results + semantic_results:
            result_id = result.get("id")
            if result_id not in seen_ids:
                seen_ids.add(result_id)
                combined.append(result)
        
        # Sort by score
        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:max_results]

    async def add_to_knowledge_base(self, item: Dict[str, Any]) -> None:
        """Add an item to the knowledge base."""
        self.knowledge_base.append(item)
        self.logger.info(f"Added item to knowledge base: {item.get('id', 'unknown')}")

    async def remove_from_knowledge_base(self, item_id: str) -> bool:
        """Remove an item from the knowledge base."""
        for i, item in enumerate(self.knowledge_base):
            if item.get("id") == item_id:
                self.knowledge_base.pop(i)
                self.logger.info(f"Removed item from knowledge base: {item_id}")
                return True
        return False

    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return {
            "total_items": len(self.knowledge_base),
            "last_updated": datetime.now().isoformat(),
        }