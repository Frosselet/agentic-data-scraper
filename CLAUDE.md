# Claude Code Configuration

## Project: Agentic Data Scraper (Main Orchestrator)

### Project Overview
Multi-agentic Python solution for building standardized data pipelines that generate AWS Lambda-ready code based on SOW and data contracts.

**Architecture**: Modular Git submodule architecture with specialized repositories for separation of concerns.

### Submodule Architecture
```
agentic-data-scraper/                 # Main orchestrator
├── ontologies/                       # → agentic-semantic-ontologies
├── core/                            # → agentic-core-engine
├── agents/                          # → agentic-baml-agents
├── contracts/                       # → agentic-business-contracts
├── collectors/                      # → agentic-data-collectors
├── pipelines/                       # → agentic-data-pipelines
└── deployment/                      # → agentic-aws-deployment
```

### Cross-Repository Workflow
- Each submodule has its own specialized CLAUDE.md with focused context
- Main repository orchestrates integration and provides unified testing
- Follow dependency hierarchy: ontologies → core → agents/contracts/collectors → pipelines → deployment

### Development Process
- Follow ADR (Architecture Decision Records) methodology
- Each ADR implementation on dedicated git branch: `adr-{number}-{description}`
- Use sub-agents for specialized tasks and learning Claude Code capabilities

### Development Standards
**DO NOT choose the easy way to escape development challenges:**
- **DEBUG, REASON, AND SOLVE** - Do not cheat, simulate, or create dummy demos where real implementation is necessary
- **We provide MVPs, not PoCs** - Build working solutions, not proof-of-concepts
- **Demos only when imperatively asked for** - Focus on real functionality first
- **Fix the actual problem** - Don't create workarounds or "minimal" versions to avoid debugging
- **Complete the implementation** - Deliver fully functional features, not shortcuts

### Key Commands
```bash
# Environment management
uv sync                    # Install/update dependencies
uv run python -m pytest   # Run tests
uv run ruff check         # Lint code
uv run ruff format        # Format code
uv run mypy .            # Type checking

# Submodule management
git submodule update --init --recursive  # Initialize all submodules
git submodule foreach 'git pull origin master'  # Update all submodules

# Development workflow
git checkout -b adr-001-project-structure  # Create ADR branch
git checkout main && git merge adr-001-project-structure  # Merge after review

# Cross-repository testing
./scripts/test-all-submodules.sh  # Run tests across all repositories
./scripts/validate-integration.sh  # Validate submodule integration
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

### BAML Prompt Engineering Guidelines
**CRITICAL: BAML uses strongly typed signatures - abandon traditional prompt engineering techniques**

**DO NOT use old prompt techniques:**
- ❌ "Return ONLY JSON object, no additional text"
- ❌ "Provide structured output format"
- ❌ "Follow this exact schema"
- ❌ Manual JSON formatting instructions

**DO use BAML's typed approach:**
- ✅ Define BAML classes for return types (strongly typed signatures)
- ✅ Let BAML handle parsing and validation automatically
- ✅ Focus on natural language instructions for business logic
- ✅ Trust BAML's type system to enforce structure
- ✅ Write prompts that describe WHAT to extract, not HOW to format

**BAML Philosophy:**
BAML's power comes from strongly typed class signatures that automatically parse LLM responses into structured data. The prompt should focus on domain expertise and business logic, while BAML handles the structural parsing without failure.

### Security Constraints
- Human-in-the-loop for sensitive operations during development
- No credential harvesting or malicious code generation
- Defensive security focus only

### Output Target
- Generated Python code for AWS Lambda
- SOW and data contract enforcement at runtime
- Support for S3 flat files and Iceberg tables

