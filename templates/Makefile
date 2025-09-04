# Makefile for Agentic Data Scraper Lambda with Playwright
# Optimized for Python 3.12+ and Docker deployment

.PHONY: help build build-prod test test-local clean deploy health-check logs

# Default target
help:
	@echo "Agentic Data Scraper Lambda - Docker Build Commands"
	@echo ""
	@echo "Development Commands:"
	@echo "  build          - Build development Docker image"
	@echo "  build-prod     - Build production-optimized Docker image"
	@echo "  test           - Run tests in Docker container"
	@echo "  test-local     - Test Lambda function locally"
	@echo "  dev            - Start development environment"
	@echo "  debug          - Start with headed browser debugging"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  deploy         - Deploy to AWS Lambda (requires AWS CLI)"
	@echo "  push           - Push image to ECR"
	@echo ""
	@echo "Utility Commands:"
	@echo "  health-check   - Run health check on running container"
	@echo "  logs           - Show container logs"
	@echo "  clean          - Clean up Docker images and containers"
	@echo "  shell          - Open shell in running container"

# Build development image
build:
	@echo "Building development Docker image with Python 3.12+ and Playwright..."
	docker build -f Dockerfile.lambda-base -t agentic-scraper:dev .

# Build production-optimized image
build-prod:
	@echo "Building production Docker image..."
	docker build -f Dockerfile.lambda-base -t agentic-scraper:prod --target runtime .

# Run tests in container
test:
	@echo "Running tests in Docker container..."
	docker run --rm \
		-v $(PWD):/var/task:ro \
		-e PYTHONPATH=/var/task \
		agentic-scraper:dev \
		python3 -m pytest tests/ -v

# Test Lambda function locally using RIE
test-local:
	@echo "Testing Lambda function locally..."
	docker run --rm -p 9000:8080 \
		-e PLAYWRIGHT_HEADED=false \
		agentic-scraper:dev &
	sleep 5
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
		-d '{"url": "https://example.com", "config": {"headless": true}}'
	docker stop $$(docker ps -q --filter ancestor=agentic-scraper:dev)

# Start development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d lambda-dev
	@echo "Lambda RIE available at http://localhost:9000"
	@echo "Use 'make logs' to view logs"

# Start with debugging support (headed browser)
debug:
	@echo "Starting debug environment with headed browser support..."
	PLAYWRIGHT_HEADED=true docker-compose --profile debug up -d
	@echo "VNC interface available at http://localhost:5800 (password: playwright)"
	@echo "Lambda RIE available at http://localhost:9000"

# Deploy to AWS Lambda
deploy:
	@echo "Deploying to AWS Lambda..."
	@if [ -z "$(AWS_ACCOUNT_ID)" ]; then \
		echo "Error: AWS_ACCOUNT_ID environment variable not set"; \
		exit 1; \
	fi
	@if [ -z "$(AWS_REGION)" ]; then \
		echo "Error: AWS_REGION environment variable not set"; \
		exit 1; \
	fi
	$(MAKE) build-prod
	docker tag agentic-scraper:prod $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/agentic-scraper:latest
	$(MAKE) push
	aws lambda update-function-code \
		--function-name agentic-scraper \
		--image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/agentic-scraper:latest

# Push image to ECR
push:
	@echo "Pushing image to ECR..."
	@if [ -z "$(AWS_ACCOUNT_ID)" ]; then \
		echo "Error: AWS_ACCOUNT_ID environment variable not set"; \
		exit 1; \
	fi
	@if [ -z "$(AWS_REGION)" ]; then \
		echo "Error: AWS_REGION environment variable not set"; \
		exit 1; \
	fi
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/agentic-scraper:latest

# Health check
health-check:
	@echo "Running health check..."
	docker exec $$(docker ps -q --filter name=agentic-scraper-lambda-dev) \
		python3 /var/task/healthcheck.py

# View logs
logs:
	@echo "Showing container logs..."
	docker-compose logs -f lambda-dev

# Open shell in running container
shell:
	@echo "Opening shell in container..."
	docker exec -it $$(docker ps -q --filter name=agentic-scraper-lambda-dev) /bin/bash

# Clean up
clean:
	@echo "Cleaning up Docker images and containers..."
	docker-compose down -v
	docker system prune -f
	docker image prune -f
	docker volume prune -f

# Performance benchmark
benchmark:
	@echo "Running performance benchmark..."
	docker run --rm \
		-v $(PWD):/var/task:ro \
		agentic-scraper:dev \
		python3 -c "
import asyncio
import time
from lambda_function import scrape_data

async def benchmark():
    urls = ['https://example.com', 'https://httpbin.org/html', 'https://httpbin.org/json']
    start_time = time.time()
    
    tasks = [scrape_data(url, {}) for url in urls]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    print(f'Processed {len(urls)} URLs in {total_time:.2f}s')
    print(f'Average time per URL: {total_time/len(urls):.2f}s')
    
    for i, result in enumerate(results):
        status = 'SUCCESS' if result['success'] else 'FAILED'
        exec_time = result.get('metadata', {}).get('execution_time', 0)
        print(f'URL {i+1}: {status} ({exec_time:.2f}s)')

asyncio.run(benchmark())
"

# CI/CD helpers
ci-test:
	$(MAKE) build
	$(MAKE) test
	$(MAKE) health-check

ci-deploy:
	$(MAKE) build-prod
	$(MAKE) push
	$(MAKE) deploy