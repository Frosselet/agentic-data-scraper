# Docker Lambda Templates for Agentic Data Scraper

This directory contains production-ready templates for deploying AWS Lambda functions with Python 3.12+ and full Playwright support using Docker containers.

## Files Overview

- **`Dockerfile.lambda-base`** - Multi-stage Docker build optimized for AWS Lambda with Python 3.12+ and Playwright
- **`lambda_function.py`** - Template Lambda function with async Playwright integration
- **`requirements.txt`** - Python dependencies optimized for Python 3.12+ performance
- **`docker-compose.yml`** - Local development environment with Lambda Runtime Interface Emulator
- **`Makefile`** - Build, test, and deployment automation
- **`README.md`** - This documentation file

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- AWS CLI configured (for deployment)
- Python 3.12+ (for local development)

### Local Development

1. **Build the development image:**
   ```bash
   make build
   ```

2. **Start the development environment:**
   ```bash
   make dev
   ```

3. **Test the Lambda function locally:**
   ```bash
   make test-local
   ```

4. **View logs:**
   ```bash
   make logs
   ```

### Debugging with Headed Browser

For debugging scraping logic with a visible browser:

```bash
make debug
```

This starts a VNC server accessible at `http://localhost:5800` (password: `playwright`)

### Production Deployment

1. **Set AWS environment variables:**
   ```bash
   export AWS_ACCOUNT_ID=123456789012
   export AWS_REGION=us-east-1
   ```

2. **Deploy to AWS Lambda:**
   ```bash
   make deploy
   ```

## Template Customization

### Dockerfile.lambda-base

The Dockerfile uses a multi-stage build optimized for:

- **Python 3.12+ performance** - Leverages latest Python optimizations
- **Cold start optimization** - Pre-compiled modules and optimized layer caching  
- **Browser support** - Full Chromium, Firefox, and WebKit browsers
- **Memory efficiency** - Optimized for Lambda memory constraints
- **Security** - Minimal attack surface with only required dependencies

Key features:
- Multi-stage build for smaller production images
- System dependencies optimized for browser automation
- Python 3.12+ specific environment variables for performance
- Support for both headless and headed browser modes
- Health check endpoint for container monitoring

### Lambda Function Template

The `lambda_function.py` template provides:

- **Async/await patterns** optimized for Python 3.12+
- **Structured logging** with Lambda context
- **Error handling** with detailed error reporting
- **Performance monitoring** with execution metrics
- **Browser lifecycle management** with proper cleanup
- **Local testing support** with mock context

Key components:
```python
# Async context manager for browser lifecycle
async with ScrapingPipeline() as pipeline:
    result = await pipeline.page.goto(url)
    
# Performance monitoring
metrics = {
    'execution_time': time.time() - start_time,
    'memory_usage': sys.getsizeof(content)
}
```

### Configuration Options

Environment variables for customization:

- **`PLAYWRIGHT_HEADED`** - Set to `'true'` for headed browser mode (debugging)
- **`PLAYWRIGHT_BROWSERS_PATH`** - Custom browser installation path
- **`CHROME_BIN`** - Custom Chrome binary path
- **`DISPLAY`** - X11 display for headed mode (`:99` default)

Python 3.12+ optimization variables:
- **`PYTHONPROFILEIMPORTTIME`** - Module import profiling
- **`PYTHONHASHSEED`** - Deterministic hash behavior
- **`PYTHONDONTWRITEBYTECODE`** - Skip .pyc file generation

## Performance Optimization

### Cold Start Optimization

The template includes several strategies to minimize cold start times:

1. **Pre-compiled modules** - Python bytecode compilation during build
2. **Module pre-warming** - Import critical modules during bootstrap
3. **Optimized browser args** - Minimal Chrome flags for faster startup
4. **Layer caching** - Efficient Docker layer structure for caching

### Memory Management

Recommended Lambda configurations:

- **Memory**: 1024-2048 MB (depending on scraping complexity)
- **Timeout**: 5-15 minutes (for complex multi-page scraping)
- **Provisioned concurrency**: Consider for high-frequency usage

### Browser Configuration

Optimized browser settings for Lambda:

```python
browser_args = [
    '--no-sandbox',                    # Required for Lambda security model
    '--disable-dev-shm-usage',        # Use disk instead of /dev/shm
    '--disable-gpu',                  # No GPU in Lambda environment
    '--memory-pressure-off',          # Disable memory pressure handling
    '--max_old_space_size=1024'       # Limit V8 heap size
]
```

## Security Considerations

### Browser Security

- Runs with `--no-sandbox` flag (required for Lambda)
- Isolated network environment
- No persistent browser state between invocations
- Automatic cleanup of browser processes

### Container Security

- Non-root user execution where possible
- Minimal system dependencies
- Regular base image updates
- Container image vulnerability scanning

## Monitoring and Observability

### Built-in Metrics

The template automatically collects:

- **Execution time** - Total function duration
- **Memory usage** - Peak memory consumption  
- **Browser metrics** - Page load times, network activity
- **Error tracking** - Structured error logging with stack traces

### CloudWatch Integration

Logs are automatically sent to CloudWatch Logs with structured JSON format:

```json
{
  "timestamp": "2025-09-04T12:00:00Z",
  "level": "INFO",
  "message": "Browser initialized in 2.34s",
  "request_id": "12345-abcde-67890",
  "function_name": "agentic-scraper",
  "memory_usage": "512MB"
}
```

### Custom Metrics

Add custom CloudWatch metrics:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')
cloudwatch.put_metric_data(
    Namespace='AgenticScraper',
    MetricData=[{
        'MetricName': 'ScrapingDuration',
        'Value': execution_time,
        'Unit': 'Seconds'
    }]
)
```

## Troubleshooting

### Common Issues

1. **Browser launch failures**
   ```bash
   # Check browser dependencies
   make health-check
   ```

2. **Memory issues**
   ```bash
   # Monitor memory usage
   docker stats agentic-scraper-lambda-dev
   ```

3. **Network timeouts**
   ```python
   # Increase page timeout
   await page.goto(url, timeout=60000)
   ```

4. **Display issues in headed mode**
   ```bash
   # Check X11 forwarding
   echo $DISPLAY
   xauth list
   ```

### Debug Commands

```bash
# Shell access to running container
make shell

# View browser processes
ps aux | grep chrome

# Check browser installation
python3 -c "from playwright.sync_api import sync_playwright; print(sync_playwright().chromium.executable_path)"

# Test network connectivity
curl -I https://example.com
```

## Extending the Template

### Adding New Browsers

```python
# In ScrapingPipeline.__aenter__()
self.firefox = await self.playwright.firefox.launch(headless=headless)
self.webkit = await self.playwright.webkit.launch(headless=headless)
```

### Custom Data Extraction

```python
async def extract_data(self, page: Page) -> Dict[str, Any]:
    # Custom extraction logic
    titles = await page.query_selector_all('h1')
    return {
        'titles': [await title.text_content() for title in titles]
    }
```

### Advanced Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def robust_scrape(url: str):
    # Retry logic for transient failures
    pass
```

## Cost Optimization

### ECR Storage

- Use multi-stage builds to minimize image size
- Implement image lifecycle policies for cleanup
- Share base layers across multiple functions

### Lambda Execution

- Right-size memory allocation based on actual usage
- Use provisioned concurrency for predictable workloads
- Consider Lambda layers for shared dependencies (if under 50MB)

### Monitoring Costs

```bash
# Get ECR repository size
aws ecr describe-repositories --repository-names agentic-scraper

# Monitor Lambda costs
aws ce get-cost-and-usage --time-period Start=2025-09-01,End=2025-09-04 \
  --granularity DAILY --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

---

For questions or issues, refer to [ADR-002](../docs/adr/ADR-002-docker-lambda-playwright.md) for the complete architectural decision record.