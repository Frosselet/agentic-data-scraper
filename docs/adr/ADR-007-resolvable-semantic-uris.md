# ADR-007: Resolvable Semantic URIs and Triple Store Integration

## Status
**PROPOSED** - Addresses critical gap identified in semantic enrichment demonstration

## Context

During implementation of the semantic ET(K)L system, we discovered that our semantic annotations use non-resolvable URIs that lead nowhere:

```
❌ Current URIs (Non-resolvable):
- http://hydrology.usgs.gov/site/05331000 (fictional)
- http://mississippi.navigation.org/entity/... (our fictional namespace)

❌ Problem:
- URIs are not dereferenceable
- No actual knowledge graph backing semantic claims
- Semantic web integration is superficial, not genuine
- Cannot perform SPARQL queries or semantic reasoning
```

This undermines the credibility and utility of our semantic enrichment approach.

## Decision

We will implement a **minimal but resolvable triple store architecture** with the following components:

### 1. Resolvable URI Namespace
- **Primary namespace**: `http://navigation-intelligence.org/`
- **Entity patterns**:
  - Sites: `http://navigation-intelligence.org/site/05331000`
  - Measurements: `http://navigation-intelligence.org/measurement/{uuid}`
  - Locations: `http://navigation-intelligence.org/location/{geonames_id}`
  - Temporal: `http://navigation-intelligence.org/time/{iso_timestamp}`

### 2. Minimal Triple Store Deployment
- **Technology**: Apache Jena Fuseki (lightweight SPARQL endpoint)
- **Deployment**: Docker container for development, cloud instance for production
- **Endpoints**:
  - SPARQL Query: `/sparql`
  - SPARQL Update: `/update` 
  - Linked Data: Content negotiation (HTML/RDF/JSON-LD)

### 3. Semantic Triple Population
- **Automatic**: Collectors populate triples during semantic enrichment
- **Structure**: Subject-Predicate-Object triples for all semantic annotations
- **Vocabularies**: Mix of standard (FOAF, DC, GEO) and domain-specific ontologies

## Implementation Strategy

### Phase 1: Minimal Triple Store Setup
```python
class ResolvableSemanticManager:
    def __init__(self, fuseki_endpoint: str):
        self.endpoint = fuseki_endpoint
        self.namespace = "http://navigation-intelligence.org/"
        
    def create_resolvable_uri(self, entity_type: str, identifier: str) -> str:
        return f"{self.namespace}{entity_type}/{identifier}"
        
    def store_semantic_triple(self, subject: str, predicate: str, obj: str):
        sparql_update = f"""
        INSERT DATA {{
            <{subject}> <{predicate}> <{obj}> .
        }}
        """
        requests.post(f"{self.endpoint}/update", data={"update": sparql_update})
        
    def make_uri_resolvable(self, uri: str) -> Dict:
        # Return JSON-LD representation when URI is dereferenced
        pass
```

### Phase 2: Collector Integration
```python
# Enhanced semantic collectors
class USGSSemanticCollector(SemanticCollectorBase):
    def __init__(self, ..., semantic_manager: ResolvableSemanticManager):
        self.semantic_manager = semantic_manager
        
    def apply_semantic_enrichment(self, structured_data):
        # Create resolvable URIs instead of fictional ones
        site_uri = self.semantic_manager.create_resolvable_uri("site", structured_data["site_id"])
        
        # Store semantic triples
        self.semantic_manager.store_semantic_triple(
            site_uri,
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            "http://navigation-intelligence.org/ontology/GaugeStation"
        )
```

### Phase 3: Content Negotiation
```python
# HTTP endpoint for resolvable URIs
@app.route("/site/<site_id>")
def resolve_site(site_id):
    accept_header = request.headers.get('Accept', 'text/html')
    
    if 'application/rdf+xml' in accept_header:
        return get_rdf_representation(site_id)
    elif 'application/ld+json' in accept_header:
        return get_jsonld_representation(site_id)
    else:
        return render_template('site.html', site_id=site_id)
```

## Benefits

### 1. Genuine Semantic Web Integration
- URIs actually resolve to meaningful content
- SPARQL queries possible across semantic data
- Integration with external knowledge graphs (DBpedia, Wikidata)

### 2. Enhanced Credibility
- Demonstrates real semantic web principles
- Addresses skeptical audience concerns about "fake" semantics
- Enables verification of semantic claims

### 3. Advanced Analytics Capabilities
- Semantic reasoning over collected data
- Cross-domain knowledge graph queries
- Integration with semantic web tools and libraries

### 4. Scalable Architecture
- Minimal overhead for development
- Scales to full knowledge graph platform
- Standards-compliant (RDF, SPARQL, Linked Data)

## Implementation Timeline

- **Week 1**: Deploy Fuseki instance, create URI resolution framework
- **Week 2**: Integrate with collectors, populate initial triples
- **Week 3**: Implement content negotiation and HTML representations
- **Week 4**: Testing, documentation, notebook demonstration updates

## Risks and Mitigations

### Risk: Triple Store Performance
- **Mitigation**: Start with minimal data, optimize queries, consider scaling options

### Risk: URI Management Complexity  
- **Mitigation**: Simple UUID-based identifiers, clear namespace conventions

### Risk: Maintenance Overhead
- **Mitigation**: Automated triple population, clear documentation, monitoring

## Success Criteria

1. **All semantic URIs are resolvable** via HTTP GET requests
2. **SPARQL queries work** against collected semantic data
3. **Content negotiation** returns appropriate formats (HTML/RDF/JSON-LD)
4. **Notebook demonstration** shows actual resolvable URIs instead of fictional ones
5. **Zero fictional URIs** in semantic annotations

## Related ADRs

- ADR-001: KuzuDB for Knowledge Graph Storage (complements with resolvable URIs)
- ADR-002: Semantic Enrichment During Acquisition (enhanced with real semantics)
- ADR-008: Rich Spatial Context Integration (proposed, will use resolvable spatial URIs)