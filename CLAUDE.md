# Claude Code Configuration

## Project: Agentic Data Scraper

### Project Overview
Multi-agentic Python solution for building standardized data pipelines that generate AWS Lambda-ready code based on SOW and data contracts.

### Development Process
- Follow ADR (Architecture Decision Records) methodology
- Each ADR implementation on dedicated git branch: `adr-{number}-{description}`
- Use sub-agents for specialized tasks and learning Claude Code capabilities

### Key Commands
```bash
# Environment management
uv sync                    # Install/update dependencies
uv run python -m pytest   # Run tests
uv run ruff check         # Lint code
uv run ruff format        # Format code
uv run mypy .            # Type checking

# Development workflow
git checkout -b adr-001-project-structure  # Create ADR branch
git checkout main && git merge adr-001-project-structure  # Merge after review
```

### Technology Stack
- **Python**: 3.12+ (modern async/await, performance improvements)
- **Environment**: uv for dependency management
- **AI Framework**: BAML (Boundary ML) for agents
- **Web Scraping**: Playwright for dynamic websites
- **Data Processing**: Polars/Pandas for efficiency
- **Schemas**: Pydantic with JSON Schema validation
- **Semantic Web**: RDFLib, OWLReady2 for ontologies
- **Target**: AWS Lambda functions (Docker images for full Playwright support)
- **CLI**: Typer/Click for code generation interface

### Agent Specializations
1. **SOW/Contract Interpreter**: Parse and validate SOW documents
2. **Data Fetcher**: Web navigation, APIs, authentication
3. **Data Parser**: Multiple format support (HTML, PDF, Excel, etc.)
4. **Data Transformer**: Schema alignment and transformation
5. **Semantic Integrator**: Ontology mapping and SKOS alignment
6. **Supervisor**: Coordination and verification

### Security Constraints
- Human-in-the-loop for sensitive operations during development
- No credential harvesting or malicious code generation
- Defensive security focus only

### Output Target
- Generated Python code for AWS Lambda
- SOW and data contract enforcement at runtime
- Support for S3 flat files and Iceberg tables