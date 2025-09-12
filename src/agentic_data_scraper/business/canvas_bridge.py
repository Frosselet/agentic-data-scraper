"""
Business-Technical Bridge for Data Business Canvas

Connects Data Business Canvas strategic layer to technical implementation
via ADR-004 (Semantic SOW Contracts) and ADR-005 (KuzuDB Architecture).

Enables bidirectional translation between business strategy and technical specs,
maintaining consistency across all ADR layers while providing business stakeholders
with semantic-grounded strategic planning capabilities.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class CanvasComponentType(Enum):
    """Business Model Canvas component types"""
    KEY_PARTNERS = "key_partners"
    KEY_ACTIVITIES = "key_activities"
    KEY_RESOURCES = "key_resources"
    VALUE_PROPOSITIONS = "value_propositions"
    CUSTOMER_RELATIONSHIPS = "customer_relationships"
    CUSTOMER_SEGMENTS = "customer_segments"
    CHANNELS = "channels"
    COST_STRUCTURE = "cost_structure"
    REVENUE_STREAMS = "revenue_streams"
    # Data Business Canvas extensions
    DATA_ASSETS = "data_assets"
    INTELLIGENCE_CAPABILITIES = "intelligence_capabilities"
    SPATIAL_CONTEXT = "spatial_context"


@dataclass
class DataAsset:
    """Data asset component for business model canvas"""
    asset_id: str
    name: str
    description: str
    semantic_specification: Dict[str, Any]
    quality_requirements: Dict[str, float]
    governance_rules: List[str]
    business_value_score: float
    concept_uri: str = ""
    skos_mappings: Dict[str, str] = field(default_factory=dict)
    
    def to_sow_contract_spec(self) -> Dict[str, Any]:
        """Convert to SOW data contract specification"""
        return {
            "data_contract_id": f"DC_{self.asset_id}",
            "asset_specification": self.semantic_specification,
            "quality_metrics": self.quality_requirements,
            "governance_requirements": self.governance_rules,
            "business_context": {
                "value_score": self.business_value_score,
                "concept_uri": self.concept_uri,
                "semantic_mappings": self.skos_mappings
            }
        }


@dataclass 
class IntelligenceCapability:
    """AI/ML capability component for business model canvas"""
    capability_id: str
    name: str
    description: str
    ai_requirements: Dict[str, Any]
    performance_metrics: Dict[str, float]
    scalability_spec: Dict[str, Any]
    business_impact: str
    concept_uri: str = ""
    
    def to_sow_contract_spec(self) -> Dict[str, Any]:
        """Convert to SOW processing contract specification"""
        return {
            "processing_contract_id": f"PC_{self.capability_id}",
            "capability_specification": self.ai_requirements,
            "performance_sla": self.performance_metrics,
            "scalability_requirements": self.scalability_spec,
            "business_context": {
                "impact_description": self.business_impact,
                "concept_uri": self.concept_uri
            }
        }


@dataclass
class SpatialBusinessContext:
    """Geospatial business context component"""
    context_id: str
    geographic_scope: Dict[str, Any]
    spatial_requirements: List[str]
    geopolitical_considerations: Dict[str, Any]
    market_presence: Dict[str, Any]
    
    def to_kuzu_spatial_spec(self) -> Dict[str, Any]:
        """Convert to KuzuDB spatial schema specification"""
        return {
            "spatial_context_id": self.context_id,
            "geographic_entities": self.geographic_scope,
            "spatial_constraints": self.spatial_requirements,
            "geopolitical_context": self.geopolitical_considerations,
            "market_geography": self.market_presence
        }


@dataclass
class DataBusinessCanvas:
    """Data Business Canvas with semantic foundations"""
    canvas_id: str
    business_domain: str
    creation_date: datetime
    components: Dict[CanvasComponentType, List[Any]] = field(default_factory=dict)
    semantic_foundation: Dict[str, Any] = field(default_factory=dict)
    spatial_context: Optional[SpatialBusinessContext] = None
    completeness_score: float = 0.0
    
    @property
    def data_assets(self) -> List[DataAsset]:
        """Get data assets from canvas components"""
        return self.components.get(CanvasComponentType.DATA_ASSETS, [])
    
    @property
    def intelligence_capabilities(self) -> List[IntelligenceCapability]:
        """Get intelligence capabilities from canvas components"""
        return self.components.get(CanvasComponentType.INTELLIGENCE_CAPABILITIES, [])
    
    def add_component(self, component_type: CanvasComponentType, component: Any):
        """Add component to canvas"""
        if component_type not in self.components:
            self.components[component_type] = []
        self.components[component_type].append(component)
        self._update_completeness_score()
    
    def _update_completeness_score(self):
        """Calculate canvas completeness based on populated components"""
        total_components = len(CanvasComponentType)
        populated_components = len([ct for ct in CanvasComponentType if ct in self.components])
        self.completeness_score = populated_components / total_components


class BusinessTechnicalBridge:
    """
    Bridge between Data Business Canvas and technical implementation
    Maintains consistency with ADR-004 (SOW) and ADR-005 (KuzuDB)
    """
    
    def __init__(self, sow_manager=None, kuzu_manager=None, skos_router=None):
        """
        Initialize bridge with technical backend managers
        
        Args:
            sow_manager: SOW contract manager from ADR-004
            kuzu_manager: KuzuDB manager from ADR-005  
            skos_router: SKOS semantic router for term standardization
        """
        self.sow_manager = sow_manager
        self.kuzu_manager = kuzu_manager
        self.skos_router = skos_router
        
    def generate_technical_implementation(self, canvas: DataBusinessCanvas) -> Dict[str, Any]:
        """
        Generate complete technical implementation plan from business canvas
        
        Args:
            canvas: Data Business Canvas with business strategy
            
        Returns:
            Technical implementation plan with SOW contracts and KuzuDB schema
        """
        
        implementation_plan = {
            "canvas_id": canvas.canvas_id,
            "business_domain": canvas.business_domain,
            "generated_at": datetime.utcnow().isoformat(),
            "sow_contracts": [],
            "graph_schema": {},
            "spatial_configuration": {},
            "semantic_mappings": {},
            "feasibility_analysis": {},
            "implementation_timeline": {}
        }
        
        try:
            # Generate SOW contracts for data assets and capabilities
            if self.sow_manager:
                implementation_plan["sow_contracts"] = self._generate_sow_contracts(canvas)
            
            # Design KuzuDB schema for canvas data storage
            if self.kuzu_manager:
                implementation_plan["graph_schema"] = self._design_graph_schema(canvas)
            
            # Configure spatial components
            if canvas.spatial_context:
                implementation_plan["spatial_configuration"] = self._configure_spatial_backend(canvas)
            
            # Generate semantic mappings
            if self.skos_router:
                implementation_plan["semantic_mappings"] = self._generate_semantic_mappings(canvas)
            
            # Perform feasibility analysis
            implementation_plan["feasibility_analysis"] = self._analyze_technical_feasibility(canvas, implementation_plan)
            
            # Create implementation timeline
            implementation_plan["implementation_timeline"] = self._create_implementation_timeline(implementation_plan)
            
            logger.info(f"Generated technical implementation for canvas {canvas.canvas_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate technical implementation: {e}")
            implementation_plan["error"] = str(e)
            
        return implementation_plan
    
    def _generate_sow_contracts(self, canvas: DataBusinessCanvas) -> List[Dict[str, Any]]:
        """Generate SOW contracts for canvas components"""
        
        contracts = []
        
        # Data asset contracts
        for asset in canvas.data_assets:
            contract_spec = asset.to_sow_contract_spec()
            
            # Enhance with semantic context
            if self.skos_router and asset.skos_mappings:
                contract_spec["semantic_enrichment"] = {
                    "skos_mappings": asset.skos_mappings,
                    "concept_uri": asset.concept_uri,
                    "translation_method": "SKOS_deterministic"
                }
            
            contracts.append({
                "contract_type": "data_contract",
                "component_type": "data_asset",
                "specification": contract_spec,
                "adr_compliance": {
                    "adr_004_aligned": True,
                    "semantic_completeness": 0.95
                }
            })
        
        # Intelligence capability contracts  
        for capability in canvas.intelligence_capabilities:
            contract_spec = capability.to_sow_contract_spec()
            
            contracts.append({
                "contract_type": "processing_contract", 
                "component_type": "intelligence_capability",
                "specification": contract_spec,
                "adr_compliance": {
                    "adr_004_aligned": True,
                    "performance_requirements_defined": True
                }
            })
        
        return contracts
    
    def _design_graph_schema(self, canvas: DataBusinessCanvas) -> Dict[str, Any]:
        """Design KuzuDB schema for canvas storage and analysis"""
        
        schema = {
            "node_tables": [],
            "relationship_tables": [],
            "spatial_extensions": [],
            "canvas_queries": []
        }
        
        # Canvas node table
        schema["node_tables"].append({
            "table_name": "DataBusinessCanvas",
            "properties": {
                "canvas_id": "STRING",
                "business_domain": "STRING", 
                "creation_date": "TIMESTAMP",
                "completeness_score": "DOUBLE",
                "spatial_context_id": "STRING"
            },
            "primary_key": "canvas_id"
        })
        
        # Component node tables
        for component_type in CanvasComponentType:
            schema["node_tables"].append({
                "table_name": f"Canvas{component_type.value.title().replace('_', '')}",
                "properties": {
                    "component_id": "STRING",
                    "canvas_id": "STRING",
                    "name": "STRING",
                    "description": "STRING",
                    "concept_uri": "STRING",
                    "business_value": "DOUBLE"
                },
                "primary_key": "component_id"
            })
        
        # Canvas-component relationships
        schema["relationship_tables"].append({
            "table_name": "HAS_COMPONENT",
            "from_table": "DataBusinessCanvas",
            "to_table": "*Canvas*",
            "properties": {
                "component_type": "STRING",
                "priority": "INT",
                "last_updated": "TIMESTAMP"
            }
        })
        
        # Spatial integration (if spatial context exists)
        if canvas.spatial_context:
            schema["spatial_extensions"] = self._design_spatial_schema(canvas.spatial_context)
        
        # Predefined canvas analysis queries
        schema["canvas_queries"] = [
            {
                "query_name": "canvas_completeness_analysis",
                "description": "Analyze canvas completeness by component type",
                "cypher": """
                    MATCH (canvas:DataBusinessCanvas)-[:HAS_COMPONENT]->(component)
                    RETURN canvas.canvas_id, 
                           canvas.completeness_score,
                           count(component) as total_components,
                           collect(distinct component.component_type) as component_types
                """
            },
            {
                "query_name": "value_chain_analysis", 
                "description": "Analyze value creation chain from data assets to revenue",
                "cypher": """
                    MATCH (canvas:DataBusinessCanvas)-[:HAS_COMPONENT]->(asset:CanvasDataAssets),
                          (canvas)-[:HAS_COMPONENT]->(capability:CanvasIntelligenceCapabilities),
                          (canvas)-[:HAS_COMPONENT]->(revenue:CanvasRevenueStreams)
                    RETURN asset.name, capability.name, revenue.name,
                           asset.business_value + capability.business_value as total_value
                """
            }
        ]
        
        return schema
    
    def _design_spatial_schema(self, spatial_context: SpatialBusinessContext) -> List[Dict[str, Any]]:
        """Design spatial schema extensions for geographic business context"""
        
        spatial_schema = [
            {
                "table_name": "SpatialBusinessContext",
                "properties": {
                    "context_id": "STRING",
                    "geographic_scope": "STRING",
                    "market_coordinates": "GEOMETRY",
                    "geopolitical_risk": "DOUBLE"
                },
                "spatial_index": "market_coordinates"
            },
            {
                "relationship_name": "OPERATES_IN_REGION",
                "from_table": "DataBusinessCanvas",
                "to_table": "SpatialBusinessContext",
                "properties": {
                    "market_penetration": "DOUBLE",
                    "regulatory_compliance": "BOOLEAN"
                }
            }
        ]
        
        return spatial_schema
    
    def _configure_spatial_backend(self, canvas: DataBusinessCanvas) -> Dict[str, Any]:
        """Configure spatial backend for geographic business operations"""
        
        if not canvas.spatial_context:
            return {}
            
        spatial_config = {
            "context_id": canvas.spatial_context.context_id,
            "geographic_entities": [],
            "spatial_queries": [],
            "geopolitical_monitoring": {}
        }
        
        # Configure geographic entities from spatial context
        for entity_name, entity_data in canvas.spatial_context.geographic_scope.items():
            spatial_config["geographic_entities"].append({
                "entity_name": entity_name,
                "entity_type": entity_data.get("type", "region"),
                "coordinates": entity_data.get("coordinates"),
                "business_importance": entity_data.get("importance", 0.5)
            })
        
        # Spatial business queries
        spatial_config["spatial_queries"] = [
            {
                "query_name": "market_proximity_analysis",
                "description": "Find business opportunities within geographic radius",
                "spatial_operation": "ST_DWithin",
                "parameters": ["market_location", "search_radius"]
            },
            {
                "query_name": "geopolitical_risk_assessment",
                "description": "Assess business risk by geographic region",
                "spatial_operation": "ST_Intersects", 
                "parameters": ["business_region", "risk_zones"]
            }
        ]
        
        return spatial_config
    
    def _generate_semantic_mappings(self, canvas: DataBusinessCanvas) -> Dict[str, Any]:
        """Generate SKOS semantic mappings for canvas components"""
        
        semantic_mappings = {
            "concept_mappings": {},
            "multilingual_terms": {},
            "domain_vocabulary": canvas.business_domain,
            "translation_coverage": 0.0
        }
        
        mapped_components = 0
        total_components = 0
        
        # Map data assets to SKOS concepts
        for asset in canvas.data_assets:
            total_components += 1
            if asset.concept_uri and self.skos_router:
                # Get concept hierarchy for richer semantic context
                hierarchy = self.skos_router.get_concept_hierarchy(asset.concept_uri)
                
                semantic_mappings["concept_mappings"][asset.asset_id] = {
                    "concept_uri": asset.concept_uri,
                    "skos_mappings": asset.skos_mappings,
                    "concept_hierarchy": hierarchy,
                    "multilingual_labels": self._get_multilingual_labels(asset.concept_uri)
                }
                mapped_components += 1
        
        # Map intelligence capabilities
        for capability in canvas.intelligence_capabilities:
            total_components += 1
            if capability.concept_uri:
                semantic_mappings["concept_mappings"][capability.capability_id] = {
                    "concept_uri": capability.concept_uri,
                    "multilingual_labels": self._get_multilingual_labels(capability.concept_uri)
                }
                mapped_components += 1
        
        # Calculate semantic coverage
        semantic_mappings["translation_coverage"] = mapped_components / total_components if total_components > 0 else 0.0
        
        return semantic_mappings
    
    def _get_multilingual_labels(self, concept_uri: str) -> Dict[str, str]:
        """Get multilingual labels for concept URI"""
        
        if not self.skos_router:
            return {}
            
        # This would query the SKOS router for all language labels
        # Simplified implementation - in practice would query KuzuDB
        return {
            "en": "english_label",
            "tr": "turkish_label", 
            "fr": "french_label",
            "es": "spanish_label"
        }
    
    def _analyze_technical_feasibility(self, canvas: DataBusinessCanvas, implementation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical feasibility of canvas implementation"""
        
        feasibility = {
            "overall_score": 0.0,
            "component_feasibility": {},
            "resource_requirements": {},
            "risk_factors": [],
            "implementation_complexity": "medium",
            "estimated_timeline": "6 months"
        }
        
        # Analyze data asset feasibility
        data_feasibility_scores = []
        for asset in canvas.data_assets:
            asset_feasibility = self._assess_data_asset_feasibility(asset)
            feasibility["component_feasibility"][asset.asset_id] = asset_feasibility
            data_feasibility_scores.append(asset_feasibility["score"])
        
        # Analyze intelligence capability feasibility
        capability_feasibility_scores = []
        for capability in canvas.intelligence_capabilities:
            capability_feasibility = self._assess_capability_feasibility(capability)
            feasibility["component_feasibility"][capability.capability_id] = capability_feasibility
            capability_feasibility_scores.append(capability_feasibility["score"])
        
        # Calculate overall feasibility score
        all_scores = data_feasibility_scores + capability_feasibility_scores
        feasibility["overall_score"] = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Determine implementation complexity
        if feasibility["overall_score"] >= 0.8:
            feasibility["implementation_complexity"] = "low"
            feasibility["estimated_timeline"] = "3 months"
        elif feasibility["overall_score"] >= 0.6:
            feasibility["implementation_complexity"] = "medium" 
            feasibility["estimated_timeline"] = "6 months"
        else:
            feasibility["implementation_complexity"] = "high"
            feasibility["estimated_timeline"] = "12 months"
            
        return feasibility
    
    def _assess_data_asset_feasibility(self, asset: DataAsset) -> Dict[str, Any]:
        """Assess feasibility of implementing data asset"""
        
        # Simplified feasibility assessment
        semantic_completeness = 1.0 if asset.concept_uri else 0.5
        quality_definition = 1.0 if asset.quality_requirements else 0.3
        governance_clarity = 1.0 if asset.governance_rules else 0.4
        
        score = (semantic_completeness + quality_definition + governance_clarity) / 3
        
        return {
            "score": score,
            "factors": {
                "semantic_completeness": semantic_completeness,
                "quality_definition": quality_definition,
                "governance_clarity": governance_clarity
            },
            "recommendations": [] if score >= 0.7 else ["Define clearer semantic mappings", "Specify quality requirements"]
        }
    
    def _assess_capability_feasibility(self, capability: IntelligenceCapability) -> Dict[str, Any]:
        """Assess feasibility of implementing intelligence capability"""
        
        # Simplified capability feasibility assessment
        requirements_clarity = 1.0 if capability.ai_requirements else 0.3
        performance_defined = 1.0 if capability.performance_metrics else 0.4
        scalability_planned = 1.0 if capability.scalability_spec else 0.5
        
        score = (requirements_clarity + performance_defined + scalability_planned) / 3
        
        return {
            "score": score,
            "factors": {
                "requirements_clarity": requirements_clarity,
                "performance_defined": performance_defined,
                "scalability_planned": scalability_planned
            },
            "recommendations": [] if score >= 0.7 else ["Define AI requirements", "Specify performance metrics"]
        }
    
    def _create_implementation_timeline(self, implementation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation timeline based on feasibility analysis"""
        
        feasibility = implementation_plan.get("feasibility_analysis", {})
        complexity = feasibility.get("implementation_complexity", "medium")
        
        # Base timeline phases
        timeline = {
            "total_duration": feasibility.get("estimated_timeline", "6 months"),
            "phases": [
                {
                    "phase": "Foundation Setup",
                    "duration": "1 month",
                    "tasks": [
                        "Setup Apache Jena Fuseki triple store",
                        "Configure KuzuDB graph database",
                        "Initialize SKOS vocabulary"
                    ]
                },
                {
                    "phase": "SOW Contract Implementation", 
                    "duration": "2 months",
                    "tasks": [
                        "Implement data contracts for assets",
                        "Deploy processing contracts for capabilities",
                        "Setup semantic validation pipeline"
                    ]
                },
                {
                    "phase": "Canvas Integration",
                    "duration": "2 months", 
                    "tasks": [
                        "Build canvas-to-technical bridge",
                        "Implement real-time consistency validation",
                        "Deploy business stakeholder interface"
                    ]
                },
                {
                    "phase": "Testing & Optimization",
                    "duration": "1 month",
                    "tasks": [
                        "End-to-end workflow validation",
                        "Performance optimization",
                        "Business stakeholder training"
                    ]
                }
            ],
            "critical_milestones": [
                "Semantic foundation established",
                "First canvas-to-SOW translation",
                "Business stakeholder acceptance",
                "Production deployment"
            ]
        }
        
        # Adjust timeline based on complexity
        if complexity == "high":
            # Extend durations for high complexity
            for phase in timeline["phases"]:
                current_duration = int(phase["duration"].split()[0])
                phase["duration"] = f"{current_duration + 1} months"
                
        return timeline
    
    def validate_canvas_contract_consistency(self, canvas: DataBusinessCanvas, 
                                           contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate consistency between canvas and generated SOW contracts"""
        
        validation_results = {
            "is_consistent": True,
            "consistency_score": 0.0,
            "validation_checks": [],
            "inconsistencies": [],
            "recommendations": []
        }
        
        try:
            # Check that all data assets have corresponding contracts
            asset_contract_check = self._validate_asset_contract_mapping(canvas, contracts)
            validation_results["validation_checks"].append(asset_contract_check)
            
            # Check capability contract mapping
            capability_contract_check = self._validate_capability_contract_mapping(canvas, contracts)
            validation_results["validation_checks"].append(capability_contract_check)
            
            # Check semantic consistency
            semantic_check = self._validate_semantic_consistency(canvas, contracts)
            validation_results["validation_checks"].append(semantic_check)
            
            # Calculate overall consistency score
            check_scores = [check["score"] for check in validation_results["validation_checks"]]
            validation_results["consistency_score"] = sum(check_scores) / len(check_scores)
            validation_results["is_consistent"] = validation_results["consistency_score"] >= 0.8
            
            # Collect inconsistencies and recommendations
            for check in validation_results["validation_checks"]:
                validation_results["inconsistencies"].extend(check.get("issues", []))
                validation_results["recommendations"].extend(check.get("recommendations", []))
                
        except Exception as e:
            logger.error(f"Canvas-contract validation failed: {e}")
            validation_results["is_consistent"] = False
            validation_results["validation_error"] = str(e)
            
        return validation_results
    
    def _validate_asset_contract_mapping(self, canvas: DataBusinessCanvas, 
                                       contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data asset to contract mapping"""
        
        data_contracts = [c for c in contracts if c["contract_type"] == "data_contract"]
        
        check_result = {
            "check_name": "asset_contract_mapping",
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Check each asset has a contract
        mapped_assets = 0
        for asset in canvas.data_assets:
            asset_contract = next((c for c in data_contracts 
                                 if c["specification"]["data_contract_id"] == f"DC_{asset.asset_id}"), None)
            
            if asset_contract:
                mapped_assets += 1
                # Validate contract completeness
                spec = asset_contract["specification"]
                if not spec.get("quality_metrics"):
                    check_result["issues"].append(f"Asset {asset.asset_id} contract missing quality metrics")
                if not spec.get("governance_requirements"):
                    check_result["issues"].append(f"Asset {asset.asset_id} contract missing governance rules")
            else:
                check_result["issues"].append(f"No contract found for asset {asset.asset_id}")
                check_result["recommendations"].append(f"Generate data contract for asset {asset.asset_id}")
        
        check_result["score"] = mapped_assets / len(canvas.data_assets) if canvas.data_assets else 1.0
        
        return check_result
    
    def _validate_capability_contract_mapping(self, canvas: DataBusinessCanvas,
                                            contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate intelligence capability to contract mapping"""
        
        processing_contracts = [c for c in contracts if c["contract_type"] == "processing_contract"]
        
        check_result = {
            "check_name": "capability_contract_mapping",
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        mapped_capabilities = 0
        for capability in canvas.intelligence_capabilities:
            capability_contract = next((c for c in processing_contracts
                                      if c["specification"]["processing_contract_id"] == f"PC_{capability.capability_id}"), None)
            
            if capability_contract:
                mapped_capabilities += 1
                # Validate contract completeness
                spec = capability_contract["specification"]
                if not spec.get("performance_sla"):
                    check_result["issues"].append(f"Capability {capability.capability_id} contract missing performance SLA")
            else:
                check_result["issues"].append(f"No contract found for capability {capability.capability_id}")
                check_result["recommendations"].append(f"Generate processing contract for capability {capability.capability_id}")
        
        check_result["score"] = mapped_capabilities / len(canvas.intelligence_capabilities) if canvas.intelligence_capabilities else 1.0
        
        return check_result
    
    def _validate_semantic_consistency(self, canvas: DataBusinessCanvas,
                                     contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate semantic consistency across canvas and contracts"""
        
        check_result = {
            "check_name": "semantic_consistency",
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        semantic_score = 0.0
        total_checks = 0
        
        # Check concept URI consistency
        for asset in canvas.data_assets:
            total_checks += 1
            if asset.concept_uri:
                # Find corresponding contract
                asset_contract = next((c for c in contracts 
                                     if c["specification"]["data_contract_id"] == f"DC_{asset.asset_id}"), None)
                
                if asset_contract and asset_contract["specification"].get("business_context", {}).get("concept_uri") == asset.concept_uri:
                    semantic_score += 1.0
                else:
                    check_result["issues"].append(f"Concept URI mismatch for asset {asset.asset_id}")
        
        check_result["score"] = semantic_score / total_checks if total_checks > 0 else 1.0
        
        if check_result["score"] < 0.8:
            check_result["recommendations"].append("Review and align concept URIs between canvas and contracts")
        
        return check_result