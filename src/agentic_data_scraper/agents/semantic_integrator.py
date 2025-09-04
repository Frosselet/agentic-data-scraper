"""
Semantic Integrator Agent - Applies domain-specific semantic enrichment and ontology alignment.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from .base import BaseAgent
from .data_parser import ParsedData
import asyncio
import logging

class SemanticAnnotation(BaseModel):
    """Semantic enrichment results with ontology mappings and quality metrics."""
    
    ontology_mappings: Dict[str, str] = Field(
        description="Mappings from data fields to ontology concepts"
    )
    skos_concepts: List[str] = Field(
        description="SKOS concept URIs for semantic classification"
    )
    owl_alignments: List[str] = Field(
        description="OWL ontology alignments and class mappings"
    )
    semantic_quality_score: float = Field(
        description="Quality score for semantic annotations (0.0 to 1.0)"
    )
    domain_coverage: float = Field(
        description="Coverage percentage for domain-specific concepts"
    )
    linked_entities: List[str] = Field(
        description="Linked data entities and external references"
    )
    knowledge_graph_triples: List[Dict[str, str]] = Field(
        default_factory=list,
        description="RDF triples for knowledge graph representation"
    )
    semantic_validation_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results of semantic consistency validation"
    )
    recommended_ontologies: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Recommended ontologies for the business domain"
    )
    entity_resolution: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Entity resolution and disambiguation results"
    )

class SemanticIntegratorAgent(BaseAgent):
    """
    Agent specialized in semantic enrichment and ontology alignment.
    
    Applies domain-specific ontologies, creates SKOS mappings, performs OWL alignment,
    and generates knowledge graph representations for improved data interoperability.
    """
    
    def __init__(
        self,
        agent_id: str = "semantic_integrator",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 900
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.domain_ontologies = self._initialize_domain_ontologies()
        self.entity_resolvers = self._initialize_entity_resolvers()
        
    def _initialize_domain_ontologies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize domain-specific ontology mappings."""
        return {
            "agriculture": {
                "ontologies": [
                    {
                        "name": "AGROVOC",
                        "uri": "http://aims.fao.org/aos/agrovoc/",
                        "description": "FAO multilingual thesaurus for agriculture",
                        "concepts": ["crops", "livestock", "farming_practices", "food_security"]
                    },
                    {
                        "name": "FOODIE",
                        "uri": "http://foodie-cloud.org/model/foodie",
                        "description": "Farm-oriented ontology for interoperability",
                        "concepts": ["farm_management", "crop_monitoring", "precision_agriculture"]
                    },
                    {
                        "name": "SAREF4AGRI",
                        "uri": "https://saref.etsi.org/saref4agri/",
                        "description": "Smart applications for agriculture ontology",
                        "concepts": ["sensors", "iot_devices", "smart_farming"]
                    }
                ],
                "common_fields": {
                    "crop": "agrovoc:c_1972",
                    "yield": "agrovoc:c_8488", 
                    "farm": "agrovoc:c_2807",
                    "harvest": "agrovoc:c_3500"
                }
            },
            "trading": {
                "ontologies": [
                    {
                        "name": "FIBO",
                        "uri": "https://spec.edmcouncil.org/fibo/",
                        "description": "Financial Industry Business Ontology",
                        "concepts": ["financial_instruments", "markets", "organizations", "contracts"]
                    },
                    {
                        "name": "FpML",
                        "uri": "https://www.fpml.org/spec/",
                        "description": "Financial products markup language ontology",
                        "concepts": ["derivatives", "trade_data", "risk_management"]
                    }
                ],
                "common_fields": {
                    "price": "fibo:SecurityPrice",
                    "volume": "fibo:TradingVolume",
                    "instrument": "fibo:FinancialInstrument",
                    "market": "fibo:Market"
                }
            },
            "supply_chain": {
                "ontologies": [
                    {
                        "name": "GS1",
                        "uri": "https://www.gs1.org/voc/",
                        "description": "GS1 vocabulary for supply chain",
                        "concepts": ["products", "locations", "parties", "transactions"]
                    },
                    {
                        "name": "Supply Chain Ontology",
                        "uri": "http://www.supply-chain-ontology.org/",
                        "description": "Comprehensive supply chain ontology",
                        "concepts": ["logistics", "inventory", "suppliers", "transportation"]
                    }
                ],
                "common_fields": {
                    "product": "gs1:Product",
                    "location": "gs1:Place",
                    "supplier": "gs1:Organization",
                    "shipment": "gs1:Shipment"
                }
            },
            "general": {
                "ontologies": [
                    {
                        "name": "Schema.org",
                        "uri": "https://schema.org/",
                        "description": "General purpose structured data vocabulary",
                        "concepts": ["organizations", "products", "places", "events"]
                    },
                    {
                        "name": "Dublin Core",
                        "uri": "http://purl.org/dc/terms/",
                        "description": "Metadata element set",
                        "concepts": ["title", "creator", "subject", "description"]
                    }
                ],
                "common_fields": {
                    "name": "schema:name",
                    "description": "dc:description",
                    "date": "dc:date",
                    "organization": "schema:Organization"
                }
            }
        }
    
    def _initialize_entity_resolvers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize entity resolution endpoints and strategies."""
        return {
            "dbpedia": {
                "endpoint": "http://dbpedia.org/sparql",
                "lookup_url": "http://lookup.dbpedia.org/api/search",
                "confidence_threshold": 0.7
            },
            "wikidata": {
                "endpoint": "https://query.wikidata.org/sparql", 
                "api_url": "https://www.wikidata.org/w/api.php",
                "confidence_threshold": 0.8
            },
            "geonames": {
                "api_url": "http://api.geonames.org/searchJSON",
                "confidence_threshold": 0.75,
                "username": "demo"  # Should be configured
            }
        }
    
    async def _process(
        self,
        transformed_data: ParsedData,
        business_domain: str = "general",
        existing_ontologies: List[str] = None,
        entity_linking_enabled: bool = True,
        **kwargs
    ) -> SemanticAnnotation:
        """
        Apply semantic enrichment to transformed data.
        
        Args:
            transformed_data: Parsed and transformed data
            business_domain: Business domain context for ontology selection
            existing_ontologies: List of existing ontologies to align with
            entity_linking_enabled: Whether to perform entity linking
            
        Returns:
            SemanticAnnotation: Comprehensive semantic enrichment results
        """
        self.logger.info(f"Applying semantic enrichment for domain: {business_domain}")
        
        existing_ontologies = existing_ontologies or []
        
        # Select appropriate ontologies for the domain
        recommended_ontologies = await self._recommend_ontologies(
            business_domain, transformed_data.schema
        )
        
        # Generate ontology mappings
        ontology_mappings = await self._generate_ontology_mappings(
            transformed_data.schema, business_domain, recommended_ontologies
        )
        
        # Create SKOS concept mappings
        skos_concepts = await self._create_skos_mappings(
            transformed_data.schema, ontology_mappings, business_domain
        )
        
        # Generate OWL alignments
        owl_alignments = await self._generate_owl_alignments(
            ontology_mappings, existing_ontologies
        )
        
        # Perform entity linking if enabled
        linked_entities = []
        entity_resolution = {}
        if entity_linking_enabled and transformed_data.sample_data:
            linked_entities, entity_resolution = await self._perform_entity_linking(
                transformed_data.sample_data, ontology_mappings
            )
        
        # Generate knowledge graph triples
        kg_triples = await self._generate_knowledge_graph_triples(
            transformed_data.schema, ontology_mappings, linked_entities
        )
        
        # Validate semantic consistency
        validation_results = await self._validate_semantic_consistency(
            ontology_mappings, owl_alignments
        )
        
        # Calculate quality metrics
        semantic_quality_score = await self._calculate_semantic_quality(
            ontology_mappings, validation_results, linked_entities
        )
        
        domain_coverage = await self._calculate_domain_coverage(
            ontology_mappings, business_domain
        )
        
        return SemanticAnnotation(
            ontology_mappings=ontology_mappings,
            skos_concepts=skos_concepts,
            owl_alignments=owl_alignments,
            semantic_quality_score=semantic_quality_score,
            domain_coverage=domain_coverage,
            linked_entities=linked_entities,
            knowledge_graph_triples=kg_triples,
            semantic_validation_results=validation_results,
            recommended_ontologies=recommended_ontologies,
            entity_resolution=entity_resolution
        )
    
    async def _recommend_ontologies(
        self,
        business_domain: str,
        schema: Dict[str, str]
    ) -> List[Dict[str, str]]:
        """Recommend appropriate ontologies for the business domain and data schema."""
        
        domain_config = self.domain_ontologies.get(business_domain, self.domain_ontologies["general"])
        recommended = []
        
        # Add domain-specific ontologies
        for ontology in domain_config["ontologies"]:
            coverage_score = await self._calculate_ontology_coverage(ontology, schema)
            if coverage_score > 0.3:  # 30% coverage threshold
                recommended.append({
                    "name": ontology["name"],
                    "uri": ontology["uri"],
                    "description": ontology["description"],
                    "coverage_score": coverage_score,
                    "recommendation_reason": f"Good coverage ({coverage_score:.1%}) for {business_domain} domain"
                })
        
        # Add general-purpose ontologies if domain coverage is low
        if not recommended or max(r["coverage_score"] for r in recommended) < 0.5:
            for ontology in self.domain_ontologies["general"]["ontologies"]:
                coverage_score = await self._calculate_ontology_coverage(ontology, schema)
                if coverage_score > 0.2:
                    recommended.append({
                        "name": ontology["name"],
                        "uri": ontology["uri"],
                        "description": ontology["description"],
                        "coverage_score": coverage_score,
                        "recommendation_reason": "General-purpose fallback ontology"
                    })
        
        # Sort by coverage score
        recommended.sort(key=lambda x: x["coverage_score"], reverse=True)
        return recommended
    
    async def _calculate_ontology_coverage(
        self,
        ontology: Dict[str, Any],
        schema: Dict[str, str]
    ) -> float:
        """Calculate how well an ontology covers the data schema."""
        
        if "concepts" not in ontology:
            return 0.0
        
        ontology_concepts = [concept.lower() for concept in ontology["concepts"]]
        schema_fields = [field.lower() for field in schema.keys()]
        
        matches = 0
        for field in schema_fields:
            # Simple keyword matching - could be enhanced with NLP
            for concept in ontology_concepts:
                if concept in field or field in concept:
                    matches += 1
                    break
        
        return matches / len(schema_fields) if schema_fields else 0.0
    
    async def _generate_ontology_mappings(
        self,
        schema: Dict[str, str],
        business_domain: str,
        recommended_ontologies: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """Generate mappings from data fields to ontology concepts."""
        
        mappings = {}
        domain_config = self.domain_ontologies.get(business_domain, self.domain_ontologies["general"])
        
        # Use pre-defined common field mappings
        common_mappings = domain_config.get("common_fields", {})
        
        for field_name in schema.keys():
            field_lower = field_name.lower()
            
            # Check direct matches
            if field_lower in common_mappings:
                mappings[field_name] = common_mappings[field_lower]
                continue
            
            # Check partial matches
            best_match = None
            best_score = 0.0
            
            for concept_name, concept_uri in common_mappings.items():
                similarity = await self._calculate_field_concept_similarity(field_lower, concept_name)
                if similarity > best_score and similarity > 0.6:  # 60% similarity threshold
                    best_score = similarity
                    best_match = concept_uri
            
            if best_match:
                mappings[field_name] = best_match
            else:
                # Generate generic mapping
                mappings[field_name] = await self._generate_generic_mapping(field_name, business_domain)
        
        return mappings
    
    async def _calculate_field_concept_similarity(self, field_name: str, concept_name: str) -> float:
        """Calculate similarity between field name and ontology concept."""
        import difflib
        
        # Simple string similarity
        base_similarity = difflib.SequenceMatcher(None, field_name, concept_name).ratio()
        
        # Check for partial matches
        if field_name in concept_name or concept_name in field_name:
            base_similarity = max(base_similarity, 0.8)
        
        # Check for common synonyms (simplified)
        synonyms = {
            "price": ["cost", "amount", "value"],
            "date": ["time", "timestamp", "when"],
            "name": ["title", "label", "identifier"],
            "location": ["place", "address", "site"]
        }
        
        for primary, synonym_list in synonyms.items():
            if field_name == primary and concept_name in synonym_list:
                base_similarity = max(base_similarity, 0.9)
            elif concept_name == primary and field_name in synonym_list:
                base_similarity = max(base_similarity, 0.9)
        
        return base_similarity
    
    async def _generate_generic_mapping(self, field_name: str, business_domain: str) -> str:
        """Generate generic ontology mapping for unmapped fields."""
        
        # Use Schema.org as fallback
        schema_org_base = "https://schema.org/"
        
        # Simple heuristics for common field types
        field_lower = field_name.lower()
        
        if any(keyword in field_lower for keyword in ["name", "title", "label"]):
            return f"{schema_org_base}name"
        elif any(keyword in field_lower for keyword in ["date", "time", "when"]):
            return f"{schema_org_base}dateTime"
        elif any(keyword in field_lower for keyword in ["price", "cost", "amount"]):
            return f"{schema_org_base}price"
        elif any(keyword in field_lower for keyword in ["description", "desc", "summary"]):
            return f"{schema_org_base}description"
        elif any(keyword in field_lower for keyword in ["location", "place", "address"]):
            return f"{schema_org_base}Place"
        else:
            return f"{schema_org_base}Property"
    
    async def _create_skos_mappings(
        self,
        schema: Dict[str, str],
        ontology_mappings: Dict[str, str],
        business_domain: str
    ) -> List[str]:
        """Create SKOS concept mappings for hierarchical classification."""
        
        skos_concepts = []
        
        # Generate SKOS concept scheme for the domain
        domain_scheme_uri = f"http://example.org/concepts/{business_domain}"
        skos_concepts.append(f"{domain_scheme_uri}#ConceptScheme")
        
        # Create concept hierarchy based on field groupings
        field_groups = await self._group_related_fields(schema, ontology_mappings)
        
        for group_name, fields in field_groups.items():
            group_concept_uri = f"{domain_scheme_uri}#{group_name}"
            skos_concepts.append(group_concept_uri)
            
            # Add narrower concepts for individual fields
            for field in fields:
                field_concept_uri = f"{domain_scheme_uri}#{field.replace(' ', '_')}"
                skos_concepts.append(field_concept_uri)
        
        return skos_concepts
    
    async def _group_related_fields(
        self,
        schema: Dict[str, str],
        ontology_mappings: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """Group related fields for SKOS hierarchy creation."""
        
        groups = {
            "identification": [],
            "temporal": [],
            "spatial": [],
            "quantitative": [],
            "qualitative": []
        }
        
        for field_name, field_type in schema.items():
            field_lower = field_name.lower()
            
            # Temporal fields
            if field_type == "datetime" or any(keyword in field_lower for keyword in ["date", "time", "when"]):
                groups["temporal"].append(field_name)
            
            # Spatial fields  
            elif any(keyword in field_lower for keyword in ["location", "place", "address", "lat", "lon", "geo"]):
                groups["spatial"].append(field_name)
            
            # Quantitative fields
            elif field_type in ["integer", "float"] or any(keyword in field_lower for keyword in ["amount", "count", "price", "value"]):
                groups["quantitative"].append(field_name)
            
            # Identification fields
            elif any(keyword in field_lower for keyword in ["id", "name", "identifier", "code"]):
                groups["identification"].append(field_name)
            
            # Everything else is qualitative
            else:
                groups["qualitative"].append(field_name)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    async def _generate_owl_alignments(
        self,
        ontology_mappings: Dict[str, str],
        existing_ontologies: List[str]
    ) -> List[str]:
        """Generate OWL ontology alignments and class mappings."""
        
        owl_alignments = []
        
        # Generate class definitions
        for field_name, concept_uri in ontology_mappings.items():
            class_definition = f"""
            Class: {concept_uri}
                SubClassOf: owl:Thing
                Annotations: rdfs:label "{field_name}"@en
            """
            owl_alignments.append(class_definition.strip())
        
        # Generate property definitions
        for field_name in ontology_mappings.keys():
            property_uri = f"http://example.org/properties/{field_name.lower().replace(' ', '_')}"
            property_definition = f"""
            ObjectProperty: {property_uri}
                Domain: owl:Thing
                Range: {ontology_mappings[field_name]}
                Annotations: rdfs:label "has{field_name.replace(' ', '')}"@en
            """
            owl_alignments.append(property_definition.strip())
        
        # Generate alignment axioms with existing ontologies
        for existing_ontology in existing_ontologies:
            alignment_axiom = f"""
            EquivalentClasses: 
                {existing_ontology}#SimilarConcept 
                {list(ontology_mappings.values())[0] if ontology_mappings else 'owl:Thing'}
            """
            owl_alignments.append(alignment_axiom.strip())
        
        return owl_alignments
    
    async def _perform_entity_linking(
        self,
        sample_data: List[Dict[str, Any]],
        ontology_mappings: Dict[str, str]
    ) -> tuple:
        """Perform entity linking to external knowledge bases."""
        
        linked_entities = []
        entity_resolution = {}
        
        for record in sample_data[:5]:  # Link first 5 records as sample
            for field_name, field_value in record.items():
                if field_name in ontology_mappings and isinstance(field_value, str):
                    # Try to resolve entities for string values
                    resolved_entities = await self._resolve_entity(field_value, field_name)
                    
                    if resolved_entities:
                        linked_entities.extend(resolved_entities)
                        if field_name not in entity_resolution:
                            entity_resolution[field_name] = []
                        entity_resolution[field_name].extend(resolved_entities)
        
        # Remove duplicates
        linked_entities = list(set(linked_entities))
        
        return linked_entities, entity_resolution
    
    async def _resolve_entity(self, entity_value: str, field_name: str) -> List[str]:
        """Resolve entity to external knowledge base URIs."""
        
        resolved = []
        
        # Skip if value is too short or looks like a number
        if len(entity_value.strip()) < 3 or entity_value.strip().isdigit():
            return resolved
        
        # Try different resolvers based on field type
        field_lower = field_name.lower()
        
        if any(keyword in field_lower for keyword in ["location", "place", "city", "country"]):
            # Use GeoNames for geographic entities
            geonames_uri = await self._resolve_geonames_entity(entity_value)
            if geonames_uri:
                resolved.append(geonames_uri)
        
        # Try DBpedia for general entities
        dbpedia_uri = await self._resolve_dbpedia_entity(entity_value)
        if dbpedia_uri:
            resolved.append(dbpedia_uri)
        
        return resolved
    
    async def _resolve_geonames_entity(self, entity_value: str) -> Optional[str]:
        """Resolve geographic entity using GeoNames."""
        try:
            # Simulate GeoNames API call
            # In real implementation, would make HTTP request to GeoNames API
            if any(keyword in entity_value.lower() for keyword in ["new york", "london", "paris", "tokyo"]):
                return f"http://sws.geonames.org/{hash(entity_value) % 10000000}/"
        except Exception as e:
            self.logger.warning(f"GeoNames resolution failed for '{entity_value}': {e}")
        
        return None
    
    async def _resolve_dbpedia_entity(self, entity_value: str) -> Optional[str]:
        """Resolve entity using DBpedia lookup service."""
        try:
            # Simulate DBpedia lookup
            # In real implementation, would make HTTP request to DBpedia lookup API
            if len(entity_value.split()) <= 3:  # Reasonable entity name length
                entity_normalized = entity_value.replace(" ", "_")
                return f"http://dbpedia.org/resource/{entity_normalized}"
        except Exception as e:
            self.logger.warning(f"DBpedia resolution failed for '{entity_value}': {e}")
        
        return None
    
    async def _generate_knowledge_graph_triples(
        self,
        schema: Dict[str, str],
        ontology_mappings: Dict[str, str],
        linked_entities: List[str]
    ) -> List[Dict[str, str]]:
        """Generate RDF triples for knowledge graph representation."""
        
        triples = []
        
        # Generate schema triples
        for field_name, concept_uri in ontology_mappings.items():
            triples.append({
                "subject": f"http://example.org/schema#{field_name}",
                "predicate": "rdf:type",
                "object": concept_uri
            })
            
            triples.append({
                "subject": f"http://example.org/schema#{field_name}",
                "predicate": "rdfs:label",
                "object": f'"{field_name}"@en'
            })
        
        # Generate entity triples
        for entity_uri in linked_entities[:10]:  # Limit to first 10
            triples.append({
                "subject": entity_uri,
                "predicate": "rdf:type",
                "object": "owl:Thing"
            })
            
            triples.append({
                "subject": "http://example.org/dataset",
                "predicate": "schema:mentions",
                "object": entity_uri
            })
        
        return triples
    
    async def _validate_semantic_consistency(
        self,
        ontology_mappings: Dict[str, str],
        owl_alignments: List[str]
    ) -> Dict[str, Any]:
        """Validate semantic consistency of mappings and alignments."""
        
        validation_results = {
            "mapping_consistency": True,
            "owl_syntax_valid": True,
            "concept_coherence": True,
            "issues": []
        }
        
        # Check for duplicate mappings
        reverse_mappings = {}
        for field, concept in ontology_mappings.items():
            if concept in reverse_mappings:
                validation_results["issues"].append(
                    f"Multiple fields ({field}, {reverse_mappings[concept]}) mapped to same concept: {concept}"
                )
                validation_results["mapping_consistency"] = False
            else:
                reverse_mappings[concept] = field
        
        # Validate OWL syntax (simplified check)
        for alignment in owl_alignments:
            if not any(keyword in alignment for keyword in ["Class:", "ObjectProperty:", "SubClassOf:"]):
                validation_results["issues"].append(f"Invalid OWL syntax in alignment: {alignment[:50]}...")
                validation_results["owl_syntax_valid"] = False
        
        # Check concept coherence (simplified)
        if len(ontology_mappings) > 0 and len(set(ontology_mappings.values())) / len(ontology_mappings) < 0.5:
            validation_results["issues"].append("Low concept diversity - many fields mapped to few concepts")
            validation_results["concept_coherence"] = False
        
        return validation_results
    
    async def _calculate_semantic_quality(
        self,
        ontology_mappings: Dict[str, str],
        validation_results: Dict[str, Any],
        linked_entities: List[str]
    ) -> float:
        """Calculate overall semantic quality score."""
        
        scores = []
        
        # Mapping completeness (all fields have mappings)
        mapping_completeness = 1.0 if ontology_mappings else 0.0
        scores.append(mapping_completeness * 0.3)
        
        # Validation score
        validation_score = sum([
            validation_results.get("mapping_consistency", False),
            validation_results.get("owl_syntax_valid", False),
            validation_results.get("concept_coherence", False)
        ]) / 3.0
        scores.append(validation_score * 0.4)
        
        # Entity linking score
        entity_linking_score = min(len(linked_entities) / 10.0, 1.0)  # Up to 10 entities
        scores.append(entity_linking_score * 0.3)
        
        return sum(scores)
    
    async def _calculate_domain_coverage(
        self,
        ontology_mappings: Dict[str, str],
        business_domain: str
    ) -> float:
        """Calculate how well the mappings cover the business domain."""
        
        domain_config = self.domain_ontologies.get(business_domain, {})
        domain_ontologies = domain_config.get("ontologies", [])
        
        if not domain_ontologies:
            return 0.5  # Default coverage for unknown domains
        
        # Count mappings to domain-specific ontologies
        domain_specific_mappings = 0
        
        for concept_uri in ontology_mappings.values():
            for ontology in domain_ontologies:
                if ontology["uri"] in concept_uri:
                    domain_specific_mappings += 1
                    break
        
        if len(ontology_mappings) == 0:
            return 0.0
        
        return domain_specific_mappings / len(ontology_mappings)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "supported_domains": list(self.domain_ontologies.keys()),
            "ontology_support": [
                "SKOS_concept_mapping",
                "OWL_alignment",
                "RDF_triple_generation",
                "entity_linking",
                "knowledge_graph_creation"
            ],
            "entity_resolvers": list(self.entity_resolvers.keys()),
            "semantic_capabilities": [
                "domain_ontology_recommendation",
                "automatic_concept_mapping", 
                "hierarchical_classification",
                "cross_ontology_alignment",
                "semantic_validation",
                "quality_assessment"
            ],
            "output_format": "SemanticAnnotation"
        })
        return base_capabilities