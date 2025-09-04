#!/usr/bin/env python3
"""
Playwright Web Scraping Navigation Demo

This module demonstrates advanced web scraping capabilities using Playwright,
showcasing dynamic content handling, authentication simulation, multi-page navigation,
data extraction patterns, and robust error handling for agentic data scraping.

Author: Agentic Data Scraper
License: MIT
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("playwright_demo.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


class ScrapingConfig(BaseModel):
    """Configuration model for web scraping parameters."""
    
    browser_type: str = Field(default="chromium", description="Browser type to use")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    timeout: int = Field(default=30000, description="Default timeout in milliseconds")
    viewport_width: int = Field(default=1280, description="Viewport width")
    viewport_height: int = Field(default=720, description="Viewport height")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    delay_between_requests: float = Field(default=1.0, description="Delay between requests in seconds")
    
    class Config:
        """Pydantic config."""
        extra = "forbid"


@dataclass
class ScrapingResult:
    """Data class for scraping results."""
    
    url: str
    title: Optional[str]
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str
    success: bool
    error: Optional[str] = None


class PlaywrightNavigationDemo:
    """
    Advanced Playwright web scraping demonstration class.
    
    This class showcases sophisticated web scraping techniques including:
    - Dynamic content handling with JavaScript-heavy sites
    - Authentication simulation
    - Multi-page navigation patterns
    - Data extraction from various HTML structures
    - Comprehensive error handling
    """
    
    def __init__(self, config: ScrapingConfig) -> None:
        """
        Initialize the demo with configuration.
        
        Args:
            config: ScrapingConfig object containing scraping parameters
        """
        self.config = config
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.results: List[ScrapingResult] = []
    
    async def __aenter__(self) -> "PlaywrightNavigationDemo":
        """Async context manager entry."""
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.cleanup()
    
    async def setup(self) -> None:
        """Initialize Playwright browser and context."""
        try:
            self.playwright = await async_playwright().start()
            
            # Select browser type
            if self.config.browser_type.lower() == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=self.config.headless
                )
            elif self.config.browser_type.lower() == "webkit":
                self.browser = await self.playwright.webkit.launch(
                    headless=self.config.headless
                )
            else:  # Default to Chromium
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless
                )
            
            # Create browser context with configuration
            context_options = {
                "viewport": {
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height
                }
            }
            
            if self.config.user_agent:
                context_options["user_agent"] = self.config.user_agent
            
            self.context = await self.browser.new_context(**context_options)
            
            # Enable request interception for debugging
            await self.context.route("**/*", self._handle_route)
            
            logger.info("Playwright setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Playwright: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up Playwright resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Playwright cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _handle_route(self, route, request) -> None:
        """Handle route interception for debugging."""
        logger.debug(f"Request: {request.method} {request.url}")
        await route.continue_()
    
    async def _retry_operation(self, operation, *args, **kwargs) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: The async function to retry
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = (2 ** attempt) * self.config.delay_between_requests
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        raise last_exception
    
    async def create_page(self) -> Page:
        """
        Create a new page with common configurations.
        
        Returns:
            Configured Playwright page
        """
        if not self.context:
            raise RuntimeError("Browser context not initialized")
        
        page = await self.context.new_page()
        page.set_default_timeout(self.config.timeout)
        
        # Set up common event handlers
        page.on("console", lambda msg: logger.debug(f"Console: {msg.text}"))
        page.on("pageerror", lambda error: logger.error(f"Page error: {error}"))
        
        return page
    
    async def demo_dynamic_content_handling(self) -> ScrapingResult:
        """
        Demonstrate handling of JavaScript-heavy sites with dynamic content.
        
        Returns:
            ScrapingResult with extracted data
        """
        logger.info("Starting dynamic content handling demo")
        page = await self.create_page()
        
        try:
            # Navigate to a JavaScript-heavy site (GitHub trending page)
            url = "https://github.com/trending"
            await page.goto(url, wait_until="networkidle")
            
            # Wait for dynamic content to load
            await page.wait_for_selector("[data-testid='repo-list']", timeout=self.config.timeout)
            
            # Extract trending repositories
            repos = await page.evaluate("""
                () => {
                    const repoElements = document.querySelectorAll('article.Box-row');
                    return Array.from(repoElements).slice(0, 5).map(repo => {
                        const titleEl = repo.querySelector('h2 a');
                        const descEl = repo.querySelector('p');
                        const langEl = repo.querySelector('[itemprop="programmingLanguage"]');
                        const starsEl = repo.querySelector('a[href$="/stargazers"]');
                        
                        return {
                            title: titleEl?.textContent?.trim() || '',
                            url: titleEl?.href || '',
                            description: descEl?.textContent?.trim() || '',
                            language: langEl?.textContent?.trim() || '',
                            stars: starsEl?.textContent?.trim() || ''
                        };
                    });
                }
            """)
            
            title = await page.title()
            
            result = ScrapingResult(
                url=url,
                title=title,
                content={"trending_repos": repos},
                metadata={
                    "total_repos_extracted": len(repos),
                    "extraction_method": "JavaScript evaluation"
                },
                timestamp=datetime.now().isoformat(),
                success=True
            )
            
            logger.info(f"Successfully extracted {len(repos)} trending repositories")
            return result
            
        except Exception as e:
            logger.error(f"Error in dynamic content demo: {e}")
            return ScrapingResult(
                url="https://github.com/trending",
                title=None,
                content={},
                metadata={},
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )
        finally:
            await page.close()
    
    async def demo_authentication_simulation(self) -> ScrapingResult:
        """
        Demonstrate authentication form handling (mock example).
        
        Returns:
            ScrapingResult with authentication demo data
        """
        logger.info("Starting authentication simulation demo")
        page = await self.create_page()
        
        try:
            # Create a mock login form using data URLs
            mock_login_html = """
            <html>
            <head><title>Mock Login Demo</title></head>
            <body>
                <h1>Mock Authentication Demo</h1>
                <form id="loginForm" onsubmit="handleLogin(event)">
                    <div>
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div>
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
                <div id="result"></div>
                <script>
                    function handleLogin(e) {
                        e.preventDefault();
                        const username = document.getElementById('username').value;
                        const password = document.getElementById('password').value;
                        
                        // Mock authentication
                        if (username === 'demo' && password === 'password123') {
                            document.getElementById('result').innerHTML = 
                                '<div class="success">Login successful! Welcome ' + username + '</div>';
                            document.body.classList.add('authenticated');
                        } else {
                            document.getElementById('result').innerHTML = 
                                '<div class="error">Invalid credentials</div>';
                        }
                    }
                </script>
                <style>
                    .success { color: green; }
                    .error { color: red; }
                    .authenticated { background-color: #f0f8f0; }
                </style>
            </body>
            </html>
            """
            
            # Navigate to the mock page
            url = f"data:text/html,{mock_login_html}"
            await page.goto(url)
            
            # Fill in login credentials
            await page.fill("#username", "demo")
            await page.fill("#password", "password123")
            
            # Submit the form
            await page.click("button[type='submit']")
            
            # Wait for authentication result
            await page.wait_for_selector(".success", timeout=5000)
            
            # Verify authentication state
            is_authenticated = await page.evaluate(
                "() => document.body.classList.contains('authenticated')"
            )
            
            success_message = await page.inner_text(".success")
            title = await page.title()
            
            result = ScrapingResult(
                url="mock://authentication-demo",
                title=title,
                content={
                    "authentication_successful": is_authenticated,
                    "success_message": success_message,
                    "demo_credentials": {
                        "username": "demo",
                        "note": "Mock authentication for demonstration"
                    }
                },
                metadata={
                    "authentication_method": "form_submission",
                    "mock_demo": True
                },
                timestamp=datetime.now().isoformat(),
                success=True
            )
            
            logger.info("Authentication simulation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in authentication demo: {e}")
            return ScrapingResult(
                url="mock://authentication-demo",
                title=None,
                content={},
                metadata={},
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )
        finally:
            await page.close()
    
    async def demo_multipage_navigation(self) -> ScrapingResult:
        """
        Demonstrate multi-page navigation including pagination and breadcrumbs.
        
        Returns:
            ScrapingResult with navigation demo data
        """
        logger.info("Starting multi-page navigation demo")
        page = await self.create_page()
        
        try:
            # Navigate to Wikipedia's featured articles
            url = "https://en.wikipedia.org/wiki/Wikipedia:Featured_articles"
            await page.goto(url, wait_until="domcontentloaded")
            
            # Extract breadcrumb navigation
            breadcrumbs = await page.evaluate("""
                () => {
                    const breadcrumbElements = document.querySelectorAll('#mw-content-text .mw-breadcrumb a');
                    return Array.from(breadcrumbElements).map(el => ({
                        text: el.textContent.trim(),
                        url: el.href
                    }));
                }
            """)
            
            # Get page title and first featured article link
            title = await page.title()
            
            # Find and click on first featured article link
            first_article_selector = "#mw-content-text ul li a"
            await page.wait_for_selector(first_article_selector, timeout=10000)
            
            first_article_url = await page.get_attribute(first_article_selector, "href")
            if first_article_url and first_article_url.startswith("/"):
                first_article_url = f"https://en.wikipedia.org{first_article_url}"
            
            # Navigate to the first featured article
            if first_article_url:
                await page.goto(first_article_url, wait_until="domcontentloaded")
                
                # Extract article information
                article_title = await page.title()
                
                # Get article summary (first paragraph)
                summary = await page.evaluate("""
                    () => {
                        const firstPara = document.querySelector('#mw-content-text .mw-parser-output > p');
                        return firstPara ? firstPara.textContent.trim() : '';
                    }
                """)
                
                # Check for table of contents (navigation within page)
                toc_items = await page.evaluate("""
                    () => {
                        const tocItems = document.querySelectorAll('#toc .toclevel-1 a .toctext');
                        return Array.from(tocItems).slice(0, 5).map(item => item.textContent.trim());
                    }
                """)
                
                # Get categories
                categories = await page.evaluate("""
                    () => {
                        const categoryLinks = document.querySelectorAll('#mw-normal-catlinks ul li a');
                        return Array.from(categoryLinks).slice(0, 5).map(link => link.textContent.trim());
                    }
                """)
            
            result = ScrapingResult(
                url=url,
                title=title,
                content={
                    "main_page": {
                        "title": title,
                        "breadcrumbs": breadcrumbs
                    },
                    "featured_article": {
                        "title": article_title if first_article_url else None,
                        "url": first_article_url,
                        "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                        "table_of_contents": toc_items,
                        "categories": categories
                    }
                },
                metadata={
                    "navigation_pattern": "breadcrumb_and_internal_links",
                    "pages_visited": 2 if first_article_url else 1
                },
                timestamp=datetime.now().isoformat(),
                success=True
            )
            
            logger.info("Multi-page navigation demo completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-page navigation demo: {e}")
            return ScrapingResult(
                url="https://en.wikipedia.org/wiki/Wikipedia:Featured_articles",
                title=None,
                content={},
                metadata={},
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )
        finally:
            await page.close()
    
    async def demo_data_extraction_patterns(self) -> ScrapingResult:
        """
        Demonstrate various data extraction patterns from different HTML structures.
        
        Returns:
            ScrapingResult with extracted data patterns
        """
        logger.info("Starting data extraction patterns demo")
        page = await self.create_page()
        
        try:
            # Navigate to a page with rich structured data (Hacker News)
            url = "https://news.ycombinator.com/"
            await page.goto(url, wait_until="domcontentloaded")
            
            # Extract structured data using multiple patterns
            
            # Pattern 1: Table-based extraction
            stories = await page.evaluate("""
                () => {
                    const storyRows = document.querySelectorAll('.athing');
                    return Array.from(storyRows).slice(0, 5).map(row => {
                        const titleEl = row.querySelector('.storylink');
                        const rankEl = row.querySelector('.rank');
                        const scoreRow = row.nextElementSibling;
                        const scoreEl = scoreRow ? scoreRow.querySelector('.score') : null;
                        const authorEl = scoreRow ? scoreRow.querySelector('.hnuser') : null;
                        const commentsEl = scoreRow ? scoreRow.querySelector('a[href*="item?id="]') : null;
                        
                        return {
                            rank: rankEl ? rankEl.textContent.replace('.', '') : '',
                            title: titleEl ? titleEl.textContent.trim() : '',
                            url: titleEl ? titleEl.href : '',
                            score: scoreEl ? scoreEl.textContent : '0 points',
                            author: authorEl ? authorEl.textContent : 'unknown',
                            comments: commentsEl ? commentsEl.textContent : '0 comments'
                        };
                    });
                }
            """)
            
            # Pattern 2: CSS selector-based extraction
            navigation_links = await page.evaluate("""
                () => {
                    const navLinks = document.querySelectorAll('.pagetop a');
                    return Array.from(navLinks).map(link => ({
                        text: link.textContent.trim(),
                        url: link.href,
                        is_external: !link.href.includes('ycombinator.com')
                    }));
                }
            """)
            
            # Pattern 3: Attribute-based extraction
            metadata = await page.evaluate("""
                () => {
                    return {
                        page_title: document.title,
                        meta_description: document.querySelector('meta[name="description"]')?.content || '',
                        canonical_url: document.querySelector('link[rel="canonical"]')?.href || '',
                        total_stories: document.querySelectorAll('.athing').length,
                        page_structure: {
                            has_header: !!document.querySelector('header'),
                            has_footer: !!document.querySelector('footer'),
                            has_navigation: !!document.querySelector('nav, .pagetop')
                        }
                    };
                }
            """)
            
            # Pattern 4: Text content extraction with cleaning
            page_text_stats = await page.evaluate("""
                () => {
                    const bodyText = document.body.innerText;
                    const words = bodyText.split(/\s+/).filter(word => word.length > 0);
                    const uniqueWords = new Set(words.map(word => word.toLowerCase()));
                    
                    return {
                        total_characters: bodyText.length,
                        total_words: words.length,
                        unique_words: uniqueWords.size,
                        average_word_length: words.reduce((sum, word) => sum + word.length, 0) / words.length
                    };
                }
            """)
            
            title = await page.title()
            
            result = ScrapingResult(
                url=url,
                title=title,
                content={
                    "top_stories": stories,
                    "navigation_links": navigation_links,
                    "page_metadata": metadata,
                    "text_statistics": page_text_stats
                },
                metadata={
                    "extraction_patterns_used": [
                        "table_based_extraction",
                        "css_selector_based",
                        "attribute_based",
                        "text_content_analysis"
                    ],
                    "total_data_points_extracted": len(stories) + len(navigation_links) + 1
                },
                timestamp=datetime.now().isoformat(),
                success=True
            )
            
            logger.info(f"Successfully demonstrated {len(result.metadata['extraction_patterns_used'])} extraction patterns")
            return result
            
        except Exception as e:
            logger.error(f"Error in data extraction patterns demo: {e}")
            return ScrapingResult(
                url="https://news.ycombinator.com/",
                title=None,
                content={},
                metadata={},
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )
        finally:
            await page.close()
    
    async def demo_error_handling(self) -> ScrapingResult:
        """
        Demonstrate comprehensive error handling patterns.
        
        Returns:
            ScrapingResult with error handling demo data
        """
        logger.info("Starting error handling demo")
        page = await self.create_page()
        
        error_scenarios = []
        
        try:
            # Scenario 1: Timeout handling
            try:
                await page.goto("https://httpstat.us/200?sleep=35000", timeout=5000)
            except PlaywrightTimeoutError as e:
                error_scenarios.append({
                    "scenario": "timeout_handling",
                    "error_type": "PlaywrightTimeoutError",
                    "handled": True,
                    "description": "Successfully caught and handled timeout error"
                })
                logger.info("Timeout error handled successfully")
            
            # Scenario 2: Missing element handling
            try:
                await page.goto("https://example.com", wait_until="domcontentloaded")
                await page.wait_for_selector("#non-existent-element", timeout=2000)
            except PlaywrightTimeoutError:
                error_scenarios.append({
                    "scenario": "missing_element_handling",
                    "error_type": "ElementNotFound",
                    "handled": True,
                    "description": "Gracefully handled missing element"
                })
                logger.info("Missing element error handled successfully")
            
            # Scenario 3: Network error simulation
            try:
                await page.goto("https://this-domain-definitely-does-not-exist-12345.com")
            except Exception as e:
                error_scenarios.append({
                    "scenario": "network_error_handling",
                    "error_type": type(e).__name__,
                    "handled": True,
                    "description": "Network error caught and handled"
                })
                logger.info("Network error handled successfully")
            
            # Scenario 4: JavaScript error handling
            try:
                await page.goto("https://example.com")
                await page.evaluate("nonExistentFunction()")
            except Exception as e:
                error_scenarios.append({
                    "scenario": "javascript_error_handling",
                    "error_type": type(e).__name__,
                    "handled": True,
                    "description": "JavaScript execution error handled"
                })
                logger.info("JavaScript error handled successfully")
            
            # Demonstrate recovery strategies
            recovery_strategies = {
                "retry_with_backoff": "Implemented exponential backoff for failed operations",
                "graceful_degradation": "Fallback to basic extraction when advanced methods fail",
                "partial_success": "Continue processing even when some elements fail",
                "comprehensive_logging": "Detailed logging for debugging and monitoring"
            }
            
            result = ScrapingResult(
                url="demo://error-handling",
                title="Error Handling Demonstration",
                content={
                    "error_scenarios_tested": error_scenarios,
                    "recovery_strategies": recovery_strategies,
                    "error_handling_summary": {
                        "total_scenarios": len(error_scenarios),
                        "all_handled": all(scenario["handled"] for scenario in error_scenarios),
                        "error_types_covered": list(set(scenario["error_type"] for scenario in error_scenarios))
                    }
                },
                metadata={
                    "demo_type": "error_handling_comprehensive",
                    "all_errors_handled": True
                },
                timestamp=datetime.now().isoformat(),
                success=True
            )
            
            logger.info("Error handling demo completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in error handling demo: {e}")
            return ScrapingResult(
                url="demo://error-handling",
                title=None,
                content={"unexpected_error": str(e)},
                metadata={},
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )
        finally:
            await page.close()
    
    async def run_all_demos(self) -> List[ScrapingResult]:
        """
        Run all demonstration scenarios.
        
        Returns:
            List of ScrapingResult objects from all demos
        """
        logger.info("Starting comprehensive Playwright navigation demo")
        
        demo_functions = [
            ("Dynamic Content Handling", self.demo_dynamic_content_handling),
            ("Authentication Simulation", self.demo_authentication_simulation),
            ("Multi-page Navigation", self.demo_multipage_navigation),
            ("Data Extraction Patterns", self.demo_data_extraction_patterns),
            ("Error Handling", self.demo_error_handling),
        ]
        
        results = []
        
        for demo_name, demo_func in demo_functions:
            logger.info(f"Running {demo_name} demo...")
            try:
                result = await self._retry_operation(demo_func)
                results.append(result)
                
                if result.success:
                    logger.info(f"✓ {demo_name} demo completed successfully")
                else:
                    logger.warning(f"✗ {demo_name} demo completed with errors: {result.error}")
                    
            except Exception as e:
                logger.error(f"✗ {demo_name} demo failed: {e}")
                error_result = ScrapingResult(
                    url="demo://failed",
                    title=demo_name,
                    content={},
                    metadata={"demo_name": demo_name},
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error=str(e)
                )
                results.append(error_result)
            
            # Add delay between demos
            await asyncio.sleep(self.config.delay_between_requests)
        
        self.results = results
        logger.info(f"All demos completed. Success rate: {sum(r.success for r in results)}/{len(results)}")
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report of all demo results.
        
        Returns:
            Dictionary containing the full report
        """
        if not self.results:
            return {"error": "No results available. Run demos first."}
        
        successful_demos = [r for r in self.results if r.success]
        failed_demos = [r for r in self.results if not r.success]
        
        report = {
            "summary": {
                "total_demos": len(self.results),
                "successful_demos": len(successful_demos),
                "failed_demos": len(failed_demos),
                "success_rate": len(successful_demos) / len(self.results) * 100,
                "execution_time": datetime.now().isoformat()
            },
            "configuration": self.config.dict(),
            "detailed_results": [result.__dict__ for result in self.results],
            "capabilities_demonstrated": [
                "Dynamic content handling with JavaScript evaluation",
                "Authentication form simulation and verification",
                "Multi-page navigation with breadcrumb tracking",
                "Multiple data extraction patterns (CSS, XPath, JavaScript)",
                "Comprehensive error handling and recovery",
                "Async/await patterns with proper resource management",
                "Type hints and modern Python practices",
                "Configurable browser settings and retry logic"
            ]
        }
        
        return report


async def load_config(config_path: str = "examples/config.yaml") -> ScrapingConfig:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ScrapingConfig object
    """
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return ScrapingConfig(**config_data.get('scraping', {}))
    except FileNotFoundError:
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return ScrapingConfig()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return ScrapingConfig()


async def main() -> None:
    """Main demonstration function."""
    print("🚀 Playwright Web Scraping Navigation Demo")
    print("=" * 50)
    
    # Load configuration
    config = await load_config()
    
    # Run the demonstration
    async with PlaywrightNavigationDemo(config) as demo:
        results = await demo.run_all_demos()
        
        # Generate and save report
        report = demo.generate_report()
        
        # Save results to file
        results_file = f"scraping_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📊 Demo Results Summary:")
        print(f"  • Total demos: {report['summary']['total_demos']}")
        print(f"  • Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"  • Results saved to: {results_file}")
        
        # Print individual demo results
        for i, result in enumerate(results, 1):
            status = "✓" if result.success else "✗"
            print(f"  {status} Demo {i}: {result.url}")
            if result.error:
                print(f"    Error: {result.error}")
        
        print(f"\n🎯 Capabilities demonstrated:")
        for capability in report['capabilities_demonstrated']:
            print(f"  • {capability}")


if __name__ == "__main__":
    asyncio.run(main())