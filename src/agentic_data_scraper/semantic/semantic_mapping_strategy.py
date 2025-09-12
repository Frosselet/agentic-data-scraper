"""
Semantic Mapping Strategy with Named Entity Resolution

Determines what should be semantically mapped vs preserved to maintain data meaning:
- Headers/Field Names: Standardize terminology via SKOS
- Common Nouns in Data: Standardize carefully with confidence scores  
- Proper Nouns (Named Entities): PRESERVE original - do not change
- Metadata Labels: Standardize vocabularies

Uses NER to distinguish common names from proper names before applying SKOS mapping.
Preserves meaning by adding semantic annotations as metadata, not replacements.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import logging
import spacy
from spacy import displacy

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Named entity types that should NOT be semantically standardized"""
    PERSON = "PERSON"           # People names
    ORG = "ORG"                # Organizations, companies
    GPE = "GPE"                # Geopolitical entities (cities, countries as proper nouns)
    LOC = "LOC"                # Locations, non-GPE
    PRODUCT = "PRODUCT"        # Products, objects, vehicles, foods, etc.
    EVENT = "EVENT"            # Named events
    FAC = "FAC"                # Facilities, buildings, airports, highways
    LAW = "LAW"                # Named documents made into laws
    LANGUAGE = "LANGUAGE"      # Any named language
    NORP = "NORP"              # Nationalities or religious or political groups
    DATE = "DATE"              # Absolute or relative dates or periods
    TIME = "TIME"              # Times smaller than a day
    PERCENT = "PERCENT"        # Percentage, including "%"
    MONEY = "MONEY"            # Monetary values, including unit
    QUANTITY = "QUANTITY"      # Measurements, as of weight or distance
    ORDINAL = "ORDINAL"        # "first", "second", etc.
    CARDINAL = "CARDINAL"      # Numerals that do not fall under another type


class MappingDecision(Enum):
    """Decision on how to handle semantic mapping"""
    STANDARDIZE = "standardize"        # Apply SKOS mapping
    PRESERVE = "preserve"              # Keep original, no mapping
    ANNOTATE = "annotate"              # Add semantic annotation but keep original
    REVIEW = "review"                  # Manual review required


@dataclass
class SemanticMappingCandidate:
    """Candidate for semantic mapping with analysis"""
    text: str
    context: str  # field name or surrounding text
    entity_type: Optional[EntityType]
    is_proper_noun: bool
    is_header: bool
    mapping_decision: MappingDecision
    confidence_score: float
    skos_candidates: List[Dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""


class NamedEntityResolver:
    """Named Entity Resolution to identify proper nouns that shouldn't be standardized"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize NER with spaCy model
        
        Args:
            model_name: spaCy model for NER (en_core_web_sm, en_core_web_md, en_core_web_lg)
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.warning(f"spaCy model {model_name} not found, using blank model")
            self.nlp = spacy.blank("en")
            
        # Custom patterns for supply chain entities
        self.supply_chain_patterns = self._load_supply_chain_patterns()
        
    def _load_supply_chain_patterns(self) -> Dict[str, List[str]]:
        """Load supply chain specific entity patterns"""
        
        return {
            # Company/Organization indicators
            "company_suffixes": [
                "ltd", "limited", "inc", "incorporated", "corp", "corporation",
                "llc", "plc", "gmbh", "sa", "spa", "bv", "ag", "co", "company",
                "group", "holding", "international", "global", "worldwide"
            ],
            
            # Geographic proper nouns (cities, regions) vs common geographic terms
            "geographic_proper": [
                "istanbul", "ankara", "izmir", "london", "paris", "berlin",
                "new york", "los angeles", "chicago", "tokyo", "shanghai",
                "mumbai", "delhi", "moscow", "sydney", "toronto"
            ],
            
            # Product brand names that shouldn't be standardized
            "brand_indicators": [
                "brand", "trademark", "®", "™", "©"
            ]
        }
        
    def analyze_text_for_entities(self, text: str, context: str = "") -> List[Tuple[str, EntityType, float]]:
        """
        Analyze text to identify named entities
        
        Args:
            text: Text to analyze
            context: Context (field name, etc.) for better analysis
            
        Returns:
            List of (entity_text, entity_type, confidence) tuples
        """
        
        if not text or len(text.strip()) == 0:
            return []
            
        try:
            doc = self.nlp(text)
            entities = []
            
            # Extract spaCy entities
            for ent in doc.ents:
                if ent.label_ in [e.value for e in EntityType]:
                    entity_type = EntityType(ent.label_)
                    confidence = 0.8  # spaCy base confidence
                    entities.append((ent.text, entity_type, confidence))
            
            # Custom supply chain entity detection
            custom_entities = self._detect_custom_supply_chain_entities(text, context)
            entities.extend(custom_entities)
            
            return entities
            
        except Exception as e:
            logger.error(f"NER analysis failed for text '{text}': {e}")
            return []
    
    def _detect_custom_supply_chain_entities(self, text: str, context: str) -> List[Tuple[str, EntityType, float]]:
        """Detect supply chain specific entities not caught by standard NER"""
        
        entities = []
        text_lower = text.lower()
        
        # Company name detection
        for suffix in self.supply_chain_patterns["company_suffixes"]:
            if suffix in text_lower:
                # High probability this is a company name
                entities.append((text, EntityType.ORG, 0.9))
                break
        
        # Geographic proper noun detection
        for geo_name in self.supply_chain_patterns["geographic_proper"]:
            if geo_name in text_lower:
                entities.append((text, EntityType.GPE, 0.85))
                break
        
        # Brand name detection
        for brand_indicator in self.supply_chain_patterns["brand_indicators"]:
            if brand_indicator in text_lower:
                entities.append((text, EntityType.PRODUCT, 0.9))
                break
        
        # Context-based detection
        if context:
            context_lower = context.lower()
            
            # If field is about names, likely proper noun
            if any(name_field in context_lower for name_field in ["name", "title", "brand", "supplier", "company"]):
                if not any(common_term in text_lower for common_term in ["type", "category", "kind", "class"]):
                    entities.append((text, EntityType.ORG, 0.7))
        
        return entities
    
    def is_proper_noun(self, text: str, context: str = "") -> Tuple[bool, float, str]:
        """
        Determine if text is a proper noun that should be preserved
        
        Args:
            text: Text to analyze
            context: Field name or context
            
        Returns:
            (is_proper_noun, confidence, reasoning)
        """
        
        entities = self.analyze_text_for_entities(text, context)
        
        if entities:
            # Has named entities - likely proper noun
            entity_types = [ent[1] for ent in entities]
            max_confidence = max(ent[2] for ent in entities)
            
            # These entity types are definitely proper nouns
            definite_proper = {EntityType.PERSON, EntityType.ORG, EntityType.GPE, 
                             EntityType.FAC, EntityType.EVENT, EntityType.LAW}
            
            if any(et in definite_proper for et in entity_types):
                return True, max_confidence, f"Contains named entities: {[et.value for et in entity_types]}"
        
        # Capitalization analysis
        if text.isupper():
            return False, 0.3, "All caps - likely acronym or common term"
        elif text.istitle() and len(text.split()) > 1:
            return True, 0.6, "Title case multi-word - likely proper noun"
        elif text[0].isupper() and not any(word in text.lower() for word in ["the", "and", "of", "in", "for"]):
            return True, 0.5, "Capitalized without articles - possibly proper noun"
        
        return False, 0.8, "Appears to be common noun suitable for standardization"


class SemanticMappingStrategy:
    """
    Strategy for determining what should be semantically mapped while preserving meaning
    """
    
    def __init__(self, ner_resolver: NamedEntityResolver, skos_router=None):
        self.ner_resolver = ner_resolver
        self.skos_router = skos_router
        
        # Terms that should always be standardized (headers/metadata)
        self.always_standardize_patterns = {
            "field_names", "column_headers", "metadata_labels", 
            "schema_fields", "api_parameters", "configuration_keys"
        }
        
        # Terms that should never be standardized
        self.never_standardize_patterns = {
            "email", "phone", "id", "uuid", "hash", "token", 
            "password", "key", "secret", "url", "uri"
        }
    
    def analyze_mapping_candidates(self, data_structure: Dict[str, Any], 
                                 context: str = "data") -> List[SemanticMappingCandidate]:
        """
        Analyze data structure to identify semantic mapping candidates
        
        Args:
            data_structure: Data to analyze (headers, values, metadata)
            context: Context type (headers, data, metadata)
            
        Returns:
            List of semantic mapping candidates with recommendations
        """
        
        candidates = []
        
        if isinstance(data_structure, dict):
            # Analyze dictionary keys (headers/field names) and values
            for key, value in data_structure.items():
                
                # Always analyze keys as potential headers
                header_candidate = self._analyze_text(
                    text=key,
                    context=f"field_name:{context}",
                    is_header=True
                )
                candidates.append(header_candidate)
                
                # Analyze values based on type
                if isinstance(value, str) and value.strip():
                    value_candidate = self._analyze_text(
                        text=value,
                        context=f"field_value:{key}",
                        is_header=False
                    )
                    candidates.append(value_candidate)
                elif isinstance(value, (dict, list)):
                    # Recursive analysis for nested structures
                    nested_candidates = self.analyze_mapping_candidates(value, f"{context}.{key}")
                    candidates.extend(nested_candidates)
                    
        elif isinstance(data_structure, list):
            for i, item in enumerate(data_structure):
                if isinstance(item, str) and item.strip():
                    item_candidate = self._analyze_text(
                        text=item,
                        context=f"list_item:{context}[{i}]",
                        is_header=False
                    )
                    candidates.append(item_candidate)
                elif isinstance(item, dict):
                    nested_candidates = self.analyze_mapping_candidates(item, f"{context}[{i}]")
                    candidates.extend(nested_candidates)
        
        return candidates
    
    def _analyze_text(self, text: str, context: str, is_header: bool) -> SemanticMappingCandidate:
        """Analyze individual text for semantic mapping suitability"""
        
        # Initialize candidate
        candidate = SemanticMappingCandidate(
            text=text,
            context=context,
            entity_type=None,
            is_proper_noun=False,
            is_header=is_header,
            mapping_decision=MappingDecision.REVIEW,
            confidence_score=0.0,
            reasoning=""
        )
        
        try:
            # Skip if matches never standardize patterns
            if any(pattern in text.lower() for pattern in self.never_standardize_patterns):
                candidate.mapping_decision = MappingDecision.PRESERVE
                candidate.confidence_score = 0.9
                candidate.reasoning = "Matches never-standardize pattern (ID, hash, etc.)"
                return candidate
            
            # Headers/field names - usually standardize
            if is_header or any(pattern in context.lower() for pattern in self.always_standardize_patterns):
                candidate.mapping_decision = MappingDecision.STANDARDIZE
                candidate.confidence_score = 0.8
                candidate.reasoning = "Header/field name - standardize terminology"
                
                # Get SKOS candidates for headers
                if self.skos_router:
                    candidate.skos_candidates = self._get_skos_candidates(text, context)
                
                return candidate
            
            # For data values, check if proper noun
            is_proper, proper_confidence, proper_reasoning = self.ner_resolver.is_proper_noun(text, context)
            candidate.is_proper_noun = is_proper
            
            if is_proper:
                # Proper noun - preserve but maybe annotate
                candidate.mapping_decision = MappingDecision.ANNOTATE
                candidate.confidence_score = proper_confidence
                candidate.reasoning = f"Proper noun - preserve original. {proper_reasoning}"
                
                # Still get semantic annotations for context
                if self.skos_router:
                    candidate.skos_candidates = self._get_skos_candidates(text, context)
                    
            else:
                # Common noun - consider standardizing
                candidate.mapping_decision = MappingDecision.STANDARDIZE
                candidate.confidence_score = 1.0 - proper_confidence  # Inverse of proper noun confidence
                candidate.reasoning = f"Common noun - standardize. {proper_reasoning}"
                
                if self.skos_router:
                    candidate.skos_candidates = self._get_skos_candidates(text, context)
                    
                    # If no good SKOS matches, preserve original
                    if not candidate.skos_candidates or max(c.get('confidence', 0) for c in candidate.skos_candidates) < 0.6:
                        candidate.mapping_decision = MappingDecision.PRESERVE
                        candidate.reasoning += " No suitable SKOS matches found."
            
        except Exception as e:
            logger.error(f"Failed to analyze text '{text}': {e}")
            candidate.mapping_decision = MappingDecision.REVIEW
            candidate.reasoning = f"Analysis failed: {str(e)}"
        
        return candidate
    
    def _get_skos_candidates(self, text: str, context: str) -> List[Dict[str, Any]]:
        """Get SKOS mapping candidates for text"""
        
        if not self.skos_router:
            return []
            
        try:
            # Try different languages based on context
            languages_to_try = ["en", "auto"]  # Start with English, then auto-detect
            
            for lang in languages_to_try:
                result = self.skos_router.route_term_to_preferred(text, lang, "en")
                
                if result.get('preferred_label') and result.get('translation_confidence', 0) > 0.5:
                    return [{
                        'preferred_label': result['preferred_label'],
                        'concept_uri': result.get('concept_uri', ''),
                        'confidence': result['translation_confidence'],
                        'method': result['method'],
                        'source_lang': lang,
                        'target_lang': 'en'
                    }]
            
            return []
            
        except Exception as e:
            logger.error(f"SKOS candidate lookup failed for '{text}': {e}")
            return []
    
    def generate_semantic_enrichment_plan(self, candidates: List[SemanticMappingCandidate]) -> Dict[str, Any]:
        """Generate plan for semantic enrichment preserving data meaning"""
        
        plan = {
            "standardize": [],      # Apply SKOS mapping
            "preserve": [],         # Keep original unchanged  
            "annotate": [],         # Add semantic metadata but keep original
            "review": [],           # Manual review required
            "statistics": {},
            "recommendations": []
        }
        
        # Categorize candidates by decision
        for candidate in candidates:
            if candidate.mapping_decision == MappingDecision.STANDARDIZE:
                plan["standardize"].append({
                    "text": candidate.text,
                    "context": candidate.context,
                    "is_header": candidate.is_header,
                    "skos_candidates": candidate.skos_candidates,
                    "confidence": candidate.confidence_score,
                    "reasoning": candidate.reasoning
                })
            elif candidate.mapping_decision == MappingDecision.PRESERVE:
                plan["preserve"].append({
                    "text": candidate.text,
                    "context": candidate.context,
                    "reasoning": candidate.reasoning
                })
            elif candidate.mapping_decision == MappingDecision.ANNOTATE:
                plan["annotate"].append({
                    "text": candidate.text,
                    "context": candidate.context,
                    "entity_type": candidate.entity_type.value if candidate.entity_type else None,
                    "semantic_annotations": candidate.skos_candidates,
                    "reasoning": candidate.reasoning
                })
            else:
                plan["review"].append({
                    "text": candidate.text,
                    "context": candidate.context,
                    "reasoning": candidate.reasoning
                })
        
        # Generate statistics
        total_candidates = len(candidates)
        plan["statistics"] = {
            "total_candidates": total_candidates,
            "standardize_count": len(plan["standardize"]),
            "preserve_count": len(plan["preserve"]), 
            "annotate_count": len(plan["annotate"]),
            "review_count": len(plan["review"]),
            "standardize_percentage": len(plan["standardize"]) / total_candidates if total_candidates > 0 else 0,
            "meaning_preservation_score": (len(plan["preserve"]) + len(plan["annotate"])) / total_candidates if total_candidates > 0 else 0
        }
        
        # Generate recommendations
        if len(plan["review"]) > 0:
            plan["recommendations"].append(f"Manual review required for {len(plan['review'])} candidates")
        
        if plan["statistics"]["meaning_preservation_score"] < 0.3:
            plan["recommendations"].append("Consider increasing preservation threshold - many proper nouns may be getting standardized")
            
        if plan["statistics"]["standardize_percentage"] < 0.1:
            plan["recommendations"].append("Very few candidates selected for standardization - check SKOS vocabulary coverage")
        
        return plan
    
    def apply_semantic_enrichment(self, data: Dict[str, Any], enrichment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply semantic enrichment while preserving original data meaning"""
        
        enriched_data = data.copy()
        enrichment_metadata = {
            "semantic_enrichments": {},
            "preserved_originals": {},
            "semantic_annotations": {},
            "processing_summary": {}
        }
        
        try:
            # Apply standardizations (headers and common nouns)
            for item in enrichment_plan["standardize"]:
                if item["is_header"] and item["skos_candidates"]:
                    best_candidate = max(item["skos_candidates"], key=lambda x: x["confidence"])
                    
                    # For headers, create standardized version alongside original
                    original_key = item["text"]
                    standardized_key = f"{best_candidate['preferred_label']}_standardized"
                    
                    if original_key in enriched_data:
                        enriched_data[standardized_key] = enriched_data[original_key]
                        enrichment_metadata["semantic_enrichments"][original_key] = {
                            "standardized_term": best_candidate["preferred_label"],
                            "concept_uri": best_candidate.get("concept_uri", ""),
                            "confidence": best_candidate["confidence"],
                            "method": "SKOS_standardization"
                        }
                
                elif not item["is_header"] and item["skos_candidates"]:
                    # For data values, add standardized version alongside original
                    best_candidate = max(item["skos_candidates"], key=lambda x: x["confidence"])
                    
                    # Find the data in structure and add standardized version
                    field_context = item["context"].split(":")[-1]
                    if field_context in enriched_data:
                        enriched_data[f"{field_context}_standardized"] = best_candidate["preferred_label"]
                        enrichment_metadata["semantic_enrichments"][field_context] = {
                            "original_value": item["text"],
                            "standardized_value": best_candidate["preferred_label"],
                            "concept_uri": best_candidate.get("concept_uri", ""),
                            "confidence": best_candidate["confidence"]
                        }
            
            # Preserve originals with annotation
            for item in enrichment_plan["annotate"]:
                field_context = item["context"].split(":")[-1]
                enrichment_metadata["semantic_annotations"][field_context] = {
                    "original_preserved": item["text"],
                    "entity_type": item.get("entity_type"),
                    "semantic_context": item.get("semantic_annotations", []),
                    "preservation_reason": item["reasoning"]
                }
            
            # Record preserved items
            for item in enrichment_plan["preserve"]:
                field_context = item["context"].split(":")[-1] 
                enrichment_metadata["preserved_originals"][field_context] = {
                    "value": item["text"],
                    "reason": item["reasoning"]
                }
            
            # Add processing summary
            enrichment_metadata["processing_summary"] = {
                "total_processed": len(enrichment_plan["standardize"]) + len(enrichment_plan["preserve"]) + len(enrichment_plan["annotate"]),
                "standardized": len(enrichment_plan["standardize"]),
                "preserved": len(enrichment_plan["preserve"]),
                "annotated": len(enrichment_plan["annotate"]),
                "meaning_preservation_applied": True,
                "processing_timestamp": "2025-01-09T12:00:00Z"
            }
            
            # Add enrichment metadata to result
            enriched_data["_semantic_enrichment_metadata"] = enrichment_metadata
            
        except Exception as e:
            logger.error(f"Failed to apply semantic enrichment: {e}")
            enriched_data["_semantic_enrichment_error"] = str(e)
        
        return enriched_data


def create_meaning_preserving_semantic_mapper(kuzu_db_path: str = None) -> SemanticMappingStrategy:
    """
    Factory function to create semantic mapper that preserves data meaning
    
    Args:
        kuzu_db_path: Path to KuzuDB with SKOS data
        
    Returns:
        Configured semantic mapping strategy
    """
    
    # Initialize NER resolver
    ner_resolver = NamedEntityResolver()
    
    # Initialize SKOS router if path provided
    skos_router = None
    if kuzu_db_path:
        try:
            from .skos_router import SKOSSemanticRouter
            skos_router = SKOSSemanticRouter(kuzu_db_path)
        except ImportError:
            logger.warning("SKOS router not available - semantic mapping will be limited")
    
    return SemanticMappingStrategy(ner_resolver, skos_router)