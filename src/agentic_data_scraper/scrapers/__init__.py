"""
Web scraping modules for the Agentic Data Scraper.

This module provides web scraping capabilities using Playwright, Selenium, and other tools.
It includes both synchronous and asynchronous scraping interfaces, rate limiting,
and error handling for robust data collection.

Classes:
    PlaywrightScraper: High-performance browser automation scraper
    HttpScraper: Fast HTTP-based scraper for simple content
    ScraperPool: Manages multiple scraper instances
    ScraperConfig: Configuration for scraping operations

Functions:
    create_scraper: Factory function for creating scraper instances
    get_default_config: Returns default scraper configuration

Example:
    ```python
    from agentic_data_scraper.scrapers import PlaywrightScraper, ScraperConfig
    
    config = ScraperConfig(
        timeout=30000,
        user_agent="custom-agent",
        headless=True
    )
    
    async with PlaywrightScraper(config) as scraper:
        content = await scraper.scrape("https://example.com")
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .playwright_scraper import PlaywrightScraper
    from .http_scraper import HttpScraper
    from .scraper_pool import ScraperPool
    from .config import ScraperConfig

__all__ = [
    "PlaywrightScraper",
    "HttpScraper", 
    "ScraperPool",
    "ScraperConfig",
    "create_scraper",
    "get_default_config",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "PlaywrightScraper":
        from .playwright_scraper import PlaywrightScraper
        return PlaywrightScraper
    elif name == "HttpScraper":
        from .http_scraper import HttpScraper
        return HttpScraper
    elif name == "ScraperPool":
        from .scraper_pool import ScraperPool
        return ScraperPool
    elif name == "ScraperConfig":
        from .config import ScraperConfig
        return ScraperConfig
    elif name == "create_scraper":
        from .factory import create_scraper
        return create_scraper
    elif name == "get_default_config":
        from .config import get_default_config
        return get_default_config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")