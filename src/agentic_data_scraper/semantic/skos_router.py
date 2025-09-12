"""
SKOS Semantic Router for Deterministic Multilingual Term Translation

Integrates SKOS (Simple Knowledge Organization System) with KuzuDB for 
deterministic semantic translation during data extraction. Enables routing
from original terms (e.g., "zeytin yağı"@tr) to preferred labels (e.g., "olive oil"@en)
without relying on stochastic AI translators.

Key Benefits:
- 100% deterministic translation confidence
- Multilingual support with context preservation
- In-memory KuzuDB routing for performance
- Crisis-ready supply chain vocabulary
"""

from typing import Dict, Any, List, Optional
import kuzu
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SKOSSemanticRouter:
    """Routes multilingual terms to preferred labels via SKOS concepts in KuzuDB"""
    
    def __init__(self, kuzu_db_path: str, fuseki_endpoint: Optional[str] = None):
        """
        Initialize SKOS router with KuzuDB backend
        
        Args:
            kuzu_db_path: Path to KuzuDB database
            fuseki_endpoint: Optional Fuseki triple store endpoint for SKOS synchronization
        """
        self.db = kuzu.Database(kuzu_db_path)
        self.conn = kuzu.Connection(self.db)
        self.fuseki_endpoint = fuseki_endpoint
        self.setup_skos_routing_tables()
        
    def setup_skos_routing_tables(self):
        """Create KuzuDB tables for SKOS concept routing"""
        
        try:
            # SKOS Concepts table - flexible multilingual design
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS SKOSConcept(
                    concept_uri STRING,
                    scheme_uri STRING,
                    definition STRING,
                    broader_concept STRING,
                    PRIMARY KEY(concept_uri)
                )
            """)
            
            # Separate table for multilingual labels - supports ANY language
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS SKOSLabel(
                    label_id STRING,
                    concept_uri STRING,
                    label_text STRING,
                    language_code STRING,
                    label_type STRING,  -- 'prefLabel', 'altLabel', 'hiddenLabel'
                    PRIMARY KEY(label_id)
                )
            """)
            
            # Alternative Labels table for multilingual routing
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS SKOSAltLabel(
                    alt_label STRING,
                    language STRING,
                    concept_uri STRING,
                    PRIMARY KEY(alt_label, language)
                )
            """)
            
            # SKOS relationships for hierarchical navigation
            self.conn.execute("""
                CREATE REL TABLE IF NOT EXISTS SKOS_BROADER(
                    FROM SKOSConcept TO SKOSConcept
                )
            """)
            
            # Load default supply chain SKOS vocabulary
            self.load_supply_chain_skos()
            
            logger.info("SKOS routing tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create SKOS tables: {e}")
            raise
            
    def load_supply_chain_skos(self):
        """Load predefined supply chain SKOS concepts into KuzuDB"""
        
        # Supply chain vocabulary with multilingual support
        supply_concepts = [
            {
                'concept_uri': 'http://localhost:3030/dbc/ontology#OliveOilConcept',
                'scheme_uri': 'http://localhost:3030/dbc/ontology#SupplyChainVocabulary',
                'pref_label_en': 'olive oil',
                'pref_label_tr': 'zeytin yağı',
                'pref_label_fr': 'huile d\'olive',
                'pref_label_es': 'aceite de oliva',
                'definition': 'Edible oil extracted from olives',
                'broader_concept': 'http://localhost:3030/dbc/ontology#EdibleOilConcept'
            },
            {
                'concept_uri': 'http://localhost:3030/dbc/ontology#TariffConcept',
                'scheme_uri': 'http://localhost:3030/dbc/ontology#SupplyChainVocabulary',
                'pref_label_en': 'tariff',
                'pref_label_tr': 'tarife',
                'pref_label_fr': 'tarif douanier',
                'pref_label_es': 'arancel',
                'definition': 'Tax imposed on imported goods',
                'broader_concept': 'http://localhost:3030/dbc/ontology#TradePolicyConcept'
            },
            {
                'concept_uri': 'http://localhost:3030/dbc/ontology#SupplierConcept',
                'scheme_uri': 'http://localhost:3030/dbc/ontology#SupplyChainVocabulary',
                'pref_label_en': 'supplier',
                'pref_label_tr': 'tedarikçi',
                'pref_label_fr': 'fournisseur',
                'pref_label_es': 'proveedor',
                'definition': 'External organization providing goods or services',
                'broader_concept': 'http://localhost:3030/dbc/ontology#BusinessEntityConcept'
            },
            {
                'concept_uri': 'http://localhost:3030/dbc/ontology#CustomsDutyConcept',
                'scheme_uri': 'http://localhost:3030/dbc/ontology#SupplyChainVocabulary',
                'pref_label_en': 'customs duty',
                'pref_label_tr': 'gümrük vergisi',
                'pref_label_fr': 'droits de douane',
                'pref_label_es': 'derechos de aduana',
                'definition': 'Tax levied on goods imported across national borders',
                'broader_concept': 'http://localhost:3030/dbc/ontology#TariffConcept'
            }
        ]
        
        # Insert concepts
        for concept in supply_concepts:
            try:
                self.conn.execute(
                    "CREATE (:SKOSConcept {concept_uri: $uri, scheme_uri: $scheme, "
                    "pref_label_en: $en, pref_label_tr: $tr, pref_label_fr: $fr, "
                    "pref_label_es: $es, definition: $def, broader_concept: $broader})",
                    concept
                )
            except Exception as e:
                # Skip if already exists
                if "already exists" not in str(e):
                    logger.warning(f"Failed to insert concept {concept['concept_uri']}: {e}")
        
        # Alternative labels for flexible routing
        alt_labels = [
            # Olive oil variants
            {'alt_label': 'zeytin yağı', 'language': 'tr', 'concept_uri': 'http://localhost:3030/dbc/ontology#OliveOilConcept'},
            {'alt_label': 'zeytinyağı', 'language': 'tr', 'concept_uri': 'http://localhost:3030/dbc/ontology#OliveOilConcept'},
            {'alt_label': 'extra virgin olive oil', 'language': 'en', 'concept_uri': 'http://localhost:3030/dbc/ontology#OliveOilConcept'},
            
            # Tariff variants
            {'alt_label': 'gümrük vergisi', 'language': 'tr', 'concept_uri': 'http://localhost:3030/dbc/ontology#CustomsDutyConcept'},
            {'alt_label': 'customs duty', 'language': 'en', 'concept_uri': 'http://localhost:3030/dbc/ontology#CustomsDutyConcept'},
            {'alt_label': 'import tax', 'language': 'en', 'concept_uri': 'http://localhost:3030/dbc/ontology#TariffConcept'},
            {'alt_label': 'import duty', 'language': 'en', 'concept_uri': 'http://localhost:3030/dbc/ontology#TariffConcept'},
            
            # Supplier variants
            {'alt_label': 'vendor', 'language': 'en', 'concept_uri': 'http://localhost:3030/dbc/ontology#SupplierConcept'},
            {'alt_label': 'satıcı', 'language': 'tr', 'concept_uri': 'http://localhost:3030/dbc/ontology#SupplierConcept'},
            {'alt_label': 'proveedor', 'language': 'es', 'concept_uri': 'http://localhost:3030/dbc/ontology#SupplierConcept'},
        ]
        
        for alt_label in alt_labels:
            try:
                self.conn.execute(
                    "CREATE (:SKOSAltLabel {alt_label: $label, language: $lang, concept_uri: $uri})",
                    alt_label
                )
            except Exception as e:
                # Skip if already exists
                if "already exists" not in str(e):
                    logger.warning(f"Failed to insert alt label {alt_label}: {e}")
                    
        logger.info(f"Loaded {len(supply_concepts)} SKOS concepts and {len(alt_labels)} alternative labels")
    
    def route_term_to_preferred(self, original_term: str, source_language: str, target_language: str = 'en') -> Dict[str, Any]:
        """
        Route original term to preferred label via SKOS concepts
        
        Args:
            original_term: Term to translate (e.g., "zeytin yağı")
            source_language: Language code of original term (e.g., "tr")
            target_language: Target language code (e.g., "en")
            
        Returns:
            Dictionary with routing results including confidence and method
        """
        
        # Normalize term for matching
        normalized_term = original_term.lower().strip()
        
        try:
            # First, try exact match via preferred labels
            pref_query = f"""
                MATCH (concept:SKOSConcept)
                WHERE concept.pref_label_{source_language} = $term
                RETURN concept.concept_uri as uri, 
                       concept.pref_label_{target_language} as target_label,
                       concept.pref_label_en as pref_en,
                       concept.definition as definition
            """
            
            result = self.conn.execute(pref_query, {'term': normalized_term}).get_next()
            
            if result:
                target_label = result[1] if result[1] else result[2]  # Fallback to English
                return {
                    'original_term': original_term,
                    'preferred_label': target_label,
                    'concept_uri': result[0],
                    'definition': result[3],
                    'translation_confidence': 1.0,
                    'method': 'SKOS_preferred_match',
                    'language_source': source_language,
                    'language_target': target_language
                }
            
            # Second, try alternative label matching
            alt_query = f"""
                MATCH (alt:SKOSAltLabel)-[:HAS_CONCEPT]->(concept:SKOSConcept)
                WHERE alt.alt_label = $term AND alt.language = $lang
                RETURN concept.concept_uri as uri, 
                       concept.pref_label_{target_language} as target_label,
                       concept.pref_label_en as pref_en,
                       concept.definition as definition
            """
            
            result = self.conn.execute(alt_query, {
                'term': normalized_term,
                'lang': source_language
            }).get_next()
            
            if result:
                target_label = result[1] if result[1] else result[2]  # Fallback to English
                return {
                    'original_term': original_term,
                    'preferred_label': target_label,
                    'concept_uri': result[0],
                    'definition': result[3],
                    'translation_confidence': 0.95,  # Slightly lower for alt label match
                    'method': 'SKOS_alternative_match',
                    'language_source': source_language,
                    'language_target': target_language
                }
            
            # Third, try fuzzy matching (basic implementation)
            fuzzy_result = self._fuzzy_skos_match(normalized_term, source_language, target_language)
            if fuzzy_result:
                return fuzzy_result
                
        except Exception as e:
            logger.error(f"SKOS routing error for term '{original_term}': {e}")
        
        # No SKOS match found
        return {
            'original_term': original_term,
            'preferred_label': None,
            'translation_confidence': 0.0,
            'method': 'SKOS_not_found',
            'language_source': source_language,
            'language_target': target_language,
            'needs_ai_fallback': True
        }
    
    def _fuzzy_skos_match(self, term: str, source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """Basic fuzzy matching for partial term matches"""
        
        try:
            # Simple contains-based fuzzy matching
            fuzzy_query = f"""
                MATCH (concept:SKOSConcept)
                WHERE concept.pref_label_{source_lang} CONTAINS $partial_term
                RETURN concept.concept_uri as uri, 
                       concept.pref_label_{target_lang} as target_label,
                       concept.pref_label_en as pref_en,
                       concept.definition as definition
                LIMIT 1
            """
            
            result = self.conn.execute(fuzzy_query, {'partial_term': term}).get_next()
            
            if result:
                target_label = result[1] if result[1] else result[2]
                return {
                    'original_term': term,
                    'preferred_label': target_label,
                    'concept_uri': result[0],
                    'definition': result[3],
                    'translation_confidence': 0.7,  # Lower confidence for fuzzy match
                    'method': 'SKOS_fuzzy_match',
                    'language_source': source_lang,
                    'language_target': target_lang
                }
                
        except Exception as e:
            logger.debug(f"Fuzzy SKOS matching failed: {e}")
            
        return None
    
    def get_concept_hierarchy(self, concept_uri: str) -> List[Dict[str, Any]]:
        """Retrieve concept hierarchy for semantic navigation"""
        
        try:
            hierarchy_query = """
                MATCH (concept:SKOSConcept)-[:SKOS_BROADER*]->(broader:SKOSConcept)
                WHERE concept.concept_uri = $uri
                RETURN broader.concept_uri as uri,
                       broader.pref_label_en as label,
                       broader.definition as definition
            """
            
            results = self.conn.execute(hierarchy_query, {'uri': concept_uri})
            
            hierarchy = []
            for result in results:
                hierarchy.append({
                    'concept_uri': result[0],
                    'preferred_label': result[1],
                    'definition': result[2]
                })
                
            return hierarchy
            
        except Exception as e:
            logger.error(f"Failed to retrieve concept hierarchy for {concept_uri}: {e}")
            return []
    
    def add_custom_concept(self, concept_data: Dict[str, Any], alt_labels: List[Dict[str, str]] = None):
        """Add custom SKOS concept for domain-specific vocabulary"""
        
        try:
            # Insert concept
            self.conn.execute(
                "CREATE (:SKOSConcept {concept_uri: $uri, scheme_uri: $scheme, "
                "pref_label_en: $en, pref_label_tr: $tr, pref_label_fr: $fr, "
                "pref_label_es: $es, definition: $def, broader_concept: $broader})",
                concept_data
            )
            
            # Insert alternative labels if provided
            if alt_labels:
                for alt_label in alt_labels:
                    self.conn.execute(
                        "CREATE (:SKOSAltLabel {alt_label: $label, language: $lang, concept_uri: $uri})",
                        {**alt_label, 'concept_uri': concept_data['concept_uri']}
                    )
                    
            logger.info(f"Added custom SKOS concept: {concept_data['concept_uri']}")
            
        except Exception as e:
            logger.error(f"Failed to add custom concept: {e}")
            raise
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'conn'):
            self.conn.close()
        if hasattr(self, 'db'):
            self.db.close()


class SKOSEnabledCollector:
    """Data collector with SKOS-based semantic enrichment"""
    
    def __init__(self, skos_router: SKOSSemanticRouter):
        self.skos_router = skos_router
        
    def extract_with_semantic_routing(self, raw_data: Dict[str, Any], 
                                    term_mappings: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Extract data with SKOS-based term standardization
        
        Args:
            raw_data: Original extracted data
            term_mappings: Field mapping configuration {field_name: {source_lang, target_lang}}
            
        Returns:
            Enriched data with semantic mappings
        """
        
        enriched_data = raw_data.copy()
        semantic_mappings = {}
        
        # Default term mappings for common supply chain fields
        if term_mappings is None:
            term_mappings = {
                'product_name_tr': {'source_lang': 'tr', 'target_lang': 'en'},
                'product_name_es': {'source_lang': 'es', 'target_lang': 'en'},
                'policy_term': {'source_lang': 'en', 'target_lang': 'en'},
                'supplier_type_tr': {'source_lang': 'tr', 'target_lang': 'en'}
            }
        
        # Route terms to preferred labels
        for field_name, mapping_config in term_mappings.items():
            if field_name in raw_data and raw_data[field_name]:
                routing_result = self.skos_router.route_term_to_preferred(
                    raw_data[field_name],
                    mapping_config['source_lang'],
                    mapping_config['target_lang']
                )
                
                if routing_result['preferred_label']:
                    # Add standardized field
                    standardized_field = field_name.replace('_tr', '').replace('_es', '') + '_standardized'
                    enriched_data[standardized_field] = routing_result['preferred_label']
                    enriched_data[f'{field_name}_concept_uri'] = routing_result['concept_uri']
                    
                    semantic_mappings[field_name] = routing_result
        
        # Add semantic enrichment metadata
        enriched_data['_semantic_mappings'] = semantic_mappings
        enriched_data['_translation_method'] = 'SKOS_deterministic'
        enriched_data['_enrichment_timestamp'] = datetime.utcnow().isoformat()
        enriched_data['_semantic_completeness'] = len(semantic_mappings) / len(term_mappings) if term_mappings else 0.0
        
        return enriched_data