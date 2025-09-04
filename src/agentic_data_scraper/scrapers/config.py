"""Configuration classes for web scrapers."""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class BrowserType(str, Enum):
    """Supported browser types."""
    
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"


class ProxyType(str, Enum):
    """Supported proxy types."""
    
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ScrapingStrategy(str, Enum):
    """Different scraping strategies."""
    
    FAST = "fast"          # HTTP-only, no JS rendering
    STANDARD = "standard"   # Basic browser automation
    STEALTH = "stealth"    # Anti-detection measures
    INTERACTIVE = "interactive"  # Handle dynamic content


class ProxyConfig(BaseModel):
    """Proxy configuration."""
    
    server: str = Field(description="Proxy server address")
    username: Optional[str] = Field(default=None, description="Proxy username")
    password: Optional[str] = Field(default=None, description="Proxy password")
    proxy_type: ProxyType = Field(default=ProxyType.HTTP, description="Proxy type")
    
    @field_validator("server")
    @classmethod
    def validate_server(cls, v: str) -> str:
        """Validate proxy server format."""
        if not v:
            raise ValueError("Proxy server cannot be empty")
        
        # Basic validation - should contain host and optionally port
        if "://" not in v and ":" not in v:
            raise ValueError("Proxy server should include protocol or port")
        
        return v


class BrowserConfig(BaseModel):
    """Browser configuration for Playwright."""
    
    browser_type: BrowserType = Field(default=BrowserType.CHROMIUM, description="Browser type")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    timeout: int = Field(default=30000, description="Default timeout in milliseconds")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent")
    viewport: Dict[str, int] = Field(
        default={"width": 1920, "height": 1080},
        description="Browser viewport size"
    )
    ignore_https_errors: bool = Field(default=False, description="Ignore HTTPS certificate errors")
    java_script_enabled: bool = Field(default=True, description="Enable JavaScript")
    
    # Stealth options
    disable_web_security: bool = Field(default=False, description="Disable web security")
    disable_features: List[str] = Field(
        default_factory=list,
        description="Chrome features to disable"
    )
    args: List[str] = Field(default_factory=list, description="Additional browser arguments")


class HttpConfig(BaseModel):
    """HTTP client configuration."""
    
    timeout: int = Field(default=30, description="HTTP timeout in seconds")
    max_redirects: int = Field(default=5, description="Maximum redirects to follow")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    user_agent: Optional[str] = Field(default=None, description="HTTP user agent")
    headers: Dict[str, str] = Field(default_factory=dict, description="Default HTTP headers")
    cookies: Dict[str, str] = Field(default_factory=dict, description="Default cookies")


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    
    enabled: bool = Field(default=True, description="Enable rate limiting")
    requests_per_second: float = Field(default=1.0, description="Requests per second limit")
    burst_size: int = Field(default=5, description="Burst size for token bucket")
    delay_between_requests: float = Field(default=0.0, description="Fixed delay between requests")
    randomize_delay: bool = Field(default=True, description="Add random jitter to delays")
    respect_robots_txt: bool = Field(default=True, description="Respect robots.txt")


class RetryConfig(BaseModel):
    """Retry configuration for failed requests."""
    
    max_attempts: int = Field(default=3, description="Maximum retry attempts")
    base_delay: float = Field(default=1.0, description="Base delay between retries")
    max_delay: float = Field(default=60.0, description="Maximum delay between retries")
    exponential_base: float = Field(default=2.0, description="Exponential backoff base")
    jitter: bool = Field(default=True, description="Add random jitter to delays")
    retry_on_status: List[int] = Field(
        default=[500, 502, 503, 504, 429],
        description="HTTP status codes to retry on"
    )


class ScraperConfig(BaseModel):
    """
    Comprehensive configuration for web scrapers.
    
    This class provides configuration options for all types of scrapers,
    including HTTP clients, browser automation, and various scraping strategies.
    
    Attributes:
        name: Configuration name for identification
        strategy: Scraping strategy to use
        browser: Browser-specific configuration
        http: HTTP client configuration  
        rate_limit: Rate limiting settings
        retry: Retry configuration for failures
        proxy: Optional proxy configuration
        output_dir: Directory to save scraped data
        save_screenshots: Whether to save screenshots during scraping
        save_html: Whether to save raw HTML content
        enable_logging: Enable detailed logging
        custom_settings: Additional custom settings
    """
    
    # General settings
    name: str = Field(description="Configuration name")
    strategy: ScrapingStrategy = Field(
        default=ScrapingStrategy.STANDARD,
        description="Scraping strategy"
    )
    
    # Component configurations
    browser: BrowserConfig = Field(default_factory=BrowserConfig, description="Browser settings")
    http: HttpConfig = Field(default_factory=HttpConfig, description="HTTP client settings")
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limiting settings"
    )
    retry: RetryConfig = Field(default_factory=RetryConfig, description="Retry settings")
    
    # Optional configurations
    proxy: Optional[ProxyConfig] = Field(default=None, description="Proxy configuration")
    
    # Output settings
    output_dir: Optional[Path] = Field(default=None, description="Output directory")
    save_screenshots: bool = Field(default=False, description="Save screenshots")
    save_html: bool = Field(default=False, description="Save raw HTML")
    
    # Debugging and logging
    enable_logging: bool = Field(default=True, description="Enable detailed logging")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Custom settings
    custom_settings: Dict[str, Union[str, int, float, bool]] = Field(
        default_factory=dict,
        description="Additional custom settings"
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate configuration name."""
        if not v or not v.strip():
            raise ValueError("Configuration name cannot be empty")
        return v.strip()
    
    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: Optional[Path]) -> Optional[Path]:
        """Validate output directory."""
        if v is not None:
            # Ensure it's a Path object
            if isinstance(v, str):
                v = Path(v)
            
            # Create directory if it doesn't exist
            v.mkdir(parents=True, exist_ok=True)
        
        return v
    
    def get_effective_timeout(self) -> int:
        """Get the effective timeout for operations."""
        if self.strategy == ScrapingStrategy.FAST:
            return self.http.timeout * 1000  # Convert to milliseconds
        else:
            return self.browser.timeout
    
    def get_effective_user_agent(self) -> Optional[str]:
        """Get the effective user agent string."""
        if self.strategy == ScrapingStrategy.FAST:
            return self.http.user_agent
        else:
            return self.browser.user_agent
    
    def is_browser_required(self) -> bool:
        """Check if browser automation is required."""
        return self.strategy in [
            ScrapingStrategy.STANDARD,
            ScrapingStrategy.STEALTH,
            ScrapingStrategy.INTERACTIVE
        ]
    
    class Config:
        """Pydantic configuration."""
        
        use_enum_values = True


def get_default_config(name: str = "default") -> ScraperConfig:
    """
    Get default scraper configuration.
    
    Args:
        name: Configuration name
        
    Returns:
        Default ScraperConfig instance
    """
    return ScraperConfig(name=name)


def get_fast_config(name: str = "fast") -> ScraperConfig:
    """
    Get configuration optimized for fast scraping.
    
    Args:
        name: Configuration name
        
    Returns:
        Fast ScraperConfig instance
    """
    return ScraperConfig(
        name=name,
        strategy=ScrapingStrategy.FAST,
        rate_limit=RateLimitConfig(requests_per_second=5.0),
        retry=RetryConfig(max_attempts=2, base_delay=0.5)
    )


def get_stealth_config(name: str = "stealth") -> ScraperConfig:
    """
    Get configuration optimized for stealth scraping.
    
    Args:
        name: Configuration name
        
    Returns:
        Stealth ScraperConfig instance
    """
    browser_config = BrowserConfig(
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox"
        ],
        disable_features=["VizDisplayCompositor"]
    )
    
    rate_limit_config = RateLimitConfig(
        requests_per_second=0.5,  # Slower for stealth
        randomize_delay=True
    )
    
    return ScraperConfig(
        name=name,
        strategy=ScrapingStrategy.STEALTH,
        browser=browser_config,
        rate_limit=rate_limit_config
    )