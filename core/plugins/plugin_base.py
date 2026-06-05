from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class PluginMetadata(BaseModel):
    name: str
    version: str
    description: str
    author: str
    category: str # "analytics", "automation", "integration", "communication", "security", "workflow"

class Plugin(ABC):
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass

    @property
    @abstractmethod
    def required_permissions(self) -> List[str]:
        """e.g., ['filesystem:read', 'network:external_api']"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Keywords defining what this plugin does for routing purposes."""
        pass

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """The main execution hook. Must return a structured dictionary."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Called when the plugin is unloaded or the system shuts down."""
        pass
