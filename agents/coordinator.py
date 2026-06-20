from typing import Any, Dict, List, Optional
import asyncio
import logging
from datetime import datetime

from .ingestion_agent import IngestionAgent
from .retrieval_agent import RetrievalAgent
from .synthesis_agent import SynthesisAgent
from .organization_agent import OrganizationAgent

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordinates multiple agents to work together on knowledge management tasks."""

    def __init__(self):
        self.agents = {
            "ingestion": IngestionAgent(),
            "retrieval": RetrievalAgent(),
            "synthesis": SynthesisAgent(),
            "organization": OrganizationAgent(),
        }
        self.workflow_history = []
        self.is_initialized = False
        self.logger = logging.getLogger(__name__)

    async def initialize(self) -> None:
        """Initialize all agents."""
        self.logger.info("Initializing Agent Coordinator")
        
        for name, agent in self.agents.items():
            try:
                await agent.initialize()
                self.logger.info(f"Initialized agent: {name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {name}: {e}")
                raise
        
        self.is_initialized = True
        self.logger.info("All agents initialized successfully")

    async def cleanup(self) -> None:
        """Clean up all agents."""
        self.logger.info("Cleaning up Agent Coordinator")
        
        for name, agent in self.agents.items():
            try:
                await agent.cleanup()
                self.logger.info(f"Cleaned up agent: {name}")
            except Exception as e:
                self.logger.error(f"Failed to clean up agent {name}: {e}")
        
        self.is_initialized = False

    async def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single item through the agent pipeline."""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow = {
            "id": workflow_id,
            "item": item,
            "steps": [],
            "started_at": datetime.now().isoformat(),
        }
        
        try:
            # Step 1: Ingest the item
            ingestion_result = await self.agents["ingestion"].process(item)
            workflow["steps"].append({
                "agent": "ingestion",
                "result": ingestion_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 2: Organize and categorize
            organization_result = await self.agents["organization"].process({
                "content": ingestion_result.get("content", ""),
                "metadata": ingestion_result.get("metadata", {}),
                "action": "categorize"
            })
            workflow["steps"].append({
                "agent": "organization",
                "result": organization_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 3: Add tags
            tagging_result = await self.agents["organization"].process({
                "content": ingestion_result.get("content", ""),
                "metadata": ingestion_result.get("metadata", {}),
                "action": "tag"
            })
            workflow["steps"].append({
                "agent": "organization_tag",
                "result": tagging_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 4: Add to knowledge base for retrieval
            knowledge_item = {
                "id": f"item_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "content": ingestion_result.get("content", ""),
                "metadata": {
                    **ingestion_result.get("metadata", {}),
                    "category": organization_result.get("result", {}).get("primary_category", "unknown"),
                    "tags": tagging_result.get("result", {}).get("tags", [])
                }
            }
            
            await self.agents["retrieval"].add_to_knowledge_base(knowledge_item)
            
            workflow["completed_at"] = datetime.now().isoformat()
            workflow["status"] = "success"
            workflow["knowledge_item"] = knowledge_item
            
        except Exception as e:
            workflow["error"] = str(e)
            workflow["status"] = "failed"
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
        
        self.workflow_history.append(workflow)
        return workflow

    async def search_knowledge(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search the knowledge base."""
        return await self.agents["retrieval"].process({
            "query": query,
            "strategy": "combined",
            "max_results": max_results
        })

    async def synthesize_information(self, items: List[Dict[str, Any]], synthesis_type: str = "summary") -> Dict[str, Any]:
        """Synthesize information from multiple items."""
        return await self.agents["synthesis"].process({
            "items": items,
            "type": synthesis_type
        })

    async def find_connections(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find connections between items."""
        return await self.agents["organization"].process({
            "items": items,
            "action": "connect"
        })

    async def build_knowledge_graph(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a knowledge graph from items."""
        return await self.agents["organization"].process({
            "items": items,
            "action": "graph"
        })

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        return {
            "coordinator": {
                "is_initialized": self.is_initialized,
                "workflow_count": len(self.workflow_history),
            },
            "agents": {
                name: agent.get_status()
                for name, agent in self.agents.items()
            }
        }

    def get_workflow_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow history."""
        return self.workflow_history[-limit:]