"""
Agent interface definitions for the Agentic Data Scraper multi-agent system.

This module provides the core interfaces and data models for the BAML-based
agent architecture that generates production-ready data pipelines from SOW documents.
"""

from .base import BaseAgent, AgentResult
from .sow_interpreter import SOWInterpreterAgent, DataContract
from .data_fetcher import DataFetcherAgent, DataSource
from .data_parser import DataParserAgent, ParsedData
from .data_transformer import DataTransformerAgent, TransformationStrategy
from .semantic_integrator import SemanticIntegratorAgent, SemanticAnnotation
from .supervisor import SupervisorAgent, GeneratedPipeline
from .security_decision import SecurityDecisionAgent, SecurityDecision

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentResult",
    
    # Specialist agents
    "SOWInterpreterAgent",
    "DataFetcherAgent", 
    "DataParserAgent",
    "DataTransformerAgent",
    "SemanticIntegratorAgent",
    "SupervisorAgent",
    "SecurityDecisionAgent",
    
    # Data models
    "DataContract",
    "DataSource",
    "ParsedData", 
    "TransformationStrategy",
    "SemanticAnnotation",
    "GeneratedPipeline",
    "SecurityDecision",
]