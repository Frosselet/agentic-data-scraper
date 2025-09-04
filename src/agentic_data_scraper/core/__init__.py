"""
Core business logic and interfaces for the Agentic Data Scraper.

This module contains the fundamental abstractions, base classes, and core interfaces
that define the architecture of the system. It provides the foundation for all other modules.

Classes:
    BaseAgent: Base class for all agents
    BaseProcessor: Base class for data processors
    BaseConnector: Base class for external connectors
    EventBus: Event-driven communication system
    Registry: Component registration and discovery
    Context: Execution context management

Functions:
    create_context: Create execution context
    register_component: Register system components
    get_component: Retrieve registered components
    publish_event: Publish events to the event bus

Example:
    ```python
    from agentic_data_scraper.core import (
        BaseAgent, EventBus, create_context
    )
    
    # Create execution context
    context = create_context(
        user_id="user123",
        session_id="session456"
    )
    
    # Initialize event bus
    event_bus = EventBus()
    
    # Create custom agent
    class CustomAgent(BaseAgent):
        async def process(self, data):
            return {"processed": True}
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_agent import BaseAgent
    from .base_processor import BaseProcessor  
    from .base_connector import BaseConnector
    from .event_bus import EventBus
    from .registry import Registry
    from .context import Context

__all__ = [
    "BaseAgent",
    "BaseProcessor",
    "BaseConnector",
    "EventBus",
    "Registry", 
    "Context",
    "create_context",
    "register_component",
    "get_component", 
    "publish_event",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "BaseAgent":
        from .base_agent import BaseAgent
        return BaseAgent
    elif name == "BaseProcessor":
        from .base_processor import BaseProcessor
        return BaseProcessor
    elif name == "BaseConnector":
        from .base_connector import BaseConnector
        return BaseConnector
    elif name == "EventBus":
        from .event_bus import EventBus
        return EventBus
    elif name == "Registry":
        from .registry import Registry
        return Registry
    elif name == "Context":
        from .context import Context
        return Context
    elif name == "create_context":
        from .context import create_context
        return create_context
    elif name == "register_component":
        from .registry import register_component
        return register_component
    elif name == "get_component":
        from .registry import get_component
        return get_component
    elif name == "publish_event":
        from .event_bus import publish_event
        return publish_event
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")