"""
Data Fetcher Specialist Agent - Implements sophisticated data acquisition strategies.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from .base import BaseAgent
import asyncio
import logging

class DataSource(BaseModel):
    """Specification for a data source with access requirements."""
    
    type: str = Field(description="Type of data source (web, api, sharepoint, s3, database)")
    url: Optional[str] = Field(default=None, description="URL or connection string")
    authentication_type: Optional[str] = Field(
        default=None,
        description="Authentication method (oauth, token, cookie, certificate, none)"
    )
    access_patterns: List[str] = Field(
        default_factory=list,
        description="Access patterns and navigation strategies"
    )
    rate_limits: Optional[int] = Field(
        default=None,
        description="Rate limit in requests per minute"
    )
    documentation_url: Optional[str] = Field(
        default=None,
        description="URL to API documentation or source description"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Required HTTP headers for requests"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for data access"
    )
    retry_config: Dict[str, int] = Field(
        default_factory=dict,
        description="Retry configuration (max_retries, backoff_factor, etc.)"
    )

class FetchingStrategy(BaseModel):
    """Generated strategy for data fetching operations."""
    
    source_type: str = Field(description="Type of data source being accessed")
    playwright_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Playwright automation configuration"
    )
    authentication_steps: List[str] = Field(
        default_factory=list,
        description="Step-by-step authentication procedure"
    )
    navigation_steps: List[str] = Field(
        default_factory=list,
        description="Navigation and data extraction steps"
    )
    error_handling: Dict[str, str] = Field(
        default_factory=dict,
        description="Error handling strategies for different scenarios"
    )
    performance_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Performance optimization settings"
    )
    generated_code: str = Field(
        default="",
        description="Generated Python code for data fetching"
    )

class DataFetcherAgent(BaseAgent):
    """
    Agent specialized in generating robust data acquisition strategies.
    
    Creates Playwright-based automation, handles authentication, and provides
    strategies for accessing diverse data sources including web, APIs, and cloud storage.
    """
    
    def __init__(
        self,
        agent_id: str = "data_fetcher",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 600
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.supported_sources = [
            "web", "api", "sharepoint", "s3", "database", 
            "file_share", "ftp", "sftp", "oauth_api"
        ]
        self.auth_strategies = self._initialize_auth_strategies()
        
    def _initialize_auth_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize authentication strategy templates."""
        return {
            "oauth": {
                "flow_type": "authorization_code",
                "required_params": ["client_id", "client_secret", "redirect_uri"],
                "token_handling": "bearer",
                "refresh_strategy": "automatic"
            },
            "token": {
                "placement": "header", 
                "format": "Bearer {token}",
                "validation": "required",
                "rotation": "optional"
            },
            "cookie": {
                "session_management": "automatic",
                "persistence": "file_based",
                "domain_handling": "flexible"
            },
            "certificate": {
                "format": "pem",
                "validation": "strict",
                "client_cert": "required"
            },
            "basic": {
                "encoding": "base64",
                "header": "Authorization",
                "credential_source": "environment"
            }
        }
    
    async def _process(
        self,
        data_sources: List[DataSource],
        security_requirements: List[str] = None,
        performance_targets: Dict[str, Any] = None,
        **kwargs
    ) -> List[FetchingStrategy]:
        """
        Generate comprehensive data fetching strategies for provided sources.
        
        Args:
            data_sources: List of data sources to create strategies for
            security_requirements: Security constraints and requirements
            performance_targets: Performance targets and optimization goals
            
        Returns:
            List[FetchingStrategy]: Generated strategies for each data source
        """
        self.logger.info(f"Generating fetching strategies for {len(data_sources)} sources")
        
        security_requirements = security_requirements or []
        performance_targets = performance_targets or {}
        
        strategies = []
        
        for source in data_sources:
            strategy = await self._create_source_strategy(
                source, security_requirements, performance_targets
            )
            strategies.append(strategy)
        
        return strategies
    
    async def _create_source_strategy(
        self,
        source: DataSource,
        security_requirements: List[str],
        performance_targets: Dict[str, Any]
    ) -> FetchingStrategy:
        """Create a comprehensive fetching strategy for a single data source."""
        
        if source.type == "web":
            return await self._create_web_strategy(source, security_requirements, performance_targets)
        elif source.type == "api":
            return await self._create_api_strategy(source, security_requirements, performance_targets)
        elif source.type == "sharepoint":
            return await self._create_sharepoint_strategy(source, security_requirements, performance_targets)
        elif source.type == "s3":
            return await self._create_s3_strategy(source, security_requirements, performance_targets)
        elif source.type == "database":
            return await self._create_database_strategy(source, security_requirements, performance_targets)
        else:
            return await self._create_generic_strategy(source, security_requirements, performance_targets)
    
    async def _create_web_strategy(
        self,
        source: DataSource,
        security_requirements: List[str],
        performance_targets: Dict[str, Any]
    ) -> FetchingStrategy:
        """Create web scraping strategy using Playwright."""
        
        playwright_config = {
            "headless": True,
            "browser": "chromium",
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (compatible; DataScrapingBot/1.0)",
            "timeout": 30000,
            "wait_for_selector_timeout": 10000
        }
        
        # Adjust for security requirements
        if "stealth_mode" in security_requirements:
            playwright_config.update({
                "headless": False,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "extra_http_headers": {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br"
                }
            })
        
        auth_steps = await self._generate_web_auth_steps(source)
        navigation_steps = await self._generate_navigation_steps(source)
        error_handling = await self._generate_web_error_handling()
        generated_code = await self._generate_web_scraping_code(source, playwright_config)
        
        return FetchingStrategy(
            source_type="web",
            playwright_config=playwright_config,
            authentication_steps=auth_steps,
            navigation_steps=navigation_steps,
            error_handling=error_handling,
            performance_config=performance_targets,
            generated_code=generated_code
        )
    
    async def _create_api_strategy(
        self,
        source: DataSource,
        security_requirements: List[str],
        performance_targets: Dict[str, Any]
    ) -> FetchingStrategy:
        """Create API consumption strategy."""
        
        auth_steps = await self._generate_api_auth_steps(source)
        
        performance_config = {
            "connection_pool_size": 10,
            "timeout": 30,
            "retry_attempts": 3,
            "backoff_factor": 2,
            "concurrent_requests": 5
        }
        
        if "rate_limit" in source.parameters:
            performance_config["rate_limit"] = source.parameters["rate_limit"]
        
        error_handling = await self._generate_api_error_handling()
        generated_code = await self._generate_api_client_code(source, performance_config)
        
        return FetchingStrategy(
            source_type="api",
            authentication_steps=auth_steps,
            error_handling=error_handling,
            performance_config=performance_config,
            generated_code=generated_code
        )
    
    async def _create_sharepoint_strategy(
        self,
        source: DataSource,
        security_requirements: List[str],
        performance_targets: Dict[str, Any]
    ) -> FetchingStrategy:
        """Create SharePoint access strategy."""
        
        auth_steps = [
            "Initialize Microsoft Graph client",
            "Authenticate using OAuth 2.0 with Azure AD",
            "Obtain access token with SharePoint permissions",
            "Set up site and list access credentials"
        ]
        
        navigation_steps = [
            "Connect to SharePoint site collection",
            "Navigate to specified document library or list",
            "Query items with filters and pagination",
            "Download files or extract list data",
            "Handle versioning and metadata extraction"
        ]
        
        error_handling = {
            "authentication_failure": "retry_with_token_refresh",
            "permission_denied": "escalate_to_admin",
            "rate_limit_exceeded": "exponential_backoff",
            "network_timeout": "circuit_breaker_pattern"
        }
        
        generated_code = await self._generate_sharepoint_code(source)
        
        return FetchingStrategy(
            source_type="sharepoint",
            authentication_steps=auth_steps,
            navigation_steps=navigation_steps,
            error_handling=error_handling,
            generated_code=generated_code
        )
    
    async def _create_s3_strategy(
        self,
        source: DataSource,
        security_requirements: List[str],
        performance_targets: Dict[str, Any]
    ) -> FetchingStrategy:
        """Create AWS S3 access strategy."""
        
        auth_steps = [
            "Configure AWS credentials (IAM role or access keys)",
            "Set up boto3 session with appropriate region",
            "Validate bucket access permissions",
            "Configure encryption settings if required"
        ]
        
        performance_config = {
            "multipart_threshold": 64 * 1024 * 1024,  # 64MB
            "max_concurrency": 10,
            "use_threads": True,
            "transfer_config": "optimized"
        }
        
        error_handling = {
            "access_denied": "check_iam_permissions",
            "bucket_not_found": "verify_bucket_name_and_region",
            "network_error": "retry_with_exponential_backoff",
            "rate_limit": "implement_client_side_throttling"
        }
        
        generated_code = await self._generate_s3_code(source, performance_config)
        
        return FetchingStrategy(
            source_type="s3",
            authentication_steps=auth_steps,
            error_handling=error_handling,
            performance_config=performance_config,
            generated_code=generated_code
        )
    
    async def _create_database_strategy(
        self,
        source: DataSource,
        security_requirements: List[str],
        performance_targets: Dict[str, Any]
    ) -> FetchingStrategy:
        """Create database access strategy."""
        
        auth_steps = [
            "Establish secure database connection",
            "Authenticate using provided credentials",
            "Set connection pool parameters",
            "Configure SSL/TLS if required"
        ]
        
        performance_config = {
            "connection_pool_size": 5,
            "connection_timeout": 30,
            "query_timeout": 300,
            "batch_size": 10000,
            "use_streaming": True
        }
        
        error_handling = {
            "connection_failed": "retry_with_backoff",
            "query_timeout": "break_into_smaller_chunks",
            "permission_denied": "verify_user_permissions",
            "deadlock": "retry_with_jitter"
        }
        
        generated_code = await self._generate_database_code(source, performance_config)
        
        return FetchingStrategy(
            source_type="database",
            authentication_steps=auth_steps,
            error_handling=error_handling,
            performance_config=performance_config,
            generated_code=generated_code
        )
    
    async def _create_generic_strategy(
        self,
        source: DataSource,
        security_requirements: List[str],
        performance_targets: Dict[str, Any]
    ) -> FetchingStrategy:
        """Create generic fetching strategy for unknown source types."""
        
        return FetchingStrategy(
            source_type=source.type,
            authentication_steps=[f"Configure {source.type} authentication"],
            navigation_steps=[f"Implement {source.type} data extraction"],
            error_handling={"generic_error": "log_and_retry"},
            performance_config=performance_targets,
            generated_code=f"# Generated code for {source.type} data source\n# TODO: Implement specific logic"
        )
    
    # Code generation methods
    
    async def _generate_web_scraping_code(
        self, 
        source: DataSource, 
        config: Dict[str, Any]
    ) -> str:
        """Generate Playwright-based web scraping code."""
        
        code_template = '''
import asyncio
from playwright.async_api import async_playwright, Page, Browser
from typing import List, Dict, Any, Optional
import logging

class WebDataFetcher:
    """Generated web data fetcher using Playwright."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def initialize(self) -> None:
        """Initialize browser and page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless={headless},
            timeout={timeout}
        )
        
        context = await self.browser.new_context(
            viewport={viewport},
            user_agent="{user_agent}"
        )
        
        self.page = await context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout({timeout})
    
    async def authenticate(self) -> None:
        """Handle authentication if required."""
        # Authentication steps will be implemented based on source requirements
        pass
    
    async def fetch_data(self, url: str) -> Dict[str, Any]:
        """Fetch data from the specified URL."""
        try:
            await self.page.goto(url, wait_until="networkidle")
            
            # Wait for content to load
            await self.page.wait_for_selector("body", timeout={selector_timeout})
            
            # Extract data based on selectors
            data = await self._extract_page_data()
            
            return {{"success": True, "data": data}}
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {{e}}")
            return {{"success": False, "error": str(e)}}
    
    async def _extract_page_data(self) -> Dict[str, Any]:
        """Extract structured data from the page."""
        # Implementation depends on specific page structure
        # This will be customized based on the data source
        
        # Example extraction patterns
        title = await self.page.title()
        content = await self.page.content()
        
        return {{
            "title": title,
            "content_length": len(content),
            "timestamp": "{{datetime.now().isoformat()}}"
        }}
    
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()

# Usage example
async def main():
    fetcher = WebDataFetcher({{
        "url": "{url}",
        "headless": {headless}
    }})
    
    try:
        await fetcher.initialize()
        await fetcher.authenticate()
        result = await fetcher.fetch_data("{url}")
        return result
    finally:
        await fetcher.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        return code_template.format(
            url=source.url or "https://example.com",
            headless=config.get("headless", True),
            timeout=config.get("timeout", 30000),
            viewport=config.get("viewport", {"width": 1920, "height": 1080}),
            user_agent=config.get("user_agent", "DataScrapingBot/1.0"),
            selector_timeout=config.get("wait_for_selector_timeout", 10000)
        )
    
    async def _generate_api_client_code(
        self,
        source: DataSource,
        config: Dict[str, Any]
    ) -> str:
        """Generate API client code."""
        
        code_template = '''
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime

class APIDataFetcher:
    """Generated API client for data fetching."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = "{base_url}"
        self.headers = {headers}
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize HTTP session."""
        connector = aiohttp.TCPConnector(
            limit={connection_pool_size},
            timeout=aiohttp.ClientTimeout(total={timeout})
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers=self.headers
        )
    
    async def authenticate(self) -> None:
        """Handle API authentication."""
        auth_type = "{auth_type}"
        
        if auth_type == "oauth":
            await self._oauth_authentication()
        elif auth_type == "token":
            await self._token_authentication()
        # Add other authentication methods as needed
    
    async def fetch_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch data from API endpoint."""
        if not self.session:
            await self.initialize()
        
        url = f"{{self.base_url}}/{{endpoint}}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {{"success": True, "data": data, "status": response.status}}
                else:
                    error_text = await response.text()
                    return {{"success": False, "error": error_text, "status": response.status}}
                    
        except Exception as e:
            self.logger.error(f"API request failed: {{e}}")
            return {{"success": False, "error": str(e)}}
    
    async def _oauth_authentication(self) -> None:
        """Handle OAuth authentication."""
        # OAuth implementation based on source requirements
        pass
    
    async def _token_authentication(self) -> None:
        """Handle token-based authentication."""
        # Token authentication implementation
        pass
    
    async def cleanup(self) -> None:
        """Clean up session resources."""
        if self.session:
            await self.session.close()

# Usage example
async def main():
    fetcher = APIDataFetcher({{
        "base_url": "{base_url}",
        "auth_type": "{auth_type}"
    }})
    
    try:
        await fetcher.initialize()
        await fetcher.authenticate()
        result = await fetcher.fetch_data("data-endpoint")
        return result
    finally:
        await fetcher.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        return code_template.format(
            base_url=source.url or "https://api.example.com",
            auth_type=source.authentication_type or "none",
            headers=source.headers or {},
            connection_pool_size=config.get("connection_pool_size", 10),
            timeout=config.get("timeout", 30)
        )
    
    async def _generate_sharepoint_code(self, source: DataSource) -> str:
        """Generate SharePoint access code."""
        
        return '''
import asyncio
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import logging

class SharePointDataFetcher:
    """Generated SharePoint data fetcher."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.site_url = config.get("site_url")
        self.username = config.get("username")
        self.password = config.get("password")
        self.ctx = None
        self.logger = logging.getLogger(__name__)
    
    async def authenticate(self) -> bool:
        """Authenticate with SharePoint."""
        try:
            auth_ctx = AuthenticationContext(self.site_url)
            auth_ctx.acquire_token_for_user(self.username, self.password)
            self.ctx = ClientContext(self.site_url, auth_ctx)
            return True
        except Exception as e:
            self.logger.error(f"SharePoint authentication failed: {e}")
            return False
    
    async def fetch_list_data(self, list_title: str) -> Dict[str, Any]:
        """Fetch data from SharePoint list."""
        try:
            target_list = self.ctx.web.lists.get_by_title(list_title)
            items = target_list.items
            self.ctx.load(items)
            self.ctx.execute_query()
            
            data = []
            for item in items:
                data.append(item.properties)
            
            return {"success": True, "data": data}
            
        except Exception as e:
            self.logger.error(f"Error fetching SharePoint data: {e}")
            return {"success": False, "error": str(e)}
'''
    
    async def _generate_s3_code(
        self,
        source: DataSource,
        config: Dict[str, Any]
    ) -> str:
        """Generate AWS S3 access code."""
        
        return f'''
import asyncio
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any, List
import logging

class S3DataFetcher:
    """Generated AWS S3 data fetcher."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bucket_name = config.get("bucket_name", "{source.parameters.get('bucket', 'default-bucket')}")
        self.s3_client = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize S3 client."""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.config.get('region', 'us-east-1')
            )
        except NoCredentialsError:
            self.logger.error("AWS credentials not found")
            raise
    
    async def fetch_object(self, key: str) -> Dict[str, Any]:
        """Fetch object from S3 bucket."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            content = response['Body'].read()
            
            return {{
                "success": True,
                "data": content,
                "metadata": response.get('Metadata', {{}})
            }}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self.logger.error(f"S3 error {{error_code}}: {{e}}")
            return {{"success": False, "error": str(e)}}
    
    async def list_objects(self, prefix: str = "") -> Dict[str, Any]:
        """List objects in S3 bucket."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            objects = response.get('Contents', [])
            
            return {{
                "success": True,
                "objects": [obj['Key'] for obj in objects],
                "count": len(objects)
            }}
            
        except ClientError as e:
            self.logger.error(f"Error listing S3 objects: {{e}}")
            return {{"success": False, "error": str(e)}}
'''
    
    async def _generate_database_code(
        self,
        source: DataSource,
        config: Dict[str, Any]
    ) -> str:
        """Generate database access code."""
        
        return '''
import asyncio
import asyncpg  # For PostgreSQL, adjust for other databases
from typing import Dict, Any, List
import logging

class DatabaseDataFetcher:
    """Generated database data fetcher."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection_string = config.get("connection_string")
        self.pool = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=config.get("pool_size", 5),
                command_timeout=config.get("query_timeout", 300)
            )
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    async def fetch_data(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Execute query and fetch results."""
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *(params or ()))
                
                # Convert to list of dictionaries
                data = [dict(row) for row in rows]
                
                return {
                    "success": True,
                    "data": data,
                    "row_count": len(data)
                }
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup(self) -> None:
        """Close database connections."""
        if self.pool:
            await self.pool.close()
'''
    
    # Helper methods for generating authentication and navigation steps
    
    async def _generate_web_auth_steps(self, source: DataSource) -> List[str]:
        """Generate web authentication steps."""
        
        if not source.authentication_type or source.authentication_type == "none":
            return ["No authentication required"]
        
        auth_type = source.authentication_type.lower()
        
        if auth_type == "cookie":
            return [
                "Navigate to login page",
                "Fill username and password fields",
                "Submit login form",
                "Wait for redirect to dashboard",
                "Store session cookies for subsequent requests"
            ]
        elif auth_type == "oauth":
            return [
                "Redirect to OAuth provider authorization URL",
                "Handle user authorization callback",
                "Exchange authorization code for access token",
                "Store access token for API requests"
            ]
        else:
            return [f"Implement {auth_type} authentication"]
    
    async def _generate_navigation_steps(self, source: DataSource) -> List[str]:
        """Generate navigation steps for web sources."""
        
        return [
            f"Navigate to {source.url}",
            "Wait for page to load completely", 
            "Handle any dynamic content loading",
            "Locate and interact with data elements",
            "Extract structured data from page",
            "Handle pagination if present",
            "Save extracted data in structured format"
        ]
    
    async def _generate_api_auth_steps(self, source: DataSource) -> List[str]:
        """Generate API authentication steps."""
        
        if not source.authentication_type:
            return ["No authentication required"]
        
        auth_type = source.authentication_type.lower()
        
        if auth_type == "oauth":
            return [
                "Register application with OAuth provider",
                "Obtain client credentials (ID and secret)", 
                "Implement OAuth 2.0 authorization code flow",
                "Exchange authorization code for access token",
                "Include Bearer token in API request headers",
                "Handle token refresh automatically"
            ]
        elif auth_type == "token":
            return [
                "Obtain API token from provider",
                "Store token securely in environment variables",
                "Include token in Authorization header",
                "Handle token expiration and renewal"
            ]
        else:
            return [f"Implement {auth_type} authentication for API"]
    
    async def _generate_web_error_handling(self) -> Dict[str, str]:
        """Generate web-specific error handling strategies."""
        
        return {
            "page_not_found": "verify_url_and_retry",
            "authentication_failed": "refresh_credentials_and_retry",
            "timeout": "increase_timeout_and_retry",
            "element_not_found": "wait_longer_or_modify_selector",
            "network_error": "retry_with_exponential_backoff",
            "captcha_detected": "notify_human_intervention_required",
            "rate_limited": "implement_respectful_delays",
            "javascript_error": "enable_debug_mode_and_log_console"
        }
    
    async def _generate_api_error_handling(self) -> Dict[str, str]:
        """Generate API-specific error handling strategies."""
        
        return {
            "401_unauthorized": "refresh_authentication_token",
            "403_forbidden": "check_permissions_and_escalate",
            "404_not_found": "verify_endpoint_url_and_parameters",
            "429_rate_limited": "implement_exponential_backoff",
            "500_server_error": "retry_with_circuit_breaker",
            "timeout": "increase_timeout_or_break_into_smaller_requests",
            "connection_error": "check_network_and_retry",
            "invalid_response": "log_response_and_handle_gracefully"
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "supported_sources": self.supported_sources,
            "authentication_methods": list(self.auth_strategies.keys()),
            "generation_capabilities": [
                "playwright_web_scraping",
                "api_client_generation",
                "sharepoint_integration",
                "s3_access_patterns",
                "database_connection_management",
                "authentication_flow_implementation",
                "error_handling_strategies",
                "performance_optimization"
            ],
            "output_format": "FetchingStrategy"
        })
        return base_capabilities