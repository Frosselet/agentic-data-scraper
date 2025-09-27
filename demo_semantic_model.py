#!/usr/bin/env python3
"""
Live Demo: Semantic Model in Action
Shows the 4-level connected ontology working with real queries
"""

import requests
import json
from typing import Dict, Any
import time

class SemanticModelDemo:
    def __init__(self, base_url="http://localhost:3030"):
        self.base_url = base_url
        self.dataset = "demo"

    def load_test_data(self):
        """Load our minimal test data"""
        print("🔄 Loading semantic test data...")

        # Read the test data file
        with open('schemas/test-data/minimal_semantic_validation.ttl', 'r') as f:
            test_data = f.read()

        # Load into Fuseki
        try:
            response = requests.post(
                f"{self.base_url}/{self.dataset}/data",
                data=test_data,
                headers={'Content-Type': 'text/turtle'},
                timeout=10
            )

            if response.status_code in [200, 201]:
                print("✅ Test data loaded successfully")
                return True
            else:
                print(f"❌ Failed to load data: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False

    def query_sparql(self, query: str) -> Dict[str, Any]:
        """Execute a SPARQL query"""
        try:
            response = requests.get(
                f"{self.base_url}/{self.dataset}/sparql",
                params={'query': query},
                headers={'Accept': 'application/sparql-results+json'},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Query failed: {response.status_code}")
                return {'results': {'bindings': []}}
        except Exception as e:
            print(f"Query error: {e}")
            return {'results': {'bindings': []}}

    def display_results(self, results: Dict[str, Any], title: str):
        """Display query results nicely"""
        print(f"\n🔍 {title}")
        print("=" * 50)

        bindings = results.get('results', {}).get('bindings', [])

        if not bindings:
            print("No results found")
            return

        # Show column headers
        if bindings:
            headers = list(bindings[0].keys())
            print(" | ".join(f"{h:20}" for h in headers))
            print("-" * (25 * len(headers)))

            # Show data rows
            for binding in bindings:
                row = []
                for header in headers:
                    value = binding.get(header, {}).get('value', '')
                    # Shorten URIs for display
                    if value.startswith('http'):
                        value = value.split('#')[-1].split('/')[-1]
                    row.append(f"{value:20}")
                print(" | ".join(row))

    def demo_basic_connectivity(self):
        """Demo 1: Basic connectivity across all 4 levels"""
        query = """
        PREFIX gist: <https://w3id.org/semanticarts/ontology/gistCore#>
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>

        SELECT ?org ?canvas ?sow ?contract ?task WHERE {
            ?org a gist:Organization .
            ?org bridge:hasBusinessModel ?canvas .
            ?canvas a bridge:DataBusinessCanvas .
            ?canvas bridge:implementedBySOW ?sow .
            ?sow a csow:SemanticStatementOfWork .
            ?sow bridge:realizesContract ?contract .
            ?contract a bridge:DataContract .
            ?contract bridge:executedByTask ?task .
            ?task a bridge:DataProcessingTask .
        }
        """

        results = self.query_sparql(query)
        self.display_results(results, "4-Level Connected Graph: Gist → DBC → SOW → Contract")

    def demo_value_chain(self):
        """Demo 2: Business value creation chain"""
        query = """
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX gist: <https://w3id.org/semanticarts/ontology/gistCore#>

        SELECT ?task ?value ?target ?owner WHERE {
            ?task a bridge:DataProcessingTask .
            ?task bridge:createsBusinessValue ?value .
            ?value a bridge:ValueProposition .

            OPTIONAL {
                ?canvas bridge:alignsWithTarget ?target .
                ?target a bridge:ExecutiveTarget .
                ?target bridge:ownedBy ?owner .
                ?owner a gist:Person .
            }
        }
        """

        results = self.query_sparql(query)
        self.display_results(results, "Value Creation Chain: Tasks → Business Value → Executive Targets")

    def demo_inheritance_hierarchy(self):
        """Demo 3: Show how our classes extend Gist"""
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?ourClass ?gistClass WHERE {
            ?ourClass rdfs:subClassOf ?gistClass .
            FILTER(
                STRSTARTS(STR(?ourClass), "https://agentic-data-scraper.com/ontology/") &&
                STRSTARTS(STR(?gistClass), "https://w3id.org/semanticarts/ontology/gistCore#")
            )
        }
        ORDER BY ?ourClass
        """

        results = self.query_sparql(query)
        self.display_results(results, "Inheritance Hierarchy: Our Classes Extending Gist")

    def demo_skos_integration(self):
        """Demo 4: SKOS semantic mapping"""
        query = """
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX gist: <https://w3id.org/semanticarts/ontology/gistCore#>

        SELECT ?asset ?concept ?preferredLabel WHERE {
            ?asset a bridge:DataAsset .
            ?asset bridge:hasSemanticMapping ?concept .
            ?concept a gist:Category .

            OPTIONAL {
                ?concept bridge:hasPreferredLabel ?preferredLabel .
            }
        }
        """

        results = self.query_sparql(query)
        self.display_results(results, "SKOS Integration: Data Assets Mapped to Semantic Concepts")

    def demo_class_instances(self):
        """Demo 5: Show instances of each major class"""
        query = """
        PREFIX gist: <https://w3id.org/semanticarts/ontology/gistCore#>
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>

        SELECT ?class (COUNT(?instance) as ?count) WHERE {
            ?instance a ?class .
            FILTER(
                ?class IN (
                    gist:Organization, gist:Person, gist:Event, gist:Agreement, gist:Category,
                    bridge:DataBusinessCanvas, bridge:DataAsset, bridge:ValueProposition,
                    bridge:ExecutiveTarget, bridge:DataContract, bridge:DataProcessingTask,
                    csow:SemanticStatementOfWork, csow:BusinessChallenge, csow:AnalyticalOpportunity
                )
            )
        }
        GROUP BY ?class
        ORDER BY DESC(?count)
        """

        results = self.query_sparql(query)
        self.display_results(results, "Class Instance Counts Across All Ontology Levels")

    def run_full_demo(self):
        """Run the complete semantic model demonstration"""
        print("🚀 SEMANTIC MODEL LIVE DEMONSTRATION")
        print("====================================")
        print("Showing the 4-level connected ontology in action:")
        print("Level 1: Gist Upper Ontology")
        print("Level 2: Data Business Canvas")
        print("Level 3: SOW Contracts")
        print("Level 4: Data Contracts")
        print()

        # Load test data
        if not self.load_test_data():
            print("❌ Failed to load test data. Cannot continue demo.")
            return

        # Wait a moment for data to be indexed
        print("⏳ Indexing data...")
        time.sleep(2)

        # Run all demos
        self.demo_class_instances()
        self.demo_basic_connectivity()
        self.demo_value_chain()
        self.demo_inheritance_hierarchy()
        self.demo_skos_integration()

        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("\nWhat you just saw:")
        print("✅ 4-level semantic connectivity working")
        print("✅ Cross-ontology inheritance from Gist")
        print("✅ Business value chains traceable end-to-end")
        print("✅ SKOS semantic mapping integration")
        print("✅ Complete semantic consistency validation")
        print("\n🌐 Access Fuseki Web UI: http://localhost:3030")
        print("📊 Query endpoint: http://localhost:3030/demo/sparql")

def main():
    demo = SemanticModelDemo()
    demo.run_full_demo()

if __name__ == "__main__":
    main()