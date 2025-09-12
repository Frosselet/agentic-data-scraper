// BAML Agent Configuration for Source Discovery Assistant
// Defines agents for business-question-first data source discovery
// Uses GPT4 client defined in agents.baml

// Types for discovery workflow
class BusinessContext {
  question string
  success_criteria string
  timeline string
  budget string
  risk_tolerance string // low, medium, high
  persona_id string
  interaction_level string // executive, standard, technical, rapid
}

class DataSourceRecommendation {
  name string
  type string // api, web, database, file, stream
  description string
  feasibility_score float // 0.0 to 1.0
  cost_estimate string
  implementation_effort string // low, medium, high, very_high
  platform_compatibility float // 0.0 to 1.0 - how well it fits our platform
  data_quality_expected float // 0.0 to 1.0
  access_requirements string[]
  sample_data_url string?
  documentation_url string?
  pros string[]
  cons string[]
  semantic_vocabularies string[] // SKOS/OWL vocabularies this source aligns with
}

class FeasibilityAnalysis {
  overall_feasibility string // very_high, high, medium, low, very_low
  technical_risks string[]
  business_risks string[]
  mitigation_strategies string[]
  platform_gaps string[]
  recommended_alternatives string[]
  estimated_timeline_weeks int
  confidence_level float // 0.0 to 1.0
}

class SOWContract {
  project_title string
  executive_summary string
  business_objectives string[]
  success_metrics string[]
  data_sources DataSourceRecommendation[]
  technical_approach string
  deliverables string[]
  timeline_weeks int
  cost_estimate string
  risk_assessment string
  acceptance_criteria string[]
  semantic_framework string // Description of SKOS/OWL approach
}

// Business Context Interpreter Agent
function BusinessContextAgent(
  business_question: string,
  success_criteria: string,
  timeline: string,
  budget: string,
  risk_tolerance: string,
  persona_id: string
) -> BusinessContext {
  client GPT4
  prompt #"
    You are a business context interpreter specializing in translating business questions into structured data requirements.
    
    Your task is to analyze and structure the business context for optimal data source discovery.
    
    Business Question: {{ business_question }}
    Success Criteria: {{ success_criteria }}
    Timeline: {{ timeline }}
    Budget: {{ budget }}
    Risk Tolerance: {{ risk_tolerance }}
    Persona: {{ persona_id }}
    
    Analyze and structure this business context:
    
    1. Question Analysis:
       - Identify the core business problem to solve
       - Extract key entities, relationships, and metrics needed
       - Determine data freshness and update frequency requirements
       - Identify stakeholders who will use the insights
    
    2. Success Criteria Validation:
       - Ensure criteria are measurable and specific
       - Identify data points needed to track success
       - Suggest additional metrics if current criteria are incomplete
       - Note any unrealistic expectations given the timeline/budget
    
    3. Timeline Feasibility:
       - Assess if timeline is realistic for the complexity
       - Identify critical path dependencies
       - Suggest phased approach if needed
       - Note any time-sensitive data requirements
    
    4. Budget Alignment:
       - Evaluate if budget matches complexity and timeline
       - Identify potential cost optimization opportunities
       - Note any premium data sources that may be needed
       - Suggest trade-offs between cost and data quality
    
    5. Risk Assessment:
       - Evaluate data availability risks
       - Assess technical integration complexity
       - Identify regulatory or compliance considerations
       - Note any single points of failure
    
    Return a structured BusinessContext that optimizes for the persona's preferences and interaction style.
  "#
}

// Source Discovery Agent
function SourceDiscoveryAgent(
  business_context: BusinessContext,
  platform_capabilities: string[]
) -> DataSourceRecommendation[] {
  client GPT4
  prompt #"
    You are a data source discovery specialist with deep knowledge of our platform capabilities and 5,000+ available data sources.
    
    Your task is to recommend optimal data sources that align with business needs and platform strengths.
    
    Business Context:
    Question: {{ business_context.question }}
    Success Criteria: {{ business_context.success_criteria }}
    Timeline: {{ business_context.timeline }}
    Budget: {{ business_context.budget }}
    Risk Tolerance: {{ business_context.risk_tolerance }}
    Persona: {{ business_context.persona_id }}
    
    Platform Capabilities:
    {% for capability in platform_capabilities %}
    - {{ capability }}
    {% endfor %}
    
    Our Platform Strengths (prioritize these):
    1. REST APIs - 500+ successful integrations
    2. Semantic Web - SKOS, SPARQL, 40+ languages  
    3. Real-time Processing - KuzuDB, streaming pipelines
    4. Authentication - OAuth, tokens, certificates
    
    Platform Limitations (suggest alternatives):
    1. Computer Vision - Limited capability
    2. Legacy Database Connectors - Prefer API access
    3. Real-time Trading Data - High cost, suggest alternatives
    
    Recommend 5-8 data sources with:
    
    1. Platform-Aligned Sources (High Priority):
       - Favor sources with good REST APIs
       - Prioritize sources with semantic metadata
       - Choose sources that match our authentication capabilities
       - Select sources with good documentation
    
    2. Feasibility Scoring:
       - Technical feasibility (0.0-1.0) based on our platform
       - Implementation effort (low/medium/high/very_high)
       - Expected data quality (0.0-1.0)
       - Platform compatibility (0.0-1.0)
    
    3. Business Value Assessment:
       - How well it addresses the business question
       - Cost vs. value analysis
       - Timeline fit assessment  
       - Risk level evaluation
    
    4. Semantic Enrichment:
       - Identify relevant SKOS vocabularies for each source
       - Note semantic standardization opportunities
       - Suggest ontology alignments
       - Recommend multilingual translation needs
    
    5. Implementation Guidance:
       - Required authentication methods
       - API rate limits and access patterns
       - Data transformation requirements
       - Quality validation approaches
    
    Return data sources ranked by overall fit with detailed justifications for each recommendation.
  "#
}

// Feasibility Analyzer Agent  
function FeasibilityAnalyzerAgent(
  business_context: BusinessContext,
  recommended_sources: DataSourceRecommendation[]
) -> FeasibilityAnalysis {
  client GPT4
  prompt #"
    You are a feasibility analysis specialist with deep expertise in data project risk assessment and platform capabilities.
    
    Your task is to provide comprehensive feasibility analysis for the recommended data sources and overall project approach.
    
    Business Context:
    Question: {{ business_context.question }}
    Timeline: {{ business_context.timeline }}
    Budget: {{ business_context.budget }}
    Risk Tolerance: {{ business_context.risk_tolerance }}
    
    Recommended Sources:
    {% for source in recommended_sources %}
    - {{ source.name }} ({{ source.type }})
      Feasibility: {{ source.feasibility_score }}
      Effort: {{ source.implementation_effort }}
      Platform Fit: {{ source.platform_compatibility }}
    {% endfor %}
    
    Analyze comprehensive feasibility:
    
    1. Technical Feasibility Assessment:
       - Evaluate each source's technical complexity
       - Assess integration challenges with our platform
       - Identify potential performance bottlenecks  
       - Note any missing platform capabilities
    
    2. Risk Analysis:
       - Data availability and reliability risks
       - API stability and provider reliability
       - Authentication and access risks
       - Data quality and consistency risks
       - Timeline and delivery risks
    
    3. Platform Gap Analysis:
       - Identify capabilities we lack for optimal implementation
       - Suggest workarounds or alternative approaches
       - Note any third-party integrations needed
       - Assess impact on overall project feasibility
    
    4. Resource Requirements:
       - Development effort estimation
       - Infrastructure and operational costs
       - Maintenance and ongoing support needs
       - Required expertise and skill gaps
    
    5. Success Probability Assessment:
       - Overall likelihood of meeting success criteria
       - Confidence level in timeline achievement
       - Budget adequacy assessment
       - Risk mitigation effectiveness
    
    6. Recommendations:
       - Suggest project scope adjustments if needed
       - Recommend phased approach if beneficial
       - Identify critical success factors
       - Propose alternative strategies for high-risk elements
    
    Provide honest, realistic assessment with actionable recommendations for maximizing project success.
  "#
}

// SOW Contract Generator Agent
function SOWGeneratorAgent(
  business_context: BusinessContext,
  selected_sources: DataSourceRecommendation[],
  feasibility_analysis: FeasibilityAnalysis
) -> SOWContract {
  client GPT4
  prompt #"
    You are an expert SOW (Statement of Work) generator specializing in data integration projects with semantic enrichment.
    
    Your task is to generate a comprehensive, professional SOW contract that clearly defines project scope, deliverables, and success criteria.
    
    Business Context:
    Question: {{ business_context.question }}
    Success Criteria: {{ business_context.success_criteria }}
    Timeline: {{ business_context.timeline }}
    Budget: {{ business_context.budget }}
    
    Selected Data Sources:
    {% for source in selected_sources %}
    - {{ source.name }}: {{ source.description }}
      Type: {{ source.type }}
      Effort: {{ source.implementation_effort }}
      Cost: {{ source.cost_estimate }}
    {% endfor %}
    
    Feasibility Analysis:
    Overall Feasibility: {{ feasibility_analysis.overall_feasibility }}
    Timeline Estimate: {{ feasibility_analysis.estimated_timeline_weeks }} weeks
    Confidence: {{ feasibility_analysis.confidence_level }}
    
    Generate a comprehensive SOW contract:
    
    1. Executive Summary:
       - Clear business problem statement
       - Proposed solution approach
       - Expected business outcomes
       - High-level timeline and investment
    
    2. Project Objectives:
       - Specific, measurable business goals
       - Success metrics and KPIs
       - Stakeholder value propositions
       - ROI expectations and timeline
    
    3. Technical Approach:
       - Data source integration strategy
       - Semantic enrichment methodology (SKOS/OWL)
       - Platform architecture and design
       - Quality assurance and validation approach
    
    4. Detailed Deliverables:
       - Data ingestion pipelines for each source
       - Semantic mapping and enrichment layer
       - Quality monitoring and alerting system
       - Documentation and knowledge transfer
       - Training and support materials
    
    5. Project Timeline and Milestones:
       - Phase-based delivery schedule
       - Key milestones and dependencies
       - Testing and validation checkpoints
       - Go-live and production readiness criteria
    
    6. Investment and Resource Requirements:
       - Development effort breakdown
       - Infrastructure and tooling costs
       - Data source licensing and access costs
       - Ongoing operational expenses
    
    7. Risk Management:
       - Identified risks and impact assessment
       - Mitigation strategies and contingency plans
       - Change management and scope control
       - Success criteria and acceptance testing
    
    8. Semantic Framework:
       - SKOS vocabulary selection and mapping strategy
       - Multilingual support and translation approach
       - Ontology alignment and validation process
       - Knowledge graph design and query optimization
    
    Generate a professional, detailed SOW that instills confidence while being realistic about timelines, costs, and deliverables.
  "#
}

// Persona-Aware Response Agent
function PersonaResponseAgent(
  base_response: string,
  persona_id: string,
  interaction_level: string,
  technical_depth: string
) -> string {
  client GPT4
  prompt #"
    You are a persona adaptation specialist who customizes responses based on user roles and interaction preferences.
    
    Your task is to adapt the base response to match the persona's communication style, technical depth, and attention span.
    
    Base Response: {{ base_response }}
    Persona: {{ persona_id }}
    Interaction Level: {{ interaction_level }}
    Technical Depth: {{ technical_depth }}
    
    Persona Characteristics:
    
    Business Analyst (business_analyst):
    - Focus: Business impact, feasibility, stakeholder communication
    - Style: Structured, strategic, risk-aware
    - Technical Depth: Balanced - some technical detail but focus on business value
    - Attention Span: High - willing to engage with comprehensive analysis
    
    Data Analyst (data_analyst):  
    - Focus: Data quality, structure, integration patterns
    - Style: Detail-oriented, technically precise, methodology-focused
    - Technical Depth: Detailed - wants specific technical information
    - Attention Span: High - enjoys deep technical discussions
    
    Data Lead/Architect (data_lead):
    - Focus: Platform capabilities, team capacity, architectural decisions
    - Style: Strategic, systems-thinking, long-term focused
    - Technical Depth: Expert - expects sophisticated technical discussion
    - Attention Span: Very High - engages with complex architectural topics
    
    Trader/Business User (trader):
    - Focus: Speed to insights, cost/benefit, implementation timeline
    - Style: Direct, results-focused, impatient with unnecessary detail
    - Technical Depth: Minimal - wants business outcomes, not technical details
    - Attention Span: Medium - prefers concise, actionable information
    
    Interaction Level Preferences:
    - Executive: High-level strategic focus, minimal technical detail
    - Standard: Balanced business and technical information
    - Technical: Deep technical detail with implementation specifics
    - Rapid: Quick, concise responses focusing on key decisions
    
    Adapt the response by:
    
    1. Adjusting Technical Detail:
       - Minimal: Focus on business outcomes and timelines
       - Balanced: Mix business value with key technical considerations
       - Detailed: Include technical specifications and implementation details
       - Expert: Provide architectural insights and advanced technical concepts
    
    2. Modifying Communication Style:
       - Use vocabulary and tone appropriate for the persona
       - Adjust response length based on attention span
       - Emphasize information most valuable to their role
       - Structure information to match their decision-making process
    
    3. Prioritizing Information:
       - Lead with information most relevant to their primary concerns
       - Include appropriate level of supporting detail
       - Suggest next steps aligned with their role responsibilities
       - Frame recommendations in terms of their success metrics
    
    Return an adapted response that feels natural and valuable for the specific persona and interaction preferences.
  "#
}

// Platform Capability Assessment Agent
function PlatformCapabilityAgent(
  data_sources: string[],
  requirements: string[]
) -> map<string, float> {
  client GPT4
  prompt #"
    You are a platform capability assessment specialist with deep knowledge of our agentic data scraper platform strengths and limitations.
    
    Your task is to assess how well our platform can handle specific data sources and requirements, providing realistic capability scores.
    
    Data Sources to Assess:
    {% for source in data_sources %}
    - {{ source }}
    {% endfor %}
    
    Requirements:
    {% for requirement in requirements %}
    - {{ requirement }}
    {% endfor %}
    
    Our Platform Strengths (Score High 0.8-1.0):
    1. REST APIs - Excellent support with 500+ successful integrations
    2. Semantic Web Technologies - SKOS, SPARQL, OWL with 40+ language support
    3. Real-time Processing - KuzuDB graph database, streaming pipelines
    4. Authentication - OAuth 2.0, API tokens, certificates, session management
    5. Data Transformation - Advanced semantic mapping and validation
    6. Quality Monitoring - Comprehensive data quality assessment and alerting
    
    Platform Limitations (Score Lower 0.2-0.6):
    1. Computer Vision - Limited OCR and image processing capabilities
    2. Legacy Database Direct Access - Prefer API-mediated access
    3. Real-time Trading Data - High cost, limited real-time market data feeds
    4. Large File Processing - Better suited for streaming than massive batch files
    5. Custom Authentication - Complex proprietary auth systems
    
    For each data source and requirement combination, assess:
    
    1. Technical Compatibility (0.0-1.0):
       - How well our platform can technically integrate with this source
       - Authentication and access pattern compatibility
       - Data format and structure alignment
       - API stability and documentation quality
    
    2. Performance Suitability (0.0-1.0):
       - Expected performance with our infrastructure
       - Scalability considerations
       - Resource efficiency
       - Real-time processing capability
    
    3. Semantic Enrichment Potential (0.0-1.0):
       - Availability of semantic metadata
       - SKOS vocabulary alignment opportunities
       - Ontology mapping potential
       - Multilingual support requirements
    
    4. Implementation Effort (0.0-1.0, where 1.0 = very easy):
       - Development complexity
       - Integration effort required
       - Testing and validation complexity
       - Maintenance overhead
    
    Return a map of source/requirement combinations to capability scores with realistic assessments that help users make informed decisions.
  "#
}