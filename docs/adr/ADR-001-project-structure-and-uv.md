# ADR-001: Project Structure and Dependency Management with uv

**Status:** Proposed  
**Date:** 2025-09-04  
**Authors:** Development Team  
**Reviewers:** TBD  
**Implementation Branch:** `adr-001-project-structure-and-uv`

## Context

The Agentic Data Scraper project is a multi-agentic Python solution for building standardized data pipelines that generate AWS Lambda code. We need to establish a solid foundation for project structure and dependency management that supports:

- Multi-agent architecture with BAML agents
- Web scraping capabilities with Playwright
- Data processing with Polars/Pandas
- Schema validation with Pydantic
- Semantic web technologies (RDFLib, OWL)
- AWS Lambda deployment targeting S3 and Iceberg tables

Current challenges:
- No established project structure
- Need for modern Python dependency management
- Requirements for reproducible builds and deployments
- Support for multiple environments (development, testing, production)
- Integration with AWS Lambda packaging requirements

Key requirements:
- Fast, reliable dependency resolution
- Support for lock files and reproducible builds
- Easy virtual environment management
- Compatibility with AWS Lambda deployment
- Support for development tools and pre-commit hooks
- Clear separation of concerns between different components

## Decision

We will adopt **uv** as our primary Python package and project manager and establish a standardized project structure that supports multi-agentic architecture.

**Project Structure:**
```
agentic-data-scraper/
├── src/
│   ├── agentic_data_scraper/
│   │   ├── __init__.py
│   │   ├── agents/           # BAML agents and agent coordination
│   │   ├── core/            # Core business logic and interfaces
│   │   ├── scrapers/        # Playwright-based scrapers
│   │   ├── pipelines/       # Data pipeline definitions
│   │   ├── schemas/         # Pydantic models and validation
│   │   ├── semantic/        # RDFLib and OWL processing
│   │   ├── aws/            # AWS integration (Lambda, S3, Iceberg)
│   │   └── utils/          # Shared utilities
├── tests/                   # Test suite
├── docs/                   # Documentation including ADRs
├── scripts/                # Development and deployment scripts
├── lambda/                 # Lambda-specific packaging and entry points
├── examples/               # Usage examples and sample configurations
├── pyproject.toml          # uv project configuration
├── uv.lock                 # Locked dependencies
└── README.md
```

**Dependency Management:**
- Use uv for all package management operations
- Maintain pyproject.toml for project configuration
- Use uv.lock for reproducible dependency resolution
- Separate dependency groups for different use cases (dev, test, lambda)

**Rationale:**
- uv provides significantly faster dependency resolution compared to pip
- Built-in support for lock files ensures reproducible builds
- Excellent integration with modern Python packaging standards
- Simple virtual environment management
- Growing ecosystem adoption and active development
- Good compatibility with AWS Lambda deployment workflows

## Consequences

### Positive
- **Fast dependency resolution**: uv is 10-100x faster than pip for most operations
- **Reproducible builds**: Lock files ensure consistent environments across deployments
- **Modern tooling**: Built on latest Python packaging standards (PEP 621, PEP 660)
- **Simplified workflow**: Single tool for package management and virtual environments
- **Clear project structure**: Organized codebase that scales with project complexity
- **AWS Lambda ready**: Structure supports efficient Lambda packaging

### Negative
- **Learning curve**: Team needs to learn uv-specific commands and workflows
- **Ecosystem maturity**: uv is newer than pip/poetry, potential for undiscovered issues
- **CI/CD updates**: Need to update build pipelines to use uv
- **Documentation**: Less community documentation compared to established tools

### Neutral
- **Migration effort**: Need to set up new project structure and migrate any existing code
- **Tool standardization**: All developers must use uv for consistency
- **Project complexity**: More sophisticated structure may be overkill for small changes

## Implementation

### Acceptance Criteria
- [ ] Project directory structure is created according to specification
- [ ] pyproject.toml is configured with all necessary dependencies and metadata
- [ ] uv.lock file is generated and committed
- [ ] Virtual environment can be created and activated using uv
- [ ] All core dependencies are installable and importable
- [ ] Pre-commit hooks are configured and working
- [ ] CI/CD pipeline is updated to use uv
- [ ] Documentation is updated with setup instructions

### Implementation Steps
1. **Create project structure**
   - Create all directories according to the defined structure
   - Add __init__.py files to make packages importable
   - Set up basic module structure with placeholder files

2. **Configure pyproject.toml**
   - Define project metadata (name, version, description, authors)
   - Specify core dependencies for each component (BAML, Playwright, Polars, Pydantic, RDFLib)
   - Create dependency groups: dev, test, lambda, semantic
   - Configure build system and tool settings

3. **Initialize uv environment**
   - Run `uv init` to initialize the project
   - Install all dependencies with `uv sync`
   - Generate and commit uv.lock file

4. **Set up development tools**
   - Configure pre-commit hooks (black, isort, flake8, mypy)
   - Set up pytest configuration
   - Configure development scripts in pyproject.toml

5. **Create documentation**
   - Update README.md with setup and development instructions
   - Document the project structure and component responsibilities
   - Create contribution guidelines

6. **Update CI/CD**
   - Modify GitHub Actions or other CI/CD to use uv
   - Ensure builds are reproducible using uv.lock
   - Set up AWS Lambda deployment pipeline

### Migration Strategy
This is a new project, so no migration from existing dependency management is required. However:
- Any existing Python code should be moved into the new structure
- Existing requirements.txt files should be converted to pyproject.toml format
- Development workflows should be updated to use uv commands

## Monitoring and Success Metrics

- **Build time**: Measure dependency installation time in CI/CD (target: <2 minutes)
- **Developer experience**: Time from git clone to running tests (target: <5 minutes)
- **Reproducibility**: No dependency-related issues across different environments
- **Lambda package size**: Monitor deployment package size (target: <50MB uncompressed)
- **Dependency security**: Zero high-severity vulnerabilities in dependencies

Warning signs:
- Frequent dependency resolution conflicts
- Slow CI/CD builds due to dependency installation
- Developers unable to set up local environment easily
- AWS Lambda deployment failures due to package size or compatibility

## References

- [uv Documentation](https://docs.astral.sh/uv/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [AWS Lambda Python Packaging](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)
- [BAML Documentation](https://docs.boundaryml.com/)
- [Playwright Python Documentation](https://playwright.dev/python/)
- [Polars Documentation](https://pola-rs.github.io/polars/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [RDFLib Documentation](https://rdflib.readthedocs.io/)

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-09-04 | Development Team | Initial version |