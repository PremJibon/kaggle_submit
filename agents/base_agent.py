from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the knowledge assistant system."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self.is_initialized = False
        self.created_at = datetime.now()

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with necessary resources."""
        pass

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources when the agent is shut down."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "name": self.name,
            "description": self.description,
            "is_initialized": self.is_initialized,
            "created_at": self.created_at.isoformat(),
        }

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data before processing."""
        if not isinstance(input_data, dict):
            self.logger.error("Input data must be a dictionary")
            return False
        return True