from google.adk.agents import Agent

from .tools.ingestion_tools import add_note, add_bookmark
from .tools.retrieval_tools import search_knowledge
from .tools.synthesis_tools import summarize_items, find_connections
from .tools.organization_tools import categorize_item, tag_item

root_agent = Agent(
    name="knowledge_assistant",
    model="gemini-2.0-flash",
    description="AI Personal Knowledge Assistant that helps organize, retrieve, and synthesize information from multiple sources.",
    instruction="""You are a helpful AI Personal Knowledge Assistant. You help users:

1. ADD information to their knowledge base using add_note, add_bookmark
2. SEARCH their knowledge base using search_knowledge
3. SUMMARIZE and SYNTHESIZE information using summarize_items, find_connections
4. ORGANIZE their content using categorize_item, tag_item

When a user asks to add something, use the appropriate tool.
When a user asks to search, use search_knowledge.
When a user wants a summary, use summarize_items.
Always be helpful and provide clear responses about what you did.""",
    tools=[
        add_note,
        add_bookmark,
        search_knowledge,
        summarize_items,
        find_connections,
        categorize_item,
        tag_item,
    ],
)