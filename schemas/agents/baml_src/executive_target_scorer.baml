enum TargetCategory {
  REVENUE
  MARKET_EXPANSION
  OPERATIONAL_EFFICIENCY
  CUSTOMER_EXPERIENCE
  INNOVATION
  COMPLIANCE
  RISK_MANAGEMENT
  COST_REDUCTION
  DIGITAL_TRANSFORMATION
  SUSTAINABILITY
  TALENT_DEVELOPMENT
  STRATEGIC_PARTNERSHIP
}

enum TargetPriority {
  CRITICAL
  HIGH
  MEDIUM
  LOW
}

class ExecutiveTarget {
  id string
  title string
  description string
  category TargetCategory
  priority TargetPriority
  owner string
  owner_role string
  deadline string?
  success_metrics string[]
  target_value string?
  baseline_value string?
  business_domain string
  stakeholders string[]
  dependencies string[]
  constraints string[]
  status string
}

class AlignmentScore {
  overall_score float
  confidence float
  strategic_fit float
  impact_potential float
  timeline_feasibility float
  resource_efficiency float
  risk_assessment float
  dependency_analysis float
  reasoning string
  key_factors string[]
  risk_factors string[]
  recommendations string[]
}

class TargetParsingResult {
  key_themes string[]
  quantitative_targets string[]
  timeframes string[]
  stakeholders string[]
  success_indicators string[]
  suggested_category TargetCategory?
  suggested_priority TargetPriority?
  complexity_score float
  required_data_types string[]
  suggested_metrics string[]
  potential_data_sources string[]
  confidence float
}

class DataBusinessCanvas {
  // Core canvas elements
  value_propositions string[]
  key_activities string[]
  key_resources string[]
  key_partnerships string[]
  customer_segments string[]
  customer_relationships string[]
  channels string[]
  cost_structure string[]
  revenue_streams string[]

  // +3 strategic extensions
  data_assets string[]
  intelligence_capabilities string[]
  competitive_advantages string[]

  // Business context
  business_domain string
  use_case_description string
  timeline string
  budget string
}

// BAML Function for Parsing Executive Target Descriptions
function ParseExecutiveTarget(target_description: string, enterprise_context: map<string, string>) -> TargetParsingResult {
  client GPT4
  prompt #"
    You are an Executive Target Intelligence Analyst. Analyze this executive target and provide your analysis using these specific categories:

    TARGET DESCRIPTION:
    {{ target_description }}

    ENTERPRISE CONTEXT:
    {% for key in enterprise_context %}
    {{ key }}: {{ enterprise_context[key] }}
    {% endfor %}

    CRITICAL: Return ONLY the structured data in the exact format below. Do NOT add explanatory text after the values.

    key_themes: ["revenue growth", "customer retention", "digital transformation"]
    quantitative_targets: ["40% increase", "$2M target", "25% improvement"]
    timeframes: ["Q2 2024", "6 months", "by end of year"]
    stakeholders: ["Sarah Chen", "VP Sales", "Marketing Team"]
    success_indicators: ["MRR target", "customer lifetime value", "conversion rates"]
    suggested_category: REVENUE
    suggested_priority: CRITICAL
    complexity_score: 0.8
    required_data_types: ["customer data", "sales metrics", "pricing data"]
    suggested_metrics: ["Monthly Recurring Revenue", "Customer Lifetime Value"]
    potential_data_sources: ["CRM system", "sales database", "analytics tools"]
    confidence: 0.9

    Important: For complexity_score and confidence, provide ONLY the decimal number (e.g., 0.8) with no additional text or explanations.
  "#
}

// BAML Function for Strategic Alignment Scoring
function ScoreStrategicAlignment(
  target: ExecutiveTarget,
  canvas: DataBusinessCanvas,
  enterprise_context: map<string, string>
) -> AlignmentScore {
  client GPT4
  prompt #"
    You are a Strategic Alignment Intelligence Agent with expertise in business-data alignment assessment.

    MISSION: Analyze alignment between the data business canvas initiative and executive target,
    providing multi-dimensional scoring that guides strategic decision-making.

    EXECUTIVE TARGET:
    Title: {{ target.title }}
    Description: {{ target.description }}
    Category: {{ target.category }}
    Priority: {{ target.priority }}
    Owner: {{ target.owner }} ({{ target.owner_role }})
    {% if target.deadline %}Deadline: {{ target.deadline }}{% endif %}
    Success Metrics: {{ target.success_metrics | join(", ") }}
    {% if target.target_value %}Target Value: {{ target.target_value }}{% endif %}
    {% if target.baseline_value %}Baseline: {{ target.baseline_value }}{% endif %}
    Business Domain: {{ target.business_domain }}

    {% if target.stakeholders %}
    Stakeholders: {{ target.stakeholders | join(", ") }}
    {% endif %}
    {% if target.dependencies %}
    Dependencies: {{ target.dependencies | join(", ") }}
    {% endif %}
    {% if target.constraints %}
    Constraints: {{ target.constraints | join(", ") }}
    {% endif %}

    DATA BUSINESS CANVAS INITIATIVE:
    Value Propositions: {{ canvas.value_propositions | join(", ") }}
    Key Activities: {{ canvas.key_activities | join(", ") }}
    Key Resources: {{ canvas.key_resources | join(", ") }}
    Customer Segments: {{ canvas.customer_segments | join(", ") }}
    Revenue Streams: {{ canvas.revenue_streams | join(", ") }}

    Data Assets: {{ canvas.data_assets | join(", ") }}
    Intelligence Capabilities: {{ canvas.intelligence_capabilities | join(", ") }}
    Competitive Advantages: {{ canvas.competitive_advantages | join(", ") }}

    Business Context:
    - Domain: {{ canvas.business_domain }}
    - Use Case: {{ canvas.use_case_description }}
    - Timeline: {{ canvas.timeline }}
    - Budget: {{ canvas.budget }}

    ENTERPRISE CONTEXT:
    {% for key in enterprise_context %}
    {{ key }}: {{ enterprise_context[key] }}
    {% endfor %}

    MULTI-DIMENSIONAL ALIGNMENT ANALYSIS:

    1. STRATEGIC FIT (0.0-1.0):
       - How well does the data initiative align with target objectives?
       - Does the initiative directly contribute to target achievement?
       - Are there synergies between data capabilities and strategic goals?

    2. IMPACT POTENTIAL (0.0-1.0):
       - What is the potential magnitude of contribution to the target?
       - Can the initiative be a primary driver or supporting enabler?
       - How measurable is the expected impact?

    3. TIMELINE FEASIBILITY (0.0-1.0):
       - Do initiative and target timelines align appropriately?
       - Is there sufficient time for data initiative to impact target?
       - Are there critical path dependencies?

    4. RESOURCE EFFICIENCY (0.0-1.0):
       - How efficiently do initiative resources support target achievement?
       - Are there shared resources or economies of scale?
       - Is the resource investment justified by target contribution?

    5. RISK ASSESSMENT (0.0-1.0):
       - What are the risks of misalignment or failure?
       - How robust is the connection between initiative and target?
       - Are there external dependency risks?

    6. DEPENDENCY ANALYSIS (0.0-1.0):
       - How well do initiative outputs feed into target requirements?
       - Are there missing links or capability gaps?
       - How resilient is the alignment to changes?

    SCORING METHODOLOGY:
    - Use quantitative reasoning for each dimension
    - Consider both direct and indirect contributions
    - Account for enterprise-specific factors and constraints
    - Provide confidence based on information completeness

    DELIVERABLES:
    - Overall alignment score (weighted average of dimensions)
    - Individual dimensional scores with reasoning
    - Key factors supporting the alignment
    - Risk factors that could impact alignment
    - Specific recommendations to improve alignment

    Be ANALYTICAL and EVIDENCE-BASED. Provide specific, actionable insights
    that enable strategic decision-making and continuous alignment optimization.
  "#
}

// BAML Function for Alignment Monitoring and Feedback
function GenerateAlignmentFeedback(
  target: ExecutiveTarget,
  canvas: DataBusinessCanvas,
  alignment_score: AlignmentScore,
  market_changes: map<string, string>,
  progress_data: map<string, string>
) -> map<string, string> {
  client GPT4
  prompt #"
    You are an Executive Alignment Monitor providing continuous feedback on strategic alignment.

    MISSION: Generate actionable feedback and recommendations based on current alignment status,
    market changes, and progress data to maintain optimal strategic alignment.

    CURRENT ALIGNMENT STATUS:
    Target: {{ target.title }} ({{ target.category }}, Priority: {{ target.priority }})
    Overall Alignment Score: {{ alignment_score.overall_score }}
    Confidence: {{ alignment_score.confidence }}

    Dimensional Scores:
    - Strategic Fit: {{ alignment_score.strategic_fit }}
    - Impact Potential: {{ alignment_score.impact_potential }}
    - Timeline Feasibility: {{ alignment_score.timeline_feasibility }}
    - Resource Efficiency: {{ alignment_score.resource_efficiency }}
    - Risk Assessment: {{ alignment_score.risk_assessment }}
    - Dependency Analysis: {{ alignment_score.dependency_analysis }}

    Key Factors: {{ alignment_score.key_factors | join(", ") }}
    Risk Factors: {{ alignment_score.risk_factors | join(", ") }}

    MARKET CHANGES:
    {% for key in market_changes %}
    {{ key }}: {{ market_changes[key] }}
    {% endfor %}

    PROGRESS DATA:
    {% for key in progress_data %}
    {{ key }}: {{ progress_data[key] }}
    {% endfor %}

    FEEDBACK ANALYSIS FRAMEWORK:

    1. ALIGNMENT DRIFT DETECTION:
       - Has the alignment improved or degraded since last assessment?
       - What factors are driving alignment changes?
       - Are there early warning indicators of misalignment?

    2. MARKET IMPACT ASSESSMENT:
       - How do market changes affect target achievability?
       - Do market conditions create new opportunities or risks?
       - Should strategic priorities be adjusted?

    3. PROGRESS IMPACT EVALUATION:
       - Is initiative progress supporting target achievement?
       - Are there performance gaps that need attention?
       - What course corrections might be needed?

    4. STRATEGIC RECOMMENDATIONS:
       - What actions should be taken to maintain/improve alignment?
       - Are there tactical adjustments that could enhance impact?
       - Should resources be reallocated or supplemented?

    FEEDBACK CATEGORIES:
    Provide feedback as a map with these keys:
    - alignment_trend: "improving" | "stable" | "degrading"
    - urgency_level: "low" | "medium" | "high" | "critical"
    - primary_concern: Brief description of main issue if any
    - recommended_actions: Comma-separated list of specific actions
    - market_response: How to respond to market changes
    - resource_adjustments: Resource allocation recommendations
    - timeline_adjustments: Any timing modifications needed
    - success_probability: Updated probability of target achievement (0.0-1.0)
    - next_review_date: When to reassess alignment
    - escalation_needed: "yes" | "no" - whether executive attention is required

    Be PROACTIVE and STRATEGIC. Focus on actionable intelligence that supports
    both target achievement and data initiative success.
  "#
}

// BAML Function for Enterprise Target Template Creation
function CreateTargetTemplate(
  target_examples: string[],
  enterprise_domain: string,
  template_name: string
) -> map<string, string> {
  client GPT4
  prompt #"
    You are an Enterprise Target Template Designer creating reusable strategic target patterns.

    MISSION: Analyze example targets from this enterprise and create a structured template
    that can be reused for similar strategic objectives.

    ENTERPRISE DOMAIN: {{ enterprise_domain }}
    TEMPLATE NAME: {{ template_name }}

    TARGET EXAMPLES:
    {% for example in target_examples %}
    {{ loop.index }}. {{ example }}
    {% endfor %}

    TEMPLATE DESIGN FRAMEWORK:

    1. PATTERN IDENTIFICATION:
       - Common themes and strategic focuses
       - Typical quantitative target structures
       - Standard timeframes and measurement cycles
       - Consistent stakeholder patterns

    2. ENTERPRISE ADAPTATION:
       - Domain-specific language and terminology
       - Industry-relevant success metrics
       - Regulatory and compliance considerations
       - Competitive positioning factors

    3. TEMPLATE STRUCTURE:
       - Standard target description format
       - Required vs. optional fields
       - Default values and ranges
       - Validation rules and constraints

    4. CUSTOMIZATION POINTS:
       - Variable elements that change per target
       - Context-sensitive adaptations
       - Scalability considerations

    TEMPLATE OUTPUT:
    Provide a map with these components:
    - template_description: Overall description of when to use this template
    - target_title_format: Standard format for target titles
    - description_template: Template with placeholders for descriptions
    - typical_category: Most common target category for this pattern
    - typical_priority: Most common priority level
    - success_metrics_template: Standard success metrics pattern
    - stakeholder_pattern: Typical stakeholder involvement
    - timeline_pattern: Standard timing expectations
    - data_requirements: Common data needs for this target type
    - validation_rules: Rules for validating targets using this template
    - customization_guidelines: How to adapt the template for specific cases

    Be SYSTEMATIC and PRACTICAL. Create templates that reduce cognitive load
    while maintaining strategic precision and enterprise alignment.
  "#
}