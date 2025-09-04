"""
Semantic web technologies and RDF processing for the Agentic Data Scraper.

This module provides semantic data processing capabilities using RDFLib, OWL ontologies,
and SPARQL queries. It enables semantic enrichment, knowledge graph construction,
and intelligent data integration.

Classes:
    RdfProcessor: Process RDF graphs and triples
    OntologyManager: Manage OWL ontologies
    SparqlEngine: Execute SPARQL queries
    KnowledgeGraph: Build and query knowledge graphs
    SemanticEnricher: Add semantic annotations to data
    ConceptMapper: Map data to semantic concepts

Functions:
    create_graph: Create RDF graph from data
    load_ontology: Load OWL ontology files
    execute_query: Execute SPARQL queries
    enrich_data: Add semantic enrichment to data

Example:
    ```python
    from agentic_data_scraper.semantic import (
        RdfProcessor, OntologyManager, create_graph
    )
    
    # Create RDF graph
    graph = create_graph(data, format="json-ld")
    
    # Load ontology
    ontology = OntologyManager()
    ontology.load("schema.org.owl")
    
    # Process with semantics
    processor = RdfProcessor(ontology=ontology)
    enriched_data = processor.enrich(graph)
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rdf_processor import RdfProcessor
    from .ontology_manager import OntologyManager
    from .sparql_engine import SparqlEngine
    from .knowledge_graph import KnowledgeGraph
    from .semantic_enricher import SemanticEnricher
    from .concept_mapper import ConceptMapper

__all__ = [
    "RdfProcessor",
    "OntologyManager",
    "SparqlEngine",
    "KnowledgeGraph",
    "SemanticEnricher",
    "ConceptMapper",
    "create_graph",
    "load_ontology",
    "execute_query", 
    "enrich_data",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "RdfProcessor":
        from .rdf_processor import RdfProcessor
        return RdfProcessor
    elif name == "OntologyManager":
        from .ontology_manager import OntologyManager
        return OntologyManager
    elif name == "SparqlEngine":
        from .sparql_engine import SparqlEngine
        return SparqlEngine
    elif name == "KnowledgeGraph":
        from .knowledge_graph import KnowledgeGraph
        return KnowledgeGraph
    elif name == "SemanticEnricher":
        from .semantic_enricher import SemanticEnricher
        return SemanticEnricher
    elif name == "ConceptMapper":
        from .concept_mapper import ConceptMapper
        return ConceptMapper
    elif name == "create_graph":
        from .graph_factory import create_graph
        return create_graph
    elif name == "load_ontology":
        from .ontology_manager import load_ontology
        return load_ontology
    elif name == "execute_query":
        from .sparql_engine import execute_query
        return execute_query
    elif name == "enrich_data":
        from .semantic_enricher import enrich_data
        return enrich_data
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")