# SKOS Taxonomy Browsing Validation Suite

Comprehensive validation for SKOS taxonomy browsing capability across all ontologies to ensure Lambda users can navigate knowledge hierarchies like browsing a taxonomy tree.

## Overview

This validation suite provides thorough testing of:

1. **SKOS ConceptScheme Navigation** - Verify all ConceptSchemes are properly defined and accessible
2. **Hierarchical Browsing** - Test skos:broader/narrower navigation paths and multi-level traversal
3. **Related Concept Discovery** - Verify cross-domain concept discovery and lateral navigation
4. **SKOS Examples and Scope Notes** - Test implementation guidance quality
5. **SPARQL Test Queries** - Comprehensive queries for taxonomy browsing patterns
6. **Lambda Readiness Assessment** - Overall readiness for AWS Lambda deployment

## Files

- `skos_taxonomy_validation.py` - Core SKOS structure validation
- `sparql_taxonomy_queries.py` - SPARQL query tests for taxonomy browsing
- `lambda_readiness_assessment.py` - Comprehensive Lambda deployment readiness assessment
- `run_taxonomy_validation.py` - Main test runner for all validation components

## Quick Start

### Run All Validations

```bash
# From project root
python tests/validation/run_taxonomy_validation.py
```

### Run Individual Components

```bash
# SKOS structure validation only
python tests/validation/run_taxonomy_validation.py --component skos

# SPARQL queries only
python tests/validation/run_taxonomy_validation.py --component sparql

# Lambda assessment only
python tests/validation/run_taxonomy_validation.py --component assessment
```

### Run Individual Modules

```bash
# SKOS validation
python tests/validation/skos_taxonomy_validation.py

# SPARQL queries
python tests/validation/sparql_taxonomy_queries.py

# Lambda assessment
python tests/validation/lambda_readiness_assessment.py
```

## Requirements

```bash
pip install rdflib
```

## Validation Tests

### 1. SKOS ConceptScheme Navigation

Tests that all ConceptSchemes are properly defined with:
- Required metadata (labels, comments, descriptions)
- Concept membership (skos:inScheme relationships)
- Cross-references for discoverability (rdfs:seeAlso)

**Expected ConceptSchemes:**
- `DataBusinessTaxonomy` - Business model components
- `ExecutiveTaxonomy` - Strategic executive concepts
- `SOWTaxonomy` - Statement of work implementation concepts
- `AnalyticsTaxonomy` - Analytical opportunities classification
- `InferenceTaxonomy` - AI-inferred opportunities and domain entities

### 2. Hierarchical Browsing Tests

Validates hierarchy navigation including:
- **Root Concept Discovery** - Find concepts with no broader concepts
- **Bidirectional Relationships** - Ensure skos:broader/narrower are properly paired
- **Multi-level Traversal** - Test navigation from root to leaf concepts
- **Orphaned Concept Detection** - Identify concepts with no relationships

**Key Hierarchies:**
- `DataBusinessCanvas` → `ValueProposition`, `CustomerSegment`, `DataAsset`, `IntelligenceCapability`
- `ExecutiveTarget` → `StrategicAlignmentScore`
- `InferredOpportunity` → `SpatialAnalysisOpportunity`, `TemporalAnalysisOpportunity`, etc.

### 3. Related Concept Discovery

Tests lateral navigation and cross-domain connections:
- **Cross-scheme Relationships** - Links between different ConceptSchemes
- **Related Concept Networks** - Comprehensive relationship mapping
- **Domain Bridge Discovery** - Find connections across business domains

### 4. SKOS Examples and Scope Notes

Validates implementation guidance quality:
- **Example Coverage** - Percentage of concepts with concrete examples
- **Scope Note Depth** - Detailed implementation guidance availability
- **Lambda-specific Guidance** - Architecture and deployment instructions

### 5. SPARQL Query Patterns

Tests comprehensive browsing scenarios:

#### ConceptScheme Browsing
```sparql
# List all concepts in DataBusinessTaxonomy
SELECT ?concept ?label WHERE {
    ?concept skos:inScheme bridge:DataBusinessTaxonomy ;
            rdfs:label ?label .
}
```

#### Hierarchical Navigation
```sparql
# Find all narrower concepts of DataBusinessCanvas
SELECT ?narrowerConcept ?label WHERE {
    bridge:DataBusinessCanvas skos:narrower ?narrowerConcept .
    ?narrowerConcept rdfs:label ?label .
}
```

#### Cross-domain Discovery
```sparql
# Find related concepts across different schemes
SELECT ?concept ?relatedConcept WHERE {
    ?concept skos:related ?relatedConcept ;
            skos:inScheme ?scheme1 .
    ?relatedConcept skos:inScheme ?scheme2 .
    FILTER(?scheme1 != ?scheme2)
}
```

#### Example Discovery
```sparql
# Get implementation examples for concepts
SELECT ?concept ?label ?example WHERE {
    ?concept rdfs:label ?label ;
            skos:example ?example .
    FILTER(CONTAINS(LCASE(?example), "lambda"))
}
```

#### Scope Note Exploration
```sparql
# Get detailed implementation guidance
SELECT ?concept ?label ?scopeNote WHERE {
    ?concept rdfs:label ?label ;
            skos:scopeNote ?scopeNote .
    FILTER(CONTAINS(?scopeNote, "Lambda") && STRLEN(?scopeNote) > 500)
}
```

## Validation Metrics

### Taxonomy Completeness Score
- ConceptScheme coverage and metadata quality
- Concept density and relationship richness
- Hierarchy depth and structure quality
- Cross-domain relationship coverage

### Navigation Effectiveness Score
- Bidirectional relationship integrity
- Hierarchy traversal completeness
- Cross-domain discoverability
- Orphaned concept minimization

### Implementation Guidance Score
- Example coverage and quality
- Scope note depth and Lambda-specific guidance
- Architectural pattern documentation
- Code generation readiness

### Lambda Readiness Assessment

#### Development Readiness
- Code generation capabilities
- API pattern readiness
- Documentation completeness

#### Deployment Readiness
- Performance optimization
- Memory efficiency
- Query optimization

#### User Experience Readiness
- Intuitive navigation patterns
- Comprehensive examples
- Clear implementation guidance

## Readiness Levels

### Production Ready (85%+)
- All validation tests pass
- Comprehensive taxonomy coverage
- Rich examples and guidance
- Optimized for Lambda deployment

### Needs Minor Improvements (75-84%)
- Most tests pass with minor issues
- Good taxonomy coverage
- Some gaps in examples or guidance
- Ready for staging deployment

### Needs Major Improvements (60-74%)
- Some validation tests fail
- Limited taxonomy coverage
- Significant gaps in guidance
- Requires substantial work

### Not Ready (<60%)
- Multiple validation failures
- Poor taxonomy structure
- Minimal implementation guidance
- Major development required

## Expected Results

Based on current ontology analysis:

**ConceptSchemes:** 5 (DataBusiness, Executive, SOW, Analytics, Inference taxonomies)

**Concepts:** 15+ core concepts with rich hierarchical relationships

**Examples:** Comprehensive olive oil supply chain examples throughout

**Scope Notes:** Detailed Lambda implementation guidance for key concepts

**SPARQL Queries:** 12+ test queries covering all browsing patterns

## Output Reports

Validation generates multiple report formats:

### Console Output
- Real-time validation progress
- Component-by-component results
- Summary with scores and recommendations

### JSON Reports
- Machine-readable validation results
- Detailed metrics and test outcomes
- Saved to `reports/taxonomy_validation/`

### HTML Reports
- Human-readable assessment reports
- Visual scoring and recommendations
- Ready for stakeholder review

## Lambda Implementation Guide

The validation results provide concrete guidance for Lambda implementation:

### Recommended Architecture
```python
# Lambda function structure for taxonomy browsing
def lambda_handler(event, context):
    # Load pre-parsed ontology graph
    graph = load_cached_ontology()

    # Execute SPARQL query based on request
    query_type = event.get('query_type')
    if query_type == 'concept_scheme':
        return browse_concept_schemes(graph)
    elif query_type == 'hierarchy':
        return navigate_hierarchy(graph, event.get('concept_uri'))
    elif query_type == 'related':
        return find_related_concepts(graph, event.get('concept_uri'))
```

### Performance Optimization
- Pre-compute common taxonomy queries
- Use compressed ontology formats
- Implement concept indexes for fast lookup
- Cache query results with TTL

### User Experience Patterns
- Breadcrumb navigation support
- Concept search and filtering
- Interactive taxonomy exploration
- Progressive disclosure of hierarchy

## Troubleshooting

### Common Issues

**RDFLib Import Errors**
```bash
pip install rdflib
```

**Ontology File Not Found**
- Ensure running from project root directory
- Verify ontology files exist in `schemas/ontologies/`

**SPARQL Query Failures**
- Check namespace bindings
- Verify concept URIs in ontology files
- Review query syntax for SPARQL 1.1 compliance

**Low Validation Scores**
- Add more skos:example annotations
- Enhance skos:scopeNote content with Lambda guidance
- Strengthen hierarchical relationships
- Add cross-domain skos:related links

### Getting Help

1. Check validation logs for specific error messages
2. Review generated reports for detailed recommendations
3. Examine failing SPARQL queries in detail
4. Cross-reference with ontology files for missing content

## Contributing

When adding new concepts or relationships:

1. **Add SKOS Annotations**
   ```turtle
   :NewConcept a owl:Class ;
       skos:inScheme :RelevantTaxonomy ;
       rdfs:label "New Concept" ;
       skos:scopeNote "Detailed implementation guidance..." ;
       skos:example "Concrete example..." .
   ```

2. **Add Hierarchical Relationships**
   ```turtle
   :ParentConcept skos:narrower :NewConcept .
   :NewConcept skos:broader :ParentConcept .
   ```

3. **Add Cross-domain Links**
   ```turtle
   :NewConcept skos:related :RelatedConceptInOtherDomain .
   ```

4. **Run Validation**
   ```bash
   python tests/validation/run_taxonomy_validation.py
   ```

5. **Address Any Issues** based on validation recommendations

## Next Steps

After validation passes:

1. **Staging Deployment** - Deploy to Lambda staging environment
2. **User Testing** - Conduct taxonomy browsing user acceptance tests
3. **Performance Testing** - Validate query response times under load
4. **Production Deployment** - Deploy with monitoring and alerting
5. **Usage Analytics** - Track taxonomy browsing patterns and optimization opportunities