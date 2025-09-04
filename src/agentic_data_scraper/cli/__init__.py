"""
Command-line interface for the Agentic Data Scraper.

This module provides a comprehensive CLI for managing pipelines, running scrapers,
configuring agents, and monitoring execution. Built with Typer and Rich for
an excellent user experience.

Classes:
    CLI: Main CLI application class
    CommandHandler: Handle individual CLI commands
    ConfigManager: Manage CLI configuration
    OutputFormatter: Format CLI output with Rich

Functions:
    main: Main CLI entry point
    run_pipeline: Run a pipeline from CLI
    list_pipelines: List available pipelines
    validate_config: Validate configuration files

Commands:
    - pipeline: Manage pipelines (list, run, create, delete)
    - scrape: Run scraping operations
    - parse: Parse data files
    - transform: Transform data
    - config: Manage configuration
    - agent: Interact with agents
    - deploy: Deploy to AWS Lambda

Example:
    ```bash
    # Run a pipeline
    agentic-scraper pipeline run web_scraping_pipeline
    
    # List available pipelines  
    agentic-scraper pipeline list
    
    # Scrape a single URL
    agentic-scraper scrape --url https://example.com --output data.json
    
    # Deploy to AWS Lambda
    agentic-scraper deploy --environment production
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main import CLI
    from .commands import CommandHandler
    from .config import ConfigManager
    from .output import OutputFormatter

__all__ = [
    "CLI",
    "CommandHandler",
    "ConfigManager", 
    "OutputFormatter",
    "main",
    "run_pipeline",
    "list_pipelines",
    "validate_config",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "CLI":
        from .main import CLI
        return CLI
    elif name == "CommandHandler":
        from .commands import CommandHandler
        return CommandHandler
    elif name == "ConfigManager":
        from .config import ConfigManager
        return ConfigManager
    elif name == "OutputFormatter":
        from .output import OutputFormatter
        return OutputFormatter
    elif name == "main":
        from .main import main
        return main
    elif name == "run_pipeline":
        from .commands.pipeline import run_pipeline
        return run_pipeline
    elif name == "list_pipelines":
        from .commands.pipeline import list_pipelines
        return list_pipelines
    elif name == "validate_config":
        from .config import validate_config
        return validate_config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")