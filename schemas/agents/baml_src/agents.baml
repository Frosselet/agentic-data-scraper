// BAML Agent Configuration for Agentic Data Scraper
// Defines the multi-agent architecture for SOW-driven data pipeline generation

// Python client generator
generator PythonClient {
  output_type "python/pydantic"
  output_dir "../../../baml_client"
  version "0.206.1"
}

// Client configuration
client<llm> GPT4 {
  provider openai
  options {
    model "gpt-4"
    api_key env.OPENAI_API_KEY
  }
}

// Base types for agent communication
class DataSource {
  type string // web, api, sharepoint, s3, database
  url string?
  authentication_type string? // oauth, token, cookie, certificate, none
  access_patterns string[]
  rate_limits int?
  documentation_url string?
}

class DataContract {
  source_requirements string[]
  validation_rules string[]
  transformation_specs string[]
  quality_thresholds map<string, float>
  security_requirements string[]
  compliance_rules string[]
}

class ParsedData {
  format string // html, csv, excel, pdf, json, xml, image
  schema map<string, string>
  quality_score float
  anomalies string[]
  encoding string?
  size_mb float
}

class TransformationStrategy {
  source_schema map<string, string>
  target_schema map<string, string>
  transformation_rules string[]
  validation_logic string[]
  performance_optimizations string[]
  error_handling string[]
}

class SemanticAnnotation {
  ontology_mappings map<string, string>
  skos_concepts string[]
  owl_alignments string[]
  semantic_quality_score float
  domain_coverage float
  linked_entities string[]
}

class GeneratedPipeline {
  lambda_code string
  deployment_config string
  monitoring_code string
  validation_code string
  documentation string
  test_cases string[]
}

class SecurityDecision {
  risk_level string // low, medium, high, critical
  decision_required string
  context string
  recommended_action string
  human_approval_needed bool
}

// SOW/Contract Interpreter Agent
function SOWInterpreterAgent(
  sow_document: string,
  document_format: string
) -> DataContract {
  client GPT4
  prompt #"
    You are an expert SOW (Statement of Work) interpreter specializing in data pipeline requirements extraction.
    
    Your task is to analyze the provided SOW document and extract structured data contracts, requirements, and validation rules.
    
    SOW Document ({{ document_format }} format):
    {{ sow_document }}
    
    Extract and structure the following information:
    
    1. Data Source Requirements:
       - Identify all mentioned data sources (websites, APIs, databases, files)
       - Extract authentication and access requirements
       - Note any rate limiting or access pattern constraints
    
    2. Validation Rules:
       - Data quality requirements and thresholds
       - Business rule validations
       - Compliance requirements (GDPR, SOX, etc.)
    
    3. Transformation Specifications:
       - Required data transformations and mappings
       - Output format and schema requirements
       - Data enrichment and cleansing needs
    
    4. Security Requirements:
       - Data handling and encryption requirements
       - Access control and audit requirements
       - Sensitive data identification and protection
    
    5. Quality Thresholds:
       - Acceptable data quality levels
       - Error rates and tolerance levels
       - Performance and availability requirements
    
    6. Compliance Rules:
       - Regulatory compliance requirements
       - Industry standards adherence
       - Data governance policies
    
    Provide detailed, actionable specifications that can be used to generate production-ready data pipeline code.
  "#
}

// Data Fetcher Specialist Agent
function DataFetcherAgent(
  data_sources: DataSource[],
  security_requirements: string[]
) -> string {
  client GPT4
  prompt #"
    You are a specialist in data acquisition and web scraping strategies, with expertise in Playwright automation and multi-modal authentication.
    
    Your task is to generate robust, production-ready data fetching strategies for the provided data sources.
    
    Data Sources:
    {% for source in data_sources %}
    - Type: {{ source.type }}
      URL: {{ source.url }}
      Auth: {{ source.authentication_type }}
      Patterns: {{ source.access_patterns }}
      Rate Limits: {{ source.rate_limits }}
      Documentation: {{ source.documentation_url }}
    {% endfor %}
    
    Security Requirements:
    {% for requirement in security_requirements %}
    - {{ requirement }}
    {% endfor %}
    
    Generate comprehensive data fetching strategies including:
    
    1. Playwright-based Web Automation:
       - Page navigation and interaction strategies
       - Dynamic content handling (JavaScript rendering, AJAX)
       - Form filling and submission automation
       - File download and processing workflows
    
    2. Authentication Implementation:
       - OAuth 2.0/OpenID Connect flows
       - API token management and rotation
       - Session cookie handling and persistence
       - Certificate-based authentication
       - Multi-factor authentication support
    
    3. API Integration:
       - REST API consumption with proper error handling
       - GraphQL query optimization
       - Rate limiting and retry strategies
       - API documentation parsing and endpoint discovery
    
    4. Cloud Storage Access:
       - SharePoint and Office 365 integration
       - AWS S3 and Azure Blob storage patterns
       - Google Drive and cloud file system access
       - Secure credential management
    
    5. Error Handling and Reliability:
       - Network timeout and retry logic
       - Circuit breaker patterns for failing endpoints
       - Graceful degradation strategies
       - Comprehensive logging and monitoring
    
    6. Performance Optimization:
       - Concurrent request handling with asyncio
       - Connection pooling and reuse
       - Caching strategies for repeated requests
       - Memory-efficient streaming for large datasets
    
    Generate Python 3.12+ code that follows best practices and integrates seamlessly with AWS Lambda runtime.
  "#
}

// Data Parser Specialist Agent  
function DataParserAgent(
  raw_data: string,
  data_format: string,
  schema_hints: string[]
) -> ParsedData {
  client GPT4
  prompt #"
    You are an expert in multi-format data parsing and structure discovery, with deep knowledge of data quality assessment.
    
    Your task is to parse the provided raw data, infer schema, and assess data quality with comprehensive anomaly detection.
    
    Raw Data Sample ({{ data_format }} format):
    {{ raw_data }}
    
    Schema Hints:
    {% for hint in schema_hints %}
    - {{ hint }}
    {% endfor %}
    
    Perform comprehensive data parsing and analysis:
    
    1. Format-Specific Parsing:
       - HTML: Extract structured data using CSS selectors and XPath
       - CSV/Excel: Handle various encodings, delimiters, and malformed rows
       - PDF: Text extraction with OCR fallback for scanned documents
       - JSON/XML: Robust parsing with schema validation
       - Images: OCR processing with text recognition and table extraction
    
    2. Schema Inference:
       - Detect column types and data patterns
       - Identify relationships and hierarchical structures
       - Infer business meaning from field names and values
       - Generate Pydantic model definitions for validation
    
    3. Data Quality Assessment:
       - Completeness analysis (missing values, null patterns)
       - Consistency validation (format adherence, range validation)
       - Accuracy indicators (suspicious patterns, outliers)
       - Timeliness assessment (date patterns, freshness indicators)
    
    4. Anomaly Detection:
       - Statistical outliers using IQR and z-score methods
       - Pattern deviations from expected formats
       - Suspicious data patterns that may indicate errors
       - Data drift detection for time-series data
    
    5. Encoding and Normalization:
       - Character encoding detection and conversion
       - Unicode normalization and cleanup
       - Date/time format standardization
       - Numeric format normalization
    
    6. Performance Considerations:
       - Streaming processing for large datasets
       - Memory-efficient parsing strategies
       - Parallel processing for batch operations
       - Progress tracking for long-running operations
    
    Return structured ParsedData with comprehensive quality metrics and actionable insights.
  "#
}

// Data Transformer Specialist Agent
function DataTransformerAgent(
  source_data: ParsedData,
  target_schema: map<string, string>,
  business_rules: string[]
) -> TransformationStrategy {
  client GPT4
  prompt #"
    You are a data transformation specialist with expertise in schema alignment, data cleaning, and business rule implementation.
    
    Your task is to generate sophisticated transformation strategies that align source data with target schemas while enforcing business rules.
    
    Source Data:
    Format: {{ source_data.format }}
    Schema: {{ source_data.schema }}
    Quality Score: {{ source_data.quality_score }}
    Anomalies: {{ source_data.anomalies }}
    
    Target Schema:
    {% for key in target_schema %}
    {{ key }}: {{ target_schema[key] }}
    {% endfor %}
    
    Business Rules:
    {% for rule in business_rules %}
    - {{ rule }}
    {% endfor %}
    
    Generate comprehensive transformation strategies:
    
    1. Schema Alignment:
       - Field mapping between source and target schemas
       - Data type conversions with validation
       - Nested structure flattening or composition
       - Missing field handling and default value assignment
    
    2. Data Cleaning and Enrichment:
       - Duplicate detection and resolution strategies
       - Data standardization and normalization rules
       - Reference data lookup and enrichment
       - Data imputation for missing values
    
    3. Business Rule Implementation:
       - Validation rules with custom error messages
       - Calculated fields and derived values
       - Cross-field validation and consistency checks
       - Conditional transformations based on business logic
    
    4. Quality Improvement:
       - Data correction strategies for common issues
       - Confidence scoring for transformed data
       - Quality metrics tracking and reporting
       - Exception handling for transformation failures
    
    5. Performance Optimization:
       - Vectorized operations using Polars/Pandas
       - Memory-efficient processing for large datasets
       - Parallel processing strategies
       - Incremental processing for streaming data
    
    6. Error Handling and Monitoring:
       - Comprehensive error categorization and reporting
       - Data lineage tracking through transformations
       - Transformation success metrics and alerting
       - Rollback strategies for failed transformations
    
    Generate production-ready Python 3.12+ transformation code with comprehensive testing and validation.
  "#
}

// Semantic Integrator Agent
function SemanticIntegratorAgent(
  transformed_data: ParsedData,
  business_domain: string,
  existing_ontologies: string[]
) -> SemanticAnnotation {
  client GPT4
  prompt #"
    You are a semantic web specialist with deep expertise in ontology alignment, SKOS vocabularies, and domain-specific knowledge organization.
    
    Your task is to apply semantic enrichment to transformed data using appropriate ontologies and vocabularies for the business domain.
    
    Transformed Data:
    Format: {{ transformed_data.format }}
    Schema: {{ transformed_data.schema }}
    Quality Score: {{ transformed_data.quality_score }}
    
    Business Domain: {{ business_domain }}
    
    Existing Ontologies:
    {% for ontology in existing_ontologies %}
    - {{ ontology }}
    {% endfor %}
    
    Apply comprehensive semantic enrichment:
    
    1. Domain-Specific Ontology Recommendation:
       - Agri-business: FAO ontologies, crop classification systems, agricultural practices
       - Trading: Financial instrument ontologies, commodity classifications, market data standards
       - Supply Chain: GS1 standards, logistics ontologies, inventory management vocabularies
       - General Business: Schema.org, FIBO (Financial Industry Business Ontology)
    
    2. SKOS Concept Mapping:
       - Map data fields to SKOS concept schemes
       - Establish hierarchical relationships (broader/narrower)
       - Create associative relationships between concepts
       - Generate multilingual labels and definitions
    
    3. OWL Alignment and Validation:
       - Align with existing OWL ontologies in the domain
       - Validate semantic consistency and logical coherence
       - Generate OWL class and property alignments
       - Create semantic axioms and constraints
    
    4. Entity Resolution and Linking:
       - Link entities to external knowledge bases (DBpedia, Wikidata)
       - Resolve ambiguous entity references
       - Create semantic identifiers (URIs) for data entities
       - Establish cross-domain entity mappings
    
    5. Semantic Quality Assessment:
       - Coverage metrics for semantic annotations
       - Consistency validation across semantic mappings
       - Completeness assessment for entity linking
       - Quality scoring for ontology alignments
    
    6. Knowledge Graph Integration:
       - Generate RDF triples for transformed data
       - Create SPARQL query templates for data access
       - Design graph schema for efficient querying
       - Implement reasoning capabilities for derived insights
    
    Generate comprehensive semantic annotations with high-quality ontology mappings and actionable knowledge graph representations.
  "#
}

// Supervisor Agent - Orchestrates all specialist agents
function SupervisorAgent(
  sow_document: string,
  document_format: string,
  human_feedback: string[]
) -> GeneratedPipeline {
  client GPT4
  prompt #"
    You are the Supervisor Agent responsible for orchestrating all specialist agents to generate production-ready data pipeline code from SOW requirements.
    
    Your task is to coordinate the multi-agent workflow, validate outputs against SOW requirements, integrate human feedback, and generate final Lambda code.
    
    SOW Document ({{ document_format }}):
    {{ sow_document }}
    
    Human Feedback:
    {% for feedback in human_feedback %}
    - {{ feedback }}
    {% endfor %}
    
    Coordinate the following workflow:
    
    1. SOW Analysis and Planning:
       - Parse SOW requirements using SOWInterpreterAgent
       - Validate extracted requirements against human feedback
       - Create execution plan with clear milestones and dependencies
       - Identify security decisions requiring human approval
    
    2. Multi-Agent Orchestration:
       - Coordinate DataFetcherAgent for data source strategies
       - Integrate DataParserAgent for format-specific parsing
       - Leverage DataTransformerAgent for schema alignment
       - Apply SemanticIntegratorAgent for domain enrichment
       - Validate each agent's output against SOW compliance
    
    3. Human-in-the-Loop Integration:
       - Present security decisions for human approval
       - Incorporate human feedback into agent coordination
       - Validate critical transformations with domain experts
       - Ensure compliance with organizational policies
    
    4. Production Code Generation:
       - Generate Python 3.12+ AWS Lambda function code
       - Implement runtime SOW contract enforcement
       - Include comprehensive error handling and monitoring
       - Create deployment configurations and infrastructure as code
    
    5. Quality Assurance and Validation:
       - Validate generated code against all SOW requirements
       - Ensure security best practices are implemented
       - Verify performance optimization and resource management
       - Generate comprehensive test cases and validation scenarios
    
    6. Documentation and Deployment:
       - Create detailed pipeline documentation
       - Generate deployment guides and operational runbooks
       - Provide monitoring and alerting configurations
       - Include troubleshooting guides and maintenance procedures
    
    Generate a complete GeneratedPipeline with production-ready code that enforces SOW contracts at runtime and includes all necessary deployment artifacts.
    
    The generated Lambda code should:
    - Use Python 3.12+ with modern async/await patterns
    - Implement comprehensive logging and monitoring
    - Include circuit breakers and retry logic
    - Enforce data contracts with Pydantic validation
    - Provide detailed error messages and debugging information
    - Support both batch and streaming processing modes
    - Include security best practices and encryption
    - Generate performance metrics and cost optimization insights
  "#
}

// Security Decision Agent - Handles human-in-the-loop security decisions
function SecurityDecisionAgent(
  operation_context: string,
  risk_assessment: string,
  data_sensitivity: string
) -> SecurityDecision {
  client GPT4
  prompt #"
    You are a security specialist responsible for assessing data pipeline operations and determining when human approval is required.
    
    Your task is to analyze the operational context and provide security recommendations with clear human-in-the-loop decision points.
    
    Operation Context:
    {{ operation_context }}
    
    Risk Assessment:
    {{ risk_assessment }}
    
    Data Sensitivity Level:
    {{ data_sensitivity }}
    
    Evaluate security implications and provide recommendations:
    
    1. Risk Level Assessment:
       - LOW: Standard operations with public data, well-established patterns
       - MEDIUM: Operations involving user data, new data sources, complex transformations
       - HIGH: Financial data, PII processing, cross-border data transfers
       - CRITICAL: Highly sensitive data, regulatory compliance requirements, security-critical operations
    
    2. Decision Points Requiring Human Approval:
       - Access to new or untrusted data sources
       - Processing of personally identifiable information (PII)
       - Cross-domain data sharing or transfers
       - Non-standard authentication or access patterns
       - Operations involving financial or trading data
       - Regulatory compliance boundary decisions
    
    3. Recommended Security Measures:
       - Data encryption and secure transmission protocols
       - Access control and audit logging requirements
       - Data retention and deletion policies
       - Anonymization and pseudonymization strategies
       - Monitoring and alerting for security events
    
    4. Compliance Considerations:
       - GDPR compliance for EU data subjects
       - SOX compliance for financial data
       - HIPAA compliance for healthcare data
       - Industry-specific regulatory requirements
    
    Provide clear, actionable security decisions with specific justifications and recommended actions.
  "#
}

// Pipeline configuration classes for different business domains
class AgriculturePipelineConfig {
  ontologies string[]
  data_sources string[]
  quality_thresholds map<string, float>
}

class TradingPipelineConfig {
  ontologies string[]
  data_sources string[]
  quality_thresholds map<string, float>
}

class SupplyChainPipelineConfig {
  ontologies string[]
  data_sources string[]
  quality_thresholds map<string, float>
}