"""
Pipeline orchestration modules for the Agentic Data Scraper.

This module provides pipeline orchestration capabilities including workflow management,
task scheduling, error handling, and monitoring. It supports both batch and streaming pipelines.

Classes:
    Pipeline: Main pipeline orchestration class
    Task: Individual pipeline task representation
    TaskScheduler: Schedule and manage pipeline tasks
    WorkflowManager: Manage complex multi-stage workflows
    PipelineMonitor: Monitor pipeline execution and performance
    ExecutionContext: Execution context for pipeline runs

Functions:
    create_pipeline: Factory function for creating pipelines
    run_pipeline: Execute a pipeline with monitoring
    schedule_pipeline: Schedule pipeline for future execution

Example:
    ```python
    from agentic_data_scraper.pipelines import Pipeline, Task
    from agentic_data_scraper.scrapers import PlaywrightScraper
    from agentic_data_scraper.parsers import HtmlParser
    
    # Create pipeline with tasks
    pipeline = Pipeline(name="web_data_pipeline")
    
    # Add scraping task
    scrape_task = Task(
        name="scrape_data",
        handler=PlaywrightScraper(),
        inputs={"url": "https://example.com"}
    )
    
    # Add parsing task
    parse_task = Task(
        name="parse_data", 
        handler=HtmlParser(),
        depends_on=[scrape_task]
    )
    
    pipeline.add_tasks([scrape_task, parse_task])
    
    # Execute pipeline
    result = pipeline.run()
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import Pipeline
    from .task import Task
    from .scheduler import TaskScheduler
    from .workflow import WorkflowManager
    from .monitor import PipelineMonitor
    from .context import ExecutionContext

__all__ = [
    "Pipeline",
    "Task",
    "TaskScheduler",
    "WorkflowManager",
    "PipelineMonitor", 
    "ExecutionContext",
    "create_pipeline",
    "run_pipeline",
    "schedule_pipeline",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "Pipeline":
        from .pipeline import Pipeline
        return Pipeline
    elif name == "Task":
        from .task import Task
        return Task
    elif name == "TaskScheduler":
        from .scheduler import TaskScheduler
        return TaskScheduler
    elif name == "WorkflowManager":
        from .workflow import WorkflowManager
        return WorkflowManager
    elif name == "PipelineMonitor":
        from .monitor import PipelineMonitor
        return PipelineMonitor
    elif name == "ExecutionContext":
        from .context import ExecutionContext
        return ExecutionContext
    elif name == "create_pipeline":
        from .factory import create_pipeline
        return create_pipeline
    elif name == "run_pipeline":
        from .runner import run_pipeline
        return run_pipeline
    elif name == "schedule_pipeline":
        from .scheduler import schedule_pipeline
        return schedule_pipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")