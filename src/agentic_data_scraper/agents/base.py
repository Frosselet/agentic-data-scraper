"""
Base agent interface and common data structures for the multi-agent system.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
import asyncio
import logging

T = TypeVar('T')

class AgentResult(BaseModel, Generic[T]):
    """Standard result wrapper for all agent operations."""
    
    success: bool = Field(description="Whether the agent operation succeeded")
    result: Optional[T] = Field(default=None, description="The agent's output result")
    error: Optional[str] = Field(default=None, description="Error message if operation failed")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings from the operation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the operation")
    execution_time_ms: Optional[float] = Field(default=None, description="Time taken for the operation in milliseconds")
    agent_id: str = Field(description="Identifier of the agent that produced this result")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this result was created")

    class Config:
        arbitrary_types_allowed = True

class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents in the system.
    
    Provides common functionality for logging, error handling, and result formatting.
    All specialist agents inherit from this base class.
    """
    
    def __init__(
        self,
        agent_id: str,
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 300
    ):
        self.agent_id = agent_id
        self.logger = logger or logging.getLogger(f"agent.{agent_id}")
        self.timeout_seconds = timeout_seconds
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize agent-specific resources. Override in subclasses."""
        self.logger.info(f"Initializing agent: {self.agent_id}")
    
    async def execute(self, *args, **kwargs) -> AgentResult:
        """
        Execute the agent's main functionality with timeout and error handling.
        
        Args:
            *args: Positional arguments for the agent's process method
            **kwargs: Keyword arguments for the agent's process method
            
        Returns:
            AgentResult: Standardized result with success/failure status and output
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting execution for agent: {self.agent_id}")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self._process(*args, **kwargs),
                timeout=self.timeout_seconds
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(f"Agent {self.agent_id} completed successfully in {execution_time:.2f}ms")
            
            return AgentResult(
                success=True,
                result=result,
                execution_time_ms=execution_time,
                agent_id=self.agent_id,
                timestamp=datetime.now()
            )
            
        except asyncio.TimeoutError:
            error_msg = f"Agent {self.agent_id} timed out after {self.timeout_seconds} seconds"
            self.logger.error(error_msg)
            return AgentResult(
                success=False,
                error=error_msg,
                agent_id=self.agent_id,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Agent {self.agent_id} failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return AgentResult(
                success=False,
                error=error_msg,
                agent_id=self.agent_id,
                timestamp=datetime.now()
            )
    
    @abstractmethod
    async def _process(self, *args, **kwargs) -> Any:
        """
        Agent-specific processing logic. Must be implemented by subclasses.
        
        Args:
            *args: Positional arguments specific to the agent
            **kwargs: Keyword arguments specific to the agent
            
        Returns:
            Any: Agent-specific result object
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _process method")
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters. Override in subclasses for specific validation.
        
        Args:
            **kwargs: Input parameters to validate
            
        Returns:
            bool: True if inputs are valid, False otherwise
        """
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return a description of this agent's capabilities.
        
        Returns:
            Dict[str, Any]: Capability description including supported operations and formats
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            "timeout_seconds": self.timeout_seconds,
            "supported_operations": [],
            "input_formats": [],
            "output_formats": []
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Return current health status of the agent.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        return {
            "agent_id": self.agent_id,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "last_execution": None,
            "error_count": 0
        }

class AgentCoordinator:
    """
    Coordinates execution of multiple agents in workflows.
    
    Provides orchestration capabilities for complex multi-agent operations
    with dependency management and error recovery.
    """
    
    def __init__(self, agents: List[BaseAgent], logger: Optional[logging.Logger] = None):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.logger = logger or logging.getLogger("agent.coordinator")
        self.execution_history: List[AgentResult] = []
    
    async def execute_sequential(
        self,
        workflow: List[Dict[str, Any]],
        stop_on_failure: bool = True
    ) -> List[AgentResult]:
        """
        Execute agents in sequential order.
        
        Args:
            workflow: List of workflow steps with agent_id and parameters
            stop_on_failure: Whether to stop the workflow on first failure
            
        Returns:
            List[AgentResult]: Results from each agent execution
        """
        results = []
        
        for step in workflow:
            agent_id = step.get("agent_id")
            params = step.get("parameters", {})
            
            if agent_id not in self.agents:
                error_result = AgentResult(
                    success=False,
                    error=f"Agent {agent_id} not found in coordinator",
                    agent_id=agent_id or "unknown"
                )
                results.append(error_result)
                
                if stop_on_failure:
                    break
                continue
            
            agent = self.agents[agent_id]
            result = await agent.execute(**params)
            results.append(result)
            self.execution_history.append(result)
            
            if not result.success and stop_on_failure:
                self.logger.error(f"Stopping workflow due to failure in agent {agent_id}")
                break
        
        return results
    
    async def execute_parallel(
        self,
        workflow: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[AgentResult]:
        """
        Execute agents in parallel with concurrency limit.
        
        Args:
            workflow: List of workflow steps with agent_id and parameters
            max_concurrent: Maximum number of concurrent agent executions
            
        Returns:
            List[AgentResult]: Results from each agent execution
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(step: Dict[str, Any]) -> AgentResult:
            async with semaphore:
                agent_id = step.get("agent_id")
                params = step.get("parameters", {})
                
                if agent_id not in self.agents:
                    return AgentResult(
                        success=False,
                        error=f"Agent {agent_id} not found in coordinator",
                        agent_id=agent_id or "unknown"
                    )
                
                agent = self.agents[agent_id]
                result = await agent.execute(**params)
                self.execution_history.append(result)
                return result
        
        tasks = [execute_with_semaphore(step) for step in workflow]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to AgentResult objects
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = AgentResult(
                    success=False,
                    error=f"Parallel execution failed: {str(result)}",
                    agent_id=workflow[i].get("agent_id", "unknown")
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of all agent executions.
        
        Returns:
            Dict[str, Any]: Summary statistics and status information
        """
        if not self.execution_history:
            return {"total_executions": 0, "success_rate": 0.0, "agents": {}}
        
        total = len(self.execution_history)
        successful = sum(1 for result in self.execution_history if result.success)
        
        agent_stats = {}
        for result in self.execution_history:
            agent_id = result.agent_id
            if agent_id not in agent_stats:
                agent_stats[agent_id] = {"total": 0, "successful": 0, "avg_time_ms": 0.0}
            
            agent_stats[agent_id]["total"] += 1
            if result.success:
                agent_stats[agent_id]["successful"] += 1
            
            if result.execution_time_ms:
                current_avg = agent_stats[agent_id]["avg_time_ms"]
                current_count = agent_stats[agent_id]["total"]
                new_avg = (current_avg * (current_count - 1) + result.execution_time_ms) / current_count
                agent_stats[agent_id]["avg_time_ms"] = new_avg
        
        return {
            "total_executions": total,
            "successful_executions": successful,
            "success_rate": successful / total,
            "agents": agent_stats,
            "last_execution": self.execution_history[-1].timestamp.isoformat() if self.execution_history else None
        }