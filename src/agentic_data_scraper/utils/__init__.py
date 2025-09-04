"""
Utility functions and helpers for the Agentic Data Scraper.

This module provides shared utility functions, decorators, and helper classes
used throughout the application. It includes logging, configuration, async utilities,
and common data processing functions.

Classes:
    Logger: Structured logging with context
    ConfigLoader: Load and validate configuration files
    AsyncUtils: Async/await utility functions
    DataUtils: Common data processing utilities
    FileUtils: File system operations
    NetworkUtils: Network and HTTP utilities

Functions:
    setup_logging: Initialize application logging
    load_config: Load configuration from files
    retry_async: Retry decorator for async functions
    validate_url: Validate URL formats
    sanitize_filename: Create safe filenames
    measure_time: Performance timing decorator

Example:
    ```python
    from agentic_data_scraper.utils import (
        setup_logging, load_config, retry_async
    )
    
    # Setup logging
    logger = setup_logging("agentic_scraper")
    
    # Load configuration
    config = load_config("config.yaml")
    
    # Use retry decorator
    @retry_async(max_attempts=3, delay=1.0)
    async def fetch_data(url: str):
        # Implementation here
        pass
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logger import Logger
    from .config_loader import ConfigLoader
    from .async_utils import AsyncUtils
    from .data_utils import DataUtils
    from .file_utils import FileUtils
    from .network_utils import NetworkUtils

__all__ = [
    "Logger",
    "ConfigLoader",
    "AsyncUtils", 
    "DataUtils",
    "FileUtils",
    "NetworkUtils",
    "setup_logging",
    "load_config",
    "retry_async",
    "validate_url",
    "sanitize_filename",
    "measure_time",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "Logger":
        from .logger import Logger
        return Logger
    elif name == "ConfigLoader":
        from .config_loader import ConfigLoader
        return ConfigLoader
    elif name == "AsyncUtils":
        from .async_utils import AsyncUtils
        return AsyncUtils
    elif name == "DataUtils":
        from .data_utils import DataUtils
        return DataUtils
    elif name == "FileUtils":
        from .file_utils import FileUtils
        return FileUtils
    elif name == "NetworkUtils":
        from .network_utils import NetworkUtils
        return NetworkUtils
    elif name == "setup_logging":
        from .logger import setup_logging
        return setup_logging
    elif name == "load_config":
        from .config_loader import load_config
        return load_config
    elif name == "retry_async":
        from .async_utils import retry_async
        return retry_async
    elif name == "validate_url":
        from .network_utils import validate_url
        return validate_url
    elif name == "sanitize_filename":
        from .file_utils import sanitize_filename
        return sanitize_filename
    elif name == "measure_time":
        from .decorators import measure_time
        return measure_time
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")