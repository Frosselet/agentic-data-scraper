# ADR-003: BAML Agent Architecture for Multi-Agentic Data Pipeline Generation

**Status:** Proposed  
**Date:** 2025-09-04  
**Authors:** François Rosselet, Claude (Anthropic)
**Reviewers:** TBD  
**Implementation Branch:** `adr-003-baml-agent-architecture`

## Context

The Agentic Data Scraper project requires a sophisticated multi-agent system to generate production-ready data pipelines from Statement of Work (SOW) documents. The system must orchestrate multiple specialist agents to interpret requirements, discover data sources, parse various formats, transform data, apply semantic enrichment, and generate AWS Lambda code that enforces SOW contracts at runtime.

**Current Challenges:**
- Complex SOW documents require intelligent parsing and requirement extraction
- Diverse data sources (web, APIs, SharePoint, S3) need specialized handling strategies
- Multiple data formats (HTML, CSV, Excel, PDF, images) require different parsing approaches
- Data transformation logic must align with business requirements and semantic standards
- Generated code must enforce SOW contracts and validation rules at runtime
- Human-in-the-loop security decisions must be integrated into the workflow
- Coordination between multiple specialized agents requires robust orchestration

**Key Requirements:**
- SOW document interpretation with structured requirement extraction
- Adaptive web scraping and API discovery strategies
- Multi-format data parsing with quality assessment
- Intelligent data transformation and schema alignment
- Semantic enrichment with domain-specific ontologies (agri-business, trading)
- Production-ready Python 3.12+ Lambda code generation
- Runtime SOW contract enforcement and validation
- Security-first approach with human oversight for sensitive operations
- Comprehensive agent coordination and workflow management

**Technical Context:**
- Building on established Docker Lambda architecture (ADR-002)
- Leveraging uv-based project structure (ADR-001)
- Integration with BAML for agent definition and coordination
- Python 3.12+ runtime with modern async patterns
- Playwright for web automation and data extraction
- Pydantic for schema validation and data contracts
- RDFLib and OWL for semantic processing
- AWS Lambda deployment with S3 and Iceberg table outputs

## Decision

We will implement a **BAML-based multi-agent architecture** with six specialized agents coordinated by a Supervisor Agent, designed to generate production-ready data pipelines that enforce SOW contracts at runtime.

**Core Agent Architecture:**

### 1. SOW/Contract Interpreter Agent
**Purpose:** Parse and interpret Statement of Work documents to extract structured requirements.
- **Inputs:** SOW documents (PDF, Word, text), contract specifications
- **Outputs:** Structured data contracts, requirement specifications, validation rules
- **Capabilities:**
  - Document parsing across multiple formats (PDF, DOCX, TXT)
  - Natural language processing for requirement extraction
  - Data source identification and classification
  - Transformation rule inference from business requirements
  - Contract validation rule generation
  - Risk assessment for data handling requirements

### 2. Data Fetcher Specialist Agent
**Purpose:** Implement sophisticated data acquisition strategies across diverse sources.
- **Inputs:** Data source specifications, authentication requirements, access patterns
- **Outputs:** Data extraction strategies, authentication configurations, scraping scripts
- **Capabilities:**
  - Playwright-based web navigation and automation
  - Multi-modal authentication (OAuth, tokens, session cookies, certificates)
  - API discovery and OpenAPI specification parsing
  - SharePoint and Office 365 integration patterns
  - S3 and cloud storage access optimization
  - Rate limiting and respectful scraping strategies
  - Error handling and retry logic generation

### 3. Data Parser Specialist Agent
**Purpose:** Parse and structure data from diverse formats with quality assessment.
- **Inputs:** Raw data files, format specifications, schema hints
- **Outputs:** Parsed data structures, quality metrics, anomaly reports
- **Capabilities:**
  - Multi-format parsing (HTML, CSV, Excel, PDF, JSON, XML)
  - OCR processing for image and scanned document extraction
  - Intelligent schema inference and data structure discovery
  - Data quality assessment and anomaly detection
  - Format-specific optimization strategies
  - Encoding detection and normalization
  - Streaming processing for large datasets

### 4. Data Transformer Specialist Agent
**Purpose:** Generate sophisticated data transformation and cleaning logic.
- **Inputs:** Source schemas, target schemas, business rules, data samples
- **Outputs:** Transformation code, validation rules, data cleaning strategies
- **Capabilities:**
  - Schema alignment and mapping generation
  - Data type conversion and normalization strategies
  - Business rule implementation and validation
  - Data enrichment and augmentation logic
  - Deduplication and merge conflict resolution
  - Performance-optimized transformation code generation
  - Error handling and data quality reporting

### 5. Semantic Integrator Agent
**Purpose:** Apply domain-specific semantic enrichment and ontology alignment.
- **Inputs:** Parsed data, business domain context, existing ontologies
- **Outputs:** Semantic annotations, ontology mappings, SKOS alignments
- **Capabilities:**
  - Domain-specific ontology recommendation (agri-business, trading, supply chain)
  - SKOS (Simple Knowledge Organization System) concept mapping
  - OWL (Web Ontology Language) alignment and validation
  - Semantic data validation and quality metrics
  - Knowledge graph integration strategies
  - Linked data publication recommendations
  - Cross-domain entity resolution and linking

### 6. Supervisor Agent
**Purpose:** Orchestrate all specialist agents and generate final production code.
- **Inputs:** SOW requirements, agent outputs, human feedback, security decisions
- **Outputs:** Production-ready Python Lambda code, deployment configurations
- **Capabilities:**
  - Multi-agent coordination and workflow orchestration
  - SOW compliance validation across all pipeline stages
  - Human-in-the-loop security decision integration
  - Production code generation with runtime contract enforcement
  - Error handling and monitoring code injection
  - Performance optimization and resource management
  - Deployment configuration and infrastructure as code generation

**BAML Integration Strategy:**
- Define agents using BAML's structured prompt and function calling capabilities
- Implement agent coordination patterns with BAML's workflow management
- Leverage BAML's type safety for agent input/output validation
- Use BAML's debugging and observability features for agent monitoring
- Integrate BAML's human-in-the-loop capabilities for security decisions

**Generated Code Architecture:**
- Python 3.12+ Lambda functions with async/await patterns
- Runtime SOW contract validation using Pydantic models
- Comprehensive error handling and logging
- Performance monitoring and metrics collection
- Configurable retry and circuit breaker patterns
- Security-first data handling with encryption and audit trails

## Consequences

### Positive
- **Intelligent automation**: Multi-agent system handles complex requirement interpretation
- **Specialized expertise**: Each agent focuses on specific domain knowledge and capabilities
- **SOW compliance**: Generated code enforces contracts and validation rules at runtime
- **Production readiness**: Output includes comprehensive error handling, monitoring, and security
- **Semantic enrichment**: Domain-specific ontologies improve data quality and interoperability
- **Human oversight**: Security decisions involve human judgment while automating routine tasks
- **Scalable architecture**: Agent-based design scales with complexity and new requirements
- **Type safety**: BAML provides structured validation for agent interactions
- **Observability**: Built-in debugging and monitoring for complex agent workflows
- **Maintainable code**: Generated code follows modern Python patterns and best practices

### Negative
- **Architectural complexity**: Six agents with coordination adds significant system complexity
- **Development overhead**: BAML learning curve and agent development requires specialized skills
- **Debugging challenges**: Multi-agent interactions can be difficult to debug and troubleshoot
- **Performance considerations**: Agent coordination may introduce latency in code generation
- **Resource requirements**: Multiple specialized agents require more computational resources
- **Integration complexity**: Coordinating diverse technologies (BAML, Playwright, RDFLib) is challenging
- **Testing complexity**: Comprehensive testing of agent interactions and workflows
- **Dependency management**: Multiple agent-specific dependencies increase maintenance burden

### Neutral
- **Technology adoption**: Team must learn BAML and multi-agent development patterns
- **Workflow changes**: Development process shifts from direct coding to agent orchestration
- **Monitoring requirements**: Need comprehensive observability for agent performance and outputs
- **Security model**: Human-in-the-loop decisions require clear processes and documentation
- **Documentation needs**: Complex architecture requires extensive documentation and examples

## Implementation

### Acceptance Criteria
- [ ] BAML agent definitions for all six specialist agents
- [ ] Supervisor agent with complete orchestration logic
- [ ] Python interface definitions for agent integration
- [ ] SOW parsing and requirement extraction functionality
- [ ] Multi-format data parsing and quality assessment
- [ ] Semantic enrichment with domain-specific ontologies
- [ ] Production code generation with runtime contract enforcement
- [ ] Human-in-the-loop security decision integration
- [ ] Comprehensive error handling and monitoring code generation
- [ ] Agent coordination testing and validation
- [ ] Performance benchmarking for agent workflows
- [ ] Documentation and usage examples

### Implementation Steps

1. **Create BAML Agent Framework**
   - Set up BAML project structure and configuration
   - Define base agent interfaces and common types
   - Implement agent coordination patterns and workflow management
   - Create debugging and observability infrastructure
   - Set up agent testing and validation frameworks

2. **Implement SOW/Contract Interpreter Agent**
   - Multi-format document parsing (PDF, DOCX, TXT)
   - Natural language processing for requirement extraction
   - Structured data contract generation
   - Validation rule inference and generation
   - Risk assessment and security requirement identification

3. **Develop Data Fetcher Specialist Agent**
   - Playwright-based web scraping strategy generation
   - Authentication handling for multiple protocols
   - API discovery and documentation parsing
   - SharePoint and cloud storage integration
   - Rate limiting and ethical scraping code generation

4. **Build Data Parser Specialist Agent**
   - Multi-format parsing implementation (HTML, CSV, Excel, PDF, images)
   - OCR integration for image and document processing
   - Schema inference and data structure discovery
   - Quality assessment and anomaly detection algorithms
   - Streaming processing for large dataset handling

5. **Create Data Transformer Specialist Agent**
   - Schema alignment and transformation logic generation
   - Data cleaning and validation strategy implementation
   - Business rule encoding and enforcement
   - Performance optimization for large-scale transformations
   - Error handling and quality reporting integration

6. **Implement Semantic Integrator Agent**
   - Domain-specific ontology recommendation system
   - SKOS and OWL alignment and validation
   - Semantic quality metrics and validation
   - Knowledge graph integration strategies
   - Cross-domain entity resolution and linking

7. **Develop Supervisor Agent**
   - Multi-agent orchestration and coordination logic
   - SOW compliance validation across all pipeline stages
   - Human-in-the-loop security decision integration
   - Production code generation with runtime enforcement
   - Monitoring and error handling code injection

8. **Integration and Testing**
   - End-to-end workflow testing with real SOW documents
   - Performance benchmarking and optimization
   - Security testing and validation
   - Generated code quality assessment
   - Agent coordination reliability testing

### Migration Strategy

**New Architecture Implementation:**
- Build new BAML-based agents alongside existing architecture
- Gradual migration of functionality to specialized agents
- Maintain backwards compatibility during transition period
- Feature flags to control agent activation and workflow routing

**Existing Code Integration:**
- Wrap existing parsing and scraping logic as agent capabilities
- Migrate validation rules to runtime contract enforcement
- Convert manual processes to agent-automated workflows
- Preserve existing data pipeline outputs and formats

**Deployment Strategy:**
- Staged rollout starting with simple SOW documents
- A/B testing between agent-generated and manually-created pipelines
- Comprehensive monitoring and rollback capabilities
- Performance comparison and optimization based on real-world usage

## Monitoring and Success Metrics

**Agent Performance Metrics:**
- SOW parsing accuracy and requirement extraction completeness (target: >95%)
- Data source discovery success rate across different websites and APIs (target: >90%)
- Data parsing accuracy across different formats and quality levels (target: >98%)
- Transformation logic correctness and data quality improvement (target: measurable improvement)
- Semantic enrichment coverage and ontology alignment quality (target: >85% coverage)
- Generated code quality and production readiness (target: 0 critical issues)

**System Performance Metrics:**
- End-to-end pipeline generation time (target: <30 minutes for complex SOWs)
- Agent coordination and workflow reliability (target: >99% success rate)
- Human-in-the-loop decision turnaround time (target: <4 hours)
- Generated Lambda function performance and cost efficiency
- Runtime contract enforcement overhead (target: <5% performance impact)

**Business Value Metrics:**
- Reduction in manual pipeline development time (target: >80% reduction)
- Improvement in data pipeline quality and reliability
- Reduction in SOW interpretation errors and rework
- Increase in semantic data interoperability and reusability
- Cost savings from automated pipeline generation and maintenance

**Warning Signs:**
- Agent coordination failures or deadlocks
- Generated code with security vulnerabilities or performance issues
- SOW interpretation accuracy declining over time
- Human security decisions becoming bottlenecks
- Semantic enrichment quality degrading with new domains
- Runtime contract enforcement causing production failures

## References

- [BAML Documentation](https://docs.boundaryml.com/)
- [Multi-Agent Systems: A Modern Approach](https://mitpress.mit.edu/books/multiagent-systems)
- [Playwright Automation Documentation](https://playwright.dev/docs/)
- [Pydantic Data Validation](https://docs.pydantic.dev/)
- [RDFLib Semantic Web Processing](https://rdflib.readthedocs.io/)
- [OWL Web Ontology Language Guide](https://www.w3.org/TR/owl-guide/)
- [SKOS Simple Knowledge Organization System](https://www.w3.org/2004/02/skos/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Python 3.12+ Performance Improvements](https://docs.python.org/3/whatsnew/3.12.html)
- [Human-in-the-Loop Machine Learning](https://www.manning.com/books/human-in-the-loop-machine-learning)
- [Semantic Web Technologies for Enterprises](https://link.springer.com/book/10.1007/978-3-642-04581-3)
- [ADR-001: Project Structure and uv](./ADR-001-project-structure-and-uv.md)
- [ADR-002: Docker Lambda Playwright](./ADR-002-docker-lambda-playwright.md)

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-09-04 | Development Team | Initial version |