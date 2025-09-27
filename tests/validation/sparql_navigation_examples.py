"""
Concrete SPARQL examples demonstrating bidirectional navigation across ontologies.

This module provides working examples of how Lambda users can navigate
concept-to-concept like web browsing across the ontology infrastructure.

Each example includes:
1. The SPARQL query
2. Expected pattern of results
3. Lambda implementation guidance
4. Navigation explanation
"""

from rdflib import Graph, Namespace
from pathlib import Path
from typing import List, Dict, Any
import json


# Namespace definitions
BRIDGE = Namespace("https://agentic-data-scraper.com/ontology/gist-dbc-bridge#")
COMPLETE_SOW = Namespace("https://agentic-data-scraper.com/ontology/complete-sow#")
SOW = Namespace("https://agentic-data-scraper.com/ontology/sow#")
GIST = Namespace("https://w3id.org/semanticarts/ontology/gistCore#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")


class SPARQLNavigationExamples:
    """Concrete examples of SPARQL-based concept navigation for Lambda users"""

    def __init__(self, ontology_dir: Path):
        self.ontology_dir = ontology_dir
        self.graph = Graph()
        self.load_ontologies()

    def load_ontologies(self):
        """Load all ontology files"""
        ontology_files = [
            "bridge/gist_dbc_bridge.owl",
            "sow/complete_sow_ontology.owl",
            "sow/sow_inference_rules.owl"
        ]

        for file_path in ontology_files:
            full_path = self.ontology_dir / file_path
            if full_path.exists():
                self.graph.parse(str(full_path), format="xml")

    def example_1_forward_navigation_challenge_to_outcome(self) -> Dict[str, Any]:
        """
        Example 1: Forward Navigation - Business Challenge → Desired Outcome

        Lambda Use Case: Given a business challenge, find all desired outcomes.
        Navigation Pattern: Challenge --hasDesiredOutcome--> Outcome
        """

        query = """
        PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?challenge ?challengeLabel ?outcome ?outcomeLabel ?sow WHERE {
            # Forward navigation: SOW → Challenge, SOW → Outcome
            ?sow a csow:SemanticStatementOfWork .
            ?sow csow:hasBusinessChallenge ?challenge .
            ?sow csow:hasDesiredOutcome ?outcome .

            # Get labels for human readability
            OPTIONAL { ?challenge rdfs:label ?challengeLabel }
            OPTIONAL { ?outcome rdfs:label ?outcomeLabel }
        }
        ORDER BY ?challenge ?outcome
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Forward Navigation: Challenge → Outcome",
            "navigation_pattern": "hasBusinessChallenge + hasDesiredOutcome",
            "lambda_use_case": "Given a business challenge, find related outcomes",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def get_outcomes_for_challenge(challenge_uri: str) -> List[str]",
                "description": "Returns list of outcome URIs related to given challenge",
                "navigation_hops": 2,
                "complexity": "simple"
            },
            "sample_results": [str(row) for row in results[:3]]
        }

    def example_2_backward_navigation_outcome_to_challenge(self) -> Dict[str, Any]:
        """
        Example 2: Backward Navigation - Desired Outcome ← Business Challenge

        Lambda Use Case: Given a desired outcome, find which challenges led to it.
        Navigation Pattern: Outcome <--isDesiredOutcomeOf-- SOW <--isBusinessChallengeOf-- Challenge
        """

        query = """
        PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?outcome ?outcomeLabel ?challenge ?challengeLabel ?sow WHERE {
            # Backward navigation using inverse properties
            ?outcome csow:isDesiredOutcomeOf ?sow .
            ?challenge csow:isBusinessChallengeOf ?sow .

            # Get labels
            OPTIONAL { ?outcome rdfs:label ?outcomeLabel }
            OPTIONAL { ?challenge rdfs:label ?challengeLabel }
        }
        ORDER BY ?outcome ?challenge
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Backward Navigation: Outcome ← Challenge",
            "navigation_pattern": "isDesiredOutcomeOf + isBusinessChallengeOf",
            "lambda_use_case": "Given an outcome, find which challenges led to it",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def get_challenges_for_outcome(outcome_uri: str) -> List[str]",
                "description": "Returns list of challenge URIs that led to given outcome",
                "navigation_hops": 2,
                "complexity": "simple"
            },
            "sample_results": [str(row) for row in results[:3]]
        }

    def example_3_cross_reference_browsing_data_business_canvas(self) -> Dict[str, Any]:
        """
        Example 3: Cross-Reference Browsing - Data Business Canvas Discovery

        Lambda Use Case: From a Data Business Canvas, discover all related concepts.
        Navigation Pattern: Canvas --rdfs:seeAlso--> Related Concepts
        """

        query = """
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?canvas ?relatedConcept ?conceptType WHERE {
            ?canvas a bridge:DataBusinessCanvas .
            ?canvas rdfs:seeAlso ?relatedConcept .

            # Try to determine the type of related concept
            OPTIONAL { ?relatedConcept a ?conceptType }
        }
        ORDER BY ?canvas ?relatedConcept
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Cross-Reference Browsing: Canvas Discovery",
            "navigation_pattern": "rdfs:seeAlso",
            "lambda_use_case": "Discover all concepts related to a business canvas",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def discover_related_concepts(canvas_uri: str) -> Dict[str, List[str]]",
                "description": "Returns dictionary of concept types and their URIs related to canvas",
                "navigation_hops": 1,
                "complexity": "simple"
            },
            "sample_results": [str(row) for row in results[:5]]
        }

    def example_4_bidirectional_executive_target_navigation(self) -> Dict[str, Any]:
        """
        Example 4: Bidirectional Navigation - Executive Target ↔ Canvas

        Lambda Use Case: Navigate both ways between executive targets and business canvas.
        Navigation Pattern: Target <--alignsWithTarget--> Canvas
        """

        query = """
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?target ?canvas ?owner ?direction ?targetLabel WHERE {
            # Forward direction: Canvas → Target
            {
                ?canvas bridge:alignsWithTarget ?target .
                BIND("canvas_to_target" AS ?direction)
            }
            UNION
            # Backward direction: Target → Canvas
            {
                ?target bridge:isTargetAlignedWith ?canvas .
                BIND("target_to_canvas" AS ?direction)
            }

            # Additional navigation: Target → Owner
            OPTIONAL {
                ?target bridge:ownedBy ?owner
            }
            OPTIONAL { ?target rdfs:label ?targetLabel }
        }
        ORDER BY ?target ?canvas
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Bidirectional Navigation: Target ↔ Canvas",
            "navigation_pattern": "alignsWithTarget ↔ isTargetAlignedWith",
            "lambda_use_case": "Navigate between executive targets and business canvas in both directions",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def navigate_target_canvas(uri: str, direction: str) -> List[str]",
                "description": "Navigate bidirectionally between targets and canvas",
                "navigation_hops": 1,
                "complexity": "medium"
            },
            "sample_results": [str(row) for row in results[:3]]
        }

    def example_5_multi_hop_value_chain_navigation(self) -> Dict[str, Any]:
        """
        Example 5: Multi-hop Navigation - Complete Value Chain

        Lambda Use Case: Navigate through complete value chain from challenge to execution.
        Navigation Pattern: Challenge → Outcome → Canvas → Contract → Task
        """

        query = """
        PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?challenge ?outcome ?canvas ?contract ?task ?navigationPath WHERE {
            # Hop 1: Challenge → SOW
            ?sow csow:hasBusinessChallenge ?challenge .

            # Hop 2: SOW → Outcome
            ?sow csow:hasDesiredOutcome ?outcome .

            # Hop 3: SOW → Canvas (via implementsCanvas or cross-reference)
            {
                ?sow csow:implementsCanvas ?canvas .
                BIND("direct_implementation" AS ?implementationPath)
            }
            UNION
            {
                ?outcome rdfs:seeAlso ?canvas .
                ?canvas a bridge:DataBusinessCanvas .
                BIND("via_outcome_reference" AS ?implementationPath)
            }

            # Hop 4: Canvas → Contract (via implementedBySOW)
            OPTIONAL {
                ?canvas bridge:implementedBySOW ?sowContract .
                ?sowContract bridge:realizesContract ?contract .
            }

            # Hop 5: Contract → Task
            OPTIONAL {
                ?contract bridge:executedByTask ?task .
            }

            BIND(CONCAT("Challenge→Outcome→Canvas→Contract→Task (", ?implementationPath, ")") AS ?navigationPath)
        }
        ORDER BY ?challenge ?outcome
        LIMIT 10
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Multi-hop Navigation: Complete Value Chain",
            "navigation_pattern": "Challenge→Outcome→Canvas→Contract→Task",
            "lambda_use_case": "Trace complete value chain from business need to execution",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def trace_value_chain(challenge_uri: str) -> Dict[str, Any]",
                "description": "Traces complete path from business challenge to task execution",
                "navigation_hops": 5,
                "complexity": "high"
            },
            "sample_results": [str(row) for row in results[:2]]
        }

    def example_6_inference_based_navigation(self) -> Dict[str, Any]:
        """
        Example 6: Inference-based Navigation - Requirements → Opportunities

        Lambda Use Case: Find analytical opportunities inferred from business requirements.
        Navigation Pattern: Requirement --infersOpportunity--> Opportunity + reasoning
        """

        query = """
        PREFIX sow: <https://agentic-data-scraper.com/ontology/sow#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?requirement ?opportunity ?opportunityType ?confidence ?reasoning ?keyword WHERE {
            ?requirement a sow:BusinessRequirement .
            ?requirement sow:infersOpportunity ?opportunity .

            # Get the type of inferred opportunity
            ?opportunity a ?opportunityType .
            FILTER(?opportunityType IN (
                sow:SpatialAnalysisOpportunity,
                sow:TemporalAnalysisOpportunity,
                sow:NetworkAnalysisOpportunity,
                sow:CrossDomainOpportunity
            ))

            # Get inference metadata
            OPTIONAL { ?opportunity sow:confidenceLevel ?confidence }
            OPTIONAL { ?opportunity sow:reasoningTrace ?reasoning }
            OPTIONAL { ?requirement sow:containsKeyword ?keyword }
        }
        ORDER BY DESC(?confidence) ?opportunityType
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Inference-based Navigation: Requirements → Opportunities",
            "navigation_pattern": "infersOpportunity + inference metadata",
            "lambda_use_case": "Find AI-inferred opportunities from business requirements",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def get_inferred_opportunities(requirement_uri: str) -> List[Dict[str, Any]]",
                "description": "Returns inferred opportunities with confidence scores and reasoning",
                "navigation_hops": 1,
                "complexity": "medium"
            },
            "sample_results": [str(row) for row in results[:3]]
        }

    def example_7_cross_ontology_navigation(self) -> Dict[str, Any]:
        """
        Example 7: Cross-ontology Navigation - Bridge to SOW to Inference

        Lambda Use Case: Navigate across all three ontology layers.
        Navigation Pattern: Bridge concepts ↔ SOW concepts ↔ Inference concepts
        """

        query = """
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
        PREFIX sow: <https://agentic-data-scraper.com/ontology/sow#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?bridgeConcept ?sowConcept ?inferenceConcept ?ontologyPath WHERE {
            # Bridge → Complete SOW navigation
            {
                ?bridgeConcept rdfs:seeAlso ?sowConcept .
                ?bridgeConcept a ?bridgeType .
                ?sowConcept a ?sowType .
                FILTER(STRSTARTS(STR(?bridgeType), "https://agentic-data-scraper.com/ontology/gist-dbc-bridge#"))
                FILTER(STRSTARTS(STR(?sowType), "https://agentic-data-scraper.com/ontology/complete-sow#"))
                BIND("Bridge→SOW" AS ?ontologyPath)
            }
            UNION
            # Complete SOW → Inference navigation
            {
                ?sowConcept rdfs:seeAlso ?inferenceConcept .
                ?sowConcept a ?sowType .
                ?inferenceConcept a ?inferenceType .
                FILTER(STRSTARTS(STR(?sowType), "https://agentic-data-scraper.com/ontology/complete-sow#"))
                FILTER(STRSTARTS(STR(?inferenceType), "https://agentic-data-scraper.com/ontology/sow#"))
                BIND("SOW→Inference" AS ?ontologyPath)
            }
        }
        ORDER BY ?ontologyPath ?bridgeConcept
        LIMIT 15
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Cross-ontology Navigation: Bridge ↔ SOW ↔ Inference",
            "navigation_pattern": "rdfs:seeAlso across ontology boundaries",
            "lambda_use_case": "Navigate seamlessly across all ontology layers",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def navigate_across_ontologies(concept_uri: str) -> Dict[str, List[str]]",
                "description": "Returns related concepts from all ontology layers",
                "navigation_hops": 1,
                "complexity": "medium"
            },
            "sample_results": [str(row) for row in results[:5]]
        }

    def example_8_quality_navigation_data_contracts(self) -> Dict[str, Any]:
        """
        Example 8: Quality Navigation - Data Contracts ↔ Quality Standards

        Lambda Use Case: Navigate between contracts, quality standards, and processing tasks.
        Navigation Pattern: Contract ↔ QualityStandard ↔ Task
        """

        query = """
        PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?contract ?qualityStandard ?task ?qualityValue ?navigationPath WHERE {
            # Forward: Contract → Quality Standard
            {
                ?contract bridge:hasQualityStandard ?qualityStandard .
                OPTIONAL { ?contract bridge:executedByTask ?task }
                BIND("Contract→Quality" AS ?navigationPath)
            }
            UNION
            # Backward: Quality Standard → Contract
            {
                ?qualityStandard bridge:isQualityStandardFor ?contract .
                OPTIONAL { ?contract bridge:executedByTask ?task }
                BIND("Quality→Contract" AS ?navigationPath)
            }
            UNION
            # Multi-hop: Contract → Task → Quality (via seeAlso)
            {
                ?contract bridge:executedByTask ?task .
                ?task rdfs:seeAlso ?qualityStandard .
                ?qualityStandard a bridge:DataQualityStandard .
                BIND("Contract→Task→Quality" AS ?navigationPath)
            }

            # Get quality threshold if available
            OPTIONAL { ?qualityStandard bridge:hasQualityThreshold ?qualityValue }
        }
        ORDER BY ?contract ?navigationPath
        """

        results = list(self.graph.query(query))

        return {
            "example_name": "Quality Navigation: Contracts ↔ Standards ↔ Tasks",
            "navigation_pattern": "hasQualityStandard ↔ isQualityStandardFor + rdfs:seeAlso",
            "lambda_use_case": "Navigate quality requirements and execution relationships",
            "sparql_query": query,
            "result_count": len(results),
            "lambda_implementation": {
                "function_signature": "def navigate_quality_relationships(concept_uri: str) -> Dict[str, Any]",
                "description": "Returns quality-related concepts and their relationships",
                "navigation_hops": 2,
                "complexity": "medium"
            },
            "sample_results": [str(row) for row in results[:3]]
        }

    def generate_all_examples(self) -> Dict[str, Any]:
        """Generate all navigation examples with metadata"""

        examples = {
            "metadata": {
                "generation_date": "2025-09-25",
                "ontology_files": [
                    "schemas/ontologies/bridge/gist_dbc_bridge.owl",
                    "schemas/ontologies/sow/complete_sow_ontology.owl",
                    "schemas/ontologies/sow/sow_inference_rules.owl"
                ],
                "total_examples": 8,
                "navigation_patterns_covered": [
                    "Forward Navigation",
                    "Backward Navigation",
                    "Cross-Reference Browsing",
                    "Bidirectional Navigation",
                    "Multi-hop Navigation",
                    "Inference-based Navigation",
                    "Cross-ontology Navigation",
                    "Quality Standards Navigation"
                ]
            },
            "examples": {}
        }

        # Generate all examples
        example_methods = [
            self.example_1_forward_navigation_challenge_to_outcome,
            self.example_2_backward_navigation_outcome_to_challenge,
            self.example_3_cross_reference_browsing_data_business_canvas,
            self.example_4_bidirectional_executive_target_navigation,
            self.example_5_multi_hop_value_chain_navigation,
            self.example_6_inference_based_navigation,
            self.example_7_cross_ontology_navigation,
            self.example_8_quality_navigation_data_contracts
        ]

        for i, method in enumerate(example_methods, 1):
            try:
                example = method()
                examples["examples"][f"example_{i}"] = example
                print(f"✓ Generated Example {i}: {example['example_name']} ({example['result_count']} schema patterns)")
            except Exception as e:
                print(f"✗ Failed to generate Example {i}: {str(e)}")
                examples["examples"][f"example_{i}"] = {
                    "error": str(e),
                    "status": "failed"
                }

        return examples

    def export_examples(self, output_path: Path) -> None:
        """Export all examples to JSON file"""
        examples = self.generate_all_examples()

        with open(output_path, 'w') as f:
            json.dump(examples, f, indent=2, default=str)

        print(f"\n✓ Navigation examples exported to: {output_path}")
        print("Examples include:")
        print("  - 8 different navigation patterns")
        print("  - Concrete SPARQL queries for Lambda implementation")
        print("  - Function signatures and complexity assessments")
        print("  - Cross-ontology navigation demonstrations")


def main():
    """Run the SPARQL navigation examples generator"""

    # Set up paths
    current_dir = Path(__file__).parent
    ontology_dir = current_dir.parent.parent / "schemas" / "ontologies"
    output_path = current_dir.parent.parent / "sparql_navigation_examples.json"

    # Generate examples
    generator = SPARQLNavigationExamples(ontology_dir)
    generator.export_examples(output_path)

    print("\n" + "="*60)
    print("SPARQL NAVIGATION EXAMPLES GENERATED")
    print("="*60)
    print("Lambda developers can use these concrete examples to implement")
    print("concept-to-concept navigation across the complete ontology stack.")
    print("="*60)


if __name__ == "__main__":
    main()