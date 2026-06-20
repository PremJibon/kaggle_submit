from typing import Dict, Any
from .ingestion_tools import knowledge_base


def categorize_item(item_id: str) -> Dict[str, Any]:
    """Automatically categorize an item based on its content.

    Args:
        item_id: The ID of the item to categorize.

    Returns:
        dict: status and result or error msg.
    """
    item = next((i for i in knowledge_base if i.get("id") == item_id), None)

    if not item:
        return {
            "status": "error",
            "error_message": f"Item with ID '{item_id}' not found.",
        }

    content = " ".join([
        item.get("title", ""),
        item.get("content", ""),
        item.get("description", ""),
    ]).lower()

    categories = {
        "work": ["meeting", "project", "deadline", "client", "team", "task", "report"],
        "learning": ["course", "tutorial", "research", "study", "book", "article", "learn"],
        "personal": ["family", "friends", "health", "hobby", "home", "travel"],
        "ideas": ["idea", "brainstorm", "concept", "innovation", "creative", "inspire"],
        "reference": ["documentation", "guide", "manual", "spec", "reference", "howto"],
    }

    scores = {}
    for category, keywords in categories.items():
        score = sum(1 for kw in keywords if kw in content)
        if score > 0:
            scores[category] = score

    if scores:
        best_category = max(scores, key=scores.get)
    else:
        best_category = "uncategorized"

    item["category"] = best_category

    return {
        "status": "success",
        "report": f"Item '{item.get('title', 'Untitled')}' categorized as '{best_category}'.",
        "category": best_category,
        "all_scores": scores,
    }


def tag_item(item_id: str, new_tags: str) -> Dict[str, Any]:
    """Add new tags to an existing item.

    Args:
        item_id: The ID of the item to tag.
        new_tags: Comma-separated tags to add.

    Returns:
        dict: status and result or error msg.
    """
    item = next((i for i in knowledge_base if i.get("id") == item_id), None)

    if not item:
        return {
            "status": "error",
            "error_message": f"Item with ID '{item_id}' not found.",
        }

    tags_to_add = [t.strip() for t in new_tags.split(",") if t.strip()]
    existing_tags = set(item.get("tags", []))
    added = [t for t in tags_to_add if t not in existing_tags]

    item["tags"] = list(existing_tags.union(set(tags_to_add)))

    return {
        "status": "success",
        "report": f"Added {len(added)} new tags to '{item.get('title', 'Untitled')}'.",
        "tags": item["tags"],
        "added": added,
    }