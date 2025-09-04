"""Unit tests for Pydantic schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from agentic_data_scraper.schemas.scraped_data import (
    ScrapedData, 
    ScrapingStatus, 
    ContentType,
    HttpMethod
)


class TestScrapedData:
    """Test cases for ScrapedData schema."""
    
    def test_valid_scraped_data_creation(self):
        """Test creating valid ScrapedData."""
        data = ScrapedData(
            url="https://example.com",
            content="<html>test</html>",
            content_type=ContentType.HTML,
            status=ScrapingStatus.SUCCESS,
            status_code=200
        )
        
        assert data.url == "https://example.com"
        assert data.content == "<html>test</html>"
        assert data.content_type == ContentType.HTML
        assert data.status == ScrapingStatus.SUCCESS
        assert data.status_code == 200
        assert data.method == HttpMethod.GET  # default
        assert isinstance(data.timestamp, datetime)
    
    def test_invalid_url_validation(self):
        """Test URL validation."""
        with pytest.raises(ValidationError):
            ScrapedData(
                url="invalid-url",
                content="test",
                content_type=ContentType.HTML,
                status=ScrapingStatus.SUCCESS
            )
    
    def test_invalid_status_code_validation(self):
        """Test HTTP status code validation."""
        with pytest.raises(ValidationError):
            ScrapedData(
                url="https://example.com",
                content="test",
                content_type=ContentType.HTML,
                status=ScrapingStatus.SUCCESS,
                status_code=999  # Invalid status code
            )
    
    def test_success_without_content_validation(self):
        """Test that successful status requires content."""
        with pytest.raises(ValidationError):
            ScrapedData(
                url="https://example.com",
                content=None,
                content_type=ContentType.HTML,
                status=ScrapingStatus.SUCCESS
            )
    
    def test_failed_without_error_validation(self):
        """Test that failed status requires error message."""
        with pytest.raises(ValidationError):
            ScrapedData(
                url="https://example.com",
                content=None,
                content_type=ContentType.HTML,
                status=ScrapingStatus.FAILED
            )
    
    def test_file_size_calculation(self):
        """Test automatic file size calculation."""
        content = "test content"
        data = ScrapedData(
            url="https://example.com",
            content=content,
            content_type=ContentType.HTML,
            status=ScrapingStatus.SUCCESS
        )
        
        # File size should be calculated automatically
        assert data.file_size == len(content.encode('utf-8'))
    
    def test_domain_property(self):
        """Test domain extraction."""
        data = ScrapedData(
            url="https://example.com/path",
            content="test",
            content_type=ContentType.HTML,
            status=ScrapingStatus.SUCCESS
        )
        
        assert data.domain == "example.com"
    
    def test_is_successful_property(self):
        """Test is_successful property."""
        successful_data = ScrapedData(
            url="https://example.com",
            content="test",
            content_type=ContentType.HTML,
            status=ScrapingStatus.SUCCESS
        )
        
        failed_data = ScrapedData(
            url="https://example.com",
            content_type=ContentType.HTML,
            status=ScrapingStatus.FAILED,
            error_message="Test error"
        )
        
        assert successful_data.is_successful is True
        assert failed_data.is_successful is False
    
    def test_content_length_property(self):
        """Test content_length property."""
        data = ScrapedData(
            url="https://example.com",
            content="test",
            content_type=ContentType.HTML,
            status=ScrapingStatus.SUCCESS
        )
        
        assert data.content_length == len("test")
    
    def test_to_dict_exclude_content(self):
        """Test to_dict with content exclusion."""
        data = ScrapedData(
            url="https://example.com",
            content="sensitive content",
            content_type=ContentType.HTML,
            status=ScrapingStatus.SUCCESS
        )
        
        dict_with_content = data.to_dict(exclude_content=False)
        dict_without_content = data.to_dict(exclude_content=True)
        
        assert "content" in dict_with_content
        assert "content" not in dict_without_content
        assert dict_with_content["url"] == dict_without_content["url"]