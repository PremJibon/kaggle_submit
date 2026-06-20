from typing import Dict, Any

# In-memory knowledge base for demo purposes
knowledge_base: list = []


def add_note(title: str, content: str, tags: str = "") -> Dict[str, Any]:
    """Add a new note to the knowledge base.

    Args:
        title: The title of the note.
        content: The content/body of the note.
        tags: Comma-separated tags for the note (e.g., "meeting,project,important").

    Returns:
        dict: status and result or error msg.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    item = {
        "id": f"note_{len(knowledge_base) + 1}",
        "type": "note",
        "title": title,
        "content": content,
        "tags": tag_list,
        "source": "manual",
    }
    knowledge_base.append(item)

    return {
        "status": "success",
        "report": f"Note '{title}' added successfully with {len(tag_list)} tags.",
        "item": item,
    }


def add_bookmark(url: str, title: str, description: str = "") -> Dict[str, Any]:
    """Add a bookmark to the knowledge base.

    Args:
        url: The URL of the bookmark.
        title: The title of the bookmark.
        description: Optional description of the bookmark.

    Returns:
        dict: status and result or error msg.
    """
    item = {
        "id": f"bookmark_{len(knowledge_base) + 1}",
        "type": "bookmark",
        "url": url,
        "title": title,
        "description": description,
        "tags": ["bookmark"],
        "source": "browser",
    }
    knowledge_base.append(item)

    return {
        "status": "success",
        "report": f"Bookmark '{title}' added successfully.",
        "item": item,
    }