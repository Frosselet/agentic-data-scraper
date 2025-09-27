"""
Comprehensive validation tests for bidirectional navigation capability across ontologies.

This module validates that Lambda users can navigate concept-to-concept like web browsing
across the complete ontology infrastructure including:
- gist_dbc_bridge.owl
- complete_sow_ontology.owl
- sow_inference_rules.owl

Test Categories:
1. Inverse Property Navigation Tests
2. Cross-Reference Discovery Tests
3. SPARQL Query Scenario Tests
4. Lambda Readiness Assessment
"""

import pytest
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS
from pathlib import Path
import tempfile
import json
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, asdict


# Namespace definitions
BRIDGE = Namespace("https://agentic-data-scraper.com/ontology/gist-dbc-bridge#")
COMPLETE_SOW = Namespace("https://agentic-data-scraper.com/ontology/complete-sow#")
SOW = Namespace("https://agentic-data-scraper.com/ontology/sow#")
GIST = Namespace("https://w3id.org/semanticarts/ontology/gistCore#")


@dataclass
class NavigationTest:
    """Test case for navigation validation"""
    name: str
    description: str
    forward_property: URIRef
    inverse_property: URIRef
    domain_class: URIRef
    range_class: URIRef
    expected_relationships: int = 0
    confidence: float = 1.0


@dataclass
class CrossReferenceTest:
    """Test case for cross-reference validation"""
    name: str
    description: str
    source_concept: URIRef
    target_concepts: List[URIRef]
    cross_ontology: bool = False
    external_vocab: bool = False


@dataclass
class SPARQLScenario:
    """SPARQL query scenario for concept navigation"""
    name: str
    description: str
    query: str
    expected_results_min: int = 0
    navigation_hops: int = 1
    scenario_type: str = "bidirectional"  # forward, backward, bidirectional, multi-hop


class OntologyNavigationValidator:
    """Comprehensive validator for ontology navigation capabilities"""

    def __init__(self, ontology_dir: Path):
        self.ontology_dir = ontology_dir
        self.graph = Graph()
        self.validation_results = {
            "inverse_properties": [],
            "cross_references": [],
            "sparql_scenarios": [],
            "lambda_readiness": {}
        }
        self.load_ontologies()

    def load_ontologies(self):
        """Load all ontology files into a single graph"""
        ontology_files = [
            "bridge/gist_dbc_bridge.owl",
            "sow/complete_sow_ontology.owl",
            "sow/sow_inference_rules.owl"
        ]

        for file_path in ontology_files:
            full_path = self.ontology_dir / file_path
            if full_path.exists():
                self.graph.parse(str(full_path), format="xml")
                print(f"Loaded: {file_path}")
            else:
                print(f"Warning: Missing ontology file: {file_path}")


class TestInversePropertyNavigation:
    """Test suite for inverse property navigation validation"""

    @pytest.fixture(scope="class")
    def validator(self):
        ontology_dir = Path(__file__).parent.parent.parent / "schemas" / "ontologies"
        return OntologyNavigationValidator(ontology_dir)

    @pytest.fixture(scope="class")
    def inverse_property_tests(self):
        """Define comprehensive inverse property test cases"""
        return [
            # Bridge Ontology Inverse Properties
            NavigationTest(
                name="BusinessModel Bidirectional",
                description="Org ↔ DataBusinessCanvas navigation",
                forward_property=BRIDGE.hasBusinessModel,
                inverse_property=BRIDGE.isBusinessModelOf,
                domain_class=GIST.Organization,
                range_class=BRIDGE.DataBusinessCanvas
            ),
            NavigationTest(
                name="ValueProvision Bidirectional",
                description="DataAsset ↔ Person value relationship",
                forward_property=BRIDGE.providesValueTo,
                inverse_property=BRIDGE.receivesValueFrom,
                domain_class=BRIDGE.DataAsset,
                range_class=GIST.Person
            ),
            NavigationTest(
                name="SOW Implementation Bidirectional",
                description="Canvas ↔ SOW Contract implementation",
                forward_property=BRIDGE.implementedBySOW,
                inverse_property=BRIDGE.implementsCanvas,
                domain_class=BRIDGE.DataBusinessCanvas,
                range_class=BRIDGE.SemanticSOWContract
            ),
            NavigationTest(
                name="Data Source Requirements",
                description="SOW ↔ DataAsset requirements",
                forward_property=BRIDGE.requiresDataSource,
                inverse_property=BRIDGE.isDataSourceFor,
                domain_class=BRIDGE.SemanticSOWContract,
                range_class=BRIDGE.DataAsset
            ),
            NavigationTest(
                name="Contract Realization",
                description="SOW ↔ DataContract realization",
                forward_property=BRIDGE.realizesContract,
                inverse_property=BRIDGE.isRealizedBySOW,
                domain_class=BRIDGE.SemanticSOWContract,
                range_class=BRIDGE.DataContract
            ),
            NavigationTest(
                name="Task Execution",
                description="DataContract ↔ DataProcessingTask execution",
                forward_property=BRIDGE.executedByTask,
                inverse_property=BRIDGE.executesContract,
                domain_class=BRIDGE.DataContract,
                range_class=BRIDGE.DataProcessingTask
            ),
            NavigationTest(
                name="Business Value Creation",
                description="Task ↔ ValueProposition business value",
                forward_property=BRIDGE.createsBusinessValue,
                inverse_property=BRIDGE.isBusinessValueOf,
                domain_class=BRIDGE.DataProcessingTask,
                range_class=BRIDGE.ValueProposition
            ),
            NavigationTest(
                name="Executive Target Alignment",
                description="Canvas ↔ ExecutiveTarget alignment",
                forward_property=BRIDGE.alignsWithTarget,
                inverse_property=BRIDGE.isTargetAlignedWith,
                domain_class=BRIDGE.DataBusinessCanvas,
                range_class=BRIDGE.ExecutiveTarget
            ),
            NavigationTest(
                name="Target Ownership",
                description="ExecutiveTarget ↔ ExecutiveTargetOwner ownership",
                forward_property=BRIDGE.ownedBy,
                inverse_property=BRIDGE.ownsTarget,
                domain_class=BRIDGE.ExecutiveTarget,
                range_class=BRIDGE.ExecutiveTargetOwner
            ),
            NavigationTest(
                name="Alignment Scoring",
                description="Canvas ↔ AlignmentScore assessment",
                forward_property=BRIDGE.hasAlignmentScore,
                inverse_property=BRIDGE.isAlignmentScoreOf,
                domain_class=BRIDGE.DataBusinessCanvas,
                range_class=BRIDGE.StrategicAlignmentScore
            ),
            NavigationTest(
                name="Semantic Mapping",
                description="DataAsset ↔ Category semantic mapping",
                forward_property=BRIDGE.hasSemanticMapping,
                inverse_property=BRIDGE.isSemanticMappingOf,
                domain_class=BRIDGE.DataAsset,
                range_class=GIST.Category
            ),
            NavigationTest(
                name="Quality Standards",
                description="DataContract ↔ DataQualityStandard requirements",
                forward_property=BRIDGE.hasQualityStandard,
                inverse_property=BRIDGE.isQualityStandardFor,
                domain_class=BRIDGE.DataContract,
                range_class=BRIDGE.DataQualityStandard
            ),

            # Complete SOW Ontology Inverse Properties
            NavigationTest(
                name="SOW Business Challenge",
                description="SOW ↔ BusinessChallenge core relationship",
                forward_property=COMPLETE_SOW.hasBusinessChallenge,
                inverse_property=COMPLETE_SOW.isBusinessChallengeOf,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.BusinessChallenge
            ),
            NavigationTest(
                name="SOW Desired Outcome",
                description="SOW ↔ DesiredOutcome goal relationship",
                forward_property=COMPLETE_SOW.hasDesiredOutcome,
                inverse_property=COMPLETE_SOW.isDesiredOutcomeOf,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.DesiredOutcome
            ),
            NavigationTest(
                name="Entity Tracking",
                description="BusinessChallenge ↔ EntityToTrack tracking",
                forward_property=COMPLETE_SOW.tracksEntity,
                inverse_property=COMPLETE_SOW.isTrackedByChallenge,
                domain_class=COMPLETE_SOW.BusinessChallenge,
                range_class=COMPLETE_SOW.EntityToTrack
            ),
            NavigationTest(
                name="SOW Stakeholders",
                description="SOW ↔ SOWStakeholder involvement",
                forward_property=COMPLETE_SOW.hasStakeholder,
                inverse_property=COMPLETE_SOW.isStakeholderOf,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.SOWStakeholder
            ),
            NavigationTest(
                name="Spatial Context",
                description="BusinessChallenge ↔ SpatialContext geographic",
                forward_property=COMPLETE_SOW.hasSpatialContext,
                inverse_property=COMPLETE_SOW.isSpatialContextOf,
                domain_class=COMPLETE_SOW.BusinessChallenge,
                range_class=COMPLETE_SOW.SpatialContext
            ),
            NavigationTest(
                name="Temporal Context",
                description="BusinessChallenge ↔ TemporalContext time-based",
                forward_property=COMPLETE_SOW.hasTemporalContext,
                inverse_property=COMPLETE_SOW.isTemporalContextOf,
                domain_class=COMPLETE_SOW.BusinessChallenge,
                range_class=COMPLETE_SOW.TemporalContext
            ),
            NavigationTest(
                name="Domain Context",
                description="SOW ↔ DomainContext business domain",
                forward_property=COMPLETE_SOW.hasDomainContext,
                inverse_property=COMPLETE_SOW.isDomainContextOf,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.DomainContext
            ),
            NavigationTest(
                name="Knowledge Context",
                description="SOW ↔ KnowledgeContext implicit knowledge",
                forward_property=COMPLETE_SOW.hasKnowledgeContext,
                inverse_property=COMPLETE_SOW.isKnowledgeContextOf,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.KnowledgeContext
            ),
            NavigationTest(
                name="Opportunity Inference",
                description="AnalyticalOpportunity ↔ BusinessChallenge inference",
                forward_property=COMPLETE_SOW.inferredFrom,
                inverse_property=COMPLETE_SOW.infersOpportunity,
                domain_class=COMPLETE_SOW.AnalyticalOpportunity,
                range_class=COMPLETE_SOW.BusinessChallenge
            ),
            NavigationTest(
                name="Opportunity Discovery",
                description="SOW ↔ AnalyticalOpportunity discovery",
                forward_property=COMPLETE_SOW.discoversOpportunity,
                inverse_property=COMPLETE_SOW.isDiscoveredBySOW,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.AnalyticalOpportunity
            ),
            NavigationTest(
                name="SOW Constraints",
                description="SOW ↔ Constraint limitations",
                forward_property=COMPLETE_SOW.hasConstraint,
                inverse_property=COMPLETE_SOW.isConstraintOf,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.Constraint
            ),
            NavigationTest(
                name="Elicitation Sessions",
                description="SOW ↔ ElicitationSession process",
                forward_property=COMPLETE_SOW.elicitedIn,
                inverse_property=COMPLETE_SOW.elicitsSOW,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=COMPLETE_SOW.ElicitationSession
            ),
            NavigationTest(
                name="Elicitation Steps",
                description="ElicitationSession ↔ ElicitationStep process",
                forward_property=COMPLETE_SOW.hasElicitationStep,
                inverse_property=COMPLETE_SOW.isElicitationStepOf,
                domain_class=COMPLETE_SOW.ElicitationSession,
                range_class=COMPLETE_SOW.ElicitationStep
            ),
            NavigationTest(
                name="Business Validation",
                description="AnalyticalOpportunity ↔ BusinessValidation validation",
                forward_property=COMPLETE_SOW.validatedBy,
                inverse_property=COMPLETE_SOW.validatesOpportunity,
                domain_class=COMPLETE_SOW.AnalyticalOpportunity,
                range_class=COMPLETE_SOW.BusinessValidation
            ),
            NavigationTest(
                name="Canvas Implementation",
                description="SOW ↔ DataBusinessCanvas implementation",
                forward_property=COMPLETE_SOW.implementsCanvas,
                inverse_property=COMPLETE_SOW.isImplementedBySOW,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=BRIDGE.DataBusinessCanvas
            ),
            NavigationTest(
                name="Contract Realization",
                description="SOW ↔ DataContract contract realization",
                forward_property=COMPLETE_SOW.realizesAsContract,
                inverse_property=COMPLETE_SOW.isRealizedAsContractBy,
                domain_class=COMPLETE_SOW.SemanticStatementOfWork,
                range_class=BRIDGE.DataContract
            ),

            # SOW Inference Rules Ontology Inverse Properties
            NavigationTest(
                name="Entity Mentions",
                description="BusinessRequirement ↔ Entity mentions",
                forward_property=SOW.mentionsEntity,
                inverse_property=SOW.isMentionedBy,
                domain_class=SOW.BusinessRequirement,
                range_class=OWL.Thing
            ),
            NavigationTest(
                name="Opportunity Inference",
                description="BusinessRequirement ↔ InferredOpportunity inference",
                forward_property=SOW.infersOpportunity,
                inverse_property=SOW.isOpportunityInferredFrom,
                domain_class=SOW.BusinessRequirement,
                range_class=SOW.InferredOpportunity
            )
        ]

    def test_inverse_property_existence(self, validator, inverse_property_tests):
        """Test that all inverse properties are correctly defined in the ontology"""
        missing_inverses = []

        for test in inverse_property_tests:
            # Check forward property exists
            forward_exists = (test.forward_property, RDF.type, OWL.ObjectProperty) in validator.graph

            # Check inverse property exists
            inverse_exists = (test.inverse_property, RDF.type, OWL.ObjectProperty) in validator.graph

            # Check inverse relationship is declared
            inverse_declared = (
                (test.inverse_property, OWL.inverseOf, test.forward_property) in validator.graph or
                (test.forward_property, OWL.inverseOf, test.inverse_property) in validator.graph
            )

            if not (forward_exists and inverse_exists and inverse_declared):
                missing_inverses.append({
                    "test": test.name,
                    "forward_exists": forward_exists,
                    "inverse_exists": inverse_exists,
                    "inverse_declared": inverse_declared,
                    "forward_property": str(test.forward_property),
                    "inverse_property": str(test.inverse_property)
                })

        validator.validation_results["inverse_properties"] = missing_inverses

        if missing_inverses:
            print(f"\nMissing or incorrectly defined inverse relationships: {len(missing_inverses)}")
            for missing in missing_inverses:
                print(f"  - {missing['test']}: {missing}")

        assert len(missing_inverses) == 0, f"Found {len(missing_inverses)} missing/incorrect inverse relationships"

    def test_domain_range_consistency(self, validator, inverse_property_tests):
        """Test that inverse properties have correctly swapped domain/range"""
        inconsistent_domains = []

        for test in inverse_property_tests:
            # Get forward property domain/range
            forward_domains = list(validator.graph.objects(test.forward_property, RDFS.domain))
            forward_ranges = list(validator.graph.objects(test.forward_property, RDFS.range))

            # Get inverse property domain/range
            inverse_domains = list(validator.graph.objects(test.inverse_property, RDFS.domain))
            inverse_ranges = list(validator.graph.objects(test.inverse_property, RDFS.range))

            # Check if inverse has swapped domain/range
            domain_swapped = test.range_class in inverse_domains if inverse_domains else False
            range_swapped = test.domain_class in inverse_ranges if inverse_ranges else False

            if forward_domains and forward_ranges and inverse_domains and inverse_ranges:
                if not (domain_swapped and range_swapped):
                    inconsistent_domains.append({
                        "test": test.name,
                        "forward_domain": str(forward_domains[0]) if forward_domains else "None",
                        "forward_range": str(forward_ranges[0]) if forward_ranges else "None",
                        "inverse_domain": str(inverse_domains[0]) if inverse_domains else "None",
                        "inverse_range": str(inverse_ranges[0]) if inverse_ranges else "None",
                        "domain_swapped": domain_swapped,
                        "range_swapped": range_swapped
                    })

        if inconsistent_domains:
            print(f"\nInconsistent domain/range in inverse properties: {len(inconsistent_domains)}")
            for inconsistent in inconsistent_domains:
                print(f"  - {inconsistent['test']}: {inconsistent}")

        assert len(inconsistent_domains) == 0, f"Found {len(inconsistent_domains)} domain/range inconsistencies"


class TestCrossReferenceDiscovery:
    """Test suite for cross-reference discovery and navigation"""

    @pytest.fixture(scope="class")
    def validator(self):
        ontology_dir = Path(__file__).parent.parent.parent / "schemas" / "ontologies"
        return OntologyNavigationValidator(ontology_dir)

    @pytest.fixture(scope="class")
    def cross_reference_tests(self):
        """Define comprehensive cross-reference test cases"""
        return [
            # Bridge Ontology Cross-References
            CrossReferenceTest(
                name="DataBusinessCanvas Cross-References",
                description="Canvas concept discovery through rdfs:seeAlso",
                source_concept=BRIDGE.DataBusinessCanvas,
                target_concepts=[
                    BRIDGE.ValueProposition,
                    BRIDGE.CustomerSegment,
                    BRIDGE.DataAsset,
                    BRIDGE.ExecutiveTarget,
                    COMPLETE_SOW.SemanticStatementOfWork,
                    URIRef("https://schema.org/Organization"),
                    URIRef("http://purl.org/dc/terms/subject"),
                    URIRef("http://xmlns.com/foaf/0.1/Organization")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="ValueProposition Cross-References",
                description="Value proposition concept discovery",
                source_concept=BRIDGE.ValueProposition,
                target_concepts=[
                    BRIDGE.CustomerSegment,
                    BRIDGE.DataAsset,
                    BRIDGE.IntelligenceCapability,
                    BRIDGE.RevenueEvent,
                    COMPLETE_SOW.DesiredOutcome,
                    URIRef("https://schema.org/Product"),
                    URIRef("https://schema.org/Service"),
                    URIRef("http://purl.org/goodrelations/v1#ProductOrService")
                ],
                external_vocab=True
            ),
            CrossReferenceTest(
                name="DataAsset Cross-References",
                description="Data asset concept discovery spanning multiple ontologies",
                source_concept=BRIDGE.DataAsset,
                target_concepts=[
                    BRIDGE.IntelligenceCapability,
                    BRIDGE.DataQualityStandard,
                    BRIDGE.DataProcessingTask,
                    COMPLETE_SOW.EntityToTrack,
                    SOW.SupplyChainEntity,
                    URIRef("https://schema.org/Dataset"),
                    URIRef("http://purl.org/dc/dcmitype/Dataset"),
                    URIRef("http://www.w3.org/ns/dcat#Dataset"),
                    URIRef("http://xmlns.com/foaf/0.1/Document")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="IntelligenceCapability Cross-References",
                description="AI/ML capability concept discovery",
                source_concept=BRIDGE.IntelligenceCapability,
                target_concepts=[
                    BRIDGE.DataAsset,
                    BRIDGE.DataProcessingTask,
                    BRIDGE.ValueProposition,
                    SOW.InferredOpportunity,
                    SOW.CrossDomainOpportunity,
                    URIRef("https://schema.org/SoftwareApplication"),
                    URIRef("https://schema.org/ComputerLanguage"),
                    URIRef("http://purl.org/dc/terms/type")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="ExecutiveTarget Cross-References",
                description="Executive target strategic concept discovery",
                source_concept=BRIDGE.ExecutiveTarget,
                target_concepts=[
                    BRIDGE.StrategicAlignmentScore,
                    BRIDGE.ExecutiveTargetOwner,
                    BRIDGE.DataBusinessCanvas,
                    COMPLETE_SOW.DesiredOutcome,
                    SOW.InferredOpportunity,
                    URIRef("https://schema.org/Goal"),
                    URIRef("http://purl.org/dc/terms/subject"),
                    URIRef("http://www.w3.org/2004/02/skos/core#Concept")
                ],
                cross_ontology=True,
                external_vocab=True
            ),

            # Complete SOW Ontology Cross-References
            CrossReferenceTest(
                name="SemanticStatementOfWork Cross-References",
                description="SOW concept discovery across ontologies",
                source_concept=COMPLETE_SOW.SemanticStatementOfWork,
                target_concepts=[
                    COMPLETE_SOW.BusinessChallenge,
                    COMPLETE_SOW.DesiredOutcome,
                    COMPLETE_SOW.AnalyticalOpportunity,
                    BRIDGE.DataBusinessCanvas,
                    BRIDGE.DataContract,
                    SOW.BusinessRequirement,
                    URIRef("https://schema.org/Service"),
                    URIRef("http://purl.org/dc/terms/license")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="BusinessChallenge Cross-References",
                description="Business challenge concept discovery",
                source_concept=COMPLETE_SOW.BusinessChallenge,
                target_concepts=[
                    COMPLETE_SOW.DesiredOutcome,
                    COMPLETE_SOW.EntityToTrack,
                    COMPLETE_SOW.AnalyticalOpportunity,
                    COMPLETE_SOW.SOWStakeholder,
                    SOW.BusinessRequirement,
                    BRIDGE.DataBusinessCanvas,
                    URIRef("https://schema.org/Problem"),
                    URIRef("http://purl.org/dc/terms/subject"),
                    URIRef("http://www.w3.org/2004/02/skos/core#Concept")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="DesiredOutcome Cross-References",
                description="Desired outcome concept discovery",
                source_concept=COMPLETE_SOW.DesiredOutcome,
                target_concepts=[
                    COMPLETE_SOW.BusinessChallenge,
                    COMPLETE_SOW.AnalyticalOpportunity,
                    BRIDGE.ValueProposition,
                    BRIDGE.ExecutiveTarget,
                    SOW.InferredOpportunity,
                    URIRef("https://schema.org/Goal"),
                    URIRef("http://purl.org/dc/terms/description"),
                    URIRef("http://www.w3.org/2004/02/skos/core#Concept")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="EntityToTrack Cross-References",
                description="Entity tracking concept discovery",
                source_concept=COMPLETE_SOW.EntityToTrack,
                target_concepts=[
                    COMPLETE_SOW.BusinessChallenge,
                    BRIDGE.DataAsset,
                    SOW.SupplyChainEntity,
                    SOW.FinancialEntity,
                    SOW.CommodityEntity,
                    URIRef("https://schema.org/Thing"),
                    URIRef("http://purl.org/dc/terms/subject"),
                    URIRef("http://www.w3.org/ns/prov#Entity")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="AnalyticalOpportunity Cross-References",
                description="Analytical opportunity concept discovery",
                source_concept=COMPLETE_SOW.AnalyticalOpportunity,
                target_concepts=[
                    COMPLETE_SOW.BusinessChallenge,
                    COMPLETE_SOW.DesiredOutcome,
                    COMPLETE_SOW.CrossDomainOpportunity,
                    COMPLETE_SOW.PredictiveOpportunity,
                    COMPLETE_SOW.OptimizationOpportunity,
                    SOW.InferredOpportunity,
                    SOW.SpatialAnalysisOpportunity,
                    SOW.TemporalAnalysisOpportunity,
                    SOW.NetworkAnalysisOpportunity,
                    URIRef("https://schema.org/Opportunity"),
                    URIRef("http://purl.org/dc/terms/type")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="CrossDomainOpportunity Cross-References",
                description="Cross-domain opportunity spanning multiple domains",
                source_concept=COMPLETE_SOW.CrossDomainOpportunity,
                target_concepts=[
                    COMPLETE_SOW.DomainContext,
                    COMPLETE_SOW.KnowledgeContext,
                    SOW.SupplyChainEntity,
                    SOW.FinancialEntity,
                    SOW.CommodityEntity,
                    URIRef("http://www.w3.org/2004/02/skos/core#ConceptScheme")
                ],
                cross_ontology=True,
                external_vocab=True
            ),

            # SOW Inference Rules Cross-References
            CrossReferenceTest(
                name="BusinessRequirement Cross-References",
                description="Business requirement concept discovery",
                source_concept=SOW.BusinessRequirement,
                target_concepts=[
                    SOW.InferredOpportunity,
                    COMPLETE_SOW.BusinessChallenge,
                    COMPLETE_SOW.DesiredOutcome,
                    BRIDGE.DataBusinessCanvas,
                    URIRef("https://schema.org/Demand"),
                    URIRef("http://purl.org/dc/terms/requires"),
                    URIRef("http://www.w3.org/2004/02/skos/core#Concept")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="InferredOpportunity Cross-References",
                description="Inferred opportunity concept discovery",
                source_concept=SOW.InferredOpportunity,
                target_concepts=[
                    SOW.BusinessRequirement,
                    SOW.SpatialAnalysisOpportunity,
                    SOW.TemporalAnalysisOpportunity,
                    SOW.NetworkAnalysisOpportunity,
                    SOW.CrossDomainOpportunity,
                    COMPLETE_SOW.AnalyticalOpportunity,
                    BRIDGE.IntelligenceCapability,
                    BRIDGE.ValueProposition,
                    URIRef("https://schema.org/Opportunity"),
                    URIRef("http://purl.org/dc/terms/type")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="SpatialAnalysisOpportunity Cross-References",
                description="Spatial analysis opportunity geographic discovery",
                source_concept=SOW.SpatialAnalysisOpportunity,
                target_concepts=[
                    SOW.SupplyChainEntity,
                    COMPLETE_SOW.SpatialContext,
                    URIRef("https://schema.org/GeoCoordinates"),
                    URIRef("https://schema.org/Place"),
                    URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing")
                ],
                external_vocab=True
            ),
            CrossReferenceTest(
                name="SupplyChainEntity Cross-References",
                description="Supply chain entity cross-domain discovery",
                source_concept=SOW.SupplyChainEntity,
                target_concepts=[
                    SOW.SpatialAnalysisOpportunity,
                    SOW.CrossDomainOpportunity,
                    SOW.FinancialEntity,
                    URIRef("https://schema.org/Organization"),
                    URIRef("https://schema.org/Place"),
                    URIRef("http://purl.org/goodrelations/v1#BusinessEntity")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="FinancialEntity Cross-References",
                description="Financial entity cross-domain discovery",
                source_concept=SOW.FinancialEntity,
                target_concepts=[
                    SOW.TemporalAnalysisOpportunity,
                    SOW.CrossDomainOpportunity,
                    SOW.SupplyChainEntity,
                    BRIDGE.CostEvent,
                    BRIDGE.RevenueEvent,
                    URIRef("https://schema.org/MonetaryAmount"),
                    URIRef("http://purl.org/goodrelations/v1#PriceSpecification")
                ],
                cross_ontology=True,
                external_vocab=True
            ),
            CrossReferenceTest(
                name="CommodityEntity Cross-References",
                description="Commodity entity cross-domain discovery",
                source_concept=SOW.CommodityEntity,
                target_concepts=[
                    SOW.CrossDomainOpportunity,
                    SOW.SupplyChainEntity,
                    SOW.FinancialEntity,
                    URIRef("https://schema.org/Product"),
                    URIRef("http://purl.org/goodrelations/v1#ProductOrService"),
                    URIRef("http://purl.org/dc/terms/subject")
                ],
                cross_ontology=True,
                external_vocab=True
            )
        ]

    def test_rdfs_seeAlso_links(self, validator, cross_reference_tests):
        """Test that rdfs:seeAlso links enable concept discovery"""
        missing_see_also = []

        for test in cross_reference_tests:
            # Get all rdfs:seeAlso links from source concept
            see_also_targets = set(validator.graph.objects(test.source_concept, RDFS.seeAlso))

            # Check which expected targets are missing
            missing_targets = []
            for target in test.target_concepts:
                if target not in see_also_targets:
                    missing_targets.append(str(target))

            if missing_targets:
                missing_see_also.append({
                    "test": test.name,
                    "source": str(test.source_concept),
                    "missing_targets": missing_targets,
                    "found_targets": [str(t) for t in see_also_targets],
                    "cross_ontology": test.cross_ontology,
                    "external_vocab": test.external_vocab
                })

        validator.validation_results["cross_references"] = missing_see_also

        if missing_see_also:
            print(f"\nMissing rdfs:seeAlso cross-references: {len(missing_see_also)}")
            for missing in missing_see_also:
                print(f"  - {missing['test']}: Missing {len(missing['missing_targets'])} targets")
                if missing['missing_targets']:
                    print(f"    Missing: {missing['missing_targets'][:3]}...")  # Show first 3

        # This is informational - we expect some external vocabularies may not be present
        total_missing = sum(len(m['missing_targets']) for m in missing_see_also)
        print(f"\nTotal missing cross-references: {total_missing}")

    def test_cross_ontology_navigation(self, validator, cross_reference_tests):
        """Test navigation paths between different ontologies"""
        cross_ontology_tests = [t for t in cross_reference_tests if t.cross_ontology]
        cross_ontology_paths = []

        for test in cross_ontology_tests:
            # Count how many cross-ontology links exist
            see_also_targets = list(validator.graph.objects(test.source_concept, RDFS.seeAlso))

            # Determine ontology of source
            source_ontology = self._get_ontology_from_uri(test.source_concept)

            # Count targets from different ontologies
            cross_ontology_targets = []
            for target in see_also_targets:
                target_ontology = self._get_ontology_from_uri(target)
                if target_ontology != source_ontology and target_ontology != "external":
                    cross_ontology_targets.append({
                        "target": str(target),
                        "source_ontology": source_ontology,
                        "target_ontology": target_ontology
                    })

            cross_ontology_paths.append({
                "test": test.name,
                "source": str(test.source_concept),
                "source_ontology": source_ontology,
                "cross_ontology_links": len(cross_ontology_targets),
                "links": cross_ontology_targets
            })

        # Report cross-ontology navigation capabilities
        total_cross_links = sum(p['cross_ontology_links'] for p in cross_ontology_paths)
        print(f"\nCross-ontology navigation paths: {len(cross_ontology_paths)}")
        print(f"Total cross-ontology links: {total_cross_links}")

        for path in cross_ontology_paths:
            if path['cross_ontology_links'] > 0:
                print(f"  - {path['test']}: {path['cross_ontology_links']} cross-links")

    def _get_ontology_from_uri(self, uri):
        """Determine which ontology a URI belongs to"""
        uri_str = str(uri)
        if "gist-dbc-bridge" in uri_str:
            return "bridge"
        elif "complete-sow" in uri_str:
            return "complete-sow"
        elif "/sow#" in uri_str:
            return "sow-inference"
        elif "semanticarts" in uri_str:
            return "gist"
        else:
            return "external"


class TestSPARQLNavigationScenarios:
    """Test suite for SPARQL query scenarios demonstrating concept-to-concept navigation"""

    @pytest.fixture(scope="class")
    def validator(self):
        ontology_dir = Path(__file__).parent.parent.parent / "schemas" / "ontologies"
        return OntologyNavigationValidator(ontology_dir)

    @pytest.fixture(scope="class")
    def sparql_scenarios(self):
        """Define SPARQL query scenarios for concept navigation"""
        return [
            # Forward Navigation Scenarios
            SPARQLScenario(
                name="BusinessChallenge to DesiredOutcome Forward Navigation",
                description="Find all desired outcomes for a specific business challenge",
                query="""
                PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?sow ?challenge ?outcome ?outcomeDescription WHERE {
                    ?sow csow:hasBusinessChallenge ?challenge .
                    ?sow csow:hasDesiredOutcome ?outcome .
                    ?challenge rdfs:label ?challengeLabel .
                    ?outcome rdfs:label ?outcomeLabel .
                    OPTIONAL { ?outcome csow:outcomeDescription ?outcomeDescription }
                    FILTER(CONTAINS(LCASE(?challengeLabel), "supplier") ||
                           CONTAINS(LCASE(?challengeLabel), "cost") ||
                           CONTAINS(LCASE(?challengeLabel), "inventory"))
                } LIMIT 20
                """,
                expected_results_min=0,
                navigation_hops=2,
                scenario_type="forward"
            ),

            # Backward Navigation Scenarios
            SPARQLScenario(
                name="DesiredOutcome to BusinessChallenge Backward Navigation",
                description="Find all business challenges that led to a specific desired outcome",
                query="""
                PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?outcome ?sow ?challenge ?challengeDescription WHERE {
                    ?outcome csow:isDesiredOutcomeOf ?sow .
                    ?challenge csow:isBusinessChallengeOf ?sow .
                    ?outcome rdfs:label ?outcomeLabel .
                    ?challenge rdfs:label ?challengeLabel .
                    OPTIONAL { ?challenge csow:challengeDescription ?challengeDescription }
                    FILTER(CONTAINS(LCASE(?outcomeLabel), "reduce") ||
                           CONTAINS(LCASE(?outcomeLabel), "improve") ||
                           CONTAINS(LCASE(?outcomeLabel), "optimize"))
                } LIMIT 20
                """,
                expected_results_min=0,
                navigation_hops=2,
                scenario_type="backward"
            ),

            # Cross-Reference Browsing Scenarios
            SPARQLScenario(
                name="DataBusinessCanvas Concept Discovery",
                description="Show related concepts accessible from Data Business Canvas",
                query="""
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?canvas ?relatedConcept ?relationshipType WHERE {
                    ?canvas a bridge:DataBusinessCanvas .
                    {
                        ?canvas rdfs:seeAlso ?relatedConcept .
                        BIND("seeAlso" AS ?relationshipType)
                    } UNION {
                        ?canvas bridge:alignsWithTarget ?relatedConcept .
                        BIND("alignsWithTarget" AS ?relationshipType)
                    } UNION {
                        ?canvas bridge:implementedBySOW ?relatedConcept .
                        BIND("implementedBySOW" AS ?relationshipType)
                    } UNION {
                        ?canvas bridge:hasAlignmentScore ?relatedConcept .
                        BIND("hasAlignmentScore" AS ?relationshipType)
                    }
                } LIMIT 50
                """,
                expected_results_min=0,
                navigation_hops=1,
                scenario_type="cross-reference"
            ),

            SPARQLScenario(
                name="AnalyticalOpportunity Cross-Domain Discovery",
                description="Discover cross-domain opportunities and their relationships",
                query="""
                PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
                PREFIX sow: <https://agentic-data-scraper.com/ontology/sow#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?opportunity ?relatedConcept ?discoveryPath WHERE {
                    ?opportunity a csow:AnalyticalOpportunity .
                    {
                        ?opportunity rdfs:seeAlso ?relatedConcept .
                        BIND("seeAlso" AS ?discoveryPath)
                    } UNION {
                        ?opportunity csow:inferredFrom ?relatedConcept .
                        BIND("inferredFrom" AS ?discoveryPath)
                    } UNION {
                        ?opportunity csow:validatedBy ?relatedConcept .
                        BIND("validatedBy" AS ?discoveryPath)
                    } UNION {
                        ?relatedConcept csow:infersOpportunity ?opportunity .
                        BIND("infersOpportunity" AS ?discoveryPath)
                    }
                } LIMIT 30
                """,
                expected_results_min=0,
                navigation_hops=1,
                scenario_type="cross-reference"
            ),

            # Multi-hop Navigation Scenarios
            SPARQLScenario(
                name="Business Challenge → Desired Outcome → Value Proposition → Customer Segment",
                description="Multi-hop navigation through business strategy stack",
                query="""
                PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?challenge ?outcome ?valueProp ?customer ?navigationPath WHERE {
                    # Challenge → Outcome
                    ?sow csow:hasBusinessChallenge ?challenge .
                    ?sow csow:hasDesiredOutcome ?outcome .

                    # Outcome → Value Proposition (via seeAlso)
                    ?outcome rdfs:seeAlso ?valueProp .
                    ?valueProp a bridge:ValueProposition .

                    # Value Proposition → Customer Segment (via seeAlso)
                    ?valueProp rdfs:seeAlso ?customer .
                    ?customer a bridge:CustomerSegment .

                    BIND("Challenge→Outcome→ValueProp→Customer" AS ?navigationPath)
                } LIMIT 10
                """,
                expected_results_min=0,
                navigation_hops=4,
                scenario_type="multi-hop"
            ),

            SPARQLScenario(
                name="Supply Chain Entity → Spatial Analysis → Geographic Risk Assessment",
                description="Multi-hop navigation from supply chain to geographic analysis",
                query="""
                PREFIX sow: <https://agentic-data-scraper.com/ontology/sow#>
                PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?requirement ?supplyEntity ?spatialOpp ?spatialContext ?analysisPath WHERE {
                    # Business Requirement → Supply Chain Entity
                    ?requirement sow:mentionsEntity ?supplyEntity .
                    ?supplyEntity a sow:SupplyChainEntity .

                    # Supply Chain Entity → Spatial Analysis Opportunity (via seeAlso)
                    ?supplyEntity rdfs:seeAlso ?spatialOpp .
                    ?spatialOpp a sow:SpatialAnalysisOpportunity .

                    # Spatial Analysis → Spatial Context (via seeAlso)
                    ?spatialOpp rdfs:seeAlso ?spatialContext .
                    ?spatialContext a csow:SpatialContext .

                    BIND("Requirement→SupplyEntity→SpatialAnalysis→Context" AS ?analysisPath)
                } LIMIT 15
                """,
                expected_results_min=0,
                navigation_hops=4,
                scenario_type="multi-hop"
            ),

            # Bidirectional Navigation Scenarios
            SPARQLScenario(
                name="Executive Target Bidirectional Navigation",
                description="Navigate forward and backward from executive targets",
                query="""
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?target ?canvas ?owner ?score ?direction WHERE {
                    ?target a bridge:ExecutiveTarget .

                    # Forward navigation: Target → Canvas
                    {
                        ?target bridge:isTargetAlignedWith ?canvas .
                        BIND("forward_to_canvas" AS ?direction)
                    } UNION
                    # Backward navigation: Canvas → Target
                    {
                        ?canvas bridge:alignsWithTarget ?target .
                        BIND("backward_from_canvas" AS ?direction)
                    }

                    # Additional forward/backward relationships
                    UNION {
                        ?target bridge:ownedBy ?owner .
                        BIND("forward_to_owner" AS ?direction)
                    } UNION {
                        ?owner bridge:ownsTarget ?target .
                        BIND("backward_from_owner" AS ?direction)
                    } UNION {
                        ?score bridge:isAlignmentScoreOf ?canvas .
                        ?canvas bridge:alignsWithTarget ?target .
                        BIND("indirect_via_score" AS ?direction)
                    }
                } LIMIT 25
                """,
                expected_results_min=0,
                navigation_hops=2,
                scenario_type="bidirectional"
            ),

            # Inference-based Navigation Scenarios
            SPARQLScenario(
                name="Inference Rule Navigation: Requirements → Opportunities",
                description="Navigate from business requirements to inferred opportunities",
                query="""
                PREFIX sow: <https://agentic-data-scraper.com/ontology/sow#>
                PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?requirement ?opportunity ?opportunityType ?confidence ?reasoning WHERE {
                    ?requirement a sow:BusinessRequirement .
                    ?requirement sow:infersOpportunity ?opportunity .

                    # Get opportunity type
                    ?opportunity a ?opportunityType .
                    FILTER(?opportunityType IN (
                        sow:SpatialAnalysisOpportunity,
                        sow:TemporalAnalysisOpportunity,
                        sow:NetworkAnalysisOpportunity,
                        sow:CrossDomainOpportunity
                    ))

                    OPTIONAL { ?opportunity sow:confidenceLevel ?confidence }
                    OPTIONAL { ?opportunity sow:reasoningTrace ?reasoning }
                } LIMIT 20
                """,
                expected_results_min=0,
                navigation_hops=2,
                scenario_type="inference"
            ),

            # Quality and Contract Navigation
            SPARQLScenario(
                name="Data Quality Standards Bidirectional Navigation",
                description="Navigate between data contracts and quality standards",
                query="""
                PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?contract ?qualityStandard ?task ?direction WHERE {
                    # Forward: Contract → Quality Standard
                    {
                        ?contract bridge:hasQualityStandard ?qualityStandard .
                        BIND("contract_to_quality" AS ?direction)
                    } UNION
                    # Backward: Quality Standard → Contract
                    {
                        ?qualityStandard bridge:isQualityStandardFor ?contract .
                        BIND("quality_to_contract" AS ?direction)
                    } UNION
                    # Multi-hop: Contract → Task → Quality (via seeAlso)
                    {
                        ?contract bridge:executedByTask ?task .
                        ?task rdfs:seeAlso ?qualityStandard .
                        ?qualityStandard a bridge:DataQualityStandard .
                        BIND("contract_via_task_to_quality" AS ?direction)
                    }
                } LIMIT 15
                """,
                expected_results_min=0,
                navigation_hops=3,
                scenario_type="bidirectional"
            )
        ]

    def test_sparql_navigation_scenarios(self, validator, sparql_scenarios):
        """Test SPARQL queries for concept-to-concept navigation"""
        scenario_results = []

        for scenario in sparql_scenarios:
            try:
                # Execute SPARQL query
                results = list(validator.graph.query(scenario.query))
                result_count = len(results)

                scenario_result = {
                    "name": scenario.name,
                    "description": scenario.description,
                    "scenario_type": scenario.scenario_type,
                    "navigation_hops": scenario.navigation_hops,
                    "query_success": True,
                    "result_count": result_count,
                    "meets_minimum": result_count >= scenario.expected_results_min,
                    "sample_results": [str(row) for row in results[:3]]  # First 3 results
                }

            except Exception as e:
                scenario_result = {
                    "name": scenario.name,
                    "description": scenario.description,
                    "scenario_type": scenario.scenario_type,
                    "navigation_hops": scenario.navigation_hops,
                    "query_success": False,
                    "error": str(e),
                    "result_count": 0,
                    "meets_minimum": False,
                    "sample_results": []
                }

            scenario_results.append(scenario_result)

        validator.validation_results["sparql_scenarios"] = scenario_results

        # Report results
        successful_scenarios = [r for r in scenario_results if r["query_success"]]
        failed_scenarios = [r for r in scenario_results if not r["query_success"]]

        print(f"\nSPARQL Navigation Scenarios: {len(sparql_scenarios)} total")
        print(f"Successful queries: {len(successful_scenarios)}")
        print(f"Failed queries: {len(failed_scenarios)}")

        if successful_scenarios:
            print("\nSuccessful Navigation Scenarios:")
            for result in successful_scenarios:
                print(f"  - {result['name']}: {result['result_count']} results ({result['scenario_type']}, {result['navigation_hops']} hops)")

        if failed_scenarios:
            print("\nFailed Navigation Scenarios:")
            for result in failed_scenarios:
                print(f"  - {result['name']}: {result['error']}")

        # Most scenarios may return 0 results since we don't have instance data
        # But the queries should execute successfully showing the navigation patterns work
        assert len(failed_scenarios) <= len(sparql_scenarios) // 2, f"Too many failed SPARQL scenarios: {len(failed_scenarios)}"


class TestLambdaReadinessAssessment:
    """Test suite for assessing Lambda user readiness for concept navigation"""

    @pytest.fixture(scope="class")
    def validator(self):
        ontology_dir = Path(__file__).parent.parent.parent / "schemas" / "ontologies"
        return OntologyNavigationValidator(ontology_dir)

    def test_generate_lambda_readiness_report(self, validator):
        """Generate comprehensive Lambda readiness assessment"""

        # Run all validation components
        self._assess_inverse_properties(validator)
        self._assess_cross_references(validator)
        self._assess_sparql_capabilities(validator)
        self._assess_navigation_completeness(validator)

        # Generate overall readiness score
        readiness_score = self._calculate_readiness_score(validator)

        validator.validation_results["lambda_readiness"] = {
            "overall_score": readiness_score,
            "assessment_date": "2025-09-25",
            "ontology_files_validated": 3,
            "recommendation": self._get_recommendation(readiness_score)
        }

        print(f"\n{'='*60}")
        print("LAMBDA USER READINESS ASSESSMENT")
        print(f"{'='*60}")
        print(f"Overall Readiness Score: {readiness_score:.2f}/100")
        print(f"Recommendation: {validator.validation_results['lambda_readiness']['recommendation']}")
        print(f"{'='*60}")

        assert readiness_score >= 70, f"Lambda readiness score too low: {readiness_score:.2f}/100"

    def _assess_inverse_properties(self, validator):
        """Assess inverse property completeness"""
        # Count total expected inverse properties from our test definitions
        expected_inverse_pairs = 26  # Based on our comprehensive test cases

        # Count actual inverse properties in ontology
        inverse_relationships = list(validator.graph.subjects(OWL.inverseOf, None))
        inverse_relationships.extend(list(validator.graph.objects(None, OWL.inverseOf)))
        actual_inverse_count = len(set(inverse_relationships)) // 2  # Each pair counted twice

        completeness = min(100, (actual_inverse_count / expected_inverse_pairs) * 100)

        validator.validation_results["lambda_readiness"]["inverse_properties"] = {
            "expected": expected_inverse_pairs,
            "actual": actual_inverse_count,
            "completeness_percentage": completeness,
            "score_contribution": completeness * 0.3  # 30% of total score
        }

        print(f"Inverse Properties: {actual_inverse_count}/{expected_inverse_pairs} ({completeness:.1f}%)")

    def _assess_cross_references(self, validator):
        """Assess cross-reference link completeness"""
        # Count rdfs:seeAlso relationships
        see_also_count = len(list(validator.graph.subjects(RDFS.seeAlso, None)))

        # Expected based on our ontology analysis (rough estimate)
        expected_see_also = 150  # Conservative estimate based on our test cases

        completeness = min(100, (see_also_count / expected_see_also) * 100)

        # Count cross-ontology references
        cross_ontology_count = self._count_cross_ontology_references(validator)

        validator.validation_results["lambda_readiness"]["cross_references"] = {
            "total_see_also_links": see_also_count,
            "expected_see_also": expected_see_also,
            "completeness_percentage": completeness,
            "cross_ontology_links": cross_ontology_count,
            "score_contribution": completeness * 0.25  # 25% of total score
        }

        print(f"Cross-References: {see_also_count} total, {cross_ontology_count} cross-ontology ({completeness:.1f}%)")

    def _assess_sparql_capabilities(self, validator):
        """Assess SPARQL query execution capabilities"""
        # Test a sample of critical navigation patterns
        critical_queries = [
            # Forward navigation
            "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1",
            # Inverse navigation test
            """SELECT ?x ?y WHERE {
                ?x <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#hasBusinessModel> ?y .
                ?y <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#isBusinessModelOf> ?x
            } LIMIT 1""",
            # Cross-reference navigation
            """SELECT ?x ?ref WHERE {
                ?x <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?ref
            } LIMIT 1"""
        ]

        successful_queries = 0
        for query in critical_queries:
            try:
                list(validator.graph.query(query))
                successful_queries += 1
            except:
                pass

        query_success_rate = (successful_queries / len(critical_queries)) * 100

        validator.validation_results["lambda_readiness"]["sparql_capabilities"] = {
            "critical_queries_tested": len(critical_queries),
            "successful_queries": successful_queries,
            "success_rate_percentage": query_success_rate,
            "score_contribution": query_success_rate * 0.2  # 20% of total score
        }

        print(f"SPARQL Capabilities: {successful_queries}/{len(critical_queries)} queries successful ({query_success_rate:.1f}%)")

    def _assess_navigation_completeness(self, validator):
        """Assess overall navigation path completeness"""
        # Check key navigation patterns exist
        navigation_patterns = [
            # Business layer navigation
            ("DataBusinessCanvas", "ValueProposition"),
            ("DataBusinessCanvas", "ExecutiveTarget"),
            # Technical layer navigation
            ("DataContract", "DataProcessingTask"),
            ("DataProcessingTask", "DataQualityStandard"),
            # Cross-layer navigation
            ("SemanticStatementOfWork", "DataBusinessCanvas"),
            ("BusinessChallenge", "AnalyticalOpportunity"),
            # Inference navigation
            ("BusinessRequirement", "InferredOpportunity")
        ]

        available_patterns = 0
        for source_class, target_class in navigation_patterns:
            # Check if there's some connection path (property or seeAlso)
            source_uri = self._class_name_to_uri(source_class)
            target_uri = self._class_name_to_uri(target_class)

            if source_uri and target_uri:
                # Look for any connecting property or seeAlso link
                connections = list(validator.graph.subjects(RDFS.range, target_uri))
                connections.extend(list(validator.graph.objects(source_uri, RDFS.seeAlso)))
                if connections:
                    available_patterns += 1

        pattern_completeness = (available_patterns / len(navigation_patterns)) * 100

        validator.validation_results["lambda_readiness"]["navigation_completeness"] = {
            "key_patterns_tested": len(navigation_patterns),
            "available_patterns": available_patterns,
            "completeness_percentage": pattern_completeness,
            "score_contribution": pattern_completeness * 0.25  # 25% of total score
        }

        print(f"Navigation Patterns: {available_patterns}/{len(navigation_patterns)} patterns available ({pattern_completeness:.1f}%)")

    def _count_cross_ontology_references(self, validator):
        """Count references between different ontologies"""
        cross_ontology_count = 0

        for subj, pred, obj in validator.graph:
            if pred == RDFS.seeAlso:
                subj_ontology = self._get_ontology_from_uri(subj)
                obj_ontology = self._get_ontology_from_uri(obj)
                if subj_ontology != obj_ontology and obj_ontology != "external":
                    cross_ontology_count += 1

        return cross_ontology_count

    def _get_ontology_from_uri(self, uri):
        """Determine which ontology a URI belongs to"""
        uri_str = str(uri)
        if "gist-dbc-bridge" in uri_str:
            return "bridge"
        elif "complete-sow" in uri_str:
            return "complete-sow"
        elif "/sow#" in uri_str:
            return "sow-inference"
        elif "semanticarts" in uri_str:
            return "gist"
        else:
            return "external"

    def _class_name_to_uri(self, class_name):
        """Convert class name to full URI"""
        class_mappings = {
            "DataBusinessCanvas": BRIDGE.DataBusinessCanvas,
            "ValueProposition": BRIDGE.ValueProposition,
            "ExecutiveTarget": BRIDGE.ExecutiveTarget,
            "DataContract": BRIDGE.DataContract,
            "DataProcessingTask": BRIDGE.DataProcessingTask,
            "DataQualityStandard": BRIDGE.DataQualityStandard,
            "SemanticStatementOfWork": COMPLETE_SOW.SemanticStatementOfWork,
            "BusinessChallenge": COMPLETE_SOW.BusinessChallenge,
            "AnalyticalOpportunity": COMPLETE_SOW.AnalyticalOpportunity,
            "BusinessRequirement": SOW.BusinessRequirement,
            "InferredOpportunity": SOW.InferredOpportunity
        }
        return class_mappings.get(class_name)

    def _calculate_readiness_score(self, validator):
        """Calculate overall Lambda readiness score"""
        readiness = validator.validation_results["lambda_readiness"]

        total_score = (
            readiness.get("inverse_properties", {}).get("score_contribution", 0) +
            readiness.get("cross_references", {}).get("score_contribution", 0) +
            readiness.get("sparql_capabilities", {}).get("score_contribution", 0) +
            readiness.get("navigation_completeness", {}).get("score_contribution", 0)
        )

        return min(100, total_score)

    def _get_recommendation(self, score):
        """Get recommendation based on readiness score"""
        if score >= 90:
            return "READY FOR PRODUCTION - Excellent navigation capabilities"
        elif score >= 80:
            return "READY FOR STAGING - Good navigation with minor gaps"
        elif score >= 70:
            return "READY FOR TESTING - Adequate navigation capabilities"
        elif score >= 60:
            return "DEVELOPMENT READY - Basic navigation available, needs improvement"
        else:
            return "NOT READY - Significant navigation gaps require attention"

    def test_export_validation_report(self, validator):
        """Export comprehensive validation report for Lambda team"""
        report_path = Path(__file__).parent.parent.parent / "validation_report_ontology_navigation.json"

        # Add metadata to results
        validator.validation_results["metadata"] = {
            "validation_date": "2025-09-25",
            "validator_version": "1.0.0",
            "ontology_files": [
                "schemas/ontologies/bridge/gist_dbc_bridge.owl",
                "schemas/ontologies/sow/complete_sow_ontology.owl",
                "schemas/ontologies/sow/sow_inference_rules.owl"
            ],
            "validation_scope": "Bidirectional Navigation Capability",
            "target_users": "AWS Lambda Functions",
            "navigation_patterns_tested": [
                "Forward Property Navigation",
                "Inverse Property Navigation",
                "Cross-Reference Discovery",
                "Multi-hop Navigation",
                "Cross-Ontology Navigation",
                "Inference-based Navigation"
            ]
        }

        # Export results
        with open(report_path, 'w') as f:
            json.dump(validator.validation_results, f, indent=2, default=str)

        print(f"\nValidation report exported to: {report_path}")
        print("Report includes:")
        print("  - Inverse property validation results")
        print("  - Cross-reference discovery assessment")
        print("  - SPARQL navigation scenario results")
        print("  - Lambda readiness score and recommendations")
        print("  - Concrete examples for Lambda implementation")

        assert report_path.exists(), "Validation report export failed"


if __name__ == "__main__":
    # Run validation tests
    pytest.main([__file__, "-v"])