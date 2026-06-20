from typing import Dict, Any, List
from .ingestion_tools import knowledge_base


def search_knowledge(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search the knowledge base for relevant items.

    Args:
        query: The search query to find relevant items.
        max_results: Maximum number of results to return (default: 10).

    Returns:
        dict: status and result or error msg.
    """
    query_lower = query.lower()
    results: List[Dict[str, Any]] = []

    for item in knowledge_base:
        score = 0
        searchable = " ".join([
            item.get("title", ""),
            item.get("content", ""),
            item.get("description", ""),
            " ".join(item.get("tags", [])),
        ]).lower()

        if query_lower in searchable:
            score = searchable.count(query_lower)
        else:
            query_words = query_lower.split()
            for word in query_words:
                if word in searchable:
                    score += 1

        if score > 0:
            results.append({**item, "relevance_score": score})

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    results = results[:max_results]

    return {
        "status": "success",
        "report": f"Found {len(results)} results for '{query}'.",
        "results": results,
        "total": len(results),
    }