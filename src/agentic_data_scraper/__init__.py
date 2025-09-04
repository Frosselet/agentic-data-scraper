"""
Agentic Data Scraper: A multi-agentic Python solution for building standardized data pipelines.

This package provides a comprehensive framework for building data pipelines that generate
AWS Lambda code using BAML agents, web scraping capabilities, and semantic web technologies.

Key Components:
    - agents: BAML agent implementations for coordination and data processing
    - scrapers: Web scraping modules using Playwright and other tools
    - parsers: Data parsing and extraction modules
    - transformers: Data transformation and enrichment modules
    - pipelines: Pipeline orchestration and workflow management
    - schemas: Pydantic data models and validation schemas
    - security: Security controls and Human-in-the-Loop (HITL) modules
    - cli: Command-line interface for pipeline management
    - utils: Shared utility functions and helpers
    - core: Core business logic and interfaces
    - semantic: RDFLib and OWL processing for semantic data
    - aws: AWS integration for Lambda, S3, and Iceberg tables

Example:
    Basic usage of the agentic data scraper:

    ```python
    from agentic_data_scraper import Pipeline
    from agentic_data_scraper.agents import SupervisorAgent
    
    # Create and configure a pipeline
    pipeline = Pipeline(name="web_scraping_pipeline")
    supervisor = SupervisorAgent()
    
    # Run the pipeline
    result = pipeline.run()
    ```
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agentic-data-scraper")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "0.1.0-dev"

__author__ = "Development Team"
__email__ = "dev@example.com"
__license__ = "MIT"
__description__ = "A multi-agentic Python solution for building standardized data pipelines"

# Core exports - only export what's needed at the top level
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]

# Lazy imports to avoid circular dependencies and improve startup time
# Users should import from specific modules for better performance