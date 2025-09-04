"""Base agent class for all BAML agents in the system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from contextlib import AsyncExitStack

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for agents."""
    
    name: str = Field(description="Agent name")
    timeout: int = Field(default=30, description="Timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    enable_logging: bool = Field(default=True, description="Enable agent logging")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentResult(BaseModel):
    """Result from agent execution."""
    
    success: bool = Field(description="Whether the operation succeeded")
    data: Optional[Any] = Field(default=None, description="Result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: float = Field(description="Execution time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")


class BaseAgent(ABC):
    """
    Base class for all agents in the Agentic Data Scraper.
    
    This abstract base class defines the interface that all agents must implement.
    It provides common functionality for configuration, logging, error handling,
    and lifecycle management.
    
    Attributes:
        config: Agent configuration
        name: Agent name from configuration
    
    Example:
        ```python
        class CustomAgent(BaseAgent):
            async def _execute(self, input_data: Any) -> Any:
                # Process input_data
                return {"processed": True}
        
        agent = CustomAgent(AgentConfig(name="custom_agent"))
        result = await agent.execute({"data": "example"})
        ```
    """
    
    def __init__(self, config: AgentConfig) -> None:
        """
        Initialize the agent with configuration.
        
        Args:
            config: Agent configuration object
        """
        self.config = config
        self.name = config.name
        self._exit_stack: Optional[AsyncExitStack] = None
    
    async def __aenter__(self) -> "BaseAgent":
        """Async context manager entry."""
        self._exit_stack = AsyncExitStack()
        await self._exit_stack.__aenter__()
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type: Type, exc_val: Exception, exc_tb: Any) -> None:
        """Async context manager exit."""
        try:
            await self.cleanup()
        finally:
            if self._exit_stack:
                await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)
    
    async def setup(self) -> None:
        """
        Setup method called when entering async context.
        
        Override this method to perform any initialization required
        by the agent, such as establishing connections or loading models.
        """
        pass
    
    async def cleanup(self) -> None:
        """
        Cleanup method called when exiting async context.
        
        Override this method to perform any cleanup required
        by the agent, such as closing connections or releasing resources.
        """
        pass
    
    @abstractmethod
    async def _execute(self, input_data: Any) -> Any:
        """
        Execute the agent's core logic.
        
        This method must be implemented by all subclasses to define
        the agent's specific behavior.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed result data
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _execute method")
    
    async def execute(self, input_data: Any) -> AgentResult:
        """
        Execute the agent with error handling and result wrapping.
        
        This method provides a standardized interface for agent execution,
        including error handling, timing, and result formatting.
        
        Args:
            input_data: Input data to process
            
        Returns:
            AgentResult containing execution results and metadata
        """
        import time
        
        start_time = time.time()
        
        try:
            result_data = await self._execute(input_data)
            execution_time = time.time() - start_time
            
            return AgentResult(
                success=True,
                data=result_data,
                execution_time=execution_time,
                metadata={
                    "agent_name": self.name,
                    "agent_type": self.__class__.__name__,
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return AgentResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={
                    "agent_name": self.name,
                    "agent_type": self.__class__.__name__,
                    "exception_type": type(e).__name__,
                }
            )
    
    def validate_input(self, input_data: Any, schema: Type[BaseModel]) -> BaseModel:
        """
        Validate input data against a Pydantic schema.
        
        Args:
            input_data: Data to validate
            schema: Pydantic model class to validate against
            
        Returns:
            Validated data as Pydantic model instance
            
        Raises:
            ValidationError: If validation fails
        """
        if isinstance(input_data, schema):
            return input_data
        return schema.model_validate(input_data)
    
    def __repr__(self) -> str:
        """Return string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"