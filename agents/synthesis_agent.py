from typing import Any, Dict, List, Optional
from datetime import datetime
from .base_agent import BaseAgent


class SynthesisAgent(BaseAgent):
    """Agent responsible for combining information from multiple sources and generating insights."""

    def __init__(self):
        super().__init__(
            name="synthesis",
            description="Combines information from multiple sources, generates summaries, and creates connections."
        )
        self.synthesis_strategies = {
            "summary": self._generate_summary,
            "comparison": self._compare_information,
            "connection": self._find_connections,
        }

    async def initialize(self) -> None:
        """Initialize the synthesis agent."""
        self.logger.info("Initializing Synthesis Agent")
        self.is_initialized = True

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process multiple information items and synthesize them."""
        if not await self.validate_input(input_data):
            return {"error": "Invalid input data"}

        items = input_data.get("items", [])
        synthesis_type = input_data.get("type", "summary")
        context = input_data.get("context", "")

        if not items:
            return {"error": "No items provided for synthesis"}

        # Perform synthesis
        result = await self._synthesize(items, synthesis_type, context)

        return {
            "synthesis_type": synthesis_type,
            "input_count": len(items),
            "result": result,
            "synthesized_at": datetime.now().isoformat(),
            "agent": self.name,
        }

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up Synthesis Agent")
        self.is_initialized = False

    async def _synthesize(self, items: List[Dict[str, Any]], synthesis_type: str, context: str) -> Dict[str, Any]:
        """Perform synthesis using the specified strategy."""
        if synthesis_type in self.synthesis_strategies:
            return await self.synthesis_strategies[synthesis_type](items, context)
        else:
            self.logger.warning(f"Unknown synthesis type: {synthesis_type}, using summary")
            return await self._generate_summary(items, context)

    async def _generate_summary(self, items: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Generate a summary of multiple items."""
        summaries = []
        key_points = []
        
        for item in items:
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            
            # Generate a simple summary (first 100 chars or so)
            summary = content[:100] + "..." if len(content) > 100 else content
            summaries.append({
                "source": metadata.get("source_type", "unknown"),
                "summary": summary,
                "key_date": metadata.get("dates", ["unknown"])[0] if metadata.get("dates") else "unknown"
            })
            
            # Extract key points
            if "tags" in metadata:
                key_points.extend(metadata["tags"])

        return {
            "summaries": summaries,
            "key_points": list(set(key_points)),
            "total_items": len(items),
            "context": context,
        }

    async def _compare_information(self, items: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Compare information from multiple sources."""
        comparisons = []
        
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item1 = items[i]
                item2 = items[j]
                
                # Simple comparison based on content similarity
                content1 = item1.get("content", "").lower()
                content2 = item2.get("content", "").lower()
                
                # Find common words
                words1 = set(content1.split())
                words2 = set(content2.split())
                common_words = words1.intersection(words2)
                
                comparisons.append({
                    "item1_source": item1.get("metadata", {}).get("source_type", "unknown"),
                    "item2_source": item2.get("metadata", {}).get("source_type", "unknown"),
                    "common_words": list(common_words)[:10],  # Limit to 10 words
                    "similarity": len(common_words) / max(len(words1), len(words2), 1),
                })

        return {
            "comparisons": comparisons,
            "total_pairs": len(comparisons),
            "context": context,
        }

    async def _find_connections(self, items: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Find connections between different pieces of information."""
        connections = []
        
        # Group items by tags
        tag_groups = {}
        for item in items:
            tags = item.get("metadata", {}).get("tags", [])
            for tag in tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(item)
        
        # Find items that share tags
        for tag, group_items in tag_groups.items():
            if len(group_items) > 1:
                connections.append({
                    "connection_type": "shared_tag",
                    "tag": tag,
                    "items": [
                        {
                            "source": item.get("metadata", {}).get("source_type", "unknown"),
                            "content_preview": item.get("content", "")[:50] + "..."
                        }
                        for item in group_items
                    ]
                })

        return {
            "connections": connections,
            "total_connections": len(connections),
            "context": context,
        }

    async def generate_insights(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate insights from multiple items."""
        insights = []
        
        # Analyze content patterns
        all_content = " ".join([item.get("content", "") for item in items])
        words = all_content.lower().split()
        
        # Find frequent words (excluding common stop words)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 5 frequent words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_words:
            insights.append({
                "type": "frequent_topics",
                "description": "Most frequently mentioned topics",
                "topics": [{"word": word, "count": count} for word, count in top_words]
            })
        
        # Analyze time patterns
        all_dates = []
        for item in items:
            dates = item.get("metadata", {}).get("dates", [])
            all_dates.extend(dates)
        
        if all_dates:
            insights.append({
                "type": "temporal_patterns",
                "description": "Date references found in the content",
                "dates": list(set(all_dates))
            })

        return insights