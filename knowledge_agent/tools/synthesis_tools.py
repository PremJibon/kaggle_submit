from typing import Dict, Any, List
from .ingestion_tools import knowledge_base


def summarize_items(item_ids: str = "") -> Dict[str, Any]:
    """Summarize items from the knowledge base.

    Args:
        item_ids: Comma-separated list of item IDs to summarize. If empty, summarizes all items.

    Returns:
        dict: status and result or error msg.
    """
    if item_ids:
        ids = [i.strip() for i in item_ids.split(",")]
        items = [item for item in knowledge_base if item.get("id") in ids]
    else:
        items = knowledge_base

    if not items:
        return {
            "status": "error",
            "error_message": "No items found to summarize.",
        }

    summaries = []
    all_tags = []
    sources = set()

    for item in items:
        summary_text = item.get("content", item.get("description", ""))
        if len(summary_text) > 100:
            summary_text = summary_text[:100] + "..."

        summaries.append({
            "id": item.get("id"),
            "title": item.get("title", "Untitled"),
            "summary": summary_text,
            "type": item.get("type", "unknown"),
        })

        all_tags.extend(item.get("tags", []))
        sources.add(item.get("source", "unknown"))

    tag_freq = {}
    for tag in all_tags:
        tag_freq[tag] = tag_freq.get(tag, 0) + 1

    return {
        "status": "success",
        "report": f"Summary of {len(items)} items from {len(sources)} sources.",
        "summaries": summaries,
        "common_tags": tag_freq,
        "sources": list(sources),
    }


def find_connections() -> Dict[str, Any]:
    """Find connections between items in the knowledge base based on shared tags.

    Returns:
        dict: status and result or error msg.
    """
    if len(knowledge_base) < 2:
        return {
            "status": "error",
            "error_message": "Need at least 2 items to find connections.",
        }

    connections = []

    for i in range(len(knowledge_base)):
        for j in range(i + 1, len(knowledge_base)):
            tags1 = set(knowledge_base[i].get("tags", []))
            tags2 = set(knowledge_base[j].get("tags", []))
            common = tags1.intersection(tags2)

            if common:
                connections.append({
                    "item1": knowledge_base[i].get("title", "Untitled"),
                    "item2": knowledge_base[j].get("title", "Untitled"),
                    "shared_tags": list(common),
                })

    return {
        "status": "success",
        "report": f"Found {len(connections)} connections between items.",
        "connections": connections,
    }