"""
Intelligent Source Recommendation System

Advanced recommendation engine that analyzes discovered data sources,
applies machine learning techniques for relevance scoring, and provides
executive summary recommendations for decision makers.

Key Features:
- Multi-criteria recommendation scoring
- Business impact assessment
- Risk and feasibility analysis
- Executive summary generation
- Source comparison and ranking
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import json
import re

from .data_discovery import DataSource, DiscoveryContext
from .base import BaseAgent
from ..semantic.skos_router import SKOSSemanticRouter

logger = logging.getLogger(__name__)


@dataclass
class SourceRecommendation:
    """Enhanced recommendation for a data source"""
    source: DataSource
    recommendation_score: float  # 0.0 to 1.0 overall recommendation
    business_impact: str  # 'high', 'medium', 'low'
    implementation_effort: str  # 'low', 'medium', 'high'
    risk_level: str  # 'low', 'medium', 'high'
    key_benefits: List[str]
    potential_concerns: List[str]
    recommended_use_cases: List[str]
    integration_complexity: str
    cost_estimate: str
    timeline_estimate: str
    next_steps: List[str]


@dataclass
class ExecutiveSummary:
    """Executive summary of discovery and recommendations"""
    total_sources_discovered: int
    recommended_sources: int
    top_recommendation: Optional[SourceRecommendation]
    key_findings: List[str]
    strategic_recommendations: List[str]
    risk_mitigation_strategies: List[str]
    estimated_total_cost: str
    estimated_implementation_timeline: str
    success_metrics: List[str]
    generated_at: str


class SourceRecommendationEngine(BaseAgent):
    """
    Intelligent recommendation engine for data sources.

    Analyzes discovered sources through multiple lenses:
    - Business value alignment
    - Technical feasibility
    - Risk assessment
    - Cost-benefit analysis
    - Strategic fit
    """

    def __init__(
        self,
        agent_id: str = "source_recommender",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 300
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.recommendation_criteria = self._initialize_criteria()
        self.risk_factors = self._initialize_risk_factors()

    def _initialize_criteria(self) -> Dict[str, Dict[str, float]]:
        """Initialize recommendation scoring criteria"""
        return {
            "business_value": {
                "strategic_alignment": 0.3,  # How well it aligns with business strategy
                "revenue_impact": 0.25,      # Potential revenue/savings impact
                "competitive_advantage": 0.2, # Unique insights/advantages
                "user_adoption_potential": 0.15, # Likelihood of user adoption
                "scalability": 0.1           # Growth potential
            },
            "technical_feasibility": {
                "integration_complexity": 0.3, # Ease of integration
                "data_quality": 0.25,          # Quality and reliability
                "technical_requirements": 0.2,  # Infrastructure needs
                "maintenance_overhead": 0.15,   # Ongoing maintenance
                "documentation_quality": 0.1   # Available documentation
            },
            "risk_assessment": {
                "data_security": 0.3,       # Security and privacy risks
                "vendor_reliability": 0.25,  # Vendor/source reliability
                "compliance_risk": 0.2,     # Regulatory compliance
                "dependency_risk": 0.15,    # Lock-in and dependencies
                "cost_overrun_risk": 0.1    # Budget risk
            },
            "cost_benefit": {
                "implementation_cost": 0.3,  # Upfront costs
                "operational_cost": 0.25,    # Ongoing costs
                "time_to_value": 0.2,        # How quickly benefits are realized
                "roi_potential": 0.15,       # Return on investment
                "hidden_costs": 0.1          # Unexpected costs
            }
        }

    def _initialize_risk_factors(self) -> Dict[str, List[str]]:
        """Initialize risk assessment factors"""
        return {
            "high_risk_indicators": [
                "subscription required",
                "proprietary format",
                "limited documentation",
                "single vendor dependency",
                "compliance unclear",
                "beta/experimental"
            ],
            "medium_risk_indicators": [
                "api rate limits",
                "registration required",
                "irregular updates",
                "limited support",
                "data quality varies"
            ],
            "low_risk_indicators": [
                "public/open data",
                "standard formats",
                "well documented",
                "government source",
                "regular updates",
                "community support"
            ]
        }

    async def _process(
        self,
        discovered_sources: List[DataSource],
        discovery_context: DiscoveryContext,
        business_priorities: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Tuple[List[SourceRecommendation], ExecutiveSummary]:
        """
        Generate intelligent recommendations and executive summary.

        Args:
            discovered_sources: Sources from discovery agent
            discovery_context: Business context from canvas
            business_priorities: Optional priority weights

        Returns:
            Tuple of (recommendations, executive_summary)
        """

        self.logger.info(f"Generating recommendations for {len(discovered_sources)} sources")

        # Generate detailed recommendations for each source
        recommendations = []
        for source in discovered_sources:
            recommendation = await self._generate_source_recommendation(
                source, discovery_context, business_priorities
            )
            recommendations.append(recommendation)

        # Sort by recommendation score
        recommendations.sort(key=lambda r: r.recommendation_score, reverse=True)

        # Generate executive summary
        executive_summary = await self._generate_executive_summary(
            recommendations, discovery_context
        )

        self.logger.info(f"Generated {len(recommendations)} recommendations")

        return recommendations, executive_summary

    async def _generate_source_recommendation(
        self,
        source: DataSource,
        context: DiscoveryContext,
        priorities: Optional[Dict[str, str]]
    ) -> SourceRecommendation:
        """Generate detailed recommendation for a single source"""

        # Calculate multi-criteria scores
        business_score = await self._assess_business_value(source, context)
        technical_score = await self._assess_technical_feasibility(source, context)
        risk_score = await self._assess_risk_level(source, context)
        cost_benefit_score = await self._assess_cost_benefit(source, context)

        # Calculate weighted recommendation score
        weights = {
            "business_value": 0.35,
            "technical_feasibility": 0.25,
            "risk_assessment": 0.25,
            "cost_benefit": 0.15
        }

        # Apply priority adjustments if provided
        if priorities:
            if priorities.get("priority") == "fast_implementation":
                weights["technical_feasibility"] += 0.1
                weights["business_value"] -= 0.1
            elif priorities.get("priority") == "high_value":
                weights["business_value"] += 0.1
                weights["risk_assessment"] -= 0.1

        recommendation_score = (
            business_score * weights["business_value"] +
            technical_score * weights["technical_feasibility"] +
            (1.0 - risk_score) * weights["risk_assessment"] +  # Lower risk = higher score
            cost_benefit_score * weights["cost_benefit"]
        )

        # Determine categorical assessments
        business_impact = self._categorize_score(business_score)
        implementation_effort = self._categorize_effort(technical_score)
        risk_level = self._categorize_score(risk_score)

        # Generate insights and recommendations
        key_benefits = await self._identify_key_benefits(source, context)
        potential_concerns = await self._identify_concerns(source, context)
        use_cases = await self._suggest_use_cases(source, context)
        next_steps = await self._generate_next_steps(source, context)

        return SourceRecommendation(
            source=source,
            recommendation_score=recommendation_score,
            business_impact=business_impact,
            implementation_effort=implementation_effort,
            risk_level=risk_level,
            key_benefits=key_benefits,
            potential_concerns=potential_concerns,
            recommended_use_cases=use_cases,
            integration_complexity=self._assess_integration_complexity(source),
            cost_estimate=self._estimate_costs(source),
            timeline_estimate=self._estimate_timeline(source),
            next_steps=next_steps
        )

    async def _assess_business_value(self, source: DataSource, context: DiscoveryContext) -> float:
        """Assess business value alignment"""
        score = 0.0
        criteria = self.recommendation_criteria["business_value"]

        # Strategic alignment
        domain_match = 1.0 if context.business_domain in source.business_domains else 0.3
        strategic_score = domain_match * 0.8 + source.relevance_score * 0.2
        score += strategic_score * criteria["strategic_alignment"]

        # Revenue impact (based on data type and business context)
        revenue_impact = self._assess_revenue_potential(source, context)
        score += revenue_impact * criteria["revenue_impact"]

        # Competitive advantage
        uniqueness_score = self._assess_data_uniqueness(source)
        score += uniqueness_score * criteria["competitive_advantage"]

        # User adoption potential
        adoption_score = self._assess_adoption_potential(source, context)
        score += adoption_score * criteria["user_adoption_potential"]

        # Scalability
        scalability_score = self._assess_scalability(source)
        score += scalability_score * criteria["scalability"]

        return min(1.0, max(0.0, score))

    async def _assess_technical_feasibility(self, source: DataSource, context: DiscoveryContext) -> float:
        """Assess technical implementation feasibility"""
        score = 0.0
        criteria = self.recommendation_criteria["technical_feasibility"]

        # Integration complexity (inverse scoring - easier = higher score)
        complexity_score = 1.0 - self._calculate_integration_complexity(source)
        score += complexity_score * criteria["integration_complexity"]

        # Data quality
        score += source.quality_score * criteria["data_quality"]

        # Technical requirements alignment
        tech_alignment = self._assess_tech_requirements_alignment(source, context)
        score += tech_alignment * criteria["technical_requirements"]

        # Maintenance overhead (inverse scoring)
        maintenance_score = 1.0 - self._estimate_maintenance_overhead(source)
        score += maintenance_score * criteria["maintenance_overhead"]

        # Documentation quality
        doc_score = self._assess_documentation_quality(source)
        score += doc_score * criteria["documentation_quality"]

        return min(1.0, max(0.0, score))

    async def _assess_risk_level(self, source: DataSource, context: DiscoveryContext) -> float:
        """Assess risk level (higher score = higher risk)"""
        risk_score = 0.0
        criteria = self.recommendation_criteria["risk_assessment"]

        # Check for risk indicators
        source_text = f"{source.title} {source.description} {source.access_method}".lower()

        high_risk_count = sum(1 for indicator in self.risk_factors["high_risk_indicators"]
                             if indicator in source_text)
        medium_risk_count = sum(1 for indicator in self.risk_factors["medium_risk_indicators"]
                               if indicator in source_text)
        low_risk_count = sum(1 for indicator in self.risk_factors["low_risk_indicators"]
                            if indicator in source_text)

        # Calculate base risk score
        total_indicators = high_risk_count + medium_risk_count + low_risk_count
        if total_indicators > 0:
            base_risk = (high_risk_count * 1.0 + medium_risk_count * 0.5 + low_risk_count * 0.0) / total_indicators
        else:
            base_risk = 0.5  # Default medium risk

        # Adjust based on source characteristics
        access_risk = {
            "public": 0.0, "registration": 0.2, "api_key": 0.3,
            "subscription": 0.6, "request": 0.4
        }.get(source.access_method, 0.5)

        update_risk = {
            "real-time": 0.1, "daily": 0.2, "weekly": 0.3,
            "monthly": 0.4, "quarterly": 0.6, "static": 0.8
        }.get(source.update_frequency, 0.5)

        # Combine risk factors
        risk_score = (base_risk * 0.4 + access_risk * 0.3 + update_risk * 0.3)

        return min(1.0, max(0.0, risk_score))

    async def _assess_cost_benefit(self, source: DataSource, context: DiscoveryContext) -> float:
        """Assess cost-benefit ratio"""
        # Simplified cost-benefit assessment
        # In a real implementation, this would integrate with pricing APIs and business models

        access_cost_score = {
            "public": 1.0, "registration": 0.9, "api_key": 0.7,
            "subscription": 0.4, "request": 0.6
        }.get(source.access_method, 0.5)

        # Higher quality and relevance sources justify higher costs
        value_score = (source.quality_score + source.relevance_score) / 2

        # Time to value based on update frequency
        ttv_score = {
            "real-time": 1.0, "daily": 0.9, "weekly": 0.8,
            "monthly": 0.6, "quarterly": 0.4, "static": 0.2
        }.get(source.update_frequency, 0.5)

        cost_benefit_score = (access_cost_score * 0.4 + value_score * 0.4 + ttv_score * 0.2)

        return min(1.0, max(0.0, cost_benefit_score))

    def _assess_revenue_potential(self, source: DataSource, context: DiscoveryContext) -> float:
        """Assess potential revenue impact"""
        # Check if source aligns with revenue-generating value propositions
        revenue_keywords = ["cost", "saving", "revenue", "profit", "efficiency", "optimization"]

        source_text = f"{source.title} {source.description}".lower()
        value_props_text = " ".join(context.value_propositions).lower()

        revenue_alignment = sum(1 for keyword in revenue_keywords
                               if keyword in source_text or keyword in value_props_text)

        return min(1.0, revenue_alignment / len(revenue_keywords))

    def _assess_data_uniqueness(self, source: DataSource) -> float:
        """Assess how unique/differentiated the data source is"""
        uniqueness_indicators = ["proprietary", "exclusive", "unique", "specialized", "custom"]
        commodity_indicators = ["standard", "common", "public", "basic", "generic"]

        source_text = f"{source.title} {source.description}".lower()

        unique_score = sum(1 for indicator in uniqueness_indicators if indicator in source_text)
        commodity_score = sum(1 for indicator in commodity_indicators if indicator in source_text)

        # Balance uniqueness with accessibility
        uniqueness_score = unique_score / max(1, len(uniqueness_indicators))
        commodity_penalty = commodity_score / max(1, len(commodity_indicators))

        return max(0.0, min(1.0, uniqueness_score - commodity_penalty * 0.5))

    def _assess_adoption_potential(self, source: DataSource, context: DiscoveryContext) -> float:
        """Assess likelihood of user adoption"""
        # Easier access methods have higher adoption potential
        access_scores = {
            "public": 1.0, "registration": 0.8, "api_key": 0.6,
            "subscription": 0.4, "request": 0.3
        }

        # Common formats have higher adoption
        format_scores = {"json": 1.0, "csv": 0.9, "xml": 0.7, "excel": 0.8}
        avg_format_score = sum(format_scores.get(fmt, 0.5) for fmt in source.data_formats) / len(source.data_formats)

        access_score = access_scores.get(source.access_method, 0.5)

        return (access_score * 0.6 + avg_format_score * 0.4)

    def _assess_scalability(self, source: DataSource) -> float:
        """Assess scalability potential"""
        scalable_types = ["api", "stream"]
        scalable_frequencies = ["real-time", "daily"]

        type_score = 1.0 if source.source_type in scalable_types else 0.5
        frequency_score = 1.0 if source.update_frequency in scalable_frequencies else 0.6

        return (type_score + frequency_score) / 2

    def _calculate_integration_complexity(self, source: DataSource) -> float:
        """Calculate integration complexity (0 = simple, 1 = complex)"""
        complexity_factors = {
            "source_type": {"api": 0.2, "download": 0.4, "portal": 0.3, "database": 0.7, "stream": 0.5},
            "access_method": {"public": 0.1, "registration": 0.2, "api_key": 0.3, "subscription": 0.5, "request": 0.6},
            "data_formats": {"json": 0.1, "csv": 0.2, "xml": 0.4, "excel": 0.3, "parquet": 0.2}
        }

        type_complexity = complexity_factors["source_type"].get(source.source_type, 0.5)
        access_complexity = complexity_factors["access_method"].get(source.access_method, 0.5)

        format_complexities = [complexity_factors["data_formats"].get(fmt, 0.5) for fmt in source.data_formats]
        avg_format_complexity = sum(format_complexities) / len(format_complexities)

        return (type_complexity * 0.4 + access_complexity * 0.3 + avg_format_complexity * 0.3)

    def _assess_tech_requirements_alignment(self, source: DataSource, context: DiscoveryContext) -> float:
        """Assess alignment with technical capabilities"""
        # Check if mentioned technologies align with source requirements
        tech_capabilities = " ".join(context.technical_capabilities).lower()

        alignment_score = 0.5  # Default neutral score

        if source.source_type == "api" and ("api" in tech_capabilities or "rest" in tech_capabilities):
            alignment_score += 0.3

        if source.source_type == "stream" and "streaming" in tech_capabilities:
            alignment_score += 0.3

        if any(fmt in tech_capabilities for fmt in source.data_formats):
            alignment_score += 0.2

        return min(1.0, alignment_score)

    def _estimate_maintenance_overhead(self, source: DataSource) -> float:
        """Estimate ongoing maintenance overhead"""
        overhead_factors = {
            "update_frequency": {"real-time": 0.8, "daily": 0.6, "weekly": 0.4, "monthly": 0.2, "static": 0.1},
            "access_method": {"public": 0.1, "registration": 0.2, "api_key": 0.4, "subscription": 0.6, "request": 0.3}
        }

        frequency_overhead = overhead_factors["update_frequency"].get(source.update_frequency, 0.5)
        access_overhead = overhead_factors["access_method"].get(source.access_method, 0.5)

        return (frequency_overhead + access_overhead) / 2

    def _assess_documentation_quality(self, source: DataSource) -> float:
        """Assess documentation quality based on available information"""
        # In a real implementation, this would check actual documentation
        # For now, we'll estimate based on source characteristics

        quality_indicators = {
            "government_portals": 0.8,
            "international_organizations": 0.9,
            "specialized_portals": 0.7,
            "academic_sources": 0.6,
            "web_search": 0.4
        }

        strategy = source.metadata.get("strategy", "web_search")
        base_quality = quality_indicators.get(strategy, 0.5)

        # Adjust based on source type
        if source.source_type == "api":
            base_quality += 0.1
        elif source.source_type == "portal":
            base_quality += 0.05

        return min(1.0, base_quality)

    def _categorize_score(self, score: float) -> str:
        """Categorize numeric score into text labels"""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"

    def _categorize_effort(self, technical_score: float) -> str:
        """Categorize technical score into effort labels (inverse)"""
        if technical_score >= 0.7:
            return "low"
        elif technical_score >= 0.4:
            return "medium"
        else:
            return "high"

    async def _identify_key_benefits(self, source: DataSource, context: DiscoveryContext) -> List[str]:
        """Identify key benefits of using this source"""
        benefits = []

        # Quality-based benefits
        if source.quality_score >= 0.8:
            benefits.append("High-quality, reliable data source")

        # Relevance-based benefits
        if source.relevance_score >= 0.8:
            benefits.append("Strong alignment with business requirements")

        # Access-based benefits
        if source.access_method == "public":
            benefits.append("No licensing costs or access restrictions")

        # Update frequency benefits
        if source.update_frequency in ["real-time", "daily"]:
            benefits.append("Timely data updates for current insights")

        # Format benefits
        if "json" in source.data_formats:
            benefits.append("API-friendly format for easy integration")

        # Strategic benefits
        strategy = source.metadata.get("strategy", "")
        if strategy == "government_portals":
            benefits.append("Authoritative government data source")
        elif strategy == "international_organizations":
            benefits.append("Global perspective from international organizations")

        return benefits[:5]  # Limit to top 5 benefits

    async def _identify_concerns(self, source: DataSource, context: DiscoveryContext) -> List[str]:
        """Identify potential concerns or limitations"""
        concerns = []

        # Quality concerns
        if source.quality_score < 0.6:
            concerns.append("Data quality may require additional validation")

        # Access concerns
        if source.access_method == "subscription":
            concerns.append("Ongoing subscription costs required")
        elif source.access_method == "request":
            concerns.append("Access requires approval process")

        # Update frequency concerns
        if source.update_frequency in ["quarterly", "static"]:
            concerns.append("Infrequent updates may limit real-time insights")

        # Integration concerns
        if source.source_type == "download":
            concerns.append("Manual download process may require automation")

        # Reliability concerns
        if not source.metadata.get("verified", False):
            concerns.append("Source reliability needs verification")

        return concerns[:4]  # Limit to top 4 concerns

    async def _suggest_use_cases(self, source: DataSource, context: DiscoveryContext) -> List[str]:
        """Suggest specific use cases for this source"""
        use_cases = []

        # Based on external data needs
        for need in context.external_data_needs[:3]:
            if any(word in source.title.lower() or word in source.description.lower()
                   for word in need.lower().split()):
                use_cases.append(f"Support for {need.lower()}")

        # Based on value propositions
        for prop in context.value_propositions[:2]:
            if any(word in source.description.lower() for word in prop.lower().split()[:3]):
                use_cases.append(f"Enable {prop.lower()}")

        # Generic use cases based on source type
        if source.source_type == "api":
            use_cases.append("Real-time data integration for dashboards")
        elif source.source_type == "portal":
            use_cases.append("Periodic data analysis and reporting")

        return use_cases[:4]  # Limit to top 4 use cases

    async def _generate_next_steps(self, source: DataSource, context: DiscoveryContext) -> List[str]:
        """Generate actionable next steps"""
        steps = []

        # Verification steps
        if not source.metadata.get("verified", False):
            steps.append("Verify source accessibility and data quality")

        # Access-related steps
        if source.access_method == "registration":
            steps.append("Complete registration process")
        elif source.access_method == "api_key":
            steps.append("Obtain API credentials")
        elif source.access_method == "subscription":
            steps.append("Evaluate subscription options and costs")

        # Technical steps
        if source.source_type == "api":
            steps.append("Review API documentation and rate limits")
        elif source.source_type == "download":
            steps.append("Set up automated download process")

        # Integration steps
        steps.append("Design data integration architecture")
        steps.append("Develop proof of concept implementation")

        return steps[:5]  # Limit to top 5 steps

    def _assess_integration_complexity(self, source: DataSource) -> str:
        """Assess integration complexity category"""
        complexity_score = self._calculate_integration_complexity(source)

        if complexity_score <= 0.3:
            return "low"
        elif complexity_score <= 0.6:
            return "medium"
        else:
            return "high"

    def _estimate_costs(self, source: DataSource) -> str:
        """Estimate cost category"""
        cost_factors = {
            "public": "Free",
            "registration": "Free (registration required)",
            "api_key": "Low (usage-based)",
            "subscription": "Medium to High (subscription)",
            "request": "Variable (depends on approval)"
        }

        return cost_factors.get(source.access_method, "Unknown")

    def _estimate_timeline(self, source: DataSource) -> str:
        """Estimate implementation timeline"""
        complexity = self._assess_integration_complexity(source)

        timelines = {
            "low": "1-2 weeks",
            "medium": "3-6 weeks",
            "high": "2-3 months"
        }

        return timelines.get(complexity, "Unknown")

    async def _generate_executive_summary(
        self,
        recommendations: List[SourceRecommendation],
        context: DiscoveryContext
    ) -> ExecutiveSummary:
        """Generate executive summary of recommendations"""

        recommended_sources = [r for r in recommendations if r.recommendation_score >= 0.6]
        top_recommendation = recommendations[0] if recommendations else None

        # Generate key findings
        key_findings = []
        if recommended_sources:
            key_findings.append(f"Identified {len(recommended_sources)} high-value data sources")

            high_impact_sources = [r for r in recommended_sources if r.business_impact == "high"]
            if high_impact_sources:
                key_findings.append(f"{len(high_impact_sources)} sources offer high business impact")

            low_effort_sources = [r for r in recommended_sources if r.implementation_effort == "low"]
            if low_effort_sources:
                key_findings.append(f"{len(low_effort_sources)} sources have low implementation effort")

        # Generate strategic recommendations
        strategic_recommendations = []
        if top_recommendation:
            strategic_recommendations.append(
                f"Prioritize implementation of {top_recommendation.source.title} for immediate impact"
            )

        quick_wins = [r for r in recommendations[:5]
                     if r.implementation_effort == "low" and r.business_impact in ["medium", "high"]]
        if quick_wins:
            strategic_recommendations.append(
                f"Focus on {len(quick_wins)} quick-win sources for rapid value delivery"
            )

        # Risk mitigation strategies
        risk_mitigation = []
        high_risk_sources = [r for r in recommended_sources if r.risk_level == "high"]
        if high_risk_sources:
            risk_mitigation.append("Develop contingency plans for high-risk sources")
            risk_mitigation.append("Implement pilot programs before full deployment")

        # Cost and timeline estimates
        total_cost = "Variable based on selected sources"
        implementation_timeline = "3-6 months for full implementation"

        # Success metrics
        success_metrics = [
            "Data integration success rate > 95%",
            "User adoption rate > 80%",
            "Data quality scores > 90%",
            "Time to insight < 24 hours"
        ]

        return ExecutiveSummary(
            total_sources_discovered=len(recommendations),
            recommended_sources=len(recommended_sources),
            top_recommendation=top_recommendation,
            key_findings=key_findings,
            strategic_recommendations=strategic_recommendations,
            risk_mitigation_strategies=risk_mitigation,
            estimated_total_cost=total_cost,
            estimated_implementation_timeline=implementation_timeline,
            success_metrics=success_metrics,
            generated_at=datetime.utcnow().isoformat()
        )

    async def export_recommendations(
        self,
        recommendations: List[SourceRecommendation],
        executive_summary: ExecutiveSummary,
        format: str = "json"
    ) -> str:
        """Export recommendations and summary"""

        export_data = {
            "executive_summary": asdict(executive_summary),
            "recommendations": [asdict(rec) for rec in recommendations],
            "export_metadata": {
                "agent_id": self.agent_id,
                "export_timestamp": datetime.utcnow().isoformat(),
                "format_version": "1.0"
            }
        }

        if format == "json":
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "recommendation_criteria": list(self.recommendation_criteria.keys()),
            "assessment_dimensions": [
                "business_value", "technical_feasibility", "risk_assessment", "cost_benefit"
            ],
            "output_formats": ["json"],
            "risk_assessment": True,
            "executive_summary": True,
            "multi_criteria_scoring": True
        })
        return base_capabilities