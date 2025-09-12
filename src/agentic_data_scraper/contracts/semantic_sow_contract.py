"""
Semantic SOW Contract with Integrated SKOS Catalog Discovery

Extends ADR-004 SOW contracts with automatic semantic vocabulary discovery,
SKOS mapping recommendations, and multilingual standardization capabilities.
Integrates real semantic catalogs directly into contract specifications.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import yaml
import logging

from ..semantic.catalog_discovery import (
    SemanticCatalogRegistry, 
    SOWSemanticRecommendationEngine,
    SKOSVocabulary,
    AccessMethod
)

logger = logging.getLogger(__name__)


@dataclass
class SemanticMapping:
    """SKOS mapping specification for SOW data fields"""
    field_name: str
    vocabulary_uri: str
    vocabulary_title: str
    mapping_type: str  # skos:exactMatch, skos:closeMatch, skos:relatedMatch
    sparql_query: Optional[str] = None
    languages_supported: List[str] = field(default_factory=lambda: ["ALL"])
    quality_score: float = 0.0
    access_method: str = "sparql"


@dataclass
class VocabularyReference:
    """Reference to discovered SKOS vocabulary"""
    uri: str
    title: str
    publisher: str
    license: str
    version: str
    languages: List[str]
    access_methods: Dict[str, str]
    concept_count: int
    quality_score: float
    last_updated: str
    subject_domains: List[str]


@dataclass
class SemanticStandardization:
    """Complete semantic standardization specification for SOW"""
    catalog_discovery_enabled: bool = True
    auto_recommend: bool = True
    quality_threshold: float = 0.7
    discovered_vocabularies: List[VocabularyReference] = field(default_factory=list)
    field_mappings: List[SemanticMapping] = field(default_factory=list)
    implementation_config: Dict[str, Any] = field(default_factory=dict)
    quality_monitoring: Dict[str, bool] = field(default_factory=dict)


class SemanticSOWContract:
    """
    SOW Contract with integrated semantic catalog discovery and SKOS mapping
    Automatically discovers and integrates real semantic vocabularies
    """
    
    def __init__(self, contract_id: str, business_domain: str):
        self.contract_id = contract_id
        self.business_domain = business_domain
        self.creation_date = datetime.utcnow()
        
        # Core contract components (from ADR-004)
        self.data_requirements = {}
        self.quality_requirements = {}
        self.governance_requirements = []
        
        # NEW: Semantic standardization with real SKOS catalogs
        self.semantic_standardization = SemanticStandardization()
        
        # Initialize semantic catalog discovery
        self.catalog_registry = SemanticCatalogRegistry()
        self.recommendation_engine = SOWSemanticRecommendationEngine(self.catalog_registry)
        
    def add_data_requirement(self, field_name: str, field_spec: Dict[str, Any], 
                           enable_semantic_mapping: bool = True):
        """
        Add data requirement with automatic semantic vocabulary discovery
        
        Args:
            field_name: Name of data field
            field_spec: Field specification (type, description, constraints)
            enable_semantic_mapping: Whether to auto-discover SKOS mappings
        """
        
        self.data_requirements[field_name] = field_spec
        
        if enable_semantic_mapping and self.semantic_standardization.catalog_discovery_enabled:
            # Discover suitable vocabularies for this field
            self._discover_field_vocabularies(field_name, field_spec)
    
    def _discover_field_vocabularies(self, field_name: str, field_spec: Dict[str, Any]):
        """Discover and recommend SKOS vocabularies for specific field"""
        
        try:
            # Create mini SOW spec for field-specific recommendations
            field_sow_spec = {
                "business_domain": self.business_domain,
                "data_schema": {
                    "fields": [{
                        "name": field_name,
                        "type": field_spec.get("type", "string"),
                        "description": field_spec.get("description", "")
                    }]
                },
                "languages": field_spec.get("languages", ["en"]),
                "quality_requirements": {
                    "completeness_threshold": self.semantic_standardization.quality_threshold
                }
            }
            
            # Get vocabulary recommendations
            recommendations = self.recommendation_engine.recommend_vocabularies_for_sow(field_sow_spec)
            
            # Add discovered vocabularies to contract
            for vocab_data in recommendations.get("primary_vocabularies", []):
                vocab_ref = VocabularyReference(
                    uri=vocab_data.uri,
                    title=vocab_data.title,
                    publisher=vocab_data.publisher,
                    license=vocab_data.license,
                    version=vocab_data.version,
                    languages=vocab_data.languages_supported,
                    access_methods={
                        method.value: url for method, url in vocab_data.access_methods.items()
                    },
                    concept_count=vocab_data.concept_count,
                    quality_score=vocab_data.completeness_score,
                    last_updated=vocab_data.modified.strftime("%Y-%m-%d"),
                    subject_domains=vocab_data.subject_domains
                )
                
                # Add if not already present
                if not any(v.uri == vocab_ref.uri for v in self.semantic_standardization.discovered_vocabularies):
                    self.semantic_standardization.discovered_vocabularies.append(vocab_ref)
            
            # Add field mappings
            for mapping_suggestion in recommendations.get("mapping_suggestions", []):
                if mapping_suggestion["field_name"] == field_name:
                    for vocab_mapping in mapping_suggestion["vocabulary_mappings"]:
                        semantic_mapping = SemanticMapping(
                            field_name=field_name,
                            vocabulary_uri=vocab_mapping["vocabulary_uri"],
                            vocabulary_title=vocab_mapping["vocabulary_title"],
                            mapping_type=vocab_mapping["suggested_property"],
                            sparql_query=vocab_mapping.get("example_query"),
                            languages_supported=field_spec.get("languages", ["ALL"]),
                            quality_score=vocab_mapping["mapping_confidence"],
                            access_method=vocab_mapping["access_method"]
                        )
                        self.semantic_standardization.field_mappings.append(semantic_mapping)
            
            logger.info(f"Discovered {len(recommendations.get('primary_vocabularies', []))} vocabularies for field {field_name}")
            
        except Exception as e:
            logger.warning(f"Failed to discover vocabularies for field {field_name}: {e}")
    
    def configure_semantic_implementation(self, kuzu_db_path: str, 
                                        vocabulary_sync_schedule: str = "daily",
                                        fallback_ai_translator: bool = False):
        """Configure semantic implementation parameters"""
        
        self.semantic_standardization.implementation_config = {
            "skos_router_config": {
                "kuzu_db_path": kuzu_db_path,
                "vocabulary_sync_schedule": vocabulary_sync_schedule,
                "translation_method": "SKOS_deterministic",
                "fallback_ai_translator": fallback_ai_translator
            },
            "quality_monitoring": {
                "vocabulary_currency_check": True,
                "concept_resolution_test": True,
                "multilingual_completeness_check": True,
                "performance_threshold_ms": 50
            }
        }
    
    def validate_semantic_mappings(self) -> Dict[str, Any]:
        """Validate that all field mappings have suitable SKOS vocabularies"""
        
        validation_results = {
            "is_valid": True,
            "coverage_score": 0.0,
            "field_coverage": {},
            "vocabulary_health": {},
            "recommendations": []
        }
        
        try:
            # Check field coverage
            mapped_fields = {mapping.field_name for mapping in self.semantic_standardization.field_mappings}
            total_fields = len(self.data_requirements)
            covered_fields = len(mapped_fields.intersection(set(self.data_requirements.keys())))
            
            validation_results["coverage_score"] = covered_fields / total_fields if total_fields > 0 else 0.0
            
            # Validate each field mapping
            for field_name in self.data_requirements.keys():
                field_mappings = [m for m in self.semantic_standardization.field_mappings if m.field_name == field_name]
                
                if field_mappings:
                    best_mapping = max(field_mappings, key=lambda m: m.quality_score)
                    validation_results["field_coverage"][field_name] = {
                        "mapped": True,
                        "vocabulary": best_mapping.vocabulary_title,
                        "quality_score": best_mapping.quality_score,
                        "languages": best_mapping.languages_supported
                    }
                else:
                    validation_results["field_coverage"][field_name] = {
                        "mapped": False,
                        "recommendation": f"Add semantic mapping for {field_name}"
                    }
                    validation_results["recommendations"].append(
                        f"Discover SKOS vocabulary for field: {field_name}"
                    )
            
            # Check vocabulary health
            for vocab in self.semantic_standardization.discovered_vocabularies:
                days_since_update = (datetime.now() - datetime.strptime(vocab.last_updated, "%Y-%m-%d")).days
                
                validation_results["vocabulary_health"][vocab.title] = {
                    "quality_score": vocab.quality_score,
                    "currency_days": days_since_update,
                    "is_current": days_since_update < 365,  # Within 1 year
                    "access_available": len(vocab.access_methods) > 0
                }
            
            # Overall validation
            if validation_results["coverage_score"] < 0.7:
                validation_results["is_valid"] = False
                validation_results["recommendations"].append(
                    "Improve semantic mapping coverage (currently {:.1%})".format(validation_results["coverage_score"])
                )
            
        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["error"] = str(e)
            logger.error(f"Semantic mapping validation failed: {e}")
        
        return validation_results
    
    def export_contract_yaml(self) -> str:
        """Export complete SOW contract with semantic mappings as YAML"""
        
        contract_data = {
            "sow_contract_id": self.contract_id,
            "business_domain": self.business_domain,
            "creation_date": self.creation_date.isoformat(),
            
            # Core SOW components (ADR-004)
            "data_requirements": self.data_requirements,
            "quality_requirements": self.quality_requirements,
            "governance_requirements": self.governance_requirements,
            
            # NEW: Semantic standardization with real SKOS catalogs
            "semantic_standardization": {
                "catalog_discovery": {
                    "enabled": self.semantic_standardization.catalog_discovery_enabled,
                    "auto_recommend": self.semantic_standardization.auto_recommend,
                    "quality_threshold": self.semantic_standardization.quality_threshold
                },
                "discovered_vocabularies": {
                    "primary": [
                        {
                            "uri": vocab.uri,
                            "title": vocab.title,
                            "publisher": vocab.publisher,
                            "license": vocab.license,
                            "version": vocab.version,
                            "languages": vocab.languages,
                            "access_methods": vocab.access_methods,
                            "concept_count": vocab.concept_count,
                            "quality_score": vocab.quality_score,
                            "last_updated": vocab.last_updated,
                            "subject_domains": vocab.subject_domains
                        }
                        for vocab in self.semantic_standardization.discovered_vocabularies
                    ]
                },
                "field_mappings": {
                    mapping.field_name: {
                        "vocabulary": mapping.vocabulary_uri,
                        "vocabulary_title": mapping.vocabulary_title,
                        "mapping_type": mapping.mapping_type,
                        "sparql_query": mapping.sparql_query,
                        "languages_supported": mapping.languages_supported,
                        "quality_score": mapping.quality_score,
                        "access_method": mapping.access_method
                    }
                    for mapping in self.semantic_standardization.field_mappings
                },
                "implementation": self.semantic_standardization.implementation_config,
            }
        }
        
        return yaml.dump(contract_data, default_flow_style=False, allow_unicode=True)
    
    def get_implementation_code(self) -> str:
        """Generate implementation code for semantic SOW contract"""
        
        code_template = f'''
"""
Implementation code for SOW Contract: {self.contract_id}
Generated semantic SKOS integration with real vocabulary catalogs
"""

from agentic_data_scraper.semantic.skos_router import SKOSSemanticRouter, SKOSEnabledCollector

def setup_semantic_sow_implementation():
    """Setup semantic SOW implementation with discovered vocabularies"""
    
    # Initialize SKOS router
    skos_router = SKOSSemanticRouter("{self.semantic_standardization.implementation_config.get('skos_router_config', {}).get('kuzu_db_path', './data/skos_concepts.db')}")
    
    # Load discovered vocabularies
    discovered_vocabularies = {[vocab.uri for vocab in self.semantic_standardization.discovered_vocabularies]}
    
    for vocab_uri in discovered_vocabularies:
        # Load vocabulary from SPARQL endpoint or download
        try:
            skos_router.load_vocabulary_from_endpoint(vocab_uri)
            print(f"✅ Loaded vocabulary: {{vocab_uri}}")
        except Exception as e:
            print(f"⚠️  Failed to load {{vocab_uri}}: {{e}}")
    
    # Configure field mappings
    field_mappings = {{
        {self._generate_field_mapping_code()}
    }}
    
    # Create SKOS-enabled collector
    collector = SKOSEnabledCollector(skos_router)
    
    return collector, field_mappings

def collect_semantically_enriched_data(raw_data: dict):
    """Collect data with semantic SKOS enrichment"""
    
    collector, field_mappings = setup_semantic_sow_implementation()
    
    # Apply semantic routing
    enriched_data = collector.extract_with_semantic_routing(
        raw_data, 
        term_mappings=field_mappings
    )
    
    return enriched_data

# Example usage:
# raw_data = {{"supplier_country": "Türkiye", "product_name": "zeytin yağı"}}
# enriched = collect_semantically_enriched_data(raw_data)
# Result: {{"supplier_country": "Türkiye", "supplier_country_standardized": "Turkey", ...}}
'''
        
        return code_template
    
    def _generate_field_mapping_code(self) -> str:
        """Generate field mapping configuration code"""
        
        mapping_lines = []
        for mapping in self.semantic_standardization.field_mappings:
            languages = mapping.languages_supported if mapping.languages_supported != ["ALL"] else ["auto"]
            mapping_lines.append(
                f"'{mapping.field_name}': {{'source_lang': '{languages[0] if languages else 'auto'}', 'target_lang': 'en'}}"
            )
        
        return ',\n        '.join(mapping_lines)


# Factory function for creating semantic SOW contracts
def create_semantic_sow_contract(contract_id: str, business_domain: str, 
                                data_fields: List[Dict[str, Any]]) -> SemanticSOWContract:
    """
    Create SOW contract with automatic SKOS catalog discovery
    
    Args:
        contract_id: Unique contract identifier
        business_domain: Business domain (supply_chain, logistics, trade, etc.)
        data_fields: List of data field specifications
        
    Returns:
        Fully configured semantic SOW contract with discovered vocabularies
    """
    
    contract = SemanticSOWContract(contract_id, business_domain)
    
    # Add data requirements with automatic semantic discovery
    for field in data_fields:
        contract.add_data_requirement(
            field_name=field["name"],
            field_spec=field,
            enable_semantic_mapping=True
        )
    
    # Configure implementation
    contract.configure_semantic_implementation(
        kuzu_db_path=f"./data/{contract_id.lower()}_skos.db",
        vocabulary_sync_schedule="daily",
        fallback_ai_translator=False
    )
    
    logger.info(f"Created semantic SOW contract {contract_id} with {len(contract.semantic_standardization.discovered_vocabularies)} discovered vocabularies")
    
    return contract