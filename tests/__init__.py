"""
Test suite for the Agentic Data Scraper.

This module contains comprehensive tests for all components of the system,
organized by test type and component.

Directory Structure:
    - unit/: Unit tests for individual components
    - integration/: Integration tests for component interactions  
    - e2e/: End-to-end tests for complete workflows
    - fixtures/: Test fixtures and sample data
    - utils/: Testing utilities and helpers

Test Categories:
    - Agent tests: Test BAML agent implementations
    - Scraper tests: Test web scraping functionality
    - Parser tests: Test data parsing and extraction
    - Pipeline tests: Test pipeline orchestration
    - Security tests: Test security and access controls
    - AWS tests: Test AWS integration (with mocking)

Example:
    Run tests with pytest:
    ```bash
    # Run all tests
    pytest
    
    # Run only unit tests
    pytest tests/unit/
    
    # Run with coverage
    pytest --cov=agentic_data_scraper
    
    # Run specific test category
    pytest -m unit
    pytest -m integration
    pytest -m e2e
    ```
"""

import pytest
from pathlib import Path

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "fixtures" / "data"
TEST_CONFIG_DIR = Path(__file__).parent / "fixtures" / "config"

__all__ = [
    "TEST_DATA_DIR",
    "TEST_CONFIG_DIR",
]