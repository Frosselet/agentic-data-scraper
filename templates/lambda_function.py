#!/usr/bin/env python3
"""
Default Lambda function template for Agentic Data Scraper
Optimized for Python 3.12+ and Docker Lambda runtime with Playwright
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, Optional

# Configure structured logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import Playwright with error handling
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
    logger.info("Playwright successfully imported")
except ImportError as e:
    PLAYWRIGHT_AVAILABLE = False
    logger.error(f"Playwright import failed: {e}")


class ScrapingPipeline:
    """
    Base scraping pipeline class for generated Lambda functions
    Optimized for Python 3.12+ async performance
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.start_time = time.time()
        
    async def __aenter__(self):
        """Async context manager entry - optimized for cold start performance"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not available in this environment")
            
        logger.info("Initializing browser...")
        self.playwright = await async_playwright().__aenter__()
        
        # Browser configuration optimized for Lambda
        browser_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--memory-pressure-off',
            '--max_old_space_size=1024'
        ]
        
        # Support for headed mode in development
        headless = os.getenv('PLAYWRIGHT_HEADED', 'false').lower() != 'true'
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=browser_args
        )
        
        self.page = await self.browser.new_page()
        
        # Configure page settings for optimal performance
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        logger.info(f"Browser initialized in {time.time() - self.start_time:.2f}s")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
        if hasattr(self, 'playwright'):
            await self.playwright.__aexit__(exc_type, exc_val, exc_tb)


async def scrape_data(url: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Default scraping function - will be replaced by generated code
    
    Args:
        url: Target URL to scrape
        config: Configuration parameters for scraping
        
    Returns:
        Dictionary containing scraped data and metadata
    """
    async with ScrapingPipeline() as pipeline:
        try:
            logger.info(f"Navigating to: {url}")
            await pipeline.page.goto(url, wait_until='networkidle')
            
            # Extract basic page information
            title = await pipeline.page.title()
            content = await pipeline.page.content()
            
            # Get page metrics for performance monitoring
            metrics = await pipeline.page.evaluate("""() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    timestamp: new Date().toISOString()
                };
            }""")
            
            return {
                'success': True,
                'data': {
                    'title': title,
                    'url': url,
                    'content_length': len(content),
                    'metrics': metrics
                },
                'metadata': {
                    'scraper_version': '1.0.0',
                    'python_version': sys.version,
                    'execution_time': time.time() - pipeline.start_time,
                    'memory_usage': f"{sys.getsizeof(content)} bytes"
                }
            }
            
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'metadata': {
                    'execution_time': time.time() - pipeline.start_time
                }
            }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function optimized for Python 3.12+
    
    Args:
        event: Lambda event data
        context: Lambda context object
        
    Returns:
        Response dictionary with status code and body
    """
    start_time = time.time()
    
    try:
        logger.info(f"Lambda function started - Request ID: {context.aws_request_id}")
        logger.info(f"Event: {json.dumps(event)}")
        
        # Extract parameters from event
        url = event.get('url', 'https://example.com')
        config = event.get('config', {})
        
        # Validate input
        if not url:
            raise ValueError("URL parameter is required")
            
        # Run async scraping function
        result = asyncio.run(scrape_data(url, config))
        
        # Add Lambda context information
        result['lambda_context'] = {
            'request_id': context.aws_request_id,
            'function_name': context.function_name,
            'function_version': context.function_version,
            'memory_limit': context.memory_limit_in_mb,
            'remaining_time': context.get_remaining_time_in_millis(),
            'total_execution_time': time.time() - start_time
        }
        
        return {
            'statusCode': 200 if result['success'] else 500,
            'headers': {
                'Content-Type': 'application/json',
                'X-Lambda-Request-Id': context.aws_request_id
            },
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        error_message = f"Lambda execution failed: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'X-Lambda-Request-Id': getattr(context, 'aws_request_id', 'unknown')
            },
            'body': json.dumps({
                'success': False,
                'error': error_message,
                'error_type': type(e).__name__,
                'lambda_context': {
                    'request_id': getattr(context, 'aws_request_id', 'unknown'),
                    'execution_time': time.time() - start_time
                }
            })
        }


# For local testing
if __name__ == "__main__":
    # Simulate Lambda event for local testing
    test_event = {
        'url': 'https://example.com',
        'config': {
            'headless': True,
            'wait_for': 'networkidle'
        }
    }
    
    class MockContext:
        aws_request_id = 'local-test-123'
        function_name = 'test-function'
        function_version = '1'
        memory_limit_in_mb = 512
        
        def get_remaining_time_in_millis(self):
            return 30000
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(json.loads(result['body']), indent=2))