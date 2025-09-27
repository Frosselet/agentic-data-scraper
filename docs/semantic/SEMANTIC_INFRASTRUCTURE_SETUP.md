# Semantic Infrastructure Setup Guide

## Overview

This guide explains how to set up and validate the complete semantic infrastructure for the **Gist-Connected Data Business Canvas** architecture. The infrastructure provides a 4-level connected ontological graph:

```
Level 1: Gist Upper Ontology (Enterprise Foundation)
    ↓
Level 2: Data Business Canvas (Business Strategy)
    ↓
Level 3: SOW Contracts (Implementation Planning)
    ↓
Level 4: Data Contracts (Operational Execution)
```

## Quick Start

### 1. Start the Semantic Infrastructure

```bash
# Start Fuseki triple store and supporting services
docker-compose -f docker-compose.semantic.yml up -d

# Wait for services to initialize (about 30 seconds)
docker-compose -f docker-compose.semantic.yml logs -f fuseki
```

### 2. Access the Services

- **Fuseki Web UI**: http://localhost:3030
- **SPARQL Notebook**: http://localhost:8888
- **Query Endpoints**:
  - Main dataset: http://localhost:3030/gist-dbc-sow/sparql
  - Ontologies only: http://localhost:3030/ontologies/sparql
  - Test data: http://localhost:3030/test-data/sparql

### 3. Validate the Setup

```bash
# Run comprehensive semantic validation
python scripts/semantic_validation.py

# Expected output: All validations should PASS
```

## Architecture Components

### Docker Services

1. **Fuseki Triple Store** (`fuseki`)
   - Apache Jena Fuseki SPARQL server
   - Three configured datasets for different purposes
   - Automatic ontology loading on startup

2. **Jena Loader** (`jena-load`)
   - One-time service that loads all ontologies
   - Downloads Gist ontology if needed
   - Validates successful loading

3. **SPARQL Notebook** (`sparql-notebook`)
   - Jupyter environment for interactive SPARQL development
   - Pre-configured with semantic libraries
   - Access to all schemas and test data

### Datasets

#### Main Dataset: `gist-dbc-sow`
- **Purpose**: Complete connected graph with all ontologies and instances
- **Use**: Production queries, full semantic reasoning
- **Content**: Gist + DBC Bridge + SOW + Data Contracts + Test Instances

#### Ontologies Dataset: `ontologies`
- **Purpose**: Ontology development and validation
- **Use**: Schema queries, inheritance validation, consistency checking
- **Content**: Just the ontologies without instance data

#### Test Dataset: `test-data`
- **Purpose**: Development and testing
- **Use**: Query development, connectivity validation
- **Content**: Minimal test instances for validation

## Ontology Loading Process

The system automatically loads ontologies in the correct dependency order:

1. **Gist Core** (Downloaded from `https://w3id.org/semanticarts/ontology/gistCore`)
2. **DBC Bridge** (`schemas/ontologies/bridge/gist_dbc_bridge.owl`)
3. **SOW Inference Rules** (`schemas/ontologies/sow/sow_inference_rules.owl`)
4. **Complete SOW** (`schemas/ontologies/sow/complete_sow_ontology.owl`)

Each ontology is loaded into a named graph matching its namespace URI.

## Validation Process

The `semantic_validation.py` script performs comprehensive validation:

### 1. Health Check
- Verifies Fuseki is accessible
- Checks all dataset endpoints

### 2. Ontology Import Validation
- Confirms all 4 ontology levels are loaded
- Counts classes in each namespace
- Validates proper import chain

### 3. Inheritance Chain Validation
- Verifies our classes properly extend Gist classes
- Shows complete inheritance hierarchy
- Validates no broken inheritance links

### 4. Cross-Level Connectivity Validation
- Tests complete 4-level connection paths
- Validates Gist → DBC → SOW → Contract chains
- Ensures proper property linkage

### 5. Value Chain Validation
- Tests business value creation flows
- Validates task → value → target relationships
- Confirms executive alignment connections

## Key SPARQL Queries

### Basic Connectivity Test
```sparql
PREFIX gist: <https://w3id.org/semanticarts/ontology/gistCore#>
PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>

SELECT ?org ?canvas ?sow ?contract ?task WHERE {
  ?org a gist:Organization ;
       bridge:hasBusinessModel ?canvas .
  ?canvas bridge:implementedBySOW ?sow .
  ?sow bridge:realizesContract ?contract .
  ?contract bridge:executedByTask ?task .
}
```

### Value Creation Chain
```sparql
SELECT ?task ?value ?target ?owner WHERE {
  ?task a bridge:DataProcessingTask ;
        bridge:createsBusinessValue ?value .

  OPTIONAL {
    ?canvas bridge:alignsWithTarget ?target .
    ?target bridge:ownedBy ?owner .
  }
}
```

### Inheritance Validation
```sparql
SELECT ?subclass ?superclass WHERE {
  ?subclass rdfs:subClassOf ?superclass .
  FILTER(
    STRSTARTS(STR(?subclass), "https://agentic-data-scraper.com/ontology/") &&
    STRSTARTS(STR(?superclass), "https://w3id.org/semanticarts/ontology/gistCore#")
  )
}
```

## Directory Structure

```
semantic-infrastructure/
├── docker-compose.semantic.yml    # Main Docker configuration
├── data/
│   └── fuseki/
│       ├── config.ttl             # Fuseki server configuration
│       └── databases/              # Triple store databases (auto-created)
├── schemas/
│   ├── ontologies/
│   │   └── gist_dbc_bridge.owl    # DBC-Gist bridge ontology
│   ├── sow/ontologies/
│   │   ├── sow_inference_rules.owl     # SOW inference rules
│   │   └── complete_sow_ontology.owl   # Complete SOW structure
│   └── test-data/
│       └── minimal_semantic_validation.ttl  # Test instances
├── scripts/
│   ├── load_ontologies.sh         # Ontology loading script
│   ├── semantic_validation.py     # Validation script
│   └── test_semantic_queries.sparql   # Test queries
└── docs/semantic/
    └── SEMANTIC_INFRASTRUCTURE_SETUP.md  # This guide
```

## Troubleshooting

### Common Issues

#### 1. "Fuseki not accessible"
```bash
# Check if Fuseki is running
docker-compose -f docker-compose.semantic.yml ps

# Check Fuseki logs
docker-compose -f docker-compose.semantic.yml logs fuseki

# Restart if needed
docker-compose -f docker-compose.semantic.yml restart fuseki
```

#### 2. "No ontologies loaded"
```bash
# Check loader logs
docker-compose -f docker-compose.semantic.yml logs jena-load

# Manually run loader
docker-compose -f docker-compose.semantic.yml up jena-load
```

#### 3. "Inheritance validation fails"
- Check ontology files exist in correct locations
- Verify proper namespace declarations
- Check for syntax errors in OWL files

#### 4. "No connectivity found"
- Ensure test data is loaded
- Check property names match between ontologies
- Verify domain/range declarations

### Manual Validation

#### Check Dataset Contents
```bash
# Count triples in main dataset
curl -G "http://localhost:3030/gist-dbc-sow/sparql" \
     --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
     -H "Accept: application/sparql-results+json"
```

#### Load Test Data Manually
```bash
# Load minimal test instances
curl -X POST \
     -H "Content-Type: text/turtle" \
     --data-binary "@schemas/test-data/minimal_semantic_validation.ttl" \
     "http://localhost:3030/test-data/data"
```

#### Query Specific Classes
```bash
# Find all DataBusinessCanvas instances
curl -G "http://localhost:3030/gist-dbc-sow/sparql" \
     --data-urlencode "query=SELECT ?canvas WHERE { ?canvas a bridge:DataBusinessCanvas }" \
     -H "Accept: application/sparql-results+json"
```

## Advanced Configuration

### Custom Ontology Loading

To load additional ontologies:

1. Place OWL/TTL files in `schemas/ontologies/`
2. Update `scripts/load_ontologies.sh`
3. Restart the loader service

### Performance Tuning

For large datasets, adjust Fuseki JVM settings in `docker-compose.semantic.yml`:

```yaml
environment:
  - JVM_ARGS=-Xmx4g -XX:+UseG1GC
```

### Custom Datasets

Add new datasets by updating `data/fuseki/config.ttl`:

```turtle
<#my-custom-dataset> rdf:type fuseki:Service ;
    fuseki:name "my-custom" ;
    fuseki:serviceQuery "sparql" ;
    fuseki:dataset <#my-custom-dataset-def> .
```

## Integration with Python

### Basic SPARQL Client

```python
import requests

def query_fuseki(query: str, dataset: str = "gist-dbc-sow"):
    response = requests.get(
        f"http://localhost:3030/{dataset}/sparql",
        params={'query': query, 'format': 'json'},
        headers={'Accept': 'application/sparql-results+json'}
    )
    return response.json()

# Example usage
result = query_fuseki("""
    SELECT ?canvas ?sow WHERE {
        ?canvas a bridge:DataBusinessCanvas .
        ?canvas bridge:implementedBySOW ?sow .
    }
""")
```

### Using rdflib

```python
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

# Connect to Fuseki
store = SPARQLStore("http://localhost:3030/gist-dbc-sow/sparql")
graph = Graph(store)

# Query using rdflib
results = graph.query("""
    PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
    SELECT ?canvas WHERE { ?canvas a bridge:DataBusinessCanvas }
""")

for row in results:
    print(row.canvas)
```

## Next Steps

Once the semantic infrastructure is validated:

1. **Develop Business Cases**: Create specific use case instances
2. **Extend Ontologies**: Add domain-specific classes and properties
3. **Implement Reasoning**: Add SWRL rules for automated inference
4. **Build Applications**: Create Python applications using the semantic layer
5. **Add Visualization**: Implement graph visualization of the connected model

## Support

For issues with the semantic infrastructure:

1. Check the validation output from `semantic_validation.py`
2. Review Fuseki logs: `docker-compose logs fuseki`
3. Verify ontology files are syntactically correct
4. Test individual SPARQL queries using Fuseki web UI
5. Validate test data loads successfully

The semantic infrastructure provides a robust foundation for building semantically-aware applications that span from high-level business strategy down to operational data processing tasks.