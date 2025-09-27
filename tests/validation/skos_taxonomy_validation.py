#!/usr/bin/env python3
"""
SKOS Taxonomy Browsing Validation Suite
=======================================

Comprehensive validation for SKOS taxonomy browsing capability across all ontologies
to ensure Lambda users can navigate knowledge hierarchies like browsing a taxonomy tree.

This module provides:
1. SKOS ConceptScheme Navigation Testing
2. Hierarchical Browsing Validation
3. Related Concept Discovery Testing
4. SKOS Examples and Scope Notes Validation
5. SPARQL Test Queries for Taxonomy Browsing
6. Lambda Readiness Assessment

Usage:
    python tests/validation/skos_taxonomy_validation.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from rdflib import Graph, Namespace, URIRef, Literal, BNode
    from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD
    from rdflib.plugins.sparql import prepareQuery
    import rdflib.util
except ImportError as e:
    print(f"Error importing RDFLib: {e}")
    print("Install with: pip install rdflib")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
BRIDGE = Namespace("https://agentic-data-scraper.com/ontology/gist-dbc-bridge#")
SOW_COMPLETE = Namespace("https://agentic-data-scraper.com/ontology/complete-sow#")
SOW_INFERENCE = Namespace("https://agentic-data-scraper.com/ontology/sow#")
GIST = Namespace("https://w3id.org/semanticarts/ontology/gistCore#")

@dataclass
class ConceptSchemeInfo:
    """Information about a SKOS ConceptScheme"""
    uri: URIRef
    label: str
    comment: str
    description: str
    concepts: List[URIRef] = field(default_factory=list)
    see_also: List[URIRef] = field(default_factory=list)

@dataclass
class ConceptInfo:
    """Information about a SKOS Concept"""
    uri: URIRef
    label: str
    comment: str
    scheme: Optional[URIRef] = None
    broader: List[URIRef] = field(default_factory=list)
    narrower: List[URIRef] = field(default_factory=list)
    related: List[URIRef] = field(default_factory=list)
    scope_note: Optional[str] = None
    examples: List[str] = field(default_factory=list)

@dataclass
class ValidationResult:
    """Result of a validation test"""
    test_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0

@dataclass
class TaxonomyMetrics:
    """Metrics for taxonomy quality assessment"""
    concept_schemes_count: int = 0
    concepts_count: int = 0
    hierarchical_relationships_count: int = 0
    related_relationships_count: int = 0
    concepts_with_examples: int = 0
    concepts_with_scope_notes: int = 0
    max_hierarchy_depth: int = 0
    avg_hierarchy_depth: float = 0.0
    taxonomy_completeness_score: float = 0.0
    navigation_readiness_score: float = 0.0

class SKOSTaxonomyValidator:
    """Validates SKOS taxonomy browsing capabilities across ontologies"""

    def __init__(self):
        self.graph = Graph()
        self.concept_schemes: Dict[URIRef, ConceptSchemeInfo] = {}
        self.concepts: Dict[URIRef, ConceptInfo] = {}
        self.validation_results: List[ValidationResult] = []
        self.metrics = TaxonomyMetrics()

        # Bind namespaces
        self.graph.bind("bridge", BRIDGE)
        self.graph.bind("sow", SOW_COMPLETE)
        self.graph.bind("sowinf", SOW_INFERENCE)
        self.graph.bind("gist", GIST)
        self.graph.bind("skos", SKOS)
        self.graph.bind("rdfs", RDFS)

    def load_ontologies(self) -> bool:
        """Load all ontology files"""
        ontology_files = [
            "schemas/ontologies/bridge/gist_dbc_bridge.owl",
            "schemas/ontologies/sow/complete_sow_ontology.owl",
            "schemas/ontologies/sow/sow_inference_rules.owl"
        ]

        success = True
        for file_path in ontology_files:
            full_path = project_root / file_path
            try:
                logger.info(f"Loading ontology: {file_path}")
                self.graph.parse(str(full_path), format="xml")
                logger.info(f"Successfully loaded {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                success = False

        logger.info(f"Loaded graph with {len(self.graph)} triples")
        return success

    def discover_concept_schemes(self) -> None:
        """Discover all SKOS ConceptSchemes in the graph"""
        logger.info("Discovering SKOS ConceptSchemes...")

        query = """
        SELECT ?scheme ?label ?comment ?description ?seeAlso WHERE {
            ?scheme a skos:ConceptScheme .
            OPTIONAL { ?scheme rdfs:label ?label }
            OPTIONAL { ?scheme rdfs:comment ?comment }
            OPTIONAL { ?scheme dcterms:description ?description }
            OPTIONAL { ?scheme rdfs:seeAlso ?seeAlso }
        }
        """

        for row in self.graph.query(query):
            scheme_uri = row.scheme
            self.concept_schemes[scheme_uri] = ConceptSchemeInfo(
                uri=scheme_uri,
                label=str(row.label) if row.label else "",
                comment=str(row.comment) if row.comment else "",
                description=str(row.description) if row.description else ""
            )

            if row.seeAlso:
                self.concept_schemes[scheme_uri].see_also.append(row.seeAlso)

        self.metrics.concept_schemes_count = len(self.concept_schemes)
        logger.info(f"Discovered {len(self.concept_schemes)} ConceptSchemes")

    def discover_concepts(self) -> None:
        """Discover all SKOS Concepts and their relationships"""
        logger.info("Discovering SKOS Concepts...")

        query = """
        SELECT ?concept ?label ?comment ?scheme ?broader ?narrower ?related ?scopeNote ?example WHERE {
            ?concept skos:inScheme ?scheme .
            OPTIONAL { ?concept rdfs:label ?label }
            OPTIONAL { ?concept rdfs:comment ?comment }
            OPTIONAL { ?concept skos:broader ?broader }
            OPTIONAL { ?concept skos:narrower ?narrower }
            OPTIONAL { ?concept skos:related ?related }
            OPTIONAL { ?concept skos:scopeNote ?scopeNote }
            OPTIONAL { ?concept skos:example ?example }
        }
        """

        for row in self.graph.query(query):
            concept_uri = row.concept

            if concept_uri not in self.concepts:
                self.concepts[concept_uri] = ConceptInfo(
                    uri=concept_uri,
                    label=str(row.label) if row.label else "",
                    comment=str(row.comment) if row.comment else "",
                    scheme=row.scheme
                )

            concept = self.concepts[concept_uri]

            if row.broader and row.broader not in concept.broader:
                concept.broader.append(row.broader)
            if row.narrower and row.narrower not in concept.narrower:
                concept.narrower.append(row.narrower)
            if row.related and row.related not in concept.related:
                concept.related.append(row.related)
            if row.scopeNote:
                concept.scope_note = str(row.scopeNote)
            if row.example and str(row.example) not in concept.examples:
                concept.examples.append(str(row.example))

        # Add concepts to their schemes
        for concept in self.concepts.values():
            if concept.scheme in self.concept_schemes:
                self.concept_schemes[concept.scheme].concepts.append(concept.uri)

        self.metrics.concepts_count = len(self.concepts)
        logger.info(f"Discovered {len(self.concepts)} Concepts")

    def calculate_hierarchy_metrics(self) -> None:
        """Calculate hierarchy depth and relationship metrics"""
        logger.info("Calculating hierarchy metrics...")

        hierarchical_rels = 0
        related_rels = 0
        concepts_with_examples = 0
        concepts_with_scope_notes = 0
        depths = []

        for concept in self.concepts.values():
            hierarchical_rels += len(concept.broader) + len(concept.narrower)
            related_rels += len(concept.related)

            if concept.examples:
                concepts_with_examples += 1
            if concept.scope_note:
                concepts_with_scope_notes += 1

            # Calculate depth from root
            depth = self._calculate_concept_depth(concept.uri)
            if depth > 0:
                depths.append(depth)

        self.metrics.hierarchical_relationships_count = hierarchical_rels
        self.metrics.related_relationships_count = related_rels
        self.metrics.concepts_with_examples = concepts_with_examples
        self.metrics.concepts_with_scope_notes = concepts_with_scope_notes

        if depths:
            self.metrics.max_hierarchy_depth = max(depths)
            self.metrics.avg_hierarchy_depth = sum(depths) / len(depths)

        logger.info(f"Hierarchy metrics calculated: max_depth={self.metrics.max_hierarchy_depth}, "
                   f"avg_depth={self.metrics.avg_hierarchy_depth:.2f}")

    def _calculate_concept_depth(self, concept_uri: URIRef, visited: set = None) -> int:
        """Calculate depth of concept from root (concepts with no broader concepts)"""
        if visited is None:
            visited = set()

        if concept_uri in visited:
            return 0  # Circular reference protection

        visited.add(concept_uri)

        if concept_uri not in self.concepts:
            return 0

        concept = self.concepts[concept_uri]

        if not concept.broader:
            return 1  # Root concept

        # Find maximum depth from any parent
        max_parent_depth = 0
        for parent_uri in concept.broader:
            parent_depth = self._calculate_concept_depth(parent_uri, visited.copy())
            max_parent_depth = max(max_parent_depth, parent_depth)

        return max_parent_depth + 1

    def test_concept_scheme_navigation(self) -> ValidationResult:
        """Test 1: SKOS ConceptScheme Navigation"""
        logger.info("Testing SKOS ConceptScheme navigation...")

        issues = []
        score = 0.0

        # Check that all ConceptSchemes are properly defined
        if not self.concept_schemes:
            return ValidationResult(
                test_name="ConceptScheme Navigation",
                passed=False,
                message="No SKOS ConceptSchemes found",
                score=0.0
            )

        for scheme_uri, scheme in self.concept_schemes.items():
            scheme_issues = []

            # Check basic metadata
            if not scheme.label:
                scheme_issues.append("Missing rdfs:label")
            if not scheme.comment:
                scheme_issues.append("Missing rdfs:comment")
            if not scheme.description:
                scheme_issues.append("Missing description")

            # Check concept membership
            if not scheme.concepts:
                scheme_issues.append("No concepts linked to scheme")

            # Check see_also references for discoverability
            if not scheme.see_also:
                scheme_issues.append("No rdfs:seeAlso references for cross-navigation")

            if scheme_issues:
                issues.append(f"{scheme.label or str(scheme_uri)}: {', '.join(scheme_issues)}")

        # Calculate score
        total_schemes = len(self.concept_schemes)
        problematic_schemes = len(issues)
        score = max(0.0, (total_schemes - problematic_schemes) / total_schemes) * 100

        passed = score >= 80.0
        message = f"Found {total_schemes} ConceptSchemes, {problematic_schemes} with issues"

        return ValidationResult(
            test_name="ConceptScheme Navigation",
            passed=passed,
            message=message,
            details={
                "total_schemes": total_schemes,
                "issues": issues,
                "schemes": [{"uri": str(uri), "label": info.label} for uri, info in self.concept_schemes.items()]
            },
            score=score
        )

    def test_hierarchical_browsing(self) -> ValidationResult:
        """Test 2: Hierarchical Browsing with skos:broader/narrower"""
        logger.info("Testing hierarchical browsing...")

        issues = []
        bidirectional_count = 0
        total_hierarchical_rels = 0

        for concept_uri, concept in self.concepts.items():
            # Check bidirectional relationships
            for broader_uri in concept.broader:
                total_hierarchical_rels += 1
                if broader_uri in self.concepts:
                    broader_concept = self.concepts[broader_uri]
                    if concept_uri in broader_concept.narrower:
                        bidirectional_count += 1
                    else:
                        issues.append(f"{concept.label}: broader relationship to {broader_concept.label} not bidirectional")

        # Check for orphaned concepts (no broader or narrower)
        orphaned_concepts = []
        for concept_uri, concept in self.concepts.items():
            if not concept.broader and not concept.narrower:
                orphaned_concepts.append(concept.label or str(concept_uri))

        # Calculate score
        if total_hierarchical_rels > 0:
            bidirectional_score = (bidirectional_count / total_hierarchical_rels) * 100
        else:
            bidirectional_score = 0

        orphan_penalty = min(len(orphaned_concepts) * 10, 50)  # Max 50% penalty
        score = max(0.0, bidirectional_score - orphan_penalty)

        passed = score >= 70.0 and len(issues) < 5

        message = f"Bidirectional relationships: {bidirectional_count}/{total_hierarchical_rels}, "
        message += f"Orphaned concepts: {len(orphaned_concepts)}"

        return ValidationResult(
            test_name="Hierarchical Browsing",
            passed=passed,
            message=message,
            details={
                "bidirectional_relationships": bidirectional_count,
                "total_hierarchical_relationships": total_hierarchical_rels,
                "orphaned_concepts": orphaned_concepts,
                "issues": issues,
                "max_depth": self.metrics.max_hierarchy_depth,
                "avg_depth": self.metrics.avg_hierarchy_depth
            },
            score=score
        )

    def test_related_concept_discovery(self) -> ValidationResult:
        """Test 3: Related Concept Discovery"""
        logger.info("Testing related concept discovery...")

        cross_scheme_relations = 0
        valid_relations = 0
        issues = []

        for concept_uri, concept in self.concepts.items():
            for related_uri in concept.related:
                if related_uri in self.concepts:
                    valid_relations += 1
                    related_concept = self.concepts[related_uri]

                    # Check for cross-scheme relationships
                    if concept.scheme != related_concept.scheme:
                        cross_scheme_relations += 1
                else:
                    issues.append(f"{concept.label}: related concept {related_uri} not found")

        # Calculate coverage
        concepts_with_relations = sum(1 for c in self.concepts.values() if c.related)
        relation_coverage = (concepts_with_relations / len(self.concepts)) * 100 if self.concepts else 0

        # Score based on valid relations and cross-domain connectivity
        cross_domain_bonus = min(cross_scheme_relations * 2, 30)  # Max 30% bonus
        score = min(100, relation_coverage + cross_domain_bonus)

        passed = score >= 60.0 and len(issues) < 3

        message = f"Related concepts: {valid_relations}, Cross-scheme: {cross_scheme_relations}, "
        message += f"Coverage: {relation_coverage:.1f}%"

        return ValidationResult(
            test_name="Related Concept Discovery",
            passed=passed,
            message=message,
            details={
                "valid_relations": valid_relations,
                "cross_scheme_relations": cross_scheme_relations,
                "relation_coverage": relation_coverage,
                "concepts_with_relations": concepts_with_relations,
                "issues": issues
            },
            score=score
        )

    def test_examples_and_scope_notes(self) -> ValidationResult:
        """Test 4: SKOS Examples and Scope Notes for Implementation Guidance"""
        logger.info("Testing examples and scope notes...")

        concepts_with_examples = self.metrics.concepts_with_examples
        concepts_with_scope_notes = self.metrics.concepts_with_scope_notes
        total_concepts = len(self.concepts)

        # Analyze quality of examples and scope notes
        detailed_scope_notes = 0
        lambda_ready_examples = 0

        for concept in self.concepts.values():
            # Check scope note quality (length and Lambda-specific guidance)
            if concept.scope_note:
                if len(concept.scope_note) > 200:  # Detailed guidance
                    detailed_scope_notes += 1

            # Check example quality (specific, actionable)
            for example in concept.examples:
                if any(keyword in example.lower() for keyword in
                       ['lambda', 'aws', 'implementation', 'system', 'data']):
                    lambda_ready_examples += 1
                    break  # Count concept once

        # Calculate scores
        example_coverage = (concepts_with_examples / total_concepts) * 100 if total_concepts else 0
        scope_note_coverage = (concepts_with_scope_notes / total_concepts) * 100 if total_concepts else 0
        detail_quality = (detailed_scope_notes / concepts_with_scope_notes) * 100 if concepts_with_scope_notes else 0
        lambda_readiness = (lambda_ready_examples / concepts_with_examples) * 100 if concepts_with_examples else 0

        overall_score = (example_coverage + scope_note_coverage + detail_quality + lambda_readiness) / 4

        passed = (example_coverage >= 40 and scope_note_coverage >= 30 and
                 detail_quality >= 50 and lambda_readiness >= 30)

        message = f"Examples: {example_coverage:.1f}%, Scope notes: {scope_note_coverage:.1f}%, "
        message += f"Lambda-ready: {lambda_readiness:.1f}%"

        return ValidationResult(
            test_name="Examples and Scope Notes",
            passed=passed,
            message=message,
            details={
                "example_coverage": example_coverage,
                "scope_note_coverage": scope_note_coverage,
                "detailed_scope_notes": detailed_scope_notes,
                "lambda_ready_examples": lambda_ready_examples,
                "detail_quality": detail_quality,
                "lambda_readiness": lambda_readiness
            },
            score=overall_score
        )

    def run_all_tests(self) -> Tuple[bool, List[ValidationResult]]:
        """Run all validation tests"""
        logger.info("Starting SKOS taxonomy validation...")

        if not self.load_ontologies():
            return False, []

        self.discover_concept_schemes()
        self.discover_concepts()
        self.calculate_hierarchy_metrics()

        # Run tests
        tests = [
            self.test_concept_scheme_navigation,
            self.test_hierarchical_browsing,
            self.test_related_concept_discovery,
            self.test_examples_and_scope_notes
        ]

        results = []
        for test in tests:
            result = test()
            results.append(result)
            self.validation_results.append(result)

        # Calculate overall metrics
        self.calculate_taxonomy_readiness_scores()

        all_passed = all(result.passed for result in results)
        return all_passed, results

    def calculate_taxonomy_readiness_scores(self) -> None:
        """Calculate overall taxonomy completeness and Lambda readiness scores"""

        # Taxonomy Completeness Score
        scheme_completeness = min(self.metrics.concept_schemes_count * 25, 100)  # Max 4 schemes
        concept_density = min(self.metrics.concepts_count * 5, 100)  # Max 20 concepts
        relationship_density = min(self.metrics.hierarchical_relationships_count * 2, 50)  # Max 25 rels
        cross_relations = min(self.metrics.related_relationships_count * 3, 50)  # Max ~17 rels

        self.metrics.taxonomy_completeness_score = (
            scheme_completeness * 0.2 +
            concept_density * 0.3 +
            relationship_density * 0.3 +
            cross_relations * 0.2
        )

        # Navigation Readiness Score
        avg_test_score = sum(r.score for r in self.validation_results) / len(self.validation_results)
        example_coverage = (self.metrics.concepts_with_examples / self.metrics.concepts_count) * 100
        scope_coverage = (self.metrics.concepts_with_scope_notes / self.metrics.concepts_count) * 100

        self.metrics.navigation_readiness_score = (
            avg_test_score * 0.5 +
            example_coverage * 0.25 +
            scope_coverage * 0.25
        )

def main():
    """Main validation execution"""
    print("SKOS Taxonomy Browsing Validation Suite")
    print("=" * 50)

    validator = SKOSTaxonomyValidator()
    success, results = validator.run_all_tests()

    # Print results
    print(f"\nValidation Results:")
    print("-" * 30)

    for result in results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"{status} {result.test_name}: {result.message} (Score: {result.score:.1f}%)")

    print(f"\nTaxonomy Metrics:")
    print("-" * 20)
    metrics = validator.metrics
    print(f"ConceptSchemes: {metrics.concept_schemes_count}")
    print(f"Concepts: {metrics.concepts_count}")
    print(f"Hierarchical Relationships: {metrics.hierarchical_relationships_count}")
    print(f"Related Relationships: {metrics.related_relationships_count}")
    print(f"Max Hierarchy Depth: {metrics.max_hierarchy_depth}")
    print(f"Avg Hierarchy Depth: {metrics.avg_hierarchy_depth:.2f}")
    print(f"Concepts with Examples: {metrics.concepts_with_examples}")
    print(f"Concepts with Scope Notes: {metrics.concepts_with_scope_notes}")

    print(f"\nOverall Assessment:")
    print("-" * 20)
    print(f"Taxonomy Completeness: {metrics.taxonomy_completeness_score:.1f}%")
    print(f"Navigation Readiness: {metrics.navigation_readiness_score:.1f}%")

    overall_status = "READY" if success and metrics.navigation_readiness_score >= 70 else "NEEDS WORK"
    print(f"Lambda Readiness: {overall_status}")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)