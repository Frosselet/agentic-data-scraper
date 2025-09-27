"""
BAML-powered discovery service for the source discovery assistant.
Integrates BAML agents with the React UI components.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import asyncio
import json
from pathlib import Path

# Import BAML generated client (will be available after baml build)
try:
    import sys
    from pathlib import Path
    # Add project root to path for baml_client import
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

    from baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    print("BAML client not available. Run 'baml build' to generate client.")

@dataclass
class BusinessContext:
    question: str
    success_criteria: str
    timeline: str
    budget: str
    risk_tolerance: str
    persona_id: str
    interaction_level: str = "standard"

@dataclass
class DataSourceRecommendation:
    name: str
    type: str
    description: str
    feasibility_score: float
    cost_estimate: str
    implementation_effort: str
    platform_compatibility: float
    data_quality_expected: float
    access_requirements: List[str]
    sample_data_url: Optional[str]
    documentation_url: Optional[str]
    pros: List[str]
    cons: List[str]
    semantic_vocabularies: List[str]

@dataclass
class FeasibilityAnalysis:
    overall_feasibility: str
    technical_risks: List[str]
    business_risks: List[str]
    mitigation_strategies: List[str]
    platform_gaps: List[str]
    recommended_alternatives: List[str]
    estimated_timeline_weeks: int
    confidence_level: float

@dataclass
class SOWContract:
    project_title: str
    executive_summary: str
    business_objectives: List[str]
    success_metrics: List[str]
    data_sources: List[DataSourceRecommendation]
    technical_approach: str
    deliverables: List[str]
    timeline_weeks: int
    cost_estimate: str
    risk_assessment: str
    acceptance_criteria: List[str]
    semantic_framework: str

class BAMLDiscoveryService:
    """Service class that orchestrates BAML agents for the discovery workflow."""
    
    def __init__(self):
        self.platform_capabilities = [
            "REST API Integration - 500+ successful implementations",
            "Semantic Web Technologies - SKOS, SPARQL, OWL support",
            "Real-time Processing - KuzuDB graph database",
            "Authentication - OAuth 2.0, API tokens, certificates",
            "Data Transformation - Advanced semantic mapping",
            "Quality Monitoring - Comprehensive validation and alerting"
        ]
        
        self.platform_limitations = [
            "Computer Vision - Limited OCR capabilities",
            "Legacy Database Access - Prefer API-mediated access", 
            "Real-time Trading Data - High cost, suggest alternatives",
            "Large File Processing - Better for streaming than batch"
        ]

    async def process_business_context(
        self,
        question: str,
        success_criteria: str,
        timeline: str,
        budget: str,
        risk_tolerance: str,
        persona_id: str
    ) -> BusinessContext:
        """Process business context using BAML BusinessContextAgent."""
        
        if not BAML_AVAILABLE:
            # Fallback for development without BAML
            return BusinessContext(
                question=question,
                success_criteria=success_criteria,
                timeline=timeline,
                budget=budget,
                risk_tolerance=risk_tolerance,
                persona_id=persona_id,
                interaction_level=self._get_interaction_level(persona_id)
            )
        
        try:
            # Call BAML agent
            context = await b.BusinessContextAgent(
                business_question=question,
                success_criteria=success_criteria,
                timeline=timeline,
                budget=budget,
                risk_tolerance=risk_tolerance,
                persona_id=persona_id
            )
            
            return BusinessContext(
                question=context.question,
                success_criteria=context.success_criteria,
                timeline=context.timeline,
                budget=context.budget,
                risk_tolerance=context.risk_tolerance,
                persona_id=context.persona_id,
                interaction_level=context.interaction_level
            )
            
        except Exception as e:
            print(f"BAML BusinessContextAgent error: {e}")
            # Fallback to basic processing
            return BusinessContext(
                question=question,
                success_criteria=success_criteria,
                timeline=timeline,
                budget=budget,
                risk_tolerance=risk_tolerance,
                persona_id=persona_id,
                interaction_level=self._get_interaction_level(persona_id)
            )

    async def discover_sources(
        self,
        business_context: BusinessContext
    ) -> List[DataSourceRecommendation]:
        """Discover data sources using BAML SourceDiscoveryAgent."""
        
        if not BAML_AVAILABLE:
            # Fallback recommendations for development
            return self._get_fallback_recommendations(business_context)
        
        try:
            # Call BAML agent
            recommendations = await b.SourceDiscoveryAgent(
                business_context=asdict(business_context),
                platform_capabilities=self.platform_capabilities
            )
            
            return [
                DataSourceRecommendation(
                    name=rec.name,
                    type=rec.type,
                    description=rec.description,
                    feasibility_score=rec.feasibility_score,
                    cost_estimate=rec.cost_estimate,
                    implementation_effort=rec.implementation_effort,
                    platform_compatibility=rec.platform_compatibility,
                    data_quality_expected=rec.data_quality_expected,
                    access_requirements=rec.access_requirements,
                    sample_data_url=rec.sample_data_url,
                    documentation_url=rec.documentation_url,
                    pros=rec.pros,
                    cons=rec.cons,
                    semantic_vocabularies=rec.semantic_vocabularies
                )
                for rec in recommendations
            ]
            
        except Exception as e:
            print(f"BAML SourceDiscoveryAgent error: {e}")
            return self._get_fallback_recommendations(business_context)

    async def analyze_feasibility(
        self,
        business_context: BusinessContext,
        selected_sources: List[DataSourceRecommendation]
    ) -> FeasibilityAnalysis:
        """Analyze feasibility using BAML FeasibilityAnalyzerAgent."""
        
        if not BAML_AVAILABLE:
            return self._get_fallback_feasibility(business_context, selected_sources)
        
        try:
            analysis = await b.FeasibilityAnalyzerAgent(
                business_context=asdict(business_context),
                recommended_sources=[asdict(source) for source in selected_sources]
            )
            
            return FeasibilityAnalysis(
                overall_feasibility=analysis.overall_feasibility,
                technical_risks=analysis.technical_risks,
                business_risks=analysis.business_risks,
                mitigation_strategies=analysis.mitigation_strategies,
                platform_gaps=analysis.platform_gaps,
                recommended_alternatives=analysis.recommended_alternatives,
                estimated_timeline_weeks=analysis.estimated_timeline_weeks,
                confidence_level=analysis.confidence_level
            )
            
        except Exception as e:
            print(f"BAML FeasibilityAnalyzerAgent error: {e}")
            return self._get_fallback_feasibility(business_context, selected_sources)

    async def generate_sow(
        self,
        business_context: BusinessContext,
        selected_sources: List[DataSourceRecommendation],
        feasibility_analysis: FeasibilityAnalysis
    ) -> SOWContract:
        """Generate SOW using BAML SOWGeneratorAgent."""
        
        if not BAML_AVAILABLE:
            return self._get_fallback_sow(business_context, selected_sources, feasibility_analysis)
        
        try:
            sow = await b.SOWGeneratorAgent(
                business_context=asdict(business_context),
                selected_sources=[asdict(source) for source in selected_sources],
                feasibility_analysis=asdict(feasibility_analysis)
            )
            
            return SOWContract(
                project_title=sow.project_title,
                executive_summary=sow.executive_summary,
                business_objectives=sow.business_objectives,
                success_metrics=sow.success_metrics,
                data_sources=selected_sources,
                technical_approach=sow.technical_approach,
                deliverables=sow.deliverables,
                timeline_weeks=sow.timeline_weeks,
                cost_estimate=sow.cost_estimate,
                risk_assessment=sow.risk_assessment,
                acceptance_criteria=sow.acceptance_criteria,
                semantic_framework=sow.semantic_framework
            )
            
        except Exception as e:
            print(f"BAML SOWGeneratorAgent error: {e}")
            return self._get_fallback_sow(business_context, selected_sources, feasibility_analysis)

    async def adapt_response_for_persona(
        self,
        base_response: str,
        persona_id: str,
        interaction_level: str,
        technical_depth: str
    ) -> str:
        """Adapt response for specific persona using BAML PersonaResponseAgent."""
        
        if not BAML_AVAILABLE:
            return base_response
        
        try:
            adapted_response = await b.PersonaResponseAgent(
                base_response=base_response,
                persona_id=persona_id,
                interaction_level=interaction_level,
                technical_depth=technical_depth
            )
            return adapted_response
            
        except Exception as e:
            print(f"BAML PersonaResponseAgent error: {e}")
            return base_response

    async def assess_platform_capability(
        self,
        data_sources: List[str],
        requirements: List[str]
    ) -> Dict[str, float]:
        """Assess platform capability using BAML PlatformCapabilityAgent."""
        
        if not BAML_AVAILABLE:
            return {source: 0.8 for source in data_sources}  # Default high capability
        
        try:
            capabilities = await b.PlatformCapabilityAgent(
                data_sources=data_sources,
                requirements=requirements
            )
            return capabilities
            
        except Exception as e:
            print(f"BAML PlatformCapabilityAgent error: {e}")
            return {source: 0.8 for source in data_sources}

    # Helper methods for fallback functionality
    def _get_interaction_level(self, persona_id: str) -> str:
        """Map persona to default interaction level."""
        persona_map = {
            "trader": "rapid",
            "business_analyst": "standard", 
            "data_analyst": "technical",
            "data_lead": "technical"
        }
        return persona_map.get(persona_id, "standard")

    def _get_fallback_recommendations(self, context: BusinessContext) -> List[DataSourceRecommendation]:
        """Fallback recommendations for development."""
        base_recommendations = [
            DataSourceRecommendation(
                name="Government Open Data Portal",
                type="api",
                description="Comprehensive government datasets via REST API",
                feasibility_score=0.9,
                cost_estimate="Free - $500/month",
                implementation_effort="low",
                platform_compatibility=0.95,
                data_quality_expected=0.85,
                access_requirements=["API key registration"],
                sample_data_url="https://api.data.gov/docs",
                documentation_url="https://api.data.gov/docs",
                pros=["High reliability", "Good documentation", "Free tier available"],
                cons=["Rate limits", "Data may not be real-time"],
                semantic_vocabularies=["SKOS Government Vocabularies", "Dublin Core"]
            ),
            DataSourceRecommendation(
                name="Industry Trade Association APIs",
                type="api",
                description="Sector-specific data from industry associations",
                feasibility_score=0.75,
                cost_estimate="$1,000 - $5,000/month",
                implementation_effort="medium",
                platform_compatibility=0.8,
                data_quality_expected=0.9,
                access_requirements=["Membership verification", "OAuth 2.0"],
                sample_data_url=None,
                documentation_url="https://example-industry-api.org/docs",
                pros=["High data quality", "Industry-specific insights", "Regular updates"],
                cons=["Higher cost", "Membership requirements"],
                semantic_vocabularies=["Industry-specific SKOS", "Business ontologies"]
            )
        ]
        
        # Filter based on persona and context
        if context.persona_id == "trader":
            return [r for r in base_recommendations if "real-time" not in r.cons[0].lower()]
        
        return base_recommendations

    def _get_fallback_feasibility(self, context: BusinessContext, sources: List[DataSourceRecommendation]) -> FeasibilityAnalysis:
        """Fallback feasibility analysis."""
        return FeasibilityAnalysis(
            overall_feasibility="high",
            technical_risks=["API rate limits", "Data format variations"],
            business_risks=["Timeline constraints", "Budget overruns"],
            mitigation_strategies=["Implement robust retry logic", "Phase delivery approach"],
            platform_gaps=["Limited real-time processing for high-volume sources"],
            recommended_alternatives=["Use cached data with periodic updates"],
            estimated_timeline_weeks=8,
            confidence_level=0.8
        )

    def _get_fallback_sow(self, context: BusinessContext, sources: List[DataSourceRecommendation], analysis: FeasibilityAnalysis) -> SOWContract:
        """Fallback SOW generation."""
        return SOWContract(
            project_title=f"Data Integration Solution: {context.question[:50]}...",
            executive_summary="Comprehensive data integration solution to address business requirements using proven platform capabilities.",
            business_objectives=[context.success_criteria],
            success_metrics=["Data quality > 85%", "System uptime > 99%", "Response time < 2s"],
            data_sources=sources,
            technical_approach="REST API integration with semantic enrichment using SKOS vocabularies and KuzuDB graph storage.",
            deliverables=["Data ingestion pipelines", "Quality monitoring dashboard", "Documentation", "Training materials"],
            timeline_weeks=analysis.estimated_timeline_weeks,
            cost_estimate=context.budget,
            risk_assessment="Medium risk with proven mitigation strategies in place.",
            acceptance_criteria=["All data sources successfully integrated", "Quality thresholds met", "Documentation complete"],
            semantic_framework="SKOS-based semantic mapping with multilingual support and ontology alignment"
        )

# Factory function for easy integration
def create_discovery_service() -> BAMLDiscoveryService:
    """Factory function to create discovery service instance."""
    return BAMLDiscoveryService()