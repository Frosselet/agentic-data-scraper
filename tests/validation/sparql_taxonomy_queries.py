#!/usr/bin/env python3
"""
SPARQL Taxonomy Browsing Test Queries
=====================================

Comprehensive SPARQL queries for testing taxonomy browsing capabilities
demonstrating ConceptScheme browsing, hierarchical navigation, example discovery,
scope note exploration, and taxonomy tree building.

This module provides concrete SPARQL examples for Lambda implementations
to navigate knowledge hierarchies effectively.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from rdflib import Graph, Namespace, URIRef, Literal
    from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD
    from rdflib.plugins.sparql import prepareQuery
except ImportError as e:
    print(f"Error importing RDFLib: {e}")
    print("Install with: pip install rdflib")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
BRIDGE = Namespace("https://agentic-data-scraper.com/ontology/gist-dbc-bridge#")
SOW_COMPLETE = Namespace("https://agentic-data-scraper.com/ontology/complete-sow#")
SOW_INFERENCE = Namespace("https://agentic-data-scraper.com/ontology/sow#")
GIST = Namespace("https://w3id.org/semanticarts/ontology/gistCore#")
DCTERMS = Namespace("http://purl.org/dc/terms/")

@dataclass
class SPARQLQuery:
    """SPARQL query with metadata"""
    name: str
    description: str
    query: str
    expected_results: int
    use_case: str
    lambda_application: str

class TaxonomyBrowsingQueries:
    """Collection of SPARQL queries for taxonomy browsing validation"""

    def __init__(self):
        self.graph = Graph()
        self.queries = self._define_queries()

        # Bind namespaces
        self.graph.bind("bridge", BRIDGE)
        self.graph.bind("sow", SOW_COMPLETE)
        self.graph.bind("sowinf", SOW_INFERENCE)
        self.graph.bind("gist", GIST)
        self.graph.bind("skos", SKOS)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("dcterms", DCTERMS)

    def _define_queries(self) -> List[SPARQLQuery]:
        """Define all SPARQL test queries"""

        return [
            # 1. ConceptScheme Browsing
            SPARQLQuery(
                name="List All ConceptSchemes",
                description="Show me all concepts in DataBusinessTaxonomy",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dcterms: <http://purl.org/dc/terms/>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?scheme ?label ?description ?concept ?conceptLabel WHERE {
                    ?scheme a skos:ConceptScheme ;
                           rdfs:label ?label .

                    OPTIONAL {
                        ?scheme dcterms:description ?description
                    }

                    OPTIONAL {
                        ?concept skos:inScheme ?scheme ;
                                rdfs:label ?conceptLabel .
                    }
                }
                ORDER BY ?scheme ?concept
                """,
                expected_results=10,
                use_case="Initial taxonomy exploration",
                lambda_application="Lambda function needs to present available taxonomies to users"
            ),

            SPARQLQuery(
                name="Browse DataBusinessTaxonomy Concepts",
                description="Show all concepts in the Data Business Canvas taxonomy",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?concept ?label ?comment WHERE {
                    ?concept skos:inScheme bridge:DataBusinessTaxonomy ;
                            rdfs:label ?label .

                    OPTIONAL { ?concept rdfs:comment ?comment }
                }
                ORDER BY ?label
                """,
                expected_results=5,
                use_case="Browse business model concepts",
                lambda_application="Help users navigate business model components"
            ),

            # 2. Hierarchical Navigation
            SPARQLQuery(
                name="Find Root Concepts",
                description="Find all root concepts (no broader concepts) in taxonomies",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?concept ?label ?scheme WHERE {
                    ?concept skos:inScheme ?scheme ;
                            rdfs:label ?label .

                    # Concept has narrower concepts but no broader concepts
                    ?concept skos:narrower ?child .

                    FILTER NOT EXISTS {
                        ?concept skos:broader ?parent .
                    }
                }
                ORDER BY ?scheme ?label
                """,
                expected_results=3,
                use_case="Find taxonomy entry points",
                lambda_application="Start taxonomy browsing from root concepts"
            ),

            SPARQLQuery(
                name="Hierarchical Navigation from DataBusinessCanvas",
                description="Find all narrower concepts of DataBusinessCanvas",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?narrowerConcept ?label ?comment WHERE {
                    bridge:DataBusinessCanvas skos:narrower ?narrowerConcept .

                    ?narrowerConcept rdfs:label ?label .
                    OPTIONAL { ?narrowerConcept rdfs:comment ?comment }
                }
                ORDER BY ?label
                """,
                expected_results=4,
                use_case="Drill down from parent concept",
                lambda_application="Navigate from high-level to specific concepts"
            ),

            SPARQLQuery(
                name="Multi-Level Hierarchy Traversal",
                description="Build complete hierarchy tree from root to leaf concepts",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?level1 ?level1Label ?level2 ?level2Label ?level3 ?level3Label WHERE {
                    # Level 1: Root concepts
                    ?level1 skos:inScheme bridge:DataBusinessTaxonomy ;
                           rdfs:label ?level1Label .

                    FILTER NOT EXISTS {
                        ?level1 skos:broader ?parent .
                    }

                    # Level 2: Direct children
                    OPTIONAL {
                        ?level1 skos:narrower ?level2 .
                        ?level2 rdfs:label ?level2Label .

                        # Level 3: Grandchildren
                        OPTIONAL {
                            ?level2 skos:narrower ?level3 .
                            ?level3 rdfs:label ?level3Label .
                        }
                    }
                }
                ORDER BY ?level1Label ?level2Label ?level3Label
                """,
                expected_results=8,
                use_case="Build complete taxonomy tree",
                lambda_application="Generate hierarchical menu structures"
            ),

            # 3. Related Concept Discovery
            SPARQLQuery(
                name="Cross-Domain Concept Discovery",
                description="Find related concepts across different domains",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?concept ?conceptLabel ?relatedConcept ?relatedLabel ?conceptScheme ?relatedScheme WHERE {
                    ?concept skos:related ?relatedConcept ;
                            skos:inScheme ?conceptScheme ;
                            rdfs:label ?conceptLabel .

                    ?relatedConcept skos:inScheme ?relatedScheme ;
                                   rdfs:label ?relatedLabel .

                    # Show only cross-scheme relationships
                    FILTER(?conceptScheme != ?relatedScheme)
                }
                ORDER BY ?conceptLabel
                """,
                expected_results=5,
                use_case="Discover cross-domain connections",
                lambda_application="Suggest related concepts from other domains"
            ),

            SPARQLQuery(
                name="Find Related Concepts for IntelligenceCapability",
                description="Discover concepts related to AI/ML capabilities",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?relatedConcept ?label ?relationship ?comment WHERE {
                    {
                        bridge:IntelligenceCapability skos:related ?relatedConcept .
                        BIND("related" AS ?relationship)
                    }
                    UNION
                    {
                        bridge:IntelligenceCapability skos:broader ?relatedConcept .
                        BIND("broader" AS ?relationship)
                    }
                    UNION
                    {
                        bridge:IntelligenceCapability skos:narrower ?relatedConcept .
                        BIND("narrower" AS ?relationship)
                    }

                    ?relatedConcept rdfs:label ?label .
                    OPTIONAL { ?relatedConcept rdfs:comment ?comment }
                }
                ORDER BY ?relationship ?label
                """,
                expected_results=6,
                use_case="Explore concept relationships",
                lambda_application="Show comprehensive concept context"
            ),

            # 4. Example Discovery
            SPARQLQuery(
                name="Find Implementation Examples",
                description="Show implementation examples for IntelligenceCapability",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?concept ?label ?example WHERE {
                    ?concept rdfs:label ?label ;
                            skos:example ?example .

                    # Filter for concepts with implementation-relevant examples
                    FILTER(CONTAINS(LCASE(?example), "analytics") ||
                           CONTAINS(LCASE(?example), "prediction") ||
                           CONTAINS(LCASE(?example), "optimization") ||
                           CONTAINS(LCASE(?example), "lambda"))
                }
                ORDER BY ?label
                """,
                expected_results=8,
                use_case="Get concrete implementation guidance",
                lambda_application="Provide practical examples for developers"
            ),

            SPARQLQuery(
                name="Examples with Domain Context",
                description="Find examples for olive oil supply chain use case",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?concept ?label ?example WHERE {
                    ?concept rdfs:label ?label ;
                            skos:example ?example .

                    # Filter for olive oil supply chain examples
                    FILTER(CONTAINS(LCASE(?example), "olive") ||
                           CONTAINS(LCASE(?example), "supplier") ||
                           CONTAINS(LCASE(?example), "turkish") ||
                           CONTAINS(LCASE(?example), "mediterranean"))
                }
                ORDER BY ?label
                """,
                expected_results=10,
                use_case="Domain-specific examples",
                lambda_application="Show relevant examples for specific industries"
            ),

            # 5. Scope Note Exploration
            SPARQLQuery(
                name="Get Detailed Implementation Guidance",
                description="Find detailed scope notes for CrossDomainOpportunity",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX sow: <https://agentic-data-scraper.com/ontology/complete-sow#>

                SELECT ?concept ?label ?scopeNote WHERE {
                    ?concept rdfs:label ?label ;
                            skos:scopeNote ?scopeNote .

                    # Filter for concepts with Lambda implementation guidance
                    FILTER(CONTAINS(?scopeNote, "Lambda") &&
                           STRLEN(?scopeNote) > 500)
                }
                ORDER BY ?label
                """,
                expected_results=5,
                use_case="Get detailed implementation guidance",
                lambda_application="Provide comprehensive implementation instructions"
            ),

            SPARQLQuery(
                name="Find Architecture Guidance",
                description="Get architectural guidance from scope notes",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?concept ?label ?scopeNote WHERE {
                    ?concept rdfs:label ?label ;
                            skos:scopeNote ?scopeNote .

                    # Filter for architectural guidance
                    FILTER(CONTAINS(LCASE(?scopeNote), "architecture") ||
                           CONTAINS(LCASE(?scopeNote), "implementation") ||
                           CONTAINS(LCASE(?scopeNote), "pattern") ||
                           CONTAINS(LCASE(?scopeNote), "framework"))
                }
                ORDER BY ?label
                """,
                expected_results=8,
                use_case="Architecture and pattern guidance",
                lambda_application="Guide architectural decisions"
            ),

            # 6. Taxonomy Tree Building
            SPARQLQuery(
                name="Build Complete Executive Taxonomy Tree",
                description="Build complete hierarchy for Executive Strategy Taxonomy",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?parent ?parentLabel ?child ?childLabel ?grandchild ?grandchildLabel WHERE {
                    # Find concepts in Executive Taxonomy
                    ?parent skos:inScheme bridge:ExecutiveTaxonomy ;
                           rdfs:label ?parentLabel .

                    # Find direct children
                    OPTIONAL {
                        ?parent skos:narrower ?child .
                        ?child rdfs:label ?childLabel .

                        # Find grandchildren
                        OPTIONAL {
                            ?child skos:narrower ?grandchild .
                            ?grandchild rdfs:label ?grandchildLabel .
                        }
                    }
                }
                ORDER BY ?parentLabel ?childLabel ?grandchildLabel
                """,
                expected_results=6,
                use_case="Build executive taxonomy navigation",
                lambda_application="Create executive strategy concept browser"
            ),

            # 7. Comprehensive Taxonomy Analysis
            SPARQLQuery(
                name="Taxonomy Quality Assessment",
                description="Assess overall taxonomy quality and completeness",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT
                    (COUNT(DISTINCT ?scheme) AS ?schemeCount)
                    (COUNT(DISTINCT ?concept) AS ?conceptCount)
                    (COUNT(DISTINCT ?broader) AS ?hierarchicalRelCount)
                    (COUNT(DISTINCT ?related) AS ?relatedRelCount)
                    (COUNT(DISTINCT ?withExample) AS ?conceptsWithExamples)
                    (COUNT(DISTINCT ?withScope) AS ?conceptsWithScopeNotes)
                WHERE {
                    ?scheme a skos:ConceptScheme .

                    OPTIONAL {
                        ?concept skos:inScheme ?scheme .
                    }

                    OPTIONAL {
                        ?concept skos:broader ?broader .
                    }

                    OPTIONAL {
                        ?concept skos:related ?related .
                    }

                    OPTIONAL {
                        ?withExample skos:example ?example .
                    }

                    OPTIONAL {
                        ?withScope skos:scopeNote ?scopeNote .
                    }
                }
                """,
                expected_results=1,
                use_case="Assess taxonomy completeness",
                lambda_application="Generate taxonomy quality reports"
            ),

            # 8. Semantic Search Queries
            SPARQLQuery(
                name="Semantic Search for Data Assets",
                description="Find concepts related to data assets and their properties",
                query="""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>

                SELECT ?concept ?label ?example ?scopeNote WHERE {
                    {
                        ?concept rdfs:label ?label .
                        FILTER(CONTAINS(LCASE(?label), "data"))
                    }
                    UNION
                    {
                        ?concept skos:related bridge:DataAsset ;
                                rdfs:label ?label .
                    }
                    UNION
                    {
                        bridge:DataAsset skos:related ?concept .
                        ?concept rdfs:label ?label .
                    }

                    OPTIONAL { ?concept skos:example ?example }
                    OPTIONAL { ?concept skos:scopeNote ?scopeNote }
                }
                ORDER BY ?label
                """,
                expected_results=6,
                use_case="Find data-related concepts",
                lambda_application="Semantic search for data concepts"
            ),
        ]

    def load_ontologies(self) -> bool:
        """Load all ontology files"""
        ontology_files = [
            "schemas/ontologies/bridge/gist_dbc_bridge.owl",
            "schemas/ontologies/sow/complete_sow_ontology.owl",
            "schemas/ontologies/sow/sow_inference_rules.owl"
        ]

        for file_path in ontology_files:
            full_path = project_root / file_path
            try:
                logger.info(f"Loading ontology: {file_path}")
                self.graph.parse(str(full_path), format="xml")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                return False

        logger.info(f"Loaded graph with {len(self.graph)} triples")
        return True

    def execute_query(self, sparql_query: SPARQLQuery) -> Tuple[bool, List[Dict], str]:
        """Execute a SPARQL query and return results"""
        try:
            results = list(self.graph.query(sparql_query.query))

            # Convert results to list of dictionaries
            result_dicts = []
            for row in results:
                row_dict = {}
                for var in row.labels:
                    value = getattr(row, var)
                    if value:
                        row_dict[var] = str(value)
                result_dicts.append(row_dict)

            success = len(results) > 0
            message = f"Query returned {len(results)} results"

            return success, result_dicts, message

        except Exception as e:
            return False, [], f"Query execution failed: {str(e)}"

    def run_all_queries(self) -> Dict[str, Any]:
        """Execute all SPARQL queries and return results"""
        if not self.load_ontologies():
            return {"error": "Failed to load ontologies"}

        from datetime import datetime

        results = {
            "timestamp": str(datetime.now()),
            "total_queries": len(self.queries),
            "successful_queries": 0,
            "failed_queries": 0,
            "query_results": []
        }

        for query in self.queries:
            logger.info(f"Executing query: {query.name}")

            success, query_results, message = self.execute_query(query)

            query_result = {
                "name": query.name,
                "description": query.description,
                "use_case": query.use_case,
                "lambda_application": query.lambda_application,
                "success": success,
                "message": message,
                "result_count": len(query_results),
                "expected_results": query.expected_results,
                "meets_expectations": len(query_results) >= query.expected_results,
                "results": query_results[:5] if query_results else [],  # Limit to first 5 for readability
                "query": query.query
            }

            results["query_results"].append(query_result)

            if success:
                results["successful_queries"] += 1
            else:
                results["failed_queries"] += 1

        return results

def main():
    """Main execution function"""
    from datetime import datetime

    print("SPARQL Taxonomy Browsing Query Tests")
    print("=" * 40)

    query_tester = TaxonomyBrowsingQueries()
    results = query_tester.run_all_queries()

    if "error" in results:
        print(f"ERROR: {results['error']}")
        return False

    print(f"Executed {results['total_queries']} queries")
    print(f"Successful: {results['successful_queries']}")
    print(f"Failed: {results['failed_queries']}")
    print()

    # Print summary of each query
    for query_result in results["query_results"]:
        status = "✅" if query_result["success"] else "❌"
        expectation = "✅" if query_result["meets_expectations"] else "⚠️"

        print(f"{status} {query_result['name']}")
        print(f"   Results: {query_result['result_count']} (expected: {query_result['expected_results']}) {expectation}")
        print(f"   Use case: {query_result['use_case']}")
        print(f"   Lambda application: {query_result['lambda_application']}")

        if not query_result["success"]:
            print(f"   Error: {query_result['message']}")

        print()

    # Overall assessment
    success_rate = (results["successful_queries"] / results["total_queries"]) * 100
    print(f"Overall Success Rate: {success_rate:.1f}%")

    expectation_met = sum(1 for qr in results["query_results"] if qr["meets_expectations"])
    expectation_rate = (expectation_met / results["total_queries"]) * 100
    print(f"Expectation Met Rate: {expectation_rate:.1f}%")

    overall_ready = success_rate >= 80 and expectation_rate >= 70
    readiness = "READY" if overall_ready else "NEEDS IMPROVEMENT"
    print(f"Taxonomy Browsing Readiness: {readiness}")

    return overall_ready

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)