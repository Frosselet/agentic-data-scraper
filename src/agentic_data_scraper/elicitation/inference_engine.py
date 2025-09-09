"""
Semantic Inference Engine with OWL Reasoning

Intelligently infers implicit analytical requirements and 4D context from explicit 
business requirements using OWL reasoning, domain knowledge, and semantic analysis.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
import json
from dataclasses import dataclass

from ..schemas.sow import (
    ExplicitRequirements,
    InferredContext,
    SpatialInferences,
    TemporalInferences,
    DomainInferences,
    GraphInferences,
    AnalyticalOpportunities,
    FourDimensionalContext,
    GeographicAnalysisOpportunity,
    MultiScaleConsideration,
    TimeSeriesOpportunity,
    BiTemporalNeeds,
    DomainAnalysisOpportunity,
    RelationshipNetwork,
    DependencyAnalysis,
    TimeDimension,
    SpaceDimension,
    DomainDimension,
    KnowledgeDimension,
    TemporalPattern,
    VersioningStrategy,
    SpatialRelationship,
    OntologyMapping,
    ImplicitKnowledge,
    LearningOpportunity,
    InferenceConfidence,
    ReasoningStep
)


@dataclass
class InferenceRule:
    """Represents an OWL-based inference rule."""
    rule_id: str
    trigger_keywords: List[str]
    inference_type: str
    confidence: float
    reasoning: str
    required_capabilities: List[str]


class SemanticInferenceEngine:
    """
    Semantic inference engine that applies OWL reasoning rules to discover
    implicit analytical opportunities from explicit business requirements.
    """

    def __init__(self):
        """Initialize the inference engine."""
        self.domain_contexts = self._load_domain_contexts()
        self.inference_rules = self._initialize_inference_rules()
        self.ontology_mappings = self._load_ontology_mappings()
        self.reasoning_trace: List[ReasoningStep] = []

    def _load_domain_contexts(self) -> Dict[str, Any]:
        """Load domain-specific contexts from JSON-LD files."""
        contexts = {}
        
        # In a real implementation, would load from actual files
        # For now, create basic context mappings
        contexts["supply_chain"] = {
            "entities": ["supplier", "inventory", "logistics", "procurement", "quality"],
            "spatial_triggers": ["supplier", "logistics", "warehouse", "facility"],
            "temporal_triggers": ["delivery", "lead_time", "supply_cycle", "seasonal"],
            "inferences": {
                "geographic_analysis": 0.9,
                "temporal_patterns": 0.8,
                "network_analysis": 0.85,
                "financial_impact": 0.8
            }
        }
        
        contexts["finance"] = {
            "entities": ["cost", "revenue", "profit", "risk", "compliance", "audit"],
            "spatial_triggers": ["geographic", "currency", "market"],
            "temporal_triggers": ["quarterly", "monthly", "yearly", "reporting"],
            "inferences": {
                "temporal_trends": 0.9,
                "spatial_variations": 0.7,
                "regulatory_network": 0.85,
                "risk_correlation": 0.8
            }
        }
        
        contexts["commodities"] = {
            "entities": ["price", "commodity", "trading", "market", "volatility"],
            "spatial_triggers": ["global", "region", "country", "exchange"],
            "temporal_triggers": ["seasonal", "cycle", "trend", "forecast"],
            "inferences": {
                "geopolitical_correlation": 0.85,
                "weather_impact": 0.8,
                "supply_chain_disruption": 0.7,
                "economic_correlation": 0.75
            }
        }
        
        return contexts

    def _initialize_inference_rules(self) -> List[InferenceRule]:
        """Initialize OWL-based inference rules."""
        return [
            # Spatial Inference Rules
            InferenceRule(
                rule_id="supplier_geographic_risk",
                trigger_keywords=["supplier", "vendor", "partner"],
                inference_type="spatial",
                confidence=0.9,
                reasoning="Supplier mentions imply geographic risk analysis needs",
                required_capabilities=["geographic_analysis", "risk_assessment"]
            ),
            
            InferenceRule(
                rule_id="global_scope_multi_scale",
                trigger_keywords=["global", "international", "worldwide"],
                inference_type="spatial",
                confidence=0.85,
                reasoning="Global scope requires multi-scale geographic analysis",
                required_capabilities=["multi_scale_analysis", "geospatial_processing"]
            ),
            
            # Temporal Inference Rules
            InferenceRule(
                rule_id="cost_temporal_trends",
                trigger_keywords=["cost", "expense", "budget", "price"],
                inference_type="temporal",
                confidence=0.9,
                reasoning="Cost tracking implies temporal trend analysis needs",
                required_capabilities=["time_series_analysis", "trend_detection"]
            ),
            
            InferenceRule(
                rule_id="inventory_seasonal_patterns",
                trigger_keywords=["inventory", "stock", "demand", "supply"],
                inference_type="temporal",
                confidence=0.8,
                reasoning="Inventory management indicates seasonal pattern analysis",
                required_capabilities=["seasonality_detection", "demand_forecasting"]
            ),
            
            # Domain Inference Rules
            InferenceRule(
                rule_id="compliance_regulatory_network",
                trigger_keywords=["compliance", "regulation", "audit", "governance"],
                inference_type="network",
                confidence=0.85,
                reasoning="Compliance requirements infer regulatory network analysis",
                required_capabilities=["network_analysis", "compliance_monitoring"]
            ),
            
            InferenceRule(
                rule_id="supply_chain_financial_impact",
                trigger_keywords=["supply", "procurement", "logistics"],
                inference_type="cross_domain",
                confidence=0.8,
                reasoning="Supply chain optimization has direct financial implications",
                required_capabilities=["financial_modeling", "impact_analysis"]
            ),
            
            # Cross-Domain Rules
            InferenceRule(
                rule_id="commodities_geopolitical_correlation",
                trigger_keywords=["commodity", "trading", "market", "price"],
                inference_type="cross_domain", 
                confidence=0.75,
                reasoning="Commodities analysis uncovers geopolitical correlations",
                required_capabilities=["correlation_analysis", "geopolitical_modeling"]
            )
        ]

    def _load_ontology_mappings(self) -> Dict[str, List[OntologyMapping]]:
        """Load ontology concept mappings."""
        mappings = {}
        
        # Supply Chain to Finance mappings
        mappings["supply_to_finance"] = [
            OntologyMapping(
                source_concept="supply:Supplier",
                target_concept="finance:Counterparty",
                mapping_type="equivalentClass",
                confidence=0.9
            ),
            OntologyMapping(
                source_concept="supply:Cost",
                target_concept="finance:Expenditure",
                mapping_type="subClassOf",
                confidence=0.95
            )
        ]
        
        # Finance to Supply Chain mappings  
        mappings["finance_to_supply"] = [
            OntologyMapping(
                source_concept="finance:Risk",
                target_concept="supply:SupplyChainRisk",
                mapping_type="subClassOf",
                confidence=0.8
            )
        ]
        
        return mappings

    async def infer_context(self, requirements: ExplicitRequirements) -> InferredContext:
        """
        Infer analytical context from explicit requirements using OWL reasoning.
        """
        self.reasoning_trace = []
        
        # Extract entities and keywords from requirements
        entities, keywords = self._extract_entities_and_keywords(requirements)
        
        # Apply spatial inferences
        spatial_inferences = await self._infer_spatial_context(requirements, entities, keywords)
        
        # Apply temporal inferences
        temporal_inferences = await self._infer_temporal_context(requirements, entities, keywords)
        
        # Apply domain-specific inferences
        domain_inferences = await self._infer_domain_context(requirements, entities, keywords)
        
        # Apply graph/network inferences
        graph_inferences = await self._infer_graph_context(requirements, entities, keywords)

        return InferredContext(
            spatial_inferences=spatial_inferences,
            temporal_inferences=temporal_inferences, 
            domain_inferences=domain_inferences,
            graph_inferences=graph_inferences
        )

    async def _infer_spatial_context(
        self, 
        requirements: ExplicitRequirements,
        entities: List[str],
        keywords: Set[str]
    ) -> SpatialInferences:
        """Infer spatial analysis opportunities."""
        
        geographic_opportunities = []
        multi_scale_considerations = []
        
        # Apply spatial inference rules
        for rule in self.inference_rules:
            if rule.inference_type == "spatial":
                if any(trigger in keywords for trigger in rule.trigger_keywords):
                    
                    # Record reasoning step
                    self.reasoning_trace.append(ReasoningStep(
                        step=len(self.reasoning_trace) + 1,
                        rule_applied=rule.rule_id,
                        input=f"Keywords: {list(keywords & set(rule.trigger_keywords))}",
                        output=f"Inferred: {rule.reasoning}",
                        confidence=rule.confidence
                    ))
                    
                    # Create geographic analysis opportunity
                    opportunity = GeographicAnalysisOpportunity(
                        analysis_type=self._determine_spatial_analysis_type(rule, keywords),
                        reasoning=rule.reasoning,
                        confidence=rule.confidence,
                        potential_value=self._determine_spatial_value(rule, entities),
                        required_data=self._determine_spatial_data_needs(rule, keywords)
                    )
                    geographic_opportunities.append(opportunity)

        # Determine multi-scale considerations
        if requirements.business_challenge.spatial_context:
            scope = requirements.business_challenge.spatial_context.geographic_scope
            multi_scale_considerations = self._determine_multi_scale_needs(scope, entities)

        return SpatialInferences(
            geographic_analysis_opportunities=geographic_opportunities,
            multi_scale_considerations=multi_scale_considerations
        )

    async def _infer_temporal_context(
        self,
        requirements: ExplicitRequirements, 
        entities: List[str],
        keywords: Set[str]
    ) -> TemporalInferences:
        """Infer temporal analysis opportunities."""
        
        time_series_opportunities = []
        bi_temporal_needs = None
        
        # Apply temporal inference rules
        for rule in self.inference_rules:
            if rule.inference_type == "temporal":
                if any(trigger in keywords for trigger in rule.trigger_keywords):
                    
                    # Record reasoning step
                    self.reasoning_trace.append(ReasoningStep(
                        step=len(self.reasoning_trace) + 1,
                        rule_applied=rule.rule_id,
                        input=f"Keywords: {list(keywords & set(rule.trigger_keywords))}",
                        output=f"Inferred: {rule.reasoning}",
                        confidence=rule.confidence
                    ))
                    
                    # Determine pattern type
                    pattern_type = self._determine_temporal_pattern_type(rule, keywords)
                    
                    opportunity = TimeSeriesOpportunity(
                        pattern_type=pattern_type,
                        reasoning=rule.reasoning,
                        business_relevance=self._determine_temporal_relevance(rule, entities),
                        analysis_methods=self._determine_temporal_methods(pattern_type, keywords)
                    )
                    time_series_opportunities.append(opportunity)

        # Determine bi-temporal needs
        if any(keyword in keywords for keyword in ["audit", "compliance", "history", "version"]):
            bi_temporal_needs = BiTemporalNeeds(
                transaction_time_needed=True,
                valid_time_needed="compliance" in keywords,
                reasoning="Audit and compliance requirements suggest bi-temporal data needs"
            )

        return TemporalInferences(
            time_series_opportunities=time_series_opportunities,
            bi_temporal_needs=bi_temporal_needs
        )

    async def _infer_domain_context(
        self,
        requirements: ExplicitRequirements,
        entities: List[str], 
        keywords: Set[str]
    ) -> DomainInferences:
        """Infer domain-specific analytical opportunities."""
        
        supply_chain_analytics = []
        financial_analytics = []
        compliance_analytics = []
        
        # Analyze each domain context
        for domain, context in self.domain_contexts.items():
            domain_entities = [e for e in entities if e.lower() in context["entities"]]
            
            if domain_entities:
                # Create domain-specific opportunities
                for entity in domain_entities:
                    opportunities = self._create_domain_opportunities(domain, entity, keywords, context)
                    
                    if domain == "supply_chain":
                        supply_chain_analytics.extend(opportunities)
                    elif domain == "finance":
                        financial_analytics.extend(opportunities)
                    elif domain in ["compliance", "regulatory"]:
                        compliance_analytics.extend(opportunities)

        # Apply cross-domain inference rules
        for rule in self.inference_rules:
            if rule.inference_type == "cross_domain":
                if any(trigger in keywords for trigger in rule.trigger_keywords):
                    # Create cross-domain opportunities in appropriate categories
                    opportunity = DomainAnalysisOpportunity(
                        opportunity=f"Cross-domain analysis: {rule.rule_id}",
                        reasoning=rule.reasoning,
                        complexity="medium",
                        stakeholder_value=self._determine_stakeholder_value(rule, entities)
                    )
                    
                    # Add to appropriate category based on rule
                    if "supply" in rule.rule_id:
                        supply_chain_analytics.append(opportunity)
                    elif "finance" in rule.rule_id:
                        financial_analytics.append(opportunity)
                    else:
                        compliance_analytics.append(opportunity)

        return DomainInferences(
            supply_chain_analytics=supply_chain_analytics,
            financial_analytics=financial_analytics,
            compliance_analytics=compliance_analytics
        )

    async def _infer_graph_context(
        self,
        requirements: ExplicitRequirements,
        entities: List[str],
        keywords: Set[str]  
    ) -> GraphInferences:
        """Infer graph and network analysis opportunities."""
        
        relationship_networks = []
        dependency_analysis = []
        
        # Identify potential relationship networks
        if len(entities) >= 2:
            # Create relationship networks between entities
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    network = RelationshipNetwork(
                        network_type=f"{entity1}-{entity2} Network",
                        entities_involved=[entity1, entity2],
                        analysis_value=self._determine_network_value(entity1, entity2),
                        centrality_insights=f"Identify key {entity1} and {entity2} relationships"
                    )
                    relationship_networks.append(network)

        # Identify dependency analysis opportunities
        dependency_keywords = ["supply", "depend", "connect", "impact", "affect", "relate"]
        if any(keyword in keywords for keyword in dependency_keywords):
            for entity in entities:
                dependency = DependencyAnalysis(
                    dependency_type=f"{entity} Dependencies",
                    impact_assessment=f"Analyze how {entity} impacts other business processes",
                    mitigation_strategies=[
                        f"Diversify {entity} sources",
                        f"Monitor {entity} risks",
                        f"Build {entity} redundancy"
                    ]
                )
                dependency_analysis.append(dependency)

        return GraphInferences(
            relationship_networks=relationship_networks[:5],  # Limit to top 5
            dependency_analysis=dependency_analysis[:3]      # Limit to top 3
        )

    async def expand_4d_context(
        self,
        requirements: ExplicitRequirements,
        inferred_context: InferredContext,
        opportunities: AnalyticalOpportunities
    ) -> FourDimensionalContext:
        """Expand requirements to complete 4D context for ET(K)L platform."""
        
        # Time Dimension
        time_dimension = await self._expand_time_dimension(requirements, inferred_context)
        
        # Space Dimension  
        space_dimension = await self._expand_space_dimension(requirements, inferred_context)
        
        # Domain Dimension
        domain_dimension = await self._expand_domain_dimension(requirements, inferred_context, opportunities)
        
        # Knowledge Dimension
        knowledge_dimension = await self._expand_knowledge_dimension(requirements, inferred_context, opportunities)

        return FourDimensionalContext(
            time_dimension=time_dimension,
            space_dimension=space_dimension,
            domain_dimension=domain_dimension,
            knowledge_dimension=knowledge_dimension
        )

    # Helper methods for inference logic

    def _extract_entities_and_keywords(self, requirements: ExplicitRequirements) -> Tuple[List[str], Set[str]]:
        """Extract entities and keywords from requirements."""
        entities = [entity.entity for entity in requirements.business_challenge.entities_to_track]
        
        # Extract keywords from description and outcomes
        text = requirements.business_challenge.description + " "
        text += " ".join([outcome.outcome for outcome in requirements.desired_outcomes])
        
        keywords = set(re.findall(r'\b\w+\b', text.lower()))
        
        # Add entity names to keywords
        keywords.update([entity.lower() for entity in entities])
        
        return entities, keywords

    def _determine_spatial_analysis_type(self, rule: InferenceRule, keywords: Set[str]) -> str:
        """Determine the type of spatial analysis needed."""
        if "supplier" in keywords:
            return "Geographic Risk Assessment"
        elif "global" in keywords:
            return "Multi-Regional Analysis" 
        elif "location" in keywords:
            return "Spatial Distribution Analysis"
        else:
            return "Geographic Analysis"

    def _determine_spatial_value(self, rule: InferenceRule, entities: List[str]) -> str:
        """Determine the potential value of spatial analysis."""
        if "supplier" in rule.trigger_keywords:
            return "Identify geographic risks and optimize supplier locations"
        elif "global" in rule.trigger_keywords:
            return "Understand regional variations and optimize global operations"
        else:
            return f"Spatial insights for {', '.join(entities)}"

    def _determine_spatial_data_needs(self, rule: InferenceRule, keywords: Set[str]) -> List[str]:
        """Determine spatial data requirements."""
        data_needs = ["geographic_coordinates", "administrative_boundaries"]
        
        if "supplier" in keywords:
            data_needs.extend(["supplier_locations", "geopolitical_risk_indices"])
        if "risk" in keywords:
            data_needs.append("risk_assessment_data")
        if "market" in keywords:
            data_needs.append("market_boundaries")
            
        return data_needs

    def _determine_multi_scale_needs(self, scope: str, entities: List[str]) -> List[MultiScaleConsideration]:
        """Determine multi-scale analysis needs."""
        considerations = []
        
        scale_mapping = {
            "global": ["global", "national", "regional"],
            "international": ["national", "regional", "local"], 
            "national": ["national", "regional", "local"],
            "regional": ["regional", "local"],
            "local": ["local"]
        }
        
        scales = scale_mapping.get(scope, ["local"])
        
        for scale in scales:
            considerations.append(MultiScaleConsideration(
                scale=scale,
                relevance=f"{scale.title()}-level analysis for {', '.join(entities)}",
                analysis_needs=[f"{scale}_aggregation", f"{scale}_patterns"]
            ))
            
        return considerations

    def _determine_temporal_pattern_type(self, rule: InferenceRule, keywords: Set[str]) -> str:
        """Determine temporal pattern type."""
        if any(word in keywords for word in ["seasonal", "season", "cycle"]):
            return "seasonality"
        elif any(word in keywords for word in ["trend", "growth", "increase", "decrease"]):
            return "trend"  
        elif any(word in keywords for word in ["anomaly", "unusual", "outlier"]):
            return "anomalies"
        else:
            return "cycles"

    def _determine_temporal_relevance(self, rule: InferenceRule, entities: List[str]) -> str:
        """Determine business relevance of temporal analysis."""
        if "cost" in rule.trigger_keywords:
            return "Understanding cost trends enables budget optimization"
        elif "inventory" in rule.trigger_keywords:
            return "Seasonal patterns improve demand forecasting"
        else:
            return f"Temporal patterns provide insights for {', '.join(entities)}"

    def _determine_temporal_methods(self, pattern_type: str, keywords: Set[str]) -> List[str]:
        """Determine appropriate temporal analysis methods."""
        methods = []
        
        if pattern_type == "trend":
            methods.extend(["linear_regression", "time_series_decomposition"])
        elif pattern_type == "seasonality":
            methods.extend(["seasonal_decomposition", "fourier_analysis"])
        elif pattern_type == "cycles":
            methods.extend(["autocorrelation", "spectral_analysis"])
        elif pattern_type == "anomalies":
            methods.extend(["outlier_detection", "change_point_analysis"])
            
        if "forecast" in keywords:
            methods.append("forecasting")
            
        return methods

    def _create_domain_opportunities(
        self, 
        domain: str, 
        entity: str, 
        keywords: Set[str],
        context: Dict[str, Any]
    ) -> List[DomainAnalysisOpportunity]:
        """Create domain-specific opportunities."""
        opportunities = []
        
        # Get domain-specific inferences
        inferences = context.get("inferences", {})
        
        for inference_type, confidence in inferences.items():
            if confidence > 0.7:  # Only create opportunities with high confidence
                opportunity = DomainAnalysisOpportunity(
                    opportunity=f"{inference_type.replace('_', ' ').title()} for {entity}",
                    reasoning=f"{domain} analysis of {entity} reveals {inference_type} opportunities",
                    complexity=self._determine_complexity(inference_type),
                    stakeholder_value=self._determine_domain_value(domain, entity, inference_type)
                )
                opportunities.append(opportunity)
        
        return opportunities

    def _determine_complexity(self, inference_type: str) -> str:
        """Determine implementation complexity."""
        high_complexity = ["network_analysis", "geopolitical_correlation", "regulatory_network"]
        medium_complexity = ["temporal_trends", "spatial_variations", "financial_impact"]
        
        if inference_type in high_complexity:
            return "high"
        elif inference_type in medium_complexity:
            return "medium"
        else:
            return "low"

    def _determine_stakeholder_value(self, rule: InferenceRule, entities: List[str]) -> str:
        """Determine stakeholder value proposition."""
        if "risk" in rule.rule_id:
            return "Proactive risk management and mitigation"
        elif "cost" in rule.rule_id:
            return "Cost optimization and efficiency gains"
        elif "compliance" in rule.rule_id:
            return "Automated compliance monitoring and reporting"
        else:
            return f"Enhanced insights and optimization for {', '.join(entities)}"

    def _determine_domain_value(self, domain: str, entity: str, inference_type: str) -> str:
        """Determine domain-specific value proposition."""
        value_mapping = {
            "supply_chain": {
                "geographic_analysis": "Optimize supplier locations and reduce geographic risks",
                "temporal_patterns": "Improve demand forecasting and inventory planning",
                "network_analysis": "Identify critical supplier relationships and dependencies"
            },
            "finance": {
                "temporal_trends": "Enhance financial forecasting and budget planning",
                "spatial_variations": "Understand regional cost differences and opportunities",
                "risk_correlation": "Identify and mitigate interconnected financial risks"
            },
            "commodities": {
                "geopolitical_correlation": "Anticipate price impacts from geopolitical events",
                "weather_impact": "Model weather effects on commodity prices",
                "economic_correlation": "Understand commodity-economy relationships"
            }
        }
        
        domain_values = value_mapping.get(domain, {})
        return domain_values.get(inference_type, f"Optimize {entity} through {inference_type}")

    def _determine_network_value(self, entity1: str, entity2: str) -> str:
        """Determine value of network analysis between entities."""
        return f"Understand relationships and interdependencies between {entity1} and {entity2}"

    async def _expand_time_dimension(self, requirements: ExplicitRequirements, inferred_context: InferredContext) -> TimeDimension:
        """Expand time dimension based on requirements and inferences."""
        granularities = ["day", "month", "quarter", "year"]
        patterns = []
        
        # Add patterns from temporal inferences
        if inferred_context.temporal_inferences:
            for opp in inferred_context.temporal_inferences.time_series_opportunities:
                patterns.append(TemporalPattern(
                    pattern=opp.pattern_type,
                    frequency="monthly" if opp.pattern_type == "seasonality" else "daily",
                    business_relevance=opp.business_relevance
                ))
        
        # Determine versioning needs
        versioning = None
        if inferred_context.temporal_inferences and inferred_context.temporal_inferences.bi_temporal_needs:
            versioning = VersioningStrategy(
                bi_temporal_required=True,
                audit_trail_depth="full",
                historical_analysis_needs=["trend_analysis", "change_detection"]
            )
        
        return TimeDimension(
            temporal_granularities=granularities,
            temporal_patterns=patterns,
            versioning_strategy=versioning
        )

    async def _expand_space_dimension(self, requirements: ExplicitRequirements, inferred_context: InferredContext) -> SpaceDimension:
        """Expand space dimension based on requirements and inferences."""
        scales = ["local", "regional", "national"]
        coordinate_systems = ["WGS84", "Web_Mercator"]
        relationships = []
        
        # Add spatial relationships from inferences
        if inferred_context.spatial_inferences:
            for opp in inferred_context.spatial_inferences.geographic_analysis_opportunities:
                relationships.append(SpatialRelationship(
                    relationship="contains",
                    entities=["geographic_region", "business_entity"],
                    analysis_value=opp.potential_value
                ))
        
        return SpaceDimension(
            spatial_scales=scales,
            coordinate_systems=coordinate_systems,
            spatial_relationships=relationships
        )

    async def _expand_domain_dimension(
        self, 
        requirements: ExplicitRequirements, 
        inferred_context: InferredContext,
        opportunities: AnalyticalOpportunities
    ) -> DomainDimension:
        """Expand domain dimension with ontology mappings."""
        
        # Determine primary domains from entities
        entities = [entity.entity for entity in requirements.business_challenge.entities_to_track]
        primary_domains = self._determine_primary_domains(entities)
        
        # Determine connected domains from cross-domain opportunities
        connected_domains = []
        for opp in opportunities.cross_domain_opportunities:
            connected_domains.extend(opp.connected_domains)
        connected_domains = list(set(connected_domains))
        
        # Get relevant ontology mappings
        mappings = []
        for domain_pair, mapping_list in self.ontology_mappings.items():
            if any(domain in primary_domains for domain in domain_pair.split("_to_")):
                mappings.extend(mapping_list)
        
        return DomainDimension(
            primary_domains=primary_domains,
            connected_domains=connected_domains,
            ontology_mappings=mappings
        )

    async def _expand_knowledge_dimension(
        self,
        requirements: ExplicitRequirements,
        inferred_context: InferredContext, 
        opportunities: AnalyticalOpportunities
    ) -> KnowledgeDimension:
        """Expand knowledge dimension with implicit knowledge and learning opportunities."""
        
        implicit_knowledge = []
        learning_opportunities = []
        
        # Capture implicit knowledge from inference process
        for step in self.reasoning_trace:
            implicit_knowledge.append(ImplicitKnowledge(
                knowledge_type="inference_rule",
                source=f"OWL Rule: {step.rule_applied}",
                application=step.output,
                validation_method="confidence_threshold"
            ))
        
        # Create learning opportunities from predictive opportunities
        for pred_opp in opportunities.predictive_opportunities:
            learning_opportunities.append(LearningOpportunity(
                learning_target=pred_opp.prediction_target,
                data_sources=pred_opp.input_signals,
                methodology="machine_learning",
                business_application=pred_opp.business_impact
            ))
        
        return KnowledgeDimension(
            implicit_knowledge_captured=implicit_knowledge,
            learning_opportunities=learning_opportunities
        )

    def _determine_primary_domains(self, entities: List[str]) -> List[str]:
        """Determine primary domains from entities."""
        domains = set()
        
        for entity in entities:
            entity_lower = entity.lower()
            if entity_lower in ["supplier", "inventory", "logistics", "procurement"]:
                domains.add("supply_chain")
            elif entity_lower in ["cost", "revenue", "profit", "budget", "finance"]:
                domains.add("finance") 
            elif entity_lower in ["commodity", "trading", "market", "price"]:
                domains.add("commodities")
            else:
                domains.add("business")  # Default domain
                
        return list(domains)

    def get_inference_confidence(self) -> InferenceConfidence:
        """Calculate overall inference confidence levels."""
        spatial_confidence = 0.0
        temporal_confidence = 0.0
        domain_confidence = 0.0
        cross_domain_confidence = 0.0
        
        spatial_count = temporal_count = domain_count = cross_domain_count = 0
        
        for step in self.reasoning_trace:
            if "spatial" in step.rule_applied:
                spatial_confidence += step.confidence
                spatial_count += 1
            elif "temporal" in step.rule_applied:
                temporal_confidence += step.confidence
                temporal_count += 1
            elif "cross_domain" in step.rule_applied:
                cross_domain_confidence += step.confidence
                cross_domain_count += 1
            else:
                domain_confidence += step.confidence
                domain_count += 1
        
        return InferenceConfidence(
            spatial_inferences=spatial_confidence / max(spatial_count, 1),
            temporal_inferences=temporal_confidence / max(temporal_count, 1),
            domain_inferences=domain_confidence / max(domain_count, 1),
            cross_domain_inferences=cross_domain_confidence / max(cross_domain_count, 1)
        )