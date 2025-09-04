"""Pytest configuration and shared fixtures."""

import asyncio
import pytest
from pathlib import Path
from typing import AsyncGenerator, Generator

from agentic_data_scraper.schemas.scraped_data import ScrapedData, ScrapingStatus
from agentic_data_scraper.scrapers.config import ScraperConfig, get_default_config


@pytest.fixture
def sample_scraped_data() -> ScrapedData:
    """Sample scraped data for testing."""
    return ScrapedData(
        url="https://example.com",
        content="<html><body>Test content</body></html>",
        content_type="html",
        status=ScrapingStatus.SUCCESS,
        status_code=200
    )


@pytest.fixture
def default_scraper_config() -> ScraperConfig:
    """Default scraper configuration for testing."""
    return get_default_config("test")


@pytest.fixture
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def test_config_dir() -> Path:
    """Path to test config directory."""
    return Path(__file__).parent / "fixtures" / "config"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[None, None]:
    """Async HTTP client for testing."""
    # Placeholder for when we implement actual HTTP client
    yield None


# Markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "network: mark test as requiring network access")