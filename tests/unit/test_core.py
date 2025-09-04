"""Unit tests for core components."""

import pytest
from unittest.mock import AsyncMock

from agentic_data_scraper.core.base_agent import BaseAgent, AgentConfig, AgentResult


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent."""
    
    async def _execute(self, input_data):
        """Test implementation that returns processed data."""
        if input_data.get("should_fail"):
            raise ValueError("Test error")
        return {"processed": True, "input": input_data}


class TestBaseAgent:
    """Test cases for BaseAgent base class."""
    
    @pytest.fixture
    def agent_config(self):
        """Test agent configuration."""
        return AgentConfig(name="test_agent")
    
    @pytest.fixture
    def test_agent(self, agent_config):
        """Test agent instance."""
        return TestAgent(agent_config)
    
    def test_agent_initialization(self, agent_config, test_agent):
        """Test agent initialization."""
        assert test_agent.config == agent_config
        assert test_agent.name == "test_agent"
    
    @pytest.mark.asyncio
    async def test_successful_execution(self, test_agent):
        """Test successful agent execution."""
        input_data = {"test": "data"}
        result = await test_agent.execute(input_data)
        
        assert isinstance(result, AgentResult)
        assert result.success is True
        assert result.data["processed"] is True
        assert result.data["input"] == input_data
        assert result.error is None
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_failed_execution(self, test_agent):
        """Test failed agent execution."""
        input_data = {"should_fail": True}
        result = await test_agent.execute(input_data)
        
        assert isinstance(result, AgentResult)
        assert result.success is False
        assert result.data is None
        assert result.error == "Test error"
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_context_manager(self, test_agent):
        """Test agent as async context manager."""
        async with test_agent as agent:
            assert agent is test_agent
            
        # Test that setup and cleanup were called (implicitly)
        # In a real implementation, we'd have setup/cleanup side effects to test
    
    def test_agent_repr(self, test_agent):
        """Test string representation."""
        assert "TestAgent" in repr(test_agent)
        assert "test_agent" in repr(test_agent)