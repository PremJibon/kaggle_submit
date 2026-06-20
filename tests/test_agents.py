import asyncio
import sys
import os

# Add the parent directory to the path so we can import the agents
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.synthesis_agent import SynthesisAgent
from agents.organization_agent import OrganizationAgent
from agents.coordinator import AgentCoordinator


async def test_ingestion_agent():
    """Test the ingestion agent."""
    print("Testing Ingestion Agent...")
    agent = IngestionAgent()
    await agent.initialize()
    
    result = await agent.process({
        "content": "This is a test note with #important tag and a date 2024-01-15.",
        "source_type": "manual",
        "format": "text"
    })
    
    print(f"  Content: {result['content']}")
    print(f"  Metadata: {result['metadata']}")
    print(f"  Source: {result['source_type']}")
    
    await agent.cleanup()
    print("[PASS] Ingestion Agent test passed\n")


async def test_retrieval_agent():
    """Test the retrieval agent."""
    print("Testing Retrieval Agent...")
    agent = RetrievalAgent()
    await agent.initialize()
    
    # Add some items to the knowledge base
    await agent.add_to_knowledge_base({
        "id": "test1",
        "content": "Test content about AI agents",
        "metadata": {"tags": ["ai", "agents"]}
    })
    
    await agent.add_to_knowledge_base({
        "id": "test2",
        "content": "Another note about machine learning",
        "metadata": {"tags": ["ml", "learning"]}
    })
    
    # Search
    result = await agent.process({
        "query": "AI agents",
        "strategy": "combined",
        "max_results": 5
    })
    
    print(f"  Query: {result['query']}")
    print(f"  Results: {result['total_results']}")
    print(f"  First result: {result['results'][0]['content'] if result['results'] else 'None'}")
    
    await agent.cleanup()
    print("[PASS] Retrieval Agent test passed\n")


async def test_synthesis_agent():
    """Test the synthesis agent."""
    print("Testing Synthesis Agent...")
    agent = SynthesisAgent()
    await agent.initialize()
    
    items = [
        {
            "content": "First note about AI development",
            "metadata": {"source_type": "manual", "tags": ["ai", "development"]}
        },
        {
            "content": "Second note about machine learning",
            "metadata": {"source_type": "google_keep", "tags": ["ml", "learning"]}
        }
    ]
    
    result = await agent.process({
        "items": items,
        "type": "summary"
    })
    
    print(f"  Synthesis type: {result['synthesis_type']}")
    print(f"  Input count: {result['input_count']}")
    print(f"  Result: {result['result']}")
    
    await agent.cleanup()
    print("[PASS] Synthesis Agent test passed\n")


async def test_organization_agent():
    """Test the organization agent."""
    print("Testing Organization Agent...")
    agent = OrganizationAgent()
    await agent.initialize()
    
    # Test categorization
    result = await agent.process({
        "content": "Meeting notes about project deadline and team coordination",
        "metadata": {},
        "action": "categorize"
    })
    
    print(f"  Action: {result['action']}")
    print(f"  Primary category: {result['result']['primary_category']}")
    print(f"  Suggested tags: {result['result']['suggested_tags']}")
    
    await agent.cleanup()
    print("[PASS] Organization Agent test passed\n")


async def test_coordinator():
    """Test the agent coordinator."""
    print("Testing Agent Coordinator...")
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    # Process an item
    result = await coordinator.process_item({
        "content": "Important meeting notes about the AI project deadline",
        "source_type": "manual"
    })
    
    print(f"  Workflow ID: {result['id']}")
    print(f"  Status: {result['status']}")
    print(f"  Steps: {len(result['steps'])}")
    
    # Search knowledge
    search_result = await coordinator.search_knowledge("meeting")
    print(f"  Search results: {search_result['total_results']}")
    
    await coordinator.cleanup()
    print("[PASS] Agent Coordinator test passed\n")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("AI Personal Knowledge Assistant - Agent Tests")
    print("=" * 50 + "\n")
    
    try:
        await test_ingestion_agent()
        await test_retrieval_agent()
        await test_synthesis_agent()
        await test_organization_agent()
        await test_coordinator()
        
        print("=" * 50)
        print("All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())