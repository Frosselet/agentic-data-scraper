# Playwright Navigation Demo

This directory contains a comprehensive demonstration of advanced web scraping capabilities using Playwright, showcasing techniques essential for agentic data scraping systems.

## 🚀 Overview

The `playwright_navigation_demo.py` demonstrates sophisticated web scraping patterns including:

- **Dynamic Content Handling**: JavaScript-heavy sites with async loading
- **Authentication Simulation**: Form-based login workflows
- **Multi-page Navigation**: Following links, breadcrumbs, and pagination
- **Data Extraction Patterns**: Multiple approaches for structured data extraction
- **Error Handling**: Robust error recovery and retry mechanisms
- **Modern Python Practices**: Async/await, type hints, Pydantic models

## 📋 Requirements

### System Requirements
- Python 3.8+
- Node.js (for Playwright browser installation)
- Internet connection for demo websites

### Python Dependencies
Install the required packages:

```bash
pip install -r requirements.txt
```

### Browser Installation
After installing Playwright, install the browsers:

```bash
playwright install chromium firefox webkit
```

## 🛠️ Installation & Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd agentic-data-scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r examples/requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

4. **Run the demo**:
   ```bash
   cd examples
   python playwright_navigation_demo.py
   ```

## ⚙️ Configuration

The demo is configurable via `config.yaml`. Key settings include:

```yaml
scraping:
  browser_type: "chromium"      # chromium, firefox, or webkit
  headless: true               # Set to false for visual debugging
  timeout: 30000              # Request timeout in milliseconds
  max_retries: 3              # Retry attempts for failed operations
  delay_between_requests: 1.0  # Rate limiting between requests
```

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `browser_type` | Browser engine to use | `chromium` |
| `headless` | Run browser without GUI | `true` |
| `timeout` | Default timeout (ms) | `30000` |
| `max_retries` | Max retry attempts | `3` |
| `delay_between_requests` | Delay between requests (s) | `1.0` |
| `viewport_width` | Browser viewport width | `1280` |
| `viewport_height` | Browser viewport height | `720` |

## 🎯 Demo Scenarios

### 1. Dynamic Content Handling
- **Target**: GitHub Trending page
- **Demonstrates**: JavaScript evaluation, waiting for dynamic content
- **Key Techniques**: 
  - `wait_for_selector()` for async content
  - `page.evaluate()` for JavaScript execution
  - Network idle detection

### 2. Authentication Simulation
- **Target**: Mock login form (data URL)
- **Demonstrates**: Form filling, submission, state verification
- **Key Techniques**:
  - Form interaction with `fill()` and `click()`
  - State validation after authentication
  - Mock credential handling

### 3. Multi-page Navigation
- **Target**: Wikipedia Featured Articles
- **Demonstrates**: Link following, breadcrumb extraction
- **Key Techniques**:
  - Breadcrumb navigation tracking
  - Cross-page data correlation
  - Internal link traversal

### 4. Data Extraction Patterns
- **Target**: Hacker News front page
- **Demonstrates**: Multiple extraction strategies
- **Key Techniques**:
  - Table-based data extraction
  - CSS selector patterns
  - Attribute-based extraction
  - Text analysis and statistics

### 5. Error Handling
- **Target**: Various error scenarios
- **Demonstrates**: Comprehensive error recovery
- **Key Techniques**:
  - Timeout handling
  - Missing element graceful degradation
  - Network error recovery
  - JavaScript error catching

## 📊 Output & Results

The demo generates several outputs:

### 1. Console Output
Real-time progress and results summary:
```
🚀 Playwright Web Scraping Navigation Demo
==================================================
✓ Dynamic Content Handling demo completed successfully
✓ Authentication Simulation demo completed successfully
...
📊 Demo Results Summary:
  • Total demos: 5
  • Success rate: 100.0%
```

### 2. JSON Results File
Detailed results saved as `scraping_results_<timestamp>.json`:
```json
{
  "summary": {
    "total_demos": 5,
    "successful_demos": 5,
    "success_rate": 100.0
  },
  "detailed_results": [...],
  "capabilities_demonstrated": [...]
}
```

### 3. Log File
Detailed execution log in `playwright_demo.log`:
```
2024-01-15 10:30:15,123 - __main__ - INFO - Starting dynamic content handling demo
2024-01-15 10:30:16,456 - __main__ - INFO - Successfully extracted 5 trending repositories
```

## 🏗️ Architecture & Design Patterns

### Async Context Manager Pattern
```python
async with PlaywrightNavigationDemo(config) as demo:
    results = await demo.run_all_demos()
```

### Retry with Exponential Backoff
```python
async def _retry_operation(self, operation, *args, **kwargs):
    for attempt in range(self.config.max_retries):
        try:
            return await operation(*args, **kwargs)
        except Exception as e:
            wait_time = (2 ** attempt) * self.config.delay_between_requests
            await asyncio.sleep(wait_time)
```

### Type-Safe Configuration
```python
class ScrapingConfig(BaseModel):
    browser_type: str = Field(default="chromium")
    headless: bool = Field(default=True)
    timeout: int = Field(default=30000)
```

### Structured Results
```python
@dataclass
class ScrapingResult:
    url: str
    title: Optional[str]
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str
    success: bool
    error: Optional[str] = None
```

## 🔧 Customization

### Adding New Demo Scenarios
1. Create a new method in `PlaywrightNavigationDemo`:
```python
async def demo_custom_scenario(self) -> ScrapingResult:
    logger.info("Starting custom scenario demo")
    page = await self.create_page()
    try:
        # Your custom scraping logic here
        pass
    finally:
        await page.close()
```

2. Add to the demo functions list in `run_all_demos()`:
```python
demo_functions = [
    # ... existing demos
    ("Custom Scenario", self.demo_custom_scenario),
]
```

### Modifying Target Websites
Update `config.yaml` to change target sites:
```yaml
demo:
  test_sites:
    dynamic_content: "https://your-target-site.com"
    navigation: "https://your-navigation-site.com"
```

### Browser Configuration
Switch browsers by modifying `config.yaml`:
```yaml
scraping:
  browser_type: "firefox"  # or "webkit"
```

## 🚨 Error Handling Features

The demo includes comprehensive error handling:

- **Timeout Recovery**: Graceful handling of page load timeouts
- **Missing Elements**: Fallback strategies when elements aren't found
- **Network Issues**: Retry logic for network failures
- **JavaScript Errors**: Catching and logging execution errors
- **Partial Success**: Continuing execution when some operations fail

## 🔍 Debugging

### Visual Debugging
Set `headless: false` in `config.yaml` to see browser actions:
```yaml
scraping:
  headless: false
```

### Verbose Logging
Enable debug logging:
```yaml
logging:
  level: "DEBUG"
```

### Screenshots
Enable screenshot capture:
```yaml
demo:
  save_screenshots: true
```

## 📈 Performance Considerations

- **Rate Limiting**: Built-in delays between requests
- **Resource Management**: Proper cleanup of browser resources
- **Memory Efficiency**: Individual page contexts for each demo
- **Concurrent Safety**: Async/await patterns throughout

## 🔐 Security & Best Practices

- **No Real Credentials**: Authentication demos use mock data only
- **User Agent**: Configurable user agent string
- **Rate Limiting**: Respectful request timing
- **Error Logging**: Comprehensive but secure logging (no sensitive data)

## 📚 Learning Outcomes

After running this demo, you'll understand:

1. **Modern Python async patterns** for web scraping
2. **Playwright's capabilities** for complex navigation
3. **Error handling strategies** for production systems
4. **Configuration management** with Pydantic
5. **Structured data extraction** techniques
6. **Multi-page navigation** patterns

## 🤝 Contributing

To extend this demo:

1. Follow the existing code patterns
2. Add comprehensive error handling
3. Include detailed logging
4. Update this README with new features
5. Add appropriate type hints

## 📄 License

This demonstration code is part of the agentic-data-scraper project and follows the project's licensing terms.

## 🆘 Troubleshooting

### Common Issues

1. **Browser Installation**: Run `playwright install` if browsers are missing
2. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
3. **Timeout Errors**: Increase timeout values in `config.yaml`
4. **Network Issues**: Check internet connectivity and proxy settings

### Getting Help

- Check the log file (`playwright_demo.log`) for detailed error information
- Enable verbose logging for debugging
- Use non-headless mode to see browser interactions
- Review the generated JSON results file for detailed execution data