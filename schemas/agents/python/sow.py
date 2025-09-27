"""
Semantic Statement of Work (SOW) Pydantic Models

This module provides comprehensive Pydantic models for the revolutionary Semantic SOW Schema
that captures explicit business needs while intelligently inferring implicit requirements
for 4D analytical platforms.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, validator


class JSONLDContext(BaseModel):
    """JSON-LD context for semantic web compatibility."""
    base: HttpUrl = Field(default="https://agentic-data-scraper.com/sow/", alias="@base")
    business: HttpUrl = Field(default="https://schema.org/")
    supply: HttpUrl = Field(default="https://gs1.org/ontology/")
    finance: HttpUrl = Field(default="https://spec.edmcouncil.org/fibo/")
    commodities: HttpUrl = Field(default="https://ontology.commodities.org/")
    geo: HttpUrl = Field(default="http://www.geonames.org/ontology#")
    time: HttpUrl = Field(default="http://www.w3.org/2006/time#")
    owl: HttpUrl = Field(default="http://www.w3.org/2002/07/owl#")
    rdf: HttpUrl = Field(default="http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs: HttpUrl = Field(default="http://www.w3.org/2000/01/rdf-schema#")
    skos: HttpUrl = Field(default="http://www.w3.org/2004/02/skos/core#")
    dct: HttpUrl = Field(default="http://purl.org/dc/terms/")
    foaf: HttpUrl = Field(default="http://xmlns.com/foaf/0.1/")
    prov: HttpUrl = Field(default="http://www.w3.org/ns/prov#")


class EntityToTrack(BaseModel):
    """Entity that business wants to track."""
    entity: str = Field(..., min_length=2, max_length=100)
    importance: str = Field(..., pattern="^(critical|high|medium|low)$")
    semantic_type: Optional[str] = Field(None, description="Semantic type from ontology")
    business_context: Optional[str] = Field(None, description="Business context for this entity")


class LocationMention(BaseModel):
    """Geographic location mentioned in business requirements."""
    location: str = Field(..., min_length=2, max_length=100)
    type: str = Field(..., pattern="^(country|region|city|facility|route|market)$")
    relevance: Optional[str] = Field(None, description="How this location is relevant")


class SpatialContext(BaseModel):
    """Spatial context of business requirements."""
    locations_mentioned: List[LocationMention] = Field(default_factory=list)
    geographic_scope: str = Field(..., pattern="^(local|regional|national|international|global)$")


class CriticalPeriod(BaseModel):
    """Time periods that are critical for business operations."""
    period: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)
    business_impact: str = Field(..., min_length=5, max_length=300)


class TemporalContext(BaseModel):
    """Temporal context of business requirements."""
    time_horizons: List[str] = Field(
        default_factory=list,
        description="Time horizons of interest"
    )
    critical_periods: List[CriticalPeriod] = Field(default_factory=list)
    seasonality_mentioned: bool = Field(default=False)

    @validator('time_horizons')
    def validate_time_horizons(cls, v):
        valid_horizons = ["real-time", "daily", "weekly", "monthly", "quarterly", "yearly", "historical"]
        for horizon in v:
            if horizon not in valid_horizons:
                raise ValueError(f"Invalid time horizon: {horizon}")
        return v


class StakeholderInvolved(BaseModel):
    """Stakeholder involved in business requirements."""
    role: str = Field(..., min_length=2, max_length=100)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    responsibilities: List[str] = Field(default_factory=list)
    decision_authority: str = Field(..., pattern="^(high|medium|low|none)$")


class BusinessChallenge(BaseModel):
    """Core business challenge to solve."""
    description: str = Field(..., min_length=10, max_length=1000)
    entities_to_track: List[EntityToTrack] = Field(..., min_items=1)
    spatial_context: Optional[SpatialContext] = None
    temporal_context: Optional[TemporalContext] = None
    stakeholders_involved: List[StakeholderInvolved] = Field(default_factory=list)


class DesiredOutcome(BaseModel):
    """Desired business outcome."""
    outcome: str = Field(..., min_length=5, max_length=500)
    success_metrics: List[str] = Field(default_factory=list)
    business_value: Optional[str] = Field(None, min_length=5, max_length=300)
    priority: str = Field(..., pattern="^(must-have|should-have|nice-to-have)$")


class ConstraintsAndLimitations(BaseModel):
    """Business constraints and limitations."""
    budget_constraints: Optional[str] = None
    timeline_constraints: Optional[str] = None
    technical_constraints: List[str] = Field(default_factory=list)
    regulatory_constraints: List[str] = Field(default_factory=list)
    organizational_constraints: List[str] = Field(default_factory=list)


class ExplicitRequirements(BaseModel):
    """Business requirements explicitly stated by stakeholders."""
    business_challenge: BusinessChallenge
    desired_outcomes: List[DesiredOutcome] = Field(..., min_items=1)
    constraints_and_limitations: Optional[ConstraintsAndLimitations] = None


class GeographicAnalysisOpportunity(BaseModel):
    """Geographic analysis opportunity inferred from requirements."""
    analysis_type: str = Field(..., min_length=3, max_length=100)
    reasoning: str = Field(..., min_length=10, max_length=500)
    confidence: float = Field(..., ge=0, le=1)
    potential_value: str = Field(..., min_length=5, max_length=300)
    required_data: List[str] = Field(default_factory=list)


class MultiScaleConsideration(BaseModel):
    """Multi-scale geographic considerations."""
    scale: str = Field(..., pattern="^(local|regional|national|global)$")
    relevance: str = Field(..., min_length=5, max_length=300)
    analysis_needs: List[str] = Field(default_factory=list)


class SpatialInferences(BaseModel):
    """Spatial analysis opportunities inferred from explicit requirements."""
    geographic_analysis_opportunities: List[GeographicAnalysisOpportunity] = Field(default_factory=list)
    multi_scale_considerations: List[MultiScaleConsideration] = Field(default_factory=list)


class TimeSeriesOpportunity(BaseModel):
    """Time series analysis opportunity."""
    pattern_type: str = Field(..., pattern="^(trend|seasonality|cycles|anomalies)$")
    reasoning: str = Field(..., min_length=10, max_length=500)
    business_relevance: str = Field(..., min_length=5, max_length=300)
    analysis_methods: List[str] = Field(default_factory=list)


class BiTemporalNeeds(BaseModel):
    """Bi-temporal data management needs."""
    transaction_time_needed: bool = Field(default=False)
    valid_time_needed: bool = Field(default=False)
    reasoning: str = Field(..., min_length=10, max_length=500)


class TemporalInferences(BaseModel):
    """Temporal analysis patterns inferred from business context."""
    time_series_opportunities: List[TimeSeriesOpportunity] = Field(default_factory=list)
    bi_temporal_needs: Optional[BiTemporalNeeds] = None


class DomainAnalysisOpportunity(BaseModel):
    """Domain-specific analysis opportunity."""
    opportunity: str = Field(..., min_length=5, max_length=200)
    reasoning: str = Field(..., min_length=10, max_length=500)
    stakeholder_value: Optional[str] = Field(None, min_length=5, max_length=300)
    complexity: str = Field(..., pattern="^(low|medium|high)$")
    risk_considerations: Optional[str] = Field(None, min_length=5, max_length=300)
    regulatory_implications: List[str] = Field(default_factory=list)


class DomainInferences(BaseModel):
    """Domain-specific analysis opportunities discovered through semantic reasoning."""
    supply_chain_analytics: List[DomainAnalysisOpportunity] = Field(default_factory=list)
    financial_analytics: List[DomainAnalysisOpportunity] = Field(default_factory=list)
    compliance_analytics: List[DomainAnalysisOpportunity] = Field(default_factory=list)


class RelationshipNetwork(BaseModel):
    """Relationship network analysis opportunity."""
    network_type: str = Field(..., min_length=3, max_length=100)
    entities_involved: List[str] = Field(..., min_items=2)
    analysis_value: str = Field(..., min_length=5, max_length=300)
    centrality_insights: Optional[str] = Field(None, min_length=5, max_length=300)


class DependencyAnalysis(BaseModel):
    """Dependency analysis opportunity."""
    dependency_type: str = Field(..., min_length=3, max_length=100)
    impact_assessment: str = Field(..., min_length=5, max_length=300)
    mitigation_strategies: List[str] = Field(default_factory=list)


class GraphInferences(BaseModel):
    """Relationship and network analysis opportunities discovered through graph reasoning."""
    relationship_networks: List[RelationshipNetwork] = Field(default_factory=list)
    dependency_analysis: List[DependencyAnalysis] = Field(default_factory=list)


class InferredContext(BaseModel):
    """Context and requirements inferred through OWL reasoning and domain knowledge."""
    spatial_inferences: Optional[SpatialInferences] = None
    temporal_inferences: Optional[TemporalInferences] = None
    domain_inferences: Optional[DomainInferences] = None
    graph_inferences: Optional[GraphInferences] = None


class RequiredCapability(BaseModel):
    """Required capability for analytical opportunity."""
    capability: str = Field(..., min_length=3, max_length=100)
    justification: str = Field(..., min_length=10, max_length=300)


class CrossDomainOpportunity(BaseModel):
    """Cross-domain analytical opportunity."""
    opportunity_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=1000)
    primary_domain: str = Field(..., min_length=3, max_length=50)
    connected_domains: List[str] = Field(..., min_items=1)
    business_value_proposition: str = Field(..., min_length=10, max_length=500)
    surprise_factor: str = Field(..., min_length=10, max_length=500)
    implementation_complexity: str = Field(..., pattern="^(low|medium|high)$")
    confidence_level: float = Field(..., ge=0, le=1)
    required_capabilities: List[RequiredCapability] = Field(default_factory=list)


class PredictiveOpportunity(BaseModel):
    """Predictive analytics opportunity."""
    prediction_target: str = Field(..., min_length=3, max_length=100)
    prediction_horizon: str = Field(..., min_length=3, max_length=100)
    input_signals: List[str] = Field(..., min_items=1)
    business_impact: str = Field(..., min_length=10, max_length=300)
    accuracy_requirements: str = Field(..., min_length=5, max_length=200)


class OptimizationOpportunity(BaseModel):
    """Optimization analytics opportunity."""
    optimization_target: str = Field(..., min_length=3, max_length=100)
    constraints: List[str] = Field(..., min_items=1)
    decision_variables: List[str] = Field(..., min_items=1)
    expected_improvement: str = Field(..., min_length=5, max_length=300)


class AnalyticalOpportunities(BaseModel):
    """Discovered analytical opportunities that extend beyond explicit requirements."""
    cross_domain_opportunities: List[CrossDomainOpportunity] = Field(default_factory=list)
    predictive_opportunities: List[PredictiveOpportunity] = Field(default_factory=list)
    optimization_opportunities: List[OptimizationOpportunity] = Field(default_factory=list)


class TemporalPattern(BaseModel):
    """Temporal pattern in business context."""
    pattern: str = Field(..., min_length=3, max_length=100)
    frequency: str = Field(..., min_length=3, max_length=50)
    business_relevance: str = Field(..., min_length=5, max_length=300)


class VersioningStrategy(BaseModel):
    """Data versioning strategy."""
    bi_temporal_required: bool = Field(default=False)
    audit_trail_depth: str = Field(..., min_length=3, max_length=100)
    historical_analysis_needs: List[str] = Field(default_factory=list)


class TimeDimension(BaseModel):
    """Time dimension configuration."""
    temporal_granularities: List[str] = Field(default_factory=list)
    temporal_patterns: List[TemporalPattern] = Field(default_factory=list)
    versioning_strategy: Optional[VersioningStrategy] = None

    @validator('temporal_granularities')
    def validate_granularities(cls, v):
        valid_granularities = ["millisecond", "second", "minute", "hour", "day", "week", "month", "quarter", "year"]
        for granularity in v:
            if granularity not in valid_granularities:
                raise ValueError(f"Invalid temporal granularity: {granularity}")
        return v


class SpatialRelationship(BaseModel):
    """Spatial relationship between entities."""
    relationship: str = Field(..., min_length=3, max_length=100)
    entities: List[str] = Field(..., min_items=2)
    analysis_value: str = Field(..., min_length=5, max_length=300)


class SpaceDimension(BaseModel):
    """Space dimension configuration."""
    spatial_scales: List[str] = Field(default_factory=list)
    coordinate_systems: List[str] = Field(default_factory=list)
    spatial_relationships: List[SpatialRelationship] = Field(default_factory=list)

    @validator('spatial_scales')
    def validate_spatial_scales(cls, v):
        valid_scales = ["point", "local", "regional", "national", "continental", "global"]
        for scale in v:
            if scale not in valid_scales:
                raise ValueError(f"Invalid spatial scale: {scale}")
        return v


class OntologyMapping(BaseModel):
    """Ontology concept mapping."""
    source_concept: str = Field(..., min_length=2, max_length=100)
    target_concept: str = Field(..., min_length=2, max_length=100)
    mapping_type: str = Field(..., min_length=3, max_length=50)
    confidence: float = Field(..., ge=0, le=1)


class DomainDimension(BaseModel):
    """Domain dimension configuration."""
    primary_domains: List[str] = Field(..., min_items=1)
    connected_domains: List[str] = Field(default_factory=list)
    ontology_mappings: List[OntologyMapping] = Field(default_factory=list)


class ImplicitKnowledge(BaseModel):
    """Implicit knowledge captured during inference."""
    knowledge_type: str = Field(..., min_length=3, max_length=100)
    source: str = Field(..., min_length=5, max_length=200)
    application: str = Field(..., min_length=5, max_length=300)
    validation_method: str = Field(..., min_length=5, max_length=200)


class LearningOpportunity(BaseModel):
    """Machine learning opportunity."""
    learning_target: str = Field(..., min_length=3, max_length=100)
    data_sources: List[str] = Field(..., min_items=1)
    methodology: str = Field(..., min_length=3, max_length=100)
    business_application: str = Field(..., min_length=5, max_length=300)


class KnowledgeDimension(BaseModel):
    """Knowledge dimension configuration."""
    implicit_knowledge_captured: List[ImplicitKnowledge] = Field(default_factory=list)
    learning_opportunities: List[LearningOpportunity] = Field(default_factory=list)


class FourDimensionalContext(BaseModel):
    """Complete 4D context expansion for ET(K)L platform capabilities."""
    time_dimension: Optional[TimeDimension] = None
    space_dimension: Optional[SpaceDimension] = None
    domain_dimension: Optional[DomainDimension] = None
    knowledge_dimension: Optional[KnowledgeDimension] = None


class OntologyUsed(BaseModel):
    """Ontology used in inference process."""
    ontology_name: str = Field(..., min_length=3, max_length=100)
    version: str = Field(..., min_length=1, max_length=20)
    coverage: str = Field(..., min_length=5, max_length=200)


class InferenceConfidence(BaseModel):
    """Confidence levels for different inference types."""
    spatial_inferences: float = Field(default=0.0, ge=0, le=1)
    temporal_inferences: float = Field(default=0.0, ge=0, le=1)
    domain_inferences: float = Field(default=0.0, ge=0, le=1)
    cross_domain_inferences: float = Field(default=0.0, ge=0, le=1)


class ReasoningStep(BaseModel):
    """Step in reasoning trace."""
    step: int = Field(..., ge=1)
    rule_applied: str = Field(..., min_length=3, max_length=100)
    input: str = Field(..., min_length=5, max_length=500)
    output: str = Field(..., min_length=5, max_length=500)
    confidence: float = Field(..., ge=0, le=1)


class InferenceMetadata(BaseModel):
    """Metadata about the inference process and reasoning applied."""
    reasoning_engine_version: str = Field(..., min_length=3, max_length=50)
    ontologies_used: List[OntologyUsed] = Field(default_factory=list)
    inference_confidence: Optional[InferenceConfidence] = None
    reasoning_trace: List[ReasoningStep] = Field(default_factory=list)


class SessionParticipant(BaseModel):
    """Participant in elicitation session."""
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=3, max_length=100)
    expertise_areas: List[str] = Field(default_factory=list)


class ElicitationStep(BaseModel):
    """Step in elicitation flow."""
    step: int = Field(..., ge=1)
    question_type: str = Field(..., min_length=3, max_length=100)
    question: str = Field(..., min_length=5, max_length=1000)
    response: str = Field(..., min_length=1, max_length=2000)
    inferences_triggered: List[str] = Field(default_factory=list)


class BusinessValidation(BaseModel):
    """Business validation of discovered opportunities."""
    opportunities_presented: int = Field(..., ge=0)
    opportunities_accepted: int = Field(..., ge=0)
    opportunities_modified: int = Field(..., ge=0)
    opportunities_rejected: int = Field(..., ge=0)
    business_feedback: List[str] = Field(default_factory=list)

    @validator('opportunities_accepted', 'opportunities_modified', 'opportunities_rejected')
    def validate_opportunity_counts(cls, v, values):
        if 'opportunities_presented' in values:
            total = v + values.get('opportunities_accepted', 0) + values.get('opportunities_modified', 0) + values.get('opportunities_rejected', 0)
            if total > values['opportunities_presented']:
                raise ValueError("Total processed opportunities cannot exceed presented opportunities")
        return v


class ElicitationSession(BaseModel):
    """Metadata about the business elicitation session."""
    session_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    participants: List[SessionParticipant] = Field(..., min_items=1)
    elicitation_flow: List[ElicitationStep] = Field(default_factory=list)
    business_validation: Optional[BusinessValidation] = None


class SemanticStatementOfWork(BaseModel):
    """
    Revolutionary Semantic Statement of Work Schema
    
    Captures explicit business needs while intelligently inferring implicit requirements
    for 4D analytical platforms. This is the cornerstone where ET(K)L begins.
    """
    context: JSONLDContext = Field(default_factory=JSONLDContext, alias="@context")
    type: Literal["SemanticStatementOfWork"] = Field(default="SemanticStatementOfWork", alias="@type")
    
    # Core sections
    explicit_requirements: ExplicitRequirements
    inferred_context: InferredContext
    analytical_opportunities: AnalyticalOpportunities
    four_dimensional_context: FourDimensionalContext
    inference_metadata: InferenceMetadata
    elicitation_session: Optional[ElicitationSession] = None

    class Config:
        """Pydantic configuration."""
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"
        schema_extra = {
            "example": {
                "@context": {
                    "@base": "https://agentic-data-scraper.com/sow/",
                    "business": "https://schema.org/",
                    "supply": "https://gs1.org/ontology/",
                    "finance": "https://spec.edmcouncil.org/fibo/",
                    "geo": "http://www.geonames.org/ontology#",
                    "time": "http://www.w3.org/2006/time#"
                },
                "@type": "SemanticStatementOfWork",
                "explicit_requirements": {
                    "business_challenge": {
                        "description": "We need to track supplier performance across our global supply chain to reduce costs and improve quality.",
                        "entities_to_track": [
                            {
                                "entity": "suppliers",
                                "importance": "critical",
                                "semantic_type": "supply:Supplier",
                                "business_context": "Performance evaluation and risk assessment"
                            }
                        ],
                        "spatial_context": {
                            "geographic_scope": "global"
                        }
                    },
                    "desired_outcomes": [
                        {
                            "outcome": "Reduce supplier costs by 15%",
                            "priority": "must-have",
                            "business_value": "Direct cost savings of $2M annually"
                        }
                    ]
                },
                "inferred_context": {
                    "spatial_inferences": {
                        "geographic_analysis_opportunities": [
                            {
                                "analysis_type": "Geographic Risk Assessment",
                                "reasoning": "Global supplier network implies geographic risk analysis needs",
                                "confidence": 0.9,
                                "potential_value": "Identify high-risk supplier regions",
                                "required_data": ["supplier_locations", "geopolitical_risk_indices"]
                            }
                        ]
                    }
                },
                "analytical_opportunities": {
                    "cross_domain_opportunities": [
                        {
                            "title": "Financial Impact Analysis of Supply Chain Disruptions",
                            "description": "Analyze financial impact of supply chain disruptions using predictive analytics",
                            "primary_domain": "supply_chain",
                            "connected_domains": ["finance", "risk_management"],
                            "business_value_proposition": "Proactive financial risk management",
                            "surprise_factor": "Reveals hidden financial risks in supply chain",
                            "implementation_complexity": "medium",
                            "confidence_level": 0.85
                        }
                    ]
                },
                "four_dimensional_context": {
                    "domain_dimension": {
                        "primary_domains": ["supply_chain"],
                        "connected_domains": ["finance", "operations"]
                    }
                },
                "inference_metadata": {
                    "reasoning_engine_version": "1.0.0",
                    "inference_confidence": {
                        "spatial_inferences": 0.9,
                        "cross_domain_inferences": 0.85
                    }
                }
            }
        }

    def get_inferred_opportunities_count(self) -> int:
        """Get total count of inferred opportunities."""
        count = 0
        if self.inferred_context.spatial_inferences:
            count += len(self.inferred_context.spatial_inferences.geographic_analysis_opportunities)
        if self.inferred_context.temporal_inferences:
            count += len(self.inferred_context.temporal_inferences.time_series_opportunities)
        if self.inferred_context.domain_inferences:
            count += len(self.inferred_context.domain_inferences.supply_chain_analytics)
            count += len(self.inferred_context.domain_inferences.financial_analytics)
            count += len(self.inferred_context.domain_inferences.compliance_analytics)
        if self.inferred_context.graph_inferences:
            count += len(self.inferred_context.graph_inferences.relationship_networks)
            count += len(self.inferred_context.graph_inferences.dependency_analysis)
        count += len(self.analytical_opportunities.cross_domain_opportunities)
        count += len(self.analytical_opportunities.predictive_opportunities)
        count += len(self.analytical_opportunities.optimization_opportunities)
        return count

    def get_high_confidence_opportunities(self, threshold: float = 0.8) -> List[CrossDomainOpportunity]:
        """Get cross-domain opportunities with confidence above threshold."""
        return [
            opp for opp in self.analytical_opportunities.cross_domain_opportunities
            if opp.confidence_level >= threshold
        ]

    def get_primary_domains(self) -> List[str]:
        """Get primary domains mentioned in requirements."""
        if self.four_dimensional_context.domain_dimension:
            return self.four_dimensional_context.domain_dimension.primary_domains
        return []

    def get_connected_domains(self) -> List[str]:
        """Get domains connected through cross-domain opportunities."""
        connected = set()
        for opp in self.analytical_opportunities.cross_domain_opportunities:
            connected.update(opp.connected_domains)
        if self.four_dimensional_context.domain_dimension:
            connected.update(self.four_dimensional_context.domain_dimension.connected_domains)
        return list(connected)