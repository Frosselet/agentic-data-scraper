"""Pydantic schemas for scraped data."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator


class ScrapingStatus(str, Enum):
    """Status of scraping operation."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


class ContentType(str, Enum):
    """Type of scraped content."""
    
    HTML = "html"
    JSON = "json"
    XML = "xml"
    TEXT = "text"
    BINARY = "binary"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class HttpMethod(str, Enum):
    """HTTP methods used for scraping."""
    
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ScrapedData(BaseModel):
    """
    Model for scraped web content and metadata.
    
    This model represents the result of a web scraping operation,
    including the content, metadata, and execution details.
    
    Attributes:
        url: The URL that was scraped
        content: The scraped content (text, HTML, JSON, etc.)
        content_type: Type of content scraped
        status: Status of the scraping operation
        status_code: HTTP status code received
        method: HTTP method used for scraping
        headers: HTTP headers received
        timestamp: When the scraping was performed
        execution_time: Time taken to scrape in seconds
        file_size: Size of scraped content in bytes
        encoding: Character encoding of the content
        metadata: Additional metadata about the scraping operation
        error_message: Error message if scraping failed
        retry_count: Number of retry attempts made
    """
    
    # Core data
    url: str = Field(description="URL that was scraped")
    content: Optional[Union[str, bytes, Dict[str, Any]]] = Field(
        default=None, 
        description="Scraped content"
    )
    content_type: ContentType = Field(description="Type of scraped content")
    
    # Status information
    status: ScrapingStatus = Field(description="Scraping operation status")
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    method: HttpMethod = Field(default=HttpMethod.GET, description="HTTP method used")
    
    # Headers and metadata
    headers: Dict[str, str] = Field(
        default_factory=dict, 
        description="HTTP response headers"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when scraping was performed"
    )
    
    # Performance metrics
    execution_time: Optional[float] = Field(
        default=None, 
        description="Execution time in seconds"
    )
    file_size: Optional[int] = Field(
        default=None,
        description="Size of content in bytes" 
    )
    
    # Technical details
    encoding: Optional[str] = Field(default=None, description="Content encoding")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional scraping metadata"
    )
    
    # Error handling
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if scraping failed"
    )
    retry_count: int = Field(default=0, description="Number of retry attempts")
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v:
            raise ValueError("URL cannot be empty")
        
        try:
            result = urlparse(v)
            if not result.scheme or not result.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            raise ValueError(f"Invalid URL: {e}")
        
        return v
    
    @field_validator("status_code")
    @classmethod
    def validate_status_code(cls, v: Optional[int]) -> Optional[int]:
        """Validate HTTP status code."""
        if v is not None and (v < 100 or v > 599):
            raise ValueError("Invalid HTTP status code")
        return v
    
    @field_validator("execution_time")
    @classmethod
    def validate_execution_time(cls, v: Optional[float]) -> Optional[float]:
        """Validate execution time is positive."""
        if v is not None and v < 0:
            raise ValueError("Execution time must be non-negative")
        return v
    
    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate file size is non-negative."""
        if v is not None and v < 0:
            raise ValueError("File size must be non-negative")
        return v
    
    @model_validator(mode="after")
    def validate_consistency(self) -> "ScrapedData":
        """Validate data consistency."""
        # If status is success, we should have content
        if self.status == ScrapingStatus.SUCCESS and self.content is None:
            raise ValueError("Successful scraping should have content")
        
        # If status is failed, we should have an error message
        if self.status == ScrapingStatus.FAILED and not self.error_message:
            raise ValueError("Failed scraping should have error message")
        
        # Calculate file size if content is available and size not set
        if self.content is not None and self.file_size is None:
            if isinstance(self.content, str):
                self.file_size = len(self.content.encode('utf-8'))
            elif isinstance(self.content, bytes):
                self.file_size = len(self.content)
            elif isinstance(self.content, dict):
                import json
                self.file_size = len(json.dumps(self.content).encode('utf-8'))
        
        return self
    
    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        return urlparse(self.url).netloc
    
    @property
    def is_successful(self) -> bool:
        """Check if scraping was successful."""
        return self.status == ScrapingStatus.SUCCESS
    
    @property
    def content_length(self) -> int:
        """Get content length."""
        if self.content is None:
            return 0
        
        if isinstance(self.content, str):
            return len(self.content)
        elif isinstance(self.content, bytes):
            return len(self.content)
        elif isinstance(self.content, dict):
            import json
            return len(json.dumps(self.content))
        
        return 0
    
    def to_dict(self, exclude_content: bool = False) -> Dict[str, Any]:
        """
        Convert to dictionary with optional content exclusion.
        
        Args:
            exclude_content: If True, exclude content field from output
            
        Returns:
            Dictionary representation
        """
        data = self.model_dump()
        
        if exclude_content:
            data.pop("content", None)
        
        return data
    
    class Config:
        """Pydantic configuration."""
        
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        
    def __str__(self) -> str:
        """String representation."""
        return f"ScrapedData(url='{self.url}', status='{self.status}')"