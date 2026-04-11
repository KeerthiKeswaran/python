from abc import ABC, abstractmethod
from typing import List, Optional

class PluginBase(ABC):
    """
    Abstract base class for all plugins.
    Any plugin must inherit from this class and implement the required methods.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the plugin."""
        pass

    @property
    def dependencies(self) -> List[str]:
        """List of plugin names this plugin depends on."""
        return []

    @property
    def author(self) -> str:
        """Author of the plugin."""
        return "Unknown"

    @property
    def description(self) -> str:
        """Short description of what the plugin does."""
        return ""

    @abstractmethod
    def activate(self) -> None:
        """Lifecycle hook called when the plugin is activated."""
        pass

    @abstractmethod
    def deactivate(self) -> None:
        """Lifecycle hook called when the plugin is deactivated."""
        pass

    def __repr__(self) -> str:
        return f"{self.name} v{self.version}"
