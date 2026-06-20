from typing import Any, Dict, List, Optional
from datetime import datetime
from .base_agent import BaseAgent


class OrganizationAgent(BaseAgent):
    """Agent responsible for tagging, categorizing, and organizing content."""

    def __init__(self):
        super().__init__(
            name="organization",
            description="Tags and categorizes content automatically, creates knowledge graphs, and suggests relationships."
        )
        self.categories = {
            "personal": ["family", "friends", "health", "hobbies", "home"],
            "work": ["meeting", "project", "deadline", "client", "team"],
            "learning": ["course", "tutorial", "research", "study", "book"],
            "ideas": ["brainstorm", "concept", "innovation", "creative"],
            "reference": ["documentation", "guide", "manual", "specification"],
        }
        self.knowledge_graph = {}

    async def initialize(self) -> None:
        """Initialize the organization agent."""
        self.logger.info("Initializing Organization Agent")
        self.is_initialized = True

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and organize content."""
        if not await self.validate_input(input_data):
            return {"error": "Invalid input data"}

        content = input_data.get("content", "")
        metadata = input_data.get("metadata", {})
        action = input_data.get("action", "categorize")

        if action == "categorize":
            result = await self._categorize(content, metadata)
        elif action == "tag":
            result = await self._auto_tag(content, metadata)
        elif action == "connect":
            result = await self._find_connections(input_data.get("items", []))
        elif action == "graph":
            result = await self._build_knowledge_graph(input_data.get("items", []))
        else:
            result = await self._categorize(content, metadata)

        return {
            "action": action,
            "result": result,
            "organized_at": datetime.now().isoformat(),
            "agent": self.name,
        }

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up Organization Agent")
        self.is_initialized = False

    async def _categorize(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize content based on keywords and patterns."""
        content_lower = content.lower()
        scores = {}
        
        for category, keywords in self.categories.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                scores[category] = {
                    "score": score,
                    "matched_keywords": matched_keywords
                }
        
        # Find the best category
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1]["score"])
            return {
                "primary_category": best_category[0],
                "confidence": best_category[1]["score"] / len(self.categories[best_category[0]]),
                "all_scores": scores,
                "suggested_tags": best_category[1]["matched_keywords"]
            }
        else:
            return {
                "primary_category": "uncategorized",
                "confidence": 0,
                "all_scores": {},
                "suggested_tags": []
            }

    async def _auto_tag(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically generate tags for content."""
        tags = []
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#(\w+)', content)
        tags.extend(hashtags)
        
        # Extract based on content analysis
        content_lower = content.lower()
        
        # Common patterns
        patterns = {
            "meeting": ["meeting", "discuss", "conference", "call"],
            "deadline": ["deadline", "due", "submit", "finish"],
            "idea": ["idea", "brainstorm", "concept", "thought"],
            "question": ["question", "ask", "wonder", "curious"],
            "important": ["important", "critical", "urgent", "priority"],
        }
        
        for tag, keywords in patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)
        
        # Add existing metadata tags
        if "tags" in metadata:
            tags.extend(metadata["tags"])
        
        # Remove duplicates
        unique_tags = list(set(tags))
        
        return {
            "tags": unique_tags,
            "tag_count": len(unique_tags),
            "sources": {
                "hashtags": hashtags,
                "pattern_matching": [tag for tag in unique_tags if tag not in hashtags],
                "metadata": metadata.get("tags", [])
            }
        }

    async def _find_connections(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find connections between different pieces of content."""
        connections = []
        
        # Group by tags
        tag_groups = {}
        for item in items:
            tags = item.get("metadata", {}).get("tags", [])
            for tag in tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(item)
        
        # Find items with shared tags
        for tag, group_items in tag_groups.items():
            if len(group_items) > 1:
                connections.append({
                    "type": "shared_tag",
                    "tag": tag,
                    "items": [
                        {
                            "source": item.get("metadata", {}).get("source_type", "unknown"),
                            "preview": item.get("content", "")[:50] + "..."
                        }
                        for item in group_items
                    ]
                })
        
        # Find content similarity (simple word overlap)
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                content1 = set(items[i].get("content", "").lower().split())
                content2 = set(items[j].get("content", "").lower().split())
                common_words = content1.intersection(content2)
                
                if len(common_words) > 3:  # Threshold for similarity
                    connections.append({
                        "type": "content_similarity",
                        "common_words": list(common_words)[:10],
                        "items": [
                            {
                                "source": items[i].get("metadata", {}).get("source_type", "unknown"),
                                "preview": items[i].get("content", "")[:50] + "..."
                            },
                            {
                                "source": items[j].get("metadata", {}).get("source_type", "unknown"),
                                "preview": items[j].get("content", "")[:50] + "..."
                            }
                        ]
                    })
        
        return {
            "connections": connections,
            "total_connections": len(connections)
        }

    async def _build_knowledge_graph(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a simple knowledge graph from items."""
        nodes = []
        edges = []
        
        # Create nodes for each item
        for item in items:
            node_id = item.get("id", str(len(nodes)))
            nodes.append({
                "id": node_id,
                "label": item.get("content", "")[:30] + "...",
                "type": item.get("metadata", {}).get("source_type", "unknown"),
                "tags": item.get("metadata", {}).get("tags", [])
            })
        
        # Create edges based on shared tags
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                tags1 = set(items[i].get("metadata", {}).get("tags", []))
                tags2 = set(items[j].get("metadata", {}).get("tags", []))
                common_tags = tags1.intersection(tags2)
                
                if common_tags:
                    edges.append({
                        "source": items[i].get("id", str(i)),
                        "target": items[j].get("id", str(j)),
                        "relationship": "shared_tags",
                        "tags": list(common_tags)
                    })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }