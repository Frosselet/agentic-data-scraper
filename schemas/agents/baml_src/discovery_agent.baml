enum DiscoveryPath {
  KNOWN_SOURCE
  ZERO_START
}

enum DataSourceType {
  API
  DATABASE
  FILE_SYSTEM
  WEB_SCRAPING
  STREAM
  CLOUD_STORAGE
}

enum UpdateFrequency {
  REAL_TIME
  HOURLY
  DAILY
  WEEKLY
  MONTHLY
  QUARTERLY
  YEARLY
  STATIC
}

class DataSourceMetadata {
  // Basic identification
  name string
  url string
  description string
  source_type DataSourceType

  // Technical metadata for Operations & Resources
  access_method string
  authentication_required bool
  authentication_method string?
  rate_limits map<string, string>?
  data_formats string[]

  // Data characteristics for Data & Governance
  schema_available bool
  schema_url string?
  sample_data_url string?
  data_volume_estimate string?
  update_frequency UpdateFrequency?
  historical_data_available bool
  historical_range string?

  // Quality indicators
  data_quality_score float?
  completeness_estimate float?
  accuracy_indicators string[]
  known_data_issues string[]

  // Governance metadata
  license_type string?
  terms_of_use_url string?
  privacy_considerations string[]
  compliance_standards string[]

  // Business context from Value & Users
  relevance_score float
  business_domains string[]
  use_cases string[]

  // Discovery metadata
  discovery_method string
  confidence_score float
}

class KnownSourceRequest {
  source_urls string[]
  expected_source_type DataSourceType?
  specific_datasets string[]?
  collection_depth string // "basic" | "detailed" | "comprehensive"
}

class ZeroStartDiscovery {
  // From Value & Users canvas
  business_domain string
  use_case_description string
  required_data_types string[]
  geographic_scope string?
  time_period_requirements string?

  // Discovery preferences
  max_sources_to_find int
  preferred_source_types DataSourceType[]?
  exclude_paid_sources bool
  require_api_access bool

  // Search strategy
  search_strategy string // "comprehensive" | "focused" | "quick"
  include_academic_sources bool
  include_government_sources bool
  include_commercial_sources bool
}

class DiscoveryResult {
  discovery_path DiscoveryPath
  discovered_sources DataSourceMetadata[]
  total_sources_found int
  search_queries_used string[]
  discovery_duration_seconds float

  // Recommendations for next workflow steps
  recommended_next_steps string[]
  prefilled_operations_data map<string, string>
  prefilled_governance_data map<string, string>
}

class WorkflowPrepopulation {
  operations_data map<string, string>
  governance_data map<string, string>
  review_data map<string, string>
}

// BAML Function for Known Source Discovery
function DiscoverKnownSources(request: KnownSourceRequest) -> DataSourceMetadata[] {
  client GPT4
  prompt #"
    You are an intelligent Data Source Discovery Agent specializing in metadata collection.

    MISSION: Analyze the provided known data sources and extract comprehensive metadata
    that will be used to prepopulate downstream workflow steps (Operations & Resources,
    Data & Governance, Review & Export).

    REQUEST DETAILS:
    Source URLs: {{ request.source_urls | join(", ") }}
    Expected Type: {{ request.expected_source_type | default("Unknown") }}
    Collection Depth: {{ request.collection_depth }}
    {% if request.specific_datasets %}
    Specific Datasets: {{ request.specific_datasets | join(", ") }}
    {% endif %}

    AGENTIC BEHAVIOR INSTRUCTIONS:
    1. INVESTIGATE each source URL systematically
    2. ANALYZE the source's technical capabilities and requirements
    3. ASSESS data quality indicators and governance aspects
    4. DETERMINE business relevance and use case alignment
    5. CALCULATE confidence scores based on available information

    For each source, you must provide:

    TECHNICAL ANALYSIS (for Operations & Resources):
    - Access method (REST API, GraphQL, file download, database connection, etc.)
    - Authentication requirements and methods
    - Rate limits and usage constraints
    - Available data formats
    - API documentation quality

    DATA CHARACTERISTICS (for Data & Governance):
    - Schema availability and structure
    - Data volume estimates
    - Update frequencies
    - Historical data coverage
    - Sample data accessibility

    QUALITY ASSESSMENT:
    - Completeness estimates (0.0-1.0)
    - Known accuracy indicators
    - Data quality issues or limitations
    - Reliability indicators

    GOVERNANCE EVALUATION:
    - License types and terms
    - Privacy considerations
    - Compliance standards (GDPR, CCPA, etc.)
    - Usage restrictions

    BUSINESS CONTEXT:
    - Relevance score (0.0-1.0) based on business alignment
    - Applicable business domains
    - Potential use cases
    - Value proposition

    BE THOROUGH and ANALYTICAL. Provide realistic assessments based on what you can
    determine about each source. If information is not available, indicate uncertainty
    but provide educated estimates where appropriate.
  "#
}

// BAML Function for Zero-Start Discovery
function DiscoverFromScratch(request: ZeroStartDiscovery) -> DiscoveryResult {
  client GPT4
  prompt #"
    You are an advanced Data Discovery Agent with internet research capabilities.

    MISSION: Find 3-5 high-quality data sources from scratch based on business requirements,
    then collect comprehensive metadata for downstream workflow integration.

    BUSINESS REQUIREMENTS:
    Domain: {{ request.business_domain }}
    Use Case: {{ request.use_case_description }}
    Required Data Types: {{ request.required_data_types | join(", ") }}
    {% if request.geographic_scope %}Geographic Scope: {{ request.geographic_scope }}{% endif %}
    {% if request.time_period_requirements %}Time Period: {{ request.time_period_requirements }}{% endif %}

    DISCOVERY CONSTRAINTS:
    Max Sources: {{ request.max_sources_to_find }}
    {% if request.preferred_source_types %}Preferred Types: {{ request.preferred_source_types | join(", ") }}{% endif %}
    Exclude Paid: {{ request.exclude_paid_sources }}
    Require API: {{ request.require_api_access }}
    Strategy: {{ request.search_strategy }}

    SOURCE INCLUSION CRITERIA:
    Academic Sources: {{ request.include_academic_sources }}
    Government Sources: {{ request.include_government_sources }}
    Commercial Sources: {{ request.include_commercial_sources }}

    AGENTIC DISCOVERY PROCESS:
    1. FORMULATE targeted search strategies based on business requirements
    2. RESEARCH multiple source categories (government, academic, commercial, NGO)
    3. EVALUATE source quality, reliability, and business fit
    4. RANK sources by relevance and data quality
    5. SELECT top 3-5 sources with diverse characteristics
    6. ANALYZE each selected source for comprehensive metadata

    SEARCH STRATEGY EXECUTION:
    - Generate 5-7 diverse search queries targeting different source types
    - Prioritize authoritative sources (government agencies, research institutions, established APIs)
    - Consider both direct data sources and aggregation platforms
    - Evaluate API availability, documentation quality, and access terms
    - Assess data freshness, coverage, and update frequencies

    For each discovered source, provide complete DataSourceMetadata including:
    - Technical specifications for integration planning
    - Data quality assessments for governance
    - Business relevance scoring
    - Compliance and licensing information
    - Confidence scores for decision making

    RECOMMENDATION ENGINE:
    Based on discovered sources, recommend next steps for:
    - Operations & Resources configuration
    - Data & Governance setup
    - Integration complexity assessment
    - Risk mitigation strategies

    Provide ACTIONABLE insights that directly support the subsequent workflow steps.
    Be STRATEGIC in source selection - prefer quality over quantity, and ensure
    sources complement each other to provide comprehensive data coverage.
  "#
}

// BAML Function for Intelligent Source Analysis
function AnalyzeSourceFitness(
  source_metadata: DataSourceMetadata,
  business_context: map<string, string>
) -> map<string, string> {
  client GPT4
  prompt #"
    You are a Data Source Fitness Analyzer with expertise in business-technical alignment.

    MISSION: Analyze how well this data source fits the business requirements and
    provide specific recommendations for integration into the data pipeline workflow.

    SOURCE METADATA:
    Name: {{ source_metadata.name }}
    Type: {{ source_metadata.source_type }}
    URL: {{ source_metadata.url }}
    Description: {{ source_metadata.description }}
    Access Method: {{ source_metadata.access_method }}
    Quality Score: {{ source_metadata.data_quality_score | default("Unknown") }}
    Update Frequency: {{ source_metadata.update_frequency | default("Unknown") }}

    BUSINESS CONTEXT:
    {% for key, value in business_context %}
    {{ key }}: {{ value }}
    {% endfor %}

    ANALYSIS DIMENSIONS:
    1. TECHNICAL FEASIBILITY
       - Integration complexity assessment
       - Authentication and access challenges
       - Data format compatibility
       - Scalability considerations

    2. DATA QUALITY FIT
       - Completeness alignment with requirements
       - Accuracy expectations vs. reality
       - Timeliness match with business needs
       - Coverage gaps identification

    3. GOVERNANCE ALIGNMENT
       - Compliance requirements satisfaction
       - Privacy considerations impact
       - License compatibility assessment
       - Risk factors evaluation

    4. BUSINESS VALUE POTENTIAL
       - Use case fulfillment capability
       - Strategic value contribution
       - Operational efficiency gains
       - Decision support enhancement

    Provide your analysis as a map with keys:
    - technical_fit_score (0.0-1.0)
    - quality_fit_score (0.0-1.0)
    - governance_fit_score (0.0-1.0)
    - business_value_score (0.0-1.0)
    - integration_complexity (Low|Medium|High)
    - key_risks (comma-separated)
    - recommended_actions (comma-separated)
    - workflow_prep_notes (for next steps)

    Be ANALYTICAL and provide SPECIFIC, ACTIONABLE insights.
  "#
}

// BAML Function for Workflow Prepopulation
function PrepareWorkflowData(
  discovered_sources: DataSourceMetadata[],
  canvas_data: map<string, string>
) -> WorkflowPrepopulation {
  client GPT4
  prompt #"
    You are a Workflow Integration Specialist preparing data for downstream pipeline steps.

    MISSION: Transform discovered source metadata into structured data that prepopulates
    the Operations & Resources, Data & Governance, and Review & Export workflow steps.

    DISCOVERED SOURCES:
    {% for source in discovered_sources %}
    {{ loop.index }}. {{ source.name }} ({{ source.source_type }})
       - URL: {{ source.url }}
       - Access: {{ source.access_method }}
       - Quality: {{ source.data_quality_score | default("TBD") }}
       - Business Relevance: {{ source.relevance_score }}
    {% endfor %}

    CANVAS DATA (Value & Users):
    {% for key, value in canvas_data %}
    {{ key }}: {{ value }}
    {% endfor %}

    PREPOPULATION REQUIREMENTS:

    OPERATIONS & RESOURCES DATA:
    Generate entries for:
    - data_extraction_methods: Technical approaches for each source
    - authentication_setup: Required auth configurations
    - data_transformation_needs: Format conversions and processing
    - infrastructure_requirements: Compute, storage, networking needs
    - monitoring_and_alerting: Operational monitoring setup
    - cost_estimates: Resource and licensing cost projections

    DATA & GOVERNANCE DATA:
    Generate entries for:
    - data_quality_rules: Validation and quality checks
    - privacy_impact_assessment: GDPR/CCPA considerations
    - data_lineage_tracking: Source-to-destination mapping
    - compliance_controls: Required governance measures
    - access_controls: Who can access what data
    - retention_policies: How long to keep data

    REVIEW & EXPORT DATA:
    Generate entries for:
    - integration_risk_assessment: Technical and business risks
    - implementation_timeline: Suggested project phases
    - success_metrics: KPIs for pipeline effectiveness
    - testing_strategy: Data validation and pipeline testing
    - deployment_recommendations: Production rollout approach
    - maintenance_requirements: Ongoing operational needs

    INTEGRATION PRINCIPLES:
    - Maintain consistency with Value & Users requirements
    - Prioritize sources by business value and technical feasibility
    - Identify dependencies between sources
    - Plan for incremental implementation
    - Consider scalability and future expansion

    Provide CONCRETE, ACTIONABLE data that workflow users can immediately
    apply without additional research or analysis.
  "#
}