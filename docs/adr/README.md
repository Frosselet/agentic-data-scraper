# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records (ADRs) for the Agentic Data Scraper project. ADRs document important architectural decisions made during the development of this multi-agentic Python solution for building standardized data pipelines that generate AWS Lambda code.

## What are Architecture Decision Records?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences. ADRs help teams:

- Document the reasoning behind architectural decisions
- Maintain a historical record of decision-making processes
- Onboard new team members by providing context
- Review and potentially reverse decisions when circumstances change

## ADR Process

### When to Create an ADR

Create an ADR for decisions that:
- Affect the structure, non-functional characteristics, dependencies, interfaces, or construction techniques of the system
- Are expensive to change (e.g., choice of programming language, database, framework)
- Impact multiple teams or components
- Have significant trade-offs or are controversial
- Set precedents for future decisions

### ADR Lifecycle

1. **Proposed** - Initial draft of the ADR for discussion
2. **Accepted** - Decision has been made and approved
3. **Deprecated** - Decision is no longer relevant but kept for historical context
4. **Superseded** - Replaced by a newer ADR (reference the superseding ADR)

### Naming Convention

ADRs are numbered sequentially and follow this naming pattern:
- File: `ADR-{number:03d}-{short-description}.md`
- Branch: `adr-{number}-{description}` (for implementation)

Examples:
- `ADR-001-project-structure-and-uv.md`
- `ADR-002-baml-agent-architecture.md`
- `ADR-003-data-pipeline-orchestration.md`

## ADR Template

Use the template file `adr-template.md` as a starting point for new ADRs. The template includes all required sections and guidance for completion.

## Current ADRs

| Number | Title | Status | Date |
|--------|--------|--------|------|
| [001](./ADR-001-project-structure-and-uv.md) | Project Structure and Dependency Management with uv | Proposed | 2025-09-04 |
| [002](./ADR-002-docker-lambda-playwright.md) | Docker-based AWS Lambda with Playwright and Python 3.12+ | Accepted | 2025-09-04 |
| [003](./ADR-003-baml-agent-architecture.md) | BAML Multi-Agent Architecture for Pipeline Generation | Proposed | 2025-09-04 |

## Implementation Process

1. **Create ADR**: Copy the template and fill in the details
2. **Review & Discussion**: Share with team for feedback
3. **Implementation Branch**: Create branch following `adr-{number}-{description}` pattern
4. **Implementation**: Implement the decision in the branch
5. **Merge**: Merge implementation and update ADR status to "Accepted"

## Technology Context

This project is a multi-agentic Python solution with the following key technologies:
- **BAML Agents**: For intelligent data processing and decision making
- **Playwright**: For web scraping and browser automation
- **Polars/Pandas**: For data manipulation and analysis
- **Pydantic**: For data validation and schema definition
- **Semantic Web**: RDFLib and OWL for knowledge representation
- **AWS**: Target deployment on Lambda with S3 and Iceberg tables
- **uv**: Modern Python package and project management

## Contributing to ADRs

1. Follow the established template and naming conventions
2. Be concise but thorough in documenting context and rationale
3. Include clear implementation steps and acceptance criteria
4. Reference related ADRs and external resources
5. Update the ADR index table in this README when adding new ADRs

## Resources

- [ADR GitHub Organization](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [Architecture Decision Records in Action](https://www.thoughtworks.com/insights/articles/architecture-decision-records-in-action)