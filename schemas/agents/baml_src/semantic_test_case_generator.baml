// ET(K)L Semantic Test Case Generator Agent
// Specialized for creating ontology-compliant data instances that match our SOW framework

class SemanticTestCase {
  use_case_name string
  ontology_alignment_score float // 0-10 score
  class_instances OntologyInstance[]
  property_mappings PropertyMapping[]
  sparql_queries string[]
  validation_results ValidationResult[]
  compliance_issues string[]
  recommendations string[]
}

class OntologyInstance {
  class_uri string // e.g., "sow:SemanticStatementOfWork"
  instance_uri string // e.g., "ex:EuroEnergySOW"
  instance_label string
  required_properties string[]
  optional_properties string[]
  property_values PropertyValue[]
  inheritance_chain string[] // Parent classes this inherits from
}

class PropertyMapping {
  property_uri string // e.g., "sow:hasSpatialContext"
  source_class string
  target_class string
  cardinality string // "1..1", "0..*", etc.
  data_type string // "URI", "Literal", "Date", etc.
  example_value string
  validation_constraint string
}

class PropertyValue {
  property_uri string
  value string
  value_type string // "URI", "Literal", "TypedLiteral"
  is_required bool
  validation_status string // "valid", "invalid", "missing"
}

class ValidationResult {
  validation_type string // "ontology_compliance", "property_constraints", "cardinality_check"
  status string // "pass", "fail", "warning"
  message string
  affected_instances string[]
  suggested_fix string
}

class SOWContextFramework {
  spatial_context OntologyInstance
  temporal_context OntologyInstance
  domain_context OntologyInstance
  knowledge_context OntologyInstance
  cross_context_relationships PropertyMapping[]
}

// Main Semantic Test Case Generator Function
function GenerateSemanticTestCase(
  ontology_files: string[], // Paths to OWL ontology files
  use_case_description: string,
  target_classes: string[], // Classes to instantiate
  business_context: string
) -> SemanticTestCase {
  client GPT4
  prompt #"
    You are a specialized ET(K)L Semantic Test Case Generator. Your mission is to create
    ontology-compliant data instances that properly demonstrate the coexistence of
    data models and data instances in knowledge graphs.

    ONTOLOGY FILES PROVIDED:
    {{ ontology_files }}

    USE CASE TO MODEL:
    {{ use_case_description }}

    TARGET CLASSES TO INSTANTIATE:
    {{ target_classes }}

    BUSINESS CONTEXT:
    {{ business_context }}

    SEMANTIC MODELING REQUIREMENTS:

    1. **ONTOLOGY COMPLIANCE**:
       - Every instance MUST use classes defined in the provided ontologies
       - All properties MUST be declared in the ontology with correct domains/ranges
       - Inheritance hierarchies MUST be respected (if A subClassOf B, instance must have B's properties)
       - Cardinality constraints MUST be satisfied

    2. **SOW FRAMEWORK ALIGNMENT**:
       - Use SemanticStatementOfWork as root container class
       - Implement 4D Context Framework: SpatialContext, TemporalContext, DomainContext, KnowledgeContext
       - Connect BusinessChallenge → DesiredOutcome → EntityToTrack semantic chain
       - Include SOWStakeholder instances with proper roles

    3. **PROPERTY CHAIN VALIDATION**:
       - Check that all hasX properties point to instances of correct classes
       - Verify inverse properties are consistent
       - Ensure functional properties have exactly one value
       - Validate datatype properties against XSD types

    4. **REALISTIC BUSINESS DATA**:
       - Use actual business terminology and realistic values
       - Create instances that would make sense to domain experts
       - Include proper labels, descriptions, and identifiers
       - Connect to real-world business concepts

    5. **INFERENCE READINESS**:
       - Structure data to enable SPARQL reasoning
       - Include enough detail for AnalyticalOpportunity inference
       - Create cross-domain relationships that demonstrate knowledge connections
       - Support formal governance chain queries

    GENERATE:
    1. Complete set of ontology-compliant instances
    2. All required and recommended properties
    3. Proper URI schemes and namespaces
    4. SPARQL queries to validate the instances
    5. Validation results showing compliance
    6. Specific recommendations for any issues

    VALIDATION CHECKS TO PERFORM:
    - Class instantiation correctness
    - Property domain/range compliance
    - Cardinality constraint satisfaction
    - Data type validation
    - Inheritance completeness
    - Cross-reference consistency

    Focus on creating a WORKING semantic test case that demonstrates
    proper ontology usage and enables successful knowledge graph operations.
  "#
}

// Ontology Compliance Validator
function ValidateOntologyCompliance(
  test_case: SemanticTestCase,
  ontology_constraints: string
) -> ValidationResult[] {
  client GPT4
  prompt #"
    Validate this semantic test case against ontology constraints:

    TEST CASE: {{ test_case }}
    ONTOLOGY CONSTRAINTS: {{ ontology_constraints }}

    Perform comprehensive validation:
    1. Class instantiation validation
    2. Property domain/range checking
    3. Cardinality constraint verification
    4. Data type compliance
    5. Inheritance hierarchy completeness

    Identify specific violations and provide actionable fixes.
  "#
}

// SOW Context Framework Generator
function GenerateSOWContextFramework(
  business_scenario: string,
  spatial_scope: string,
  temporal_scope: string,
  domain_focus: string
) -> SOWContextFramework {
  client GPT4
  prompt #"
    Generate a complete 4D Context Framework for SOW semantic modeling:

    BUSINESS SCENARIO: {{ business_scenario }}
    SPATIAL SCOPE: {{ spatial_scope }}
    TEMPORAL SCOPE: {{ temporal_scope }}
    DOMAIN FOCUS: {{ domain_focus }}

    Create ontology-compliant instances for:
    1. SpatialContext - with proper geographic and jurisdictional scope
    2. TemporalContext - with realistic timeframes and business cycles
    3. DomainContext - with cross-domain connections and boundaries
    4. KnowledgeContext - with implicit knowledge and learning opportunities

    Ensure all contexts properly link to create semantic reasoning opportunities.
  "#
}

// Business-Ontology Alignment Checker
function CheckBusinessOntologyAlignment(
  business_requirements: string,
  ontology_model: string,
  proposed_instances: OntologyInstance[]
) -> SemanticTestCase {
  client GPT4
  prompt #"
    Check alignment between business requirements and ontology modeling:

    BUSINESS REQUIREMENTS: {{ business_requirements }}
    ONTOLOGY MODEL: {{ ontology_model }}
    PROPOSED INSTANCES: {{ proposed_instances }}

    Verify:
    1. All business concepts are properly represented in ontology
    2. Business relationships map to semantic properties
    3. Business constraints translate to ontology restrictions
    4. Business outcomes can be formally queried and validated

    Identify gaps and provide specific modeling recommendations.
  "#
}