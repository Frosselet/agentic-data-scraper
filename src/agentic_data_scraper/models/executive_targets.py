"""
Enterprise-Specific Executive Target Models

Supports dynamic, enterprise-typed executive targets with contextual alignment scoring
that adapts to enterprise-specific strategic language and evolving priorities.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
import uuid


class TargetCategory(str, Enum):
    """Strategic target categories"""
    REVENUE = "revenue"
    MARKET_EXPANSION = "market_expansion"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    CUSTOMER_EXPERIENCE = "customer_experience"
    INNOVATION = "innovation"
    COMPLIANCE = "compliance"
    RISK_MANAGEMENT = "risk_management"
    COST_REDUCTION = "cost_reduction"
    DIGITAL_TRANSFORMATION = "digital_transformation"
    SUSTAINABILITY = "sustainability"
    TALENT_DEVELOPMENT = "talent_development"
    STRATEGIC_PARTNERSHIP = "strategic_partnership"


class TargetPriority(str, Enum):
    """Target priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlignmentDimension(str, Enum):
    """Dimensions for alignment assessment"""
    STRATEGIC_FIT = "strategic_fit"
    IMPACT_POTENTIAL = "impact_potential"
    TIMELINE_FEASIBILITY = "timeline_feasibility"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    RISK_ASSESSMENT = "risk_assessment"
    DEPENDENCY_ANALYSIS = "dependency_analysis"


@dataclass
class ExecutiveTarget:
    """Enterprise-specific executive target with dynamic properties"""

    # Core identification
    id: str = field(default_factory=lambda: f"target_{uuid.uuid4().hex[:8]}")
    title: str = ""
    description: str = ""
    category: TargetCategory = TargetCategory.REVENUE
    priority: TargetPriority = TargetPriority.MEDIUM

    # Ownership and timing
    owner: str = ""  # Executive responsible (e.g., "Chief Revenue Officer")
    owner_role: str = ""  # Role/title
    deadline: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    # Strategic context
    success_metrics: List[str] = field(default_factory=list)
    target_value: Optional[str] = None  # e.g., "30% increase", "$5M revenue"
    baseline_value: Optional[str] = None  # Current state
    measurement_unit: Optional[str] = None  # %, $, count, etc.

    # Enterprise context
    business_domain: str = ""  # e.g., "Healthcare", "Fintech", "Retail"
    stakeholders: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    # Dynamic properties for enterprise adaptation
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # Status tracking
    status: Literal["active", "paused", "completed", "cancelled"] = "active"
    progress_percentage: float = 0.0
    last_review_date: Optional[date] = None


@dataclass
class AlignmentScore:
    """Multi-dimensional alignment scoring"""

    # Overall alignment
    overall_score: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.0  # Confidence in the scoring

    # Dimensional scores
    strategic_fit: float = 0.0
    impact_potential: float = 0.0
    timeline_feasibility: float = 0.0
    resource_efficiency: float = 0.0
    risk_assessment: float = 0.0
    dependency_analysis: float = 0.0

    # Contextual information
    reasoning: str = ""
    key_factors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Metadata
    scored_at: datetime = field(default_factory=datetime.now)
    scorer_agent: str = "ExecutiveTargetScorer"
    version: str = "1.0"


@dataclass
class TargetAlignment:
    """Alignment between data initiative and executive target"""

    target_id: str
    initiative_id: str  # Data canvas or SOW ID
    alignment_score: AlignmentScore

    # Contribution analysis
    contribution_type: str = ""  # "direct", "indirect", "enabling"
    expected_impact: str = ""
    timeline_match: str = ""  # "aligned", "accelerated", "delayed"

    # Dynamic factors
    market_conditions: Dict[str, str] = field(default_factory=dict)
    competitive_factors: List[str] = field(default_factory=list)
    technology_readiness: str = ""

    # Feedback loop
    feedback_channels: List[str] = field(default_factory=list)
    monitoring_frequency: str = "monthly"
    adjustment_triggers: List[str] = field(default_factory=list)


@dataclass
class EnterpriseTargetRegistry:
    """Registry for managing enterprise-specific targets"""

    # Enterprise identification
    enterprise_id: str
    enterprise_name: str
    fiscal_year: str
    quarter: str

    # Target collection
    targets: List[ExecutiveTarget] = field(default_factory=list)
    target_categories_used: List[TargetCategory] = field(default_factory=list)

    # Enterprise configuration
    custom_categories: Dict[str, str] = field(default_factory=dict)
    measurement_standards: Dict[str, str] = field(default_factory=dict)
    reporting_requirements: List[str] = field(default_factory=list)

    # Template library for common target patterns
    target_templates: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_sync: datetime = field(default_factory=datetime.now)
    version: str = "1.0"


@dataclass
class TargetParsingResult:
    """Result of parsing natural language target description"""

    # Extracted entities
    key_themes: List[str] = field(default_factory=list)
    quantitative_targets: List[str] = field(default_factory=list)
    timeframes: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)

    # Inferred properties
    suggested_category: Optional[TargetCategory] = None
    suggested_priority: Optional[TargetPriority] = None
    complexity_score: float = 0.0

    # Data requirements inference
    required_data_types: List[str] = field(default_factory=list)
    suggested_metrics: List[str] = field(default_factory=list)
    potential_data_sources: List[str] = field(default_factory=list)

    # Parsing metadata
    confidence: float = 0.0
    parsing_method: str = "baml_agent"
    parsed_at: datetime = field(default_factory=datetime.now)


@dataclass
class AlignmentFeedback:
    """Feedback for continuous alignment improvement"""

    target_id: str
    initiative_id: str
    description: str
    impact_on_alignment: str  # "positive", "negative", "neutral"
    feedback_type: Literal["progress_update", "target_change", "initiative_change", "external_factor"] = "progress_update"
    new_alignment_score: Optional[float] = None

    # Recommendations
    suggested_actions: List[str] = field(default_factory=list)
    urgency: Literal["low", "medium", "high", "critical"] = "medium"

    # Context
    external_factors: List[str] = field(default_factory=list)
    market_changes: Dict[str, str] = field(default_factory=dict)
    competitive_intelligence: List[str] = field(default_factory=list)

    # Metadata
    reported_by: str = ""
    reported_at: datetime = field(default_factory=datetime.now)
    processed: bool = False