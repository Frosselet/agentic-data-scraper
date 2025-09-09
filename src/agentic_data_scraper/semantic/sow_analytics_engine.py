"""
Advanced SOW Analytics Engine with KuzuDB-Native Query Patterns

This module implements sophisticated analytical queries for SOW inference,
pattern matching, and cross-domain opportunity discovery using KuzuDB's
powerful graph traversal and analytical capabilities.

Key Features:
1. Pattern-based opportunity discovery
2. Cross-domain correlation analysis  
3. Temporal opportunity evolution
4. Business value optimization
5. Risk-weighted inference scoring
"""

import kuzu
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import math
import statistics
from collections import defaultdict, Counter

from .kuzu_sow_schema import KuzuSOWGraphEngine, BusinessRequirement, AnalyticalOpportunity

logger = logging.getLogger(__name__)


class InferenceStrategy(Enum):
    """Strategies for opportunity discovery"""
    PATTERN_MATCHING = "pattern_matching"
    GRAPH_TRAVERSAL = "graph_traversal" 
    CORRELATION_ANALYSIS = "correlation_analysis"
    TEMPORAL_EVOLUTION = "temporal_evolution"
    VALUE_OPTIMIZATION = "value_optimization"


@dataclass
class AnalyticsPattern:
    """Complex analytical pattern for opportunity discovery"""
    pattern_id: str
    name: str
    description: str
    cypher_pattern: str
    confidence_threshold: float
    business_domains: List[str]
    success_indicators: List[str]
    complexity_multiplier: float
    value_multiplier: float


@dataclass
class OpportunityCluster:
    """Cluster of related opportunities with synergistic potential"""
    cluster_id: str
    opportunities: List[str]  # Opportunity IDs
    cluster_theme: str
    synergy_score: float
    combined_value: float
    implementation_order: List[str]
    dependencies: List[Tuple[str, str]]  # (prerequisite, dependent)


@dataclass
class BusinessImpactAnalysis:
    """Analysis of business impact for opportunity prioritization"""
    opportunity_id: str
    revenue_impact: float
    cost_reduction: float
    risk_mitigation: float
    strategic_alignment: float
    implementation_complexity: float
    roi_projection: float
    payback_period_months: int


class AdvancedSOWAnalytics:
    """
    Advanced analytics engine for sophisticated SOW analysis using KuzuDB.
    
    This class implements complex graph analytical patterns, cross-domain
    correlation discovery, and intelligent opportunity prioritization.
    """
    
    def __init__(self, kuzu_engine: KuzuSOWGraphEngine):
        self.kuzu_engine = kuzu_engine
        self.conn = kuzu_engine.conn
        self.patterns = self._initialize_analytical_patterns()
        self.logger = logging.getLogger(__name__)
    
    def _initialize_analytical_patterns(self) -> List[AnalyticsPattern]:
        """Initialize sophisticated analytical patterns for opportunity discovery"""
        
        patterns = [
            AnalyticsPattern(
                pattern_id="PAT_001",
                name="Data Foundation Cascade",
                description="When data collection is mentioned, discover data governance, quality, and analytics opportunities",
                cypher_pattern="""
                MATCH (req:BusinessRequirement)
                WHERE req.description CONTAINS 'data' OR req.description CONTAINS 'collect'
                OPTIONAL MATCH (entity:DomainEntity)-[:BELONGS_TO]-(req)
                WHERE entity.data_maturity IN ['ad_hoc', 'defined']
                RETURN req, entity, 
                       CASE WHEN entity.data_maturity = 'ad_hoc' THEN 0.9 ELSE 0.7 END as confidence
                """,
                confidence_threshold=0.6,
                business_domains=["all"],
                success_indicators=["data_governance", "data_quality", "analytics_platform"],
                complexity_multiplier=1.2,
                value_multiplier=1.4
            ),
            
            AnalyticsPattern(
                pattern_id="PAT_002", 
                name="Regulatory Compliance Network",
                description="Regulatory requirements often trigger broader compliance infrastructure needs",
                cypher_pattern="""
                MATCH (req:BusinessRequirement)
                WHERE req.description CONTAINS 'regulat' OR req.description CONTAINS 'complian' OR req.description CONTAINS 'audit'
                OPTIONAL MATCH (entity:DomainEntity)-[:BELONGS_TO]-(req)
                WHERE entity.industry IN ['finance', 'healthcare', 'insurance']
                RETURN req, entity, 0.85 as confidence
                """,
                confidence_threshold=0.7,
                business_domains=["finance", "healthcare", "insurance"],
                success_indicators=["compliance_monitoring", "audit_trails", "risk_management"],
                complexity_multiplier=1.5,
                value_multiplier=1.6
            ),
            
            AnalyticsPattern(
                pattern_id="PAT_003",
                name="Operational Intelligence Nexus",
                description="Process optimization requirements reveal operational analytics opportunities",
                cypher_pattern="""
                MATCH (req:BusinessRequirement)
                WHERE req.description CONTAINS 'process' OR req.description CONTAINS 'operational' OR req.description CONTAINS 'efficiency'
                OPTIONAL MATCH (entity:DomainEntity)-[:BELONGS_TO]-(req)
                WHERE entity.maturity_level IN ['growth', 'mature', 'enterprise']
                RETURN req, entity,
                       CASE 
                           WHEN entity.maturity_level = 'enterprise' THEN 0.8
                           WHEN entity.maturity_level = 'mature' THEN 0.7
                           ELSE 0.6
                       END as confidence
                """,
                confidence_threshold=0.5,
                business_domains=["manufacturing", "logistics", "services"],
                success_indicators=["process_mining", "operational_dashboards", "predictive_maintenance"],
                complexity_multiplier=1.1,
                value_multiplier=1.3
            ),
            
            AnalyticsPattern(
                pattern_id="PAT_004",
                name="Customer Intelligence Ecosystem",
                description="Customer-related requirements often enable comprehensive customer analytics",
                cypher_pattern="""
                MATCH (req:BusinessRequirement)
                WHERE req.description CONTAINS 'customer' OR req.description CONTAINS 'client' OR req.description CONTAINS 'user'
                OPTIONAL MATCH (entity:DomainEntity)-[:BELONGS_TO]-(req)
                WHERE entity.industry IN ['retail', 'e-commerce', 'financial_services']
                RETURN req, entity, 0.75 as confidence
                """,
                confidence_threshold=0.6,
                business_domains=["retail", "e-commerce", "financial_services"],
                success_indicators=["customer_segmentation", "behavioral_analytics", "recommendation_engine"],
                complexity_multiplier=1.3,
                value_multiplier=1.5
            ),
            
            AnalyticsPattern(
                pattern_id="PAT_005",
                name="Supply Chain Intelligence Web",
                description="Supply chain requirements unlock comprehensive supply network analytics",
                cypher_pattern="""
                MATCH (req:BusinessRequirement)
                WHERE req.description CONTAINS 'supplier' OR req.description CONTAINS 'supply' OR req.description CONTAINS 'inventory'
                OPTIONAL MATCH (entity:DomainEntity)-[:BELONGS_TO]-(req)
                WHERE entity.industry IN ['manufacturing', 'retail', 'logistics']
                RETURN req, entity, 0.8 as confidence
                """,
                confidence_threshold=0.7,
                business_domains=["manufacturing", "retail", "logistics"],
                success_indicators=["supply_risk_analytics", "demand_forecasting", "supplier_performance"],
                complexity_multiplier=1.4,
                value_multiplier=1.7
            )
        ]
        
        return patterns
    
    def discover_pattern_based_opportunities(self, requirement_id: str) -> List[AnalyticalOpportunity]:
        """
        Discover opportunities using sophisticated pattern matching.
        
        This method applies complex graph patterns to identify implicit
        opportunities that traditional rule-based systems might miss.
        """
        opportunities = []
        
        try:
            # Get requirement context
            req_context_query = """
            MATCH (req:BusinessRequirement {id: $req_id})
            OPTIONAL MATCH (req)-[:BELONGS_TO]->(entity:DomainEntity)
            RETURN req.description, req.domain, req.complexity, req.priority,
                   entity.industry, entity.maturity_level, entity.data_maturity
            """
            
            result = self.conn.execute(req_context_query, {"req_id": requirement_id})
            req_record = result.get_next()
            
            if not req_record:
                self.logger.warning(f"Requirement {requirement_id} not found")
                return opportunities
            
            req_description = req_record[0].lower()
            req_domain = req_record[1]
            req_complexity = req_record[2]
            req_priority = req_record[3]
            entity_industry = req_record[4]
            entity_maturity = req_record[5]
            entity_data_maturity = req_record[6]
            
            # Apply each analytical pattern
            for pattern in self.patterns:
                if self._pattern_applies(pattern, req_domain, entity_industry):
                    pattern_opportunities = self._apply_analytical_pattern(
                        pattern, requirement_id, req_description, req_complexity,
                        req_priority, entity_industry, entity_maturity, entity_data_maturity
                    )
                    opportunities.extend(pattern_opportunities)
            
            # Apply cross-pattern correlation analysis
            correlation_opportunities = self._discover_cross_pattern_correlations(
                requirement_id, req_description, req_domain, opportunities
            )
            opportunities.extend(correlation_opportunities)
            
            self.logger.info(f"Pattern-based discovery found {len(opportunities)} opportunities for {requirement_id}")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Pattern-based opportunity discovery failed: {e}")
            return opportunities
    
    def _pattern_applies(self, pattern: AnalyticsPattern, req_domain: str, entity_industry: str) -> bool:
        """Check if a pattern applies to the current requirement context"""
        if "all" in pattern.business_domains:
            return True
        return (req_domain in pattern.business_domains or 
                (entity_industry and entity_industry in pattern.business_domains))
    
    def _apply_analytical_pattern(self, pattern: AnalyticsPattern, requirement_id: str,
                                req_description: str, req_complexity: str, req_priority: int,
                                entity_industry: str, entity_maturity: str, 
                                entity_data_maturity: str) -> List[AnalyticalOpportunity]:
        """Apply a specific analytical pattern to discover opportunities"""
        opportunities = []
        
        try:
            # Execute the pattern's cypher query
            result = self.conn.execute(
                pattern.cypher_pattern, 
                {"req_id": requirement_id}
            )
            
            pattern_matches = []
            for record in result:
                pattern_matches.append(record)
            
            if not pattern_matches:
                return opportunities
            
            # Generate opportunities for each success indicator
            for indicator in pattern.success_indicators:
                confidence = self._calculate_pattern_confidence(
                    pattern, req_description, req_complexity, entity_maturity
                )
                
                if confidence >= pattern.confidence_threshold:
                    opportunity = self._generate_pattern_opportunity(
                        pattern, indicator, requirement_id, confidence,
                        req_complexity, req_priority, entity_industry
                    )
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Failed to apply pattern {pattern.pattern_id}: {e}")
            return opportunities
    
    def _calculate_pattern_confidence(self, pattern: AnalyticsPattern, req_description: str,
                                    req_complexity: str, entity_maturity: str) -> float:
        """Calculate confidence score for pattern application"""
        base_confidence = 0.7
        
        # Adjust based on requirement description relevance
        relevance_keywords = pattern.name.lower().split()
        description_matches = sum(1 for keyword in relevance_keywords if keyword in req_description)
        relevance_boost = min(description_matches * 0.1, 0.3)
        
        # Adjust based on entity maturity
        maturity_multiplier = {
            "startup": 0.8,
            "growth": 0.9,
            "mature": 1.0,
            "enterprise": 1.1
        }.get(entity_maturity, 0.9)
        
        # Adjust based on requirement complexity alignment
        complexity_alignment = {
            ("low", "low"): 1.0,
            ("low", "medium"): 0.9,
            ("medium", "medium"): 1.0,
            ("medium", "high"): 0.95,
            ("high", "high"): 1.0,
            ("high", "very_high"): 1.05
        }.get((req_complexity, "medium"), 0.9)  # Default pattern complexity = medium
        
        final_confidence = min(
            (base_confidence + relevance_boost) * maturity_multiplier * complexity_alignment,
            1.0
        )
        
        return final_confidence
    
    def _generate_pattern_opportunity(self, pattern: AnalyticsPattern, indicator: str,
                                    requirement_id: str, confidence: float,
                                    req_complexity: str, req_priority: int,
                                    entity_industry: str) -> AnalyticalOpportunity:
        """Generate an analytical opportunity from a pattern match"""
        
        # Create sophisticated opportunity descriptions
        description_templates = {
            "data_governance": f"Implement comprehensive data governance framework leveraging {pattern.name} insights",
            "data_quality": f"Deploy advanced data quality monitoring and remediation using {pattern.name} patterns",
            "analytics_platform": f"Build analytics platform optimized for {pattern.name} use cases",
            "compliance_monitoring": f"Establish automated compliance monitoring aligned with {pattern.name}",
            "audit_trails": f"Create comprehensive audit trail system supporting {pattern.name} requirements", 
            "risk_management": f"Implement risk management analytics using {pattern.name} methodology",
            "process_mining": f"Deploy process mining capabilities enhanced by {pattern.name} intelligence",
            "operational_dashboards": f"Build operational intelligence dashboards based on {pattern.name}",
            "predictive_maintenance": f"Implement predictive maintenance system using {pattern.name} insights",
            "customer_segmentation": f"Develop advanced customer segmentation leveraging {pattern.name}",
            "behavioral_analytics": f"Build behavioral analytics platform optimized for {pattern.name}",
            "recommendation_engine": f"Create intelligent recommendation engine using {pattern.name}",
            "supply_risk_analytics": f"Implement supply chain risk analytics with {pattern.name} intelligence",
            "demand_forecasting": f"Deploy demand forecasting system enhanced by {pattern.name}",
            "supplier_performance": f"Build supplier performance analytics using {pattern.name} methodology"
        }
        
        description = description_templates.get(indicator, f"Implement {indicator} using {pattern.name} approach")
        
        # Calculate business value using pattern multipliers
        base_value = 1000 + (req_priority * 500)  # Higher priority = higher value
        adjusted_value = base_value * pattern.value_multiplier * confidence
        
        # Estimate implementation hours with pattern complexity
        base_hours = {
            "low": 120,
            "medium": 240,
            "high": 400,
            "very_high": 600
        }.get(req_complexity, 240)
        
        estimated_hours = int(base_hours * pattern.complexity_multiplier)
        
        # Generate opportunity ID
        opp_id = f"{requirement_id}_PAT_{pattern.pattern_id}_{indicator.upper()}"
        
        return AnalyticalOpportunity(
            id=opp_id,
            description=description,
            complexity=self._adjust_complexity(req_complexity, pattern.complexity_multiplier),
            business_value=round(adjusted_value, 2),
            confidence_score=confidence,
            discovery_method="pattern_matching",
            related_requirements=[requirement_id],
            implementation_approach=self._generate_implementation_approach(pattern, indicator),
            estimated_hours=estimated_hours,
            roi_projection=self._calculate_roi_projection(adjusted_value, estimated_hours)
        )
    
    def _adjust_complexity(self, base_complexity: str, multiplier: float) -> str:
        """Adjust complexity based on pattern complexity multiplier"""
        complexity_scale = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
        current_level = complexity_scale.get(base_complexity, 2)
        
        adjusted_level = min(4, max(1, int(current_level * multiplier)))
        
        return {1: "low", 2: "medium", 3: "high", 4: "very_high"}[adjusted_level]
    
    def _generate_implementation_approach(self, pattern: AnalyticsPattern, indicator: str) -> str:
        """Generate tailored implementation approach"""
        approaches = {
            "data_governance": "Establish data stewardship roles, implement data catalog, create governance policies and procedures",
            "data_quality": "Deploy data profiling tools, implement quality rules engine, establish monitoring dashboards",
            "analytics_platform": "Build modern analytics stack with self-service capabilities and advanced visualization",
            "compliance_monitoring": "Implement automated compliance checking with real-time alerts and reporting",
            "audit_trails": "Create comprehensive logging framework with immutable audit records and search capabilities",
            "risk_management": "Deploy risk assessment models with scenario analysis and mitigation tracking",
            "process_mining": "Implement process discovery tools with performance analytics and optimization recommendations",
            "operational_dashboards": "Build real-time operational monitoring with KPI tracking and anomaly detection",
            "predictive_maintenance": "Deploy IoT sensors with machine learning models for failure prediction",
            "customer_segmentation": "Implement clustering algorithms with behavioral analysis and targeting capabilities",
            "behavioral_analytics": "Build user journey tracking with predictive behavior modeling",
            "recommendation_engine": "Create ML-powered recommendation system with real-time personalization",
            "supply_risk_analytics": "Implement supplier risk scoring with geopolitical and financial risk monitoring",
            "demand_forecasting": "Deploy time-series forecasting models with external factor integration",
            "supplier_performance": "Build supplier scorecard system with performance tracking and benchmarking"
        }
        
        return approaches.get(indicator, f"Implement {indicator} with modern analytics and automation")
    
    def _calculate_roi_projection(self, business_value: float, estimated_hours: int) -> float:
        """Calculate ROI projection based on value and implementation cost"""
        # Assume $150/hour average implementation cost
        implementation_cost = estimated_hours * 150
        
        if implementation_cost == 0:
            return 0.0
        
        # ROI = (Value - Cost) / Cost * 100
        roi = ((business_value - implementation_cost) / implementation_cost) * 100
        return round(roi, 2)
    
    def _discover_cross_pattern_correlations(self, requirement_id: str, req_description: str,
                                           req_domain: str, 
                                           existing_opportunities: List[AnalyticalOpportunity]) -> List[AnalyticalOpportunity]:
        """Discover opportunities through cross-pattern correlations"""
        correlation_opportunities = []
        
        try:
            # Find related requirements in the same domain
            correlation_query = """
            MATCH (req:BusinessRequirement {id: $req_id})
            MATCH (related:BusinessRequirement)
            WHERE related.domain = req.domain AND related.id <> req.id
            OPTIONAL MATCH (related)-[:IMPLIES]->(opp:AnalyticalOpportunity)
            RETURN related.id, related.description, collect(opp.description) as related_opportunities
            LIMIT 5
            """
            
            result = self.conn.execute(correlation_query, {"req_id": requirement_id})
            
            correlation_themes = defaultdict(list)
            for record in result:
                related_id = record[0]
                related_desc = record[1]
                related_opps = record[2] if record[2] else []
                
                # Extract themes from related opportunities
                for opp_desc in related_opps:
                    if opp_desc:
                        theme_words = self._extract_theme_words(opp_desc)
                        for theme in theme_words:
                            correlation_themes[theme].append((related_id, opp_desc))
            
            # Generate correlation-based opportunities
            for theme, related_items in correlation_themes.items():
                if len(related_items) >= 2:  # Theme appears in multiple related requirements
                    correlation_opp = self._generate_correlation_opportunity(
                        requirement_id, theme, related_items, req_domain
                    )
                    correlation_opportunities.append(correlation_opp)
            
            return correlation_opportunities
            
        except Exception as e:
            self.logger.error(f"Cross-pattern correlation discovery failed: {e}")
            return correlation_opportunities
    
    def _extract_theme_words(self, text: str) -> Set[str]:
        """Extract thematic keywords from opportunity descriptions"""
        themes = set()
        
        # Key analytical themes
        theme_patterns = [
            "analytics", "monitoring", "prediction", "optimization", "automation",
            "intelligence", "insights", "dashboard", "reporting", "forecasting",
            "segmentation", "classification", "clustering", "recommendation",
            "risk", "compliance", "governance", "quality", "performance"
        ]
        
        text_lower = text.lower()
        for pattern in theme_patterns:
            if pattern in text_lower:
                themes.add(pattern)
        
        return themes
    
    def _generate_correlation_opportunity(self, requirement_id: str, theme: str,
                                        related_items: List[Tuple[str, str]], 
                                        domain: str) -> AnalyticalOpportunity:
        """Generate opportunity based on cross-pattern correlations"""
        
        correlation_descriptions = {
            "analytics": f"Unified analytics platform integrating {theme} capabilities across {domain} domain",
            "monitoring": f"Comprehensive monitoring system providing {theme} insights for {domain} operations",
            "prediction": f"Advanced predictive analytics leveraging {theme} patterns in {domain}",
            "optimization": f"Optimization engine using {theme} techniques for {domain} improvement",
            "automation": f"Intelligent automation platform incorporating {theme} for {domain} processes",
            "intelligence": f"Business intelligence solution with {theme} focus for {domain} decision-making",
            "dashboard": f"Executive dashboard providing {theme} visibility across {domain} operations",
            "risk": f"Enterprise risk management system addressing {theme} in {domain}",
            "compliance": f"Automated compliance framework handling {theme} requirements in {domain}",
            "governance": f"Data governance platform managing {theme} aspects of {domain} information"
        }
        
        description = correlation_descriptions.get(
            theme, 
            f"Cross-domain {theme} solution integrating multiple {domain} requirements"
        )
        
        # Higher value for correlation opportunities (they address multiple needs)
        base_value = 2000 + len(related_items) * 500
        confidence = min(0.8, 0.5 + len(related_items) * 0.1)
        
        opp_id = f"{requirement_id}_CORR_{theme.upper()}_{len(related_items)}"
        
        return AnalyticalOpportunity(
            id=opp_id,
            description=description,
            complexity="high",  # Correlation opportunities tend to be more complex
            business_value=base_value,
            confidence_score=confidence,
            discovery_method="correlation_analysis",
            related_requirements=[requirement_id] + [item[0] for item in related_items],
            implementation_approach=f"Implement unified {theme} platform with modular architecture supporting multiple use cases",
            estimated_hours=int(320 + len(related_items) * 80),  # More complex = more hours
            roi_projection=self._calculate_roi_projection(base_value, int(320 + len(related_items) * 80))
        )
    
    def cluster_related_opportunities(self, domain: Optional[str] = None) -> List[OpportunityCluster]:
        """
        Cluster related opportunities to identify synergistic implementation paths.
        
        This analysis helps optimize implementation by identifying opportunities
        that should be implemented together for maximum synergy.
        """
        clusters = []
        
        try:
            # Get opportunities with relationships
            cluster_query = """
            MATCH (req:BusinessRequirement)-[:IMPLIES]->(opp:AnalyticalOpportunity)
            """ + (f"WHERE req.domain = '{domain}'" if domain else "") + """
            OPTIONAL MATCH (opp)-[:CORRELATES_WITH]-(related_opp:AnalyticalOpportunity)
            RETURN opp.id, opp.description, opp.business_value, opp.complexity,
                   opp.discovery_method, collect(related_opp.id) as related_ids
            """
            
            result = self.conn.execute(cluster_query)
            
            opportunities_data = []
            for record in result:
                opportunities_data.append({
                    'id': record[0],
                    'description': record[1],
                    'business_value': record[2],
                    'complexity': record[3],
                    'discovery_method': record[4],
                    'related_ids': record[5] if record[5] else []
                })
            
            # Apply clustering algorithm based on thematic similarity
            clusters = self._apply_opportunity_clustering(opportunities_data)
            
            self.logger.info(f"Created {len(clusters)} opportunity clusters")
            return clusters
            
        except Exception as e:
            self.logger.error(f"Opportunity clustering failed: {e}")
            return clusters
    
    def _apply_opportunity_clustering(self, opportunities_data: List[Dict]) -> List[OpportunityCluster]:
        """Apply clustering algorithm to group related opportunities"""
        clusters = []
        
        # Group by thematic similarity
        theme_groups = defaultdict(list)
        
        for opp in opportunities_data:
            themes = self._extract_theme_words(opp['description'])
            primary_theme = max(themes, key=len) if themes else 'general'
            theme_groups[primary_theme].append(opp)
        
        cluster_id = 1
        for theme, group_opps in theme_groups.items():
            if len(group_opps) >= 2:  # Only create clusters with multiple opportunities
                opportunity_ids = [opp['id'] for opp in group_opps]
                combined_value = sum(opp['business_value'] for opp in group_opps)
                
                # Calculate synergy score based on thematic coherence
                synergy_score = self._calculate_synergy_score(group_opps)
                
                # Determine implementation order based on dependencies
                implementation_order = self._determine_implementation_order(group_opps)
                
                cluster = OpportunityCluster(
                    cluster_id=f"CLUSTER_{cluster_id:03d}",
                    opportunities=opportunity_ids,
                    cluster_theme=theme,
                    synergy_score=synergy_score,
                    combined_value=combined_value,
                    implementation_order=implementation_order,
                    dependencies=self._identify_dependencies(group_opps)
                )
                
                clusters.append(cluster)
                cluster_id += 1
        
        return clusters
    
    def _calculate_synergy_score(self, opportunities: List[Dict]) -> float:
        """Calculate synergy score for a group of opportunities"""
        # Base synergy from having multiple related opportunities
        base_synergy = 0.5
        
        # Bonus for similar complexity (easier to implement together)
        complexities = [opp['complexity'] for opp in opportunities]
        complexity_similarity = 1.0 - (len(set(complexities)) - 1) * 0.2
        
        # Bonus for similar discovery methods (related reasoning)
        discovery_methods = [opp['discovery_method'] for opp in opportunities]
        method_similarity = 1.0 - (len(set(discovery_methods)) - 1) * 0.15
        
        # Scale with number of opportunities (more = higher synergy potential)
        scale_bonus = min(0.3, (len(opportunities) - 2) * 0.1)
        
        synergy_score = min(1.0, base_synergy + complexity_similarity * 0.3 + 
                          method_similarity * 0.2 + scale_bonus)
        
        return round(synergy_score, 3)
    
    def _determine_implementation_order(self, opportunities: List[Dict]) -> List[str]:
        """Determine optimal implementation order for opportunities"""
        # Sort by complexity (implement simpler first), then by value
        complexity_order = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
        
        sorted_opps = sorted(opportunities, key=lambda x: (
            complexity_order.get(x['complexity'], 2),
            -x['business_value']  # Higher value first within same complexity
        ))
        
        return [opp['id'] for opp in sorted_opps]
    
    def _identify_dependencies(self, opportunities: List[Dict]) -> List[Tuple[str, str]]:
        """Identify dependencies between opportunities in a cluster"""
        dependencies = []
        
        # Simple heuristic: data-related opportunities often depend on governance
        governance_opps = [opp for opp in opportunities if 'governance' in opp['description'].lower()]
        data_opps = [opp for opp in opportunities if 'data' in opp['description'].lower() and 'governance' not in opp['description'].lower()]
        
        for governance_opp in governance_opps:
            for data_opp in data_opps:
                dependencies.append((governance_opp['id'], data_opp['id']))
        
        # Analytics platforms often depend on data quality
        quality_opps = [opp for opp in opportunities if 'quality' in opp['description'].lower()]
        analytics_opps = [opp for opp in opportunities if 'analytics' in opp['description'].lower() and 'quality' not in opp['description'].lower()]
        
        for quality_opp in quality_opps:
            for analytics_opp in analytics_opps:
                dependencies.append((quality_opp['id'], analytics_opp['id']))
        
        return dependencies
    
    def analyze_business_impact(self, opportunity_id: str) -> BusinessImpactAnalysis:
        """
        Perform comprehensive business impact analysis for an opportunity.
        
        This analysis provides detailed business justification and ROI calculations.
        """
        try:
            # Get opportunity details
            impact_query = """
            MATCH (opp:AnalyticalOpportunity {id: $opp_id})
            OPTIONAL MATCH (req:BusinessRequirement)-[:IMPLIES]->(opp)
            OPTIONAL MATCH (req)-[:BELONGS_TO]->(entity:DomainEntity)
            RETURN opp.description, opp.business_value, opp.complexity, opp.estimated_hours,
                   req.priority, req.domain, entity.industry, entity.maturity_level
            """
            
            result = self.conn.execute(impact_query, {"opp_id": opportunity_id})
            record = result.get_next()
            
            if not record:
                raise ValueError(f"Opportunity {opportunity_id} not found")
            
            opp_description = record[0]
            business_value = record[1] or 1000
            complexity = record[2] or "medium"
            estimated_hours = record[3] or 200
            req_priority = record[4] or 3
            domain = record[5] or "general"
            industry = record[6] or "general"
            maturity_level = record[7] or "mature"
            
            # Calculate impact components
            revenue_impact = self._calculate_revenue_impact(opp_description, business_value, industry)
            cost_reduction = self._calculate_cost_reduction(opp_description, business_value, domain)
            risk_mitigation = self._calculate_risk_mitigation(opp_description, req_priority, industry)
            strategic_alignment = self._calculate_strategic_alignment(opp_description, maturity_level, domain)
            implementation_complexity = self._calculate_implementation_complexity(complexity, estimated_hours)
            
            # Calculate ROI and payback period
            total_benefit = revenue_impact + cost_reduction + risk_mitigation
            implementation_cost = estimated_hours * 150  # $150/hour
            
            roi_projection = ((total_benefit - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 0
            payback_period = int((implementation_cost / (total_benefit / 12)) if total_benefit > 0 else 12)
            
            return BusinessImpactAnalysis(
                opportunity_id=opportunity_id,
                revenue_impact=revenue_impact,
                cost_reduction=cost_reduction,
                risk_mitigation=risk_mitigation,
                strategic_alignment=strategic_alignment,
                implementation_complexity=implementation_complexity,
                roi_projection=roi_projection,
                payback_period_months=min(payback_period, 60)  # Cap at 5 years
            )
            
        except Exception as e:
            self.logger.error(f"Business impact analysis failed for {opportunity_id}: {e}")
            # Return default analysis
            return BusinessImpactAnalysis(
                opportunity_id=opportunity_id,
                revenue_impact=0,
                cost_reduction=0,
                risk_mitigation=0,
                strategic_alignment=0.5,
                implementation_complexity=0.5,
                roi_projection=0,
                payback_period_months=12
            )
    
    def _calculate_revenue_impact(self, description: str, base_value: float, industry: str) -> float:
        """Calculate potential revenue impact"""
        revenue_multipliers = {
            "recommendation": 1.5,
            "customer": 1.3,
            "segmentation": 1.4,
            "prediction": 1.2,
            "optimization": 1.1
        }
        
        industry_multipliers = {
            "retail": 1.3,
            "e-commerce": 1.4,
            "financial_services": 1.2,
            "manufacturing": 1.1
        }
        
        desc_lower = description.lower()
        revenue_mult = max([mult for keyword, mult in revenue_multipliers.items() if keyword in desc_lower], default=1.0)
        industry_mult = industry_multipliers.get(industry, 1.0)
        
        return round(base_value * 0.4 * revenue_mult * industry_mult, 2)
    
    def _calculate_cost_reduction(self, description: str, base_value: float, domain: str) -> float:
        """Calculate potential cost reduction"""
        cost_reduction_keywords = {
            "automation": 1.8,
            "efficiency": 1.5,
            "optimization": 1.4,
            "process": 1.3,
            "monitoring": 1.2
        }
        
        desc_lower = description.lower()
        reduction_mult = max([mult for keyword, mult in cost_reduction_keywords.items() if keyword in desc_lower], default=1.0)
        
        return round(base_value * 0.3 * reduction_mult, 2)
    
    def _calculate_risk_mitigation(self, description: str, priority: int, industry: str) -> float:
        """Calculate risk mitigation value"""
        risk_keywords = {
            "compliance": 2.0,
            "risk": 1.8,
            "governance": 1.6,
            "audit": 1.5,
            "monitoring": 1.3
        }
        
        high_risk_industries = ["finance", "healthcare", "insurance"]
        industry_mult = 1.5 if industry in high_risk_industries else 1.0
        
        desc_lower = description.lower()
        risk_mult = max([mult for keyword, mult in risk_keywords.items() if keyword in desc_lower], default=0.5)
        
        priority_mult = priority / 3.0  # Higher priority = higher risk mitigation value
        
        return round(1000 * risk_mult * industry_mult * priority_mult, 2)
    
    def _calculate_strategic_alignment(self, description: str, maturity_level: str, domain: str) -> float:
        """Calculate strategic alignment score (0-1)"""
        strategic_keywords = {
            "intelligence": 0.9,
            "analytics": 0.8,
            "insight": 0.8,
            "optimization": 0.7,
            "automation": 0.7
        }
        
        maturity_multipliers = {
            "startup": 0.6,
            "growth": 0.8,
            "mature": 1.0,
            "enterprise": 1.1
        }
        
        desc_lower = description.lower()
        strategic_score = max([score for keyword, score in strategic_keywords.items() if keyword in desc_lower], default=0.5)
        maturity_mult = maturity_multipliers.get(maturity_level, 1.0)
        
        return min(1.0, strategic_score * maturity_mult)
    
    def _calculate_implementation_complexity(self, complexity: str, estimated_hours: int) -> float:
        """Calculate implementation complexity score (0-1, higher = more complex)"""
        complexity_scores = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8,
            "very_high": 1.0
        }
        
        base_score = complexity_scores.get(complexity, 0.5)
        
        # Adjust based on estimated hours
        hours_adjustment = min(0.3, (estimated_hours - 200) / 1000)  # Normalize around 200 hours
        
        return min(1.0, max(0.1, base_score + hours_adjustment))


# Example usage and testing
if __name__ == "__main__":
    from .kuzu_sow_schema import KuzuSOWGraphEngine
    
    # Initialize engines
    kuzu_engine = KuzuSOWGraphEngine("advanced_sow.db")
    analytics_engine = AdvancedSOWAnalytics(kuzu_engine)
    
    # Add test requirement
    req = BusinessRequirement(
        id="REQ_ADV_001",
        description="Implement comprehensive supplier data collection and tracking system",
        priority=1,
        domain="manufacturing",
        complexity="high",
        estimated_hours=300,
        business_value=8000.0
    )
    
    kuzu_engine.add_business_requirement(req)
    
    # Test pattern-based discovery
    opportunities = analytics_engine.discover_pattern_based_opportunities("REQ_ADV_001")
    print(f"Pattern-based discovery found {len(opportunities)} opportunities")
    
    for opp in opportunities[:3]:  # Show first 3
        print(f"- {opp.description[:80]}...")
        print(f"  Value: ${opp.business_value}, Confidence: {opp.confidence_score:.2f}")
        print(f"  Method: {opp.discovery_method}, Hours: {opp.estimated_hours}")
        print()
    
    # Test opportunity clustering
    clusters = analytics_engine.cluster_related_opportunities("manufacturing")
    print(f"Created {len(clusters)} opportunity clusters")
    
    for cluster in clusters:
        print(f"Cluster: {cluster.cluster_theme} (Synergy: {cluster.synergy_score})")
        print(f"Opportunities: {len(cluster.opportunities)}, Combined Value: ${cluster.combined_value}")
        print()
    
    # Test business impact analysis
    if opportunities:
        impact = analytics_engine.analyze_business_impact(opportunities[0].id)
        print(f"Business Impact Analysis for {opportunities[0].id}:")
        print(f"Revenue Impact: ${impact.revenue_impact}")
        print(f"Cost Reduction: ${impact.cost_reduction}")
        print(f"Risk Mitigation: ${impact.risk_mitigation}")
        print(f"ROI Projection: {impact.roi_projection:.1f}%")
        print(f"Payback Period: {impact.payback_period_months} months")
    
    kuzu_engine.close()