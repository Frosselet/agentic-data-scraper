// ET(K)L Guru Agent - Master Supervisor for ET(K)L Vision Consistency
// Ensures all work streams align with Enterprise Transformation through Knowledge-driven Layers

class ETKLVisionAssessment {
  overall_alignment_score float // 0-10 score
  theoretical_consistency float // Theory alignment
  technical_implementation float // Code/ontology alignment
  narrative_coherence float // Documentation alignment
  governance_compliance float // ADR alignment
  critical_gaps string[]
  misalignment_risks string[]
  recommended_actions string[]
}

class ETKLPrincipleViolation {
  principle_violated string
  severity string // "critical", "major", "minor"
  location string // file/section where violation occurs
  description string
  business_impact string
  corrective_action string
  priority int // 1-5 scale
}

class ETKLManifestoCompliance {
  manifesto_section string
  compliance_level string // "excellent", "good", "partial", "poor", "missing"
  evidence string[]
  gaps string[]
  recommendations string[]
}

class ETKLWorkStreamAnalysis {
  work_stream string // "theory", "technical", "narrative", "governance"
  current_state string
  target_state string
  alignment_score float
  key_deliverables string[]
  dependencies string[]
  risks string[]
  next_actions string[]
}

class ETKLCoordinationPlan {
  coordination_strategy string
  work_stream_priorities string[]
  critical_dependencies string[]
  synchronization_points string[]
  quality_gates string[]
  escalation_triggers string[]
  success_metrics string[]
}

// Main ET(K)L Guru Supervision Function
function ETKLGuruAgent(
  project_artifacts: string, // All code, docs, ADRs, articles
  current_work_context: string,
  proposed_changes: string
) -> ETKLVisionAssessment {
  client GPT4
  prompt #"
    You are the ET(K)L Guru - the master supervisor ensuring absolute consistency
    across all aspects of the Enterprise Transformation through Knowledge-driven Layers vision.

    THE ET(K)L VISION CORE PRINCIPLES:

    1. **BUSINESS-FIRST APPROACH**:
       - Data pipelines START with business strategy, not technical requirements
       - Every data product must be supported by explicit business plan
       - Enterprise targets → Business Canvas → SOW → Data Contracts (governance chain)

    2. **SEMANTIC KNOWLEDGE FOUNDATION**:
       - All business relationships formally captured in semantic knowledge graphs
       - Ontologies make pre-development actions explicit and linkable
       - Metadata management starts with PURPOSE, not just technical schema

    3. **FORMAL GOVERNANCE CHAIN**:
       - Executive Targets ↔ Business Canvas ↔ SOW ↔ Data Contract
       - Each layer semantically linked through ontologies
       - Governance is projection of business intent, not afterthought

    4. **AGENTIC AUTOMATION**:
       - Multi-agent BAML platform automates governance enforcement
       - AI agents understand business context through semantic graphs
       - Automation serves business intent, not just technical efficiency

    5. **VALUE PROVABILITY**:
       - Data product value is NOT interpretation - it's formal chain of facts
       - Business value traceable through semantic knowledge graph
       - Clear linkage from technical implementation to business outcomes

    ANALYZE PROJECT ARTIFACTS:
    {{ project_artifacts }}

    CURRENT WORK CONTEXT:
    {{ current_work_context }}

    PROPOSED CHANGES:
    {{ proposed_changes }}

    ASSESS AGAINST ET(K)L PRINCIPLES:

    1. **Theoretical Consistency**:
       - Does work align with ET(K)L manifesto?
       - Are business-first principles respected?
       - Is semantic foundation maintained?

    2. **Technical Implementation**:
       - Do ontologies support the governance chain?
       - Are BAML agents aligned with business context?
       - Does code enforce business intent?

    3. **Narrative Coherence**:
       - Do articles/docs tell consistent ET(K)L story?
       - Is business-first approach clearly communicated?
       - Are technical details supporting business vision?

    4. **Governance Compliance**:
       - Do ADRs align with ET(K)L principles?
       - Is formal governance chain maintained?
       - Are decision patterns consistent?

    IDENTIFY CRITICAL ISSUES:
    - Principle violations that undermine ET(K)L vision
    - Work stream misalignments
    - Missing critical components
    - Inconsistencies across theory/implementation/narrative

    PROVIDE SUPERVISION GUIDANCE:
    - Specific corrective actions
    - Priority-ordered recommendations
    - Risk mitigation strategies
    - Success validation criteria

    Remember: ET(K)L is about transforming how enterprises approach data -
    making business intent explicit, formal, and automatically enforceable.
    Every piece of work must advance this vision consistently.
  "#
}

// ET(K)L Principle Validator
function ValidateETKLPrinciples(
  work_item: string,
  work_type: string // "code", "documentation", "adr", "article", "ontology"
) -> ETKLPrincipleViolation[] {
  client GPT4
  prompt #"
    Validate this work item against core ET(K)L principles:

    WORK ITEM: {{ work_item }}
    WORK TYPE: {{ work_type }}

    Check for violations of:
    1. Business-first approach (tech serving business, not driving it)
    2. Semantic knowledge foundation (formal relationships)
    3. Governance chain integrity (targets→canvas→sow→contracts)
    4. Agentic automation alignment (AI understanding business context)
    5. Value provability (formal business value chain)

    Flag any deviations that could undermine the ET(K)L vision.
  "#
}

// Work Stream Coordination Analyzer
function AnalyzeWorkStreamCoordination(
  theory_artifacts: string,
  technical_artifacts: string,
  narrative_artifacts: string,
  governance_artifacts: string
) -> ETKLWorkStreamAnalysis[] {
  client GPT4
  prompt #"
    Analyze coordination across all ET(K)L work streams:

    THEORY: {{ theory_artifacts }}
    TECHNICAL: {{ technical_artifacts }}
    NARRATIVE: {{ narrative_artifacts }}
    GOVERNANCE: {{ governance_artifacts }}

    Assess:
    1. Cross-stream consistency
    2. Missing linkages
    3. Conflicting directions
    4. Coordination gaps
    5. Synchronization needs

    Focus on ensuring unified ET(K)L vision delivery.
  "#
}

// ET(K)L Manifesto Compliance Checker
function CheckManifestoCompliance(
  work_artifacts: string,
  manifesto_sections: string[]
) -> ETKLManifestoCompliance[] {
  client GPT4
  prompt #"
    Check compliance with ET(K)L Manifesto sections:

    WORK ARTIFACTS: {{ work_artifacts }}
    MANIFESTO SECTIONS: {{ manifesto_sections }}

    For each manifesto section, assess:
    - How well work artifacts support the principle
    - Evidence of compliance
    - Gaps or violations
    - Recommendations for improvement

    Ensure work advances ET(K)L vision consistently.
  "#
}