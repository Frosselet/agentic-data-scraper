"""
Pydantic schemas and data validation for the Agentic Data Scraper.

This module provides data models and validation schemas for all components of the system.
It includes models for scraped data, pipeline configurations, agent interactions, and AWS resources.

Classes:
    ScrapedData: Model for scraped web content
    PipelineConfig: Configuration schema for pipelines
    TaskConfig: Configuration schema for individual tasks
    AgentRequest: Request schema for agent interactions
    AgentResponse: Response schema for agent outputs
    AwsResource: Schema for AWS resource descriptions
    ValidationError: Custom validation error class

Functions:
    validate_data: Validate data against a schema
    create_schema: Dynamically create validation schemas
    merge_schemas: Combine multiple schemas

Example:
    ```python
    from agentic_data_scraper.schemas import ScrapedData, PipelineConfig
    
    # Create and validate scraped data
    data = ScrapedData(
        url="https://example.com",
        content="<html>...</html>",
        metadata={"timestamp": "2024-01-01T00:00:00Z"},
        status="success"
    )
    
    # Create pipeline configuration
    config = PipelineConfig(
        name="web_scraping_pipeline",
        tasks=[
            {"name": "scrape", "type": "scraper"},
            {"name": "parse", "type": "parser"}
        ]
    )
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scraped_data import ScrapedData
    from .pipeline_config import PipelineConfig
    from .task_config import TaskConfig
    from .agent_schemas import AgentRequest, AgentResponse
    from .aws_schemas import AwsResource
    from .validation import ValidationError

__all__ = [
    "ScrapedData",
    "PipelineConfig", 
    "TaskConfig",
    "AgentRequest",
    "AgentResponse",
    "AwsResource",
    "ValidationError",
    "validate_data",
    "create_schema",
    "merge_schemas",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "ScrapedData":
        from .scraped_data import ScrapedData
        return ScrapedData
    elif name == "PipelineConfig":
        from .pipeline_config import PipelineConfig
        return PipelineConfig
    elif name == "TaskConfig":
        from .task_config import TaskConfig
        return TaskConfig
    elif name == "AgentRequest":
        from .agent_schemas import AgentRequest
        return AgentRequest
    elif name == "AgentResponse":
        from .agent_schemas import AgentResponse
        return AgentResponse
    elif name == "AwsResource":
        from .aws_schemas import AwsResource
        return AwsResource
    elif name == "ValidationError":
        from .validation import ValidationError
        return ValidationError
    elif name == "validate_data":
        from .validation import validate_data
        return validate_data
    elif name == "create_schema":
        from .factory import create_schema
        return create_schema
    elif name == "merge_schemas":
        from .utils import merge_schemas
        return merge_schemas
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")