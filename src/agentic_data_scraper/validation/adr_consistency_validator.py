"""
ADR Consistency Validator

Ensures ongoing consistency across all Architecture Decision Records (ADRs)
with automated validation rules and continuous monitoring capabilities.

Key ADR Dependencies:
- ADR-004: Semantic SOW Data Contracts
- ADR-005: Spatio-Temporal SOW Architecture  
- ADR-011: Business Model Canvas Integration
- ADR-012: Data Business Canvas with SKOS

Validates semantic consistency, technical alignment, and business coherence
across all architectural layers to prevent drift and conflicts.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class ADRValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"      # Blocks deployment
    WARNING = "warning"        # Should be addressed
    INFO = "info"             # Informational
    SUGGESTION = "suggestion"  # Optimization opportunity


class ADRValidationScope(Enum):
    """Validation scope types"""
    SEMANTIC_CONSISTENCY = "semantic_consistency"
    TECHNICAL_ALIGNMENT = "technical_alignment" 
    BUSINESS_COHERENCE = "business_coherence"
    PERFORMANCE_IMPACT = "performance_impact"
    INTEGRATION_HEALTH = "integration_health"


@dataclass
class ValidationResult:
    """Individual validation check result"""
    check_id: str
    adr_scope: List[str]  # Which ADRs are involved
    validation_scope: ADRValidationScope
    level: ADRValidationLevel
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ADRConsistencyReport:
    """Complete ADR consistency validation report"""
    validation_id: str
    timestamp: datetime
    overall_score: float  # 0.0 to 1.0
    critical_issues: int
    warning_issues: int
    info_issues: int
    results: List[ValidationResult]
    recommendations: List[str]
    next_validation: datetime
    
    @property
    def is_deployment_ready(self) -> bool:
        """Check if system passes all critical validations"""
        return self.critical_issues == 0
    
    @property 
    def health_status(self) -> str:
        """Overall health status based on validation results"""
        if self.critical_issues > 0:
            return "CRITICAL"
        elif self.warning_issues > 5:
            return "DEGRADED" 
        elif self.warning_issues > 0:
            return "WARNING"
        else:
            return "HEALTHY"


class ADRConsistencyValidator:
    """
    Validates consistency across all ADR implementations
    Prevents architectural drift and integration conflicts
    """
    
    def __init__(self, sow_manager=None, kuzu_manager=None, skos_router=None, 
                 canvas_bridge=None, fuseki_client=None):
        """
        Initialize validator with access to all ADR components
        
        Args:
            sow_manager: SOW contract manager (ADR-004)
            kuzu_manager: KuzuDB manager (ADR-005) 
            skos_router: SKOS semantic router (ADR-012)
            canvas_bridge: Business-technical bridge (ADR-012)
            fuseki_client: Apache Jena Fuseki client (ADR-012)
        """
        self.sow_manager = sow_manager
        self.kuzu_manager = kuzu_manager
        self.skos_router = skos_router
        self.canvas_bridge = canvas_bridge
        self.fuseki_client = fuseki_client
        
        # Validation rule registry
        self.validation_rules = self._initialize_validation_rules()
        
    def validate_adr_consistency(self, scope: List[ADRValidationScope] = None) -> ADRConsistencyReport:
        """
        Perform comprehensive ADR consistency validation
        
        Args:
            scope: Optional list of validation scopes to check
            
        Returns:
            Complete consistency validation report
        """
        
        if scope is None:
            scope = list(ADRValidationScope)
            
        validation_id = f"ADR_VALIDATION_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting ADR consistency validation: {validation_id}")
        
        all_results = []
        
        try:
            # Run validation checks by scope
            for validation_scope in scope:
                scope_results = self._run_validation_scope(validation_scope)
                all_results.extend(scope_results)
            
            # Analyze results and generate report
            report = self._generate_consistency_report(validation_id, all_results)
            
            logger.info(f"ADR validation completed: {report.health_status} status with {report.critical_issues} critical issues")
            
            return report
            
        except Exception as e:
            logger.error(f"ADR validation failed: {e}")
            # Return error report
            return ADRConsistencyReport(
                validation_id=validation_id,
                timestamp=datetime.utcnow(),
                overall_score=0.0,
                critical_issues=1,
                warning_issues=0,
                info_issues=0,
                results=[ValidationResult(
                    check_id="validation_error",
                    adr_scope=["ALL"],
                    validation_scope=ADRValidationScope.INTEGRATION_HEALTH,
                    level=ADRValidationLevel.CRITICAL,
                    passed=False,
                    message=f"Validation system failure: {str(e)}"
                )],
                recommendations=["Fix validation system before deployment"],
                next_validation=datetime.utcnow()
            )
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive validation rule registry"""
        
        return {
            # ADR-004 + ADR-005 Integration Rules
            "sow_kuzu_schema_alignment": {
                "description": "Validate SOW contracts align with KuzuDB schema",
                "scope": ADRValidationScope.TECHNICAL_ALIGNMENT,
                "adrs": ["ADR-004", "ADR-005"],
                "level": ADRValidationLevel.CRITICAL,
                "validator": self._validate_sow_kuzu_alignment
            },
            
            # ADR-004 + ADR-012 Integration Rules  
            "sow_canvas_semantic_consistency": {
                "description": "Validate SOW contracts match canvas semantic mappings",
                "scope": ADRValidationScope.SEMANTIC_CONSISTENCY,
                "adrs": ["ADR-004", "ADR-012"], 
                "level": ADRValidationLevel.CRITICAL,
                "validator": self._validate_sow_canvas_semantics
            },
            
            # ADR-005 + ADR-012 Integration Rules
            "kuzu_canvas_spatial_consistency": {
                "description": "Validate KuzuDB spatial schema supports canvas geography",
                "scope": ADRValidationScope.TECHNICAL_ALIGNMENT,
                "adrs": ["ADR-005", "ADR-012"],
                "level": ADRValidationLevel.WARNING,
                "validator": self._validate_kuzu_canvas_spatial
            },
            
            # ADR-012 SKOS Integration Rules
            "skos_concept_resolvability": {
                "description": "Validate all SKOS concept URIs are resolvable",
                "scope": ADRValidationScope.SEMANTIC_CONSISTENCY,
                "adrs": ["ADR-012"],
                "level": ADRValidationLevel.CRITICAL,
                "validator": self._validate_skos_concept_resolution
            },
            
            "skos_multilingual_completeness": {
                "description": "Validate SKOS multilingual coverage for business domains",
                "scope": ADRValidationScope.BUSINESS_COHERENCE,
                "adrs": ["ADR-012"],
                "level": ADRValidationLevel.WARNING,
                "validator": self._validate_skos_multilingual_coverage
            },
            
            # Cross-ADR Performance Rules
            "integration_performance_impact": {
                "description": "Validate ADR integrations maintain performance requirements",
                "scope": ADRValidationScope.PERFORMANCE_IMPACT,
                "adrs": ["ADR-004", "ADR-005", "ADR-012"],
                "level": ADRValidationLevel.WARNING,
                "validator": self._validate_integration_performance
            },
            
            # Business Model Consistency Rules  
            "canvas_business_model_alignment": {
                "description": "Validate Data Business Canvas aligns with BMC principles",
                "scope": ADRValidationScope.BUSINESS_COHERENCE,
                "adrs": ["ADR-011", "ADR-012"],
                "level": ADRValidationLevel.WARNING,
                "validator": self._validate_canvas_bmc_alignment
            },
            
            # Ontology Consistency Rules
            "ontology_namespace_consistency": {
                "description": "Validate ontology namespaces are consistent across ADRs",
                "scope": ADRValidationScope.SEMANTIC_CONSISTENCY,
                "adrs": ["ADR-004", "ADR-012"],
                "level": ADRValidationLevel.CRITICAL,
                "validator": self._validate_ontology_namespaces
            }
        }
    
    def _run_validation_scope(self, scope: ADRValidationScope) -> List[ValidationResult]:
        """Run all validation rules for a specific scope"""
        
        scope_results = []
        
        for rule_id, rule_config in self.validation_rules.items():
            if rule_config["scope"] == scope:
                try:
                    result = rule_config["validator"](rule_id, rule_config)
                    scope_results.append(result)
                except Exception as e:
                    # Create error result for failed validation
                    error_result = ValidationResult(
                        check_id=f"{rule_id}_error",
                        adr_scope=rule_config["adrs"],
                        validation_scope=scope,
                        level=ADRValidationLevel.CRITICAL,
                        passed=False,
                        message=f"Validation rule failed: {str(e)}",
                        details={"error_type": type(e).__name__, "rule_id": rule_id}
                    )
                    scope_results.append(error_result)
                    logger.error(f"Validation rule {rule_id} failed: {e}")
        
        return scope_results
    
    def _validate_sow_kuzu_alignment(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate SOW contracts align with KuzuDB schema"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"],
            level=rule_config["level"],
            passed=True,
            message="SOW-KuzuDB schema alignment validated"
        )
        
        issues = []
        
        if self.sow_manager and self.kuzu_manager:
            try:
                # Check that all SOW data contracts have corresponding KuzuDB tables
                sow_contracts = self._get_active_sow_contracts()
                kuzu_tables = self._get_kuzu_table_schemas()
                
                for contract in sow_contracts:
                    contract_id = contract.get("contract_id")
                    expected_table = f"SOW_{contract_id}"
                    
                    if expected_table not in kuzu_tables:
                        issues.append(f"Missing KuzuDB table for SOW contract {contract_id}")
                        result.affected_components.append(contract_id)
                    else:
                        # Validate schema compatibility
                        schema_issues = self._validate_contract_table_schema(contract, kuzu_tables[expected_table])
                        issues.extend(schema_issues)
                
                result.details = {
                    "sow_contracts_checked": len(sow_contracts),
                    "kuzu_tables_found": len(kuzu_tables),
                    "schema_mismatches": len(issues)
                }
                
            except Exception as e:
                issues.append(f"Failed to validate SOW-KuzuDB alignment: {str(e)}")
        else:
            issues.append("SOW manager or KuzuDB manager not available")
        
        if issues:
            result.passed = False
            result.message = f"SOW-KuzuDB alignment issues found: {len(issues)} problems"
            result.recommendations = [
                "Update KuzuDB schema to match SOW contracts",
                "Regenerate missing tables for SOW contracts",
                "Review schema compatibility requirements"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _validate_sow_canvas_semantics(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate SOW contracts match canvas semantic mappings"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"], 
            level=rule_config["level"],
            passed=True,
            message="SOW-Canvas semantic consistency validated"
        )
        
        issues = []
        
        if self.sow_manager and self.canvas_bridge:
            try:
                # Get active canvases and their SOW contracts
                active_canvases = self._get_active_business_canvases()
                
                for canvas in active_canvases:
                    canvas_contracts = self._get_canvas_sow_contracts(canvas["canvas_id"])
                    
                    # Validate semantic consistency
                    for contract in canvas_contracts:
                        semantic_issues = self._check_contract_canvas_semantics(contract, canvas)
                        if semantic_issues:
                            issues.extend(semantic_issues)
                            result.affected_components.append(canvas["canvas_id"])
                
                result.details = {
                    "canvases_checked": len(active_canvases),
                    "semantic_mismatches": len(issues)
                }
                
            except Exception as e:
                issues.append(f"Failed to validate SOW-Canvas semantics: {str(e)}")
        else:
            issues.append("SOW manager or Canvas bridge not available")
        
        if issues:
            result.passed = False
            result.message = f"SOW-Canvas semantic issues found: {len(issues)} problems"
            result.recommendations = [
                "Align concept URIs between SOW contracts and canvas components",
                "Update semantic mappings for consistency",
                "Review ontology namespace usage"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _validate_kuzu_canvas_spatial(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate KuzuDB spatial schema supports canvas geography"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"],
            level=rule_config["level"], 
            passed=True,
            message="KuzuDB-Canvas spatial consistency validated"
        )
        
        issues = []
        
        if self.kuzu_manager and self.canvas_bridge:
            try:
                # Check spatial capabilities
                spatial_canvases = self._get_canvases_with_spatial_context()
                kuzu_spatial_support = self._check_kuzu_spatial_capabilities()
                
                if spatial_canvases and not kuzu_spatial_support["enabled"]:
                    issues.append("Canvas requires spatial support but KuzuDB spatial extensions not enabled")
                
                for canvas in spatial_canvases:
                    spatial_requirements = canvas.get("spatial_context", {})
                    supported = self._validate_spatial_requirements_support(spatial_requirements, kuzu_spatial_support)
                    
                    if not supported["fully_supported"]:
                        issues.extend(supported["missing_capabilities"])
                        result.affected_components.append(canvas["canvas_id"])
                
                result.details = {
                    "spatial_canvases": len(spatial_canvases),
                    "kuzu_spatial_enabled": kuzu_spatial_support["enabled"],
                    "unsupported_features": len(issues)
                }
                
            except Exception as e:
                issues.append(f"Failed to validate KuzuDB-Canvas spatial: {str(e)}")
        else:
            issues.append("KuzuDB manager or Canvas bridge not available")
        
        if issues:
            result.passed = False
            result.message = f"KuzuDB-Canvas spatial issues: {len(issues)} problems"
            result.recommendations = [
                "Enable KuzuDB spatial extensions",
                "Update spatial schema to support canvas requirements",
                "Review geographic business context definitions"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _validate_skos_concept_resolution(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate all SKOS concept URIs are resolvable"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"],
            level=rule_config["level"],
            passed=True,
            message="SKOS concept URI resolvability validated"
        )
        
        issues = []
        
        if self.skos_router and self.fuseki_client:
            try:
                # Get all concept URIs in use
                concept_uris = self._get_all_concept_uris()
                
                unresolvable_uris = []
                for uri in concept_uris:
                    if not self._is_uri_resolvable(uri):
                        unresolvable_uris.append(uri)
                        issues.append(f"Unresolvable concept URI: {uri}")
                
                result.details = {
                    "total_concept_uris": len(concept_uris),
                    "unresolvable_uris": len(unresolvable_uris),
                    "resolution_rate": (len(concept_uris) - len(unresolvable_uris)) / len(concept_uris) if concept_uris else 1.0
                }
                
            except Exception as e:
                issues.append(f"Failed to validate SKOS concept resolution: {str(e)}")
        else:
            issues.append("SKOS router or Fuseki client not available")
        
        if issues:
            result.passed = False
            result.message = f"SKOS concept resolution issues: {len(issues)} unresolvable URIs"
            result.recommendations = [
                "Update Fuseki triple store with missing concepts",
                "Fix malformed concept URIs",
                "Verify triple store connectivity"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _validate_skos_multilingual_coverage(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate SKOS multilingual coverage for business domains"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"],
            level=rule_config["level"],
            passed=True,
            message="SKOS multilingual coverage validated"
        )
        
        issues = []
        
        if self.skos_router:
            try:
                # Check multilingual coverage for key business domains
                business_domains = self._get_active_business_domains()
                target_languages = ["en", "tr", "fr", "es"]  # Required languages
                
                for domain in business_domains:
                    domain_concepts = self._get_domain_concepts(domain)
                    
                    for concept_uri in domain_concepts:
                        missing_languages = self._check_concept_language_coverage(concept_uri, target_languages)
                        
                        if missing_languages:
                            issues.append(f"Concept {concept_uri} missing languages: {missing_languages}")
                            result.affected_components.append(domain)
                
                total_concepts = sum(len(self._get_domain_concepts(d)) for d in business_domains)
                coverage_score = 1.0 - (len(issues) / (total_concepts * len(target_languages))) if total_concepts > 0 else 1.0
                
                result.details = {
                    "business_domains": len(business_domains),
                    "target_languages": target_languages,
                    "multilingual_coverage": coverage_score,
                    "missing_translations": len(issues)
                }
                
            except Exception as e:
                issues.append(f"Failed to validate SKOS multilingual coverage: {str(e)}")
        else:
            issues.append("SKOS router not available")
        
        # This is a warning-level check, so we're more lenient
        if len(issues) > 10:  # Threshold for too many missing translations
            result.passed = False
            result.message = f"SKOS multilingual coverage insufficient: {len(issues)} missing translations"
            result.recommendations = [
                "Add missing language translations to SKOS concepts",
                "Review business domain language requirements",
                "Prioritize translations for high-value concepts"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _validate_integration_performance(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate ADR integrations maintain performance requirements"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"],
            level=rule_config["level"],
            passed=True,
            message="Integration performance validated"
        )
        
        issues = []
        performance_metrics = {}
        
        try:
            # Check SOW-KuzuDB query performance
            if self.sow_manager and self.kuzu_manager:
                sow_kuzu_latency = self._measure_sow_kuzu_integration_latency()
                performance_metrics["sow_kuzu_latency_ms"] = sow_kuzu_latency
                
                if sow_kuzu_latency > 500:  # 500ms threshold
                    issues.append(f"SOW-KuzuDB integration latency too high: {sow_kuzu_latency}ms")
            
            # Check SKOS routing performance 
            if self.skos_router:
                skos_routing_latency = self._measure_skos_routing_latency()
                performance_metrics["skos_routing_latency_ms"] = skos_routing_latency
                
                if skos_routing_latency > 50:  # 50ms threshold for in-memory routing
                    issues.append(f"SKOS routing latency too high: {skos_routing_latency}ms")
            
            # Check canvas bridge performance
            if self.canvas_bridge:
                canvas_bridge_latency = self._measure_canvas_bridge_latency()
                performance_metrics["canvas_bridge_latency_ms"] = canvas_bridge_latency
                
                if canvas_bridge_latency > 1000:  # 1s threshold for complex translations
                    issues.append(f"Canvas bridge latency too high: {canvas_bridge_latency}ms")
            
            result.details = {
                "performance_metrics": performance_metrics,
                "performance_issues": len(issues)
            }
            
        except Exception as e:
            issues.append(f"Failed to validate integration performance: {str(e)}")
        
        if issues:
            result.passed = False
            result.message = f"Integration performance issues: {len(issues)} problems"
            result.recommendations = [
                "Optimize slow integration points",
                "Add caching layers for frequently accessed data",
                "Review database index usage",
                "Consider connection pooling"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _validate_canvas_bmc_alignment(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate Data Business Canvas aligns with BMC principles"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"],
            level=rule_config["level"],
            passed=True,
            message="Canvas-BMC alignment validated"
        )
        
        issues = []
        
        if self.canvas_bridge:
            try:
                # Get active canvases and validate BMC component coverage
                active_canvases = self._get_active_business_canvases()
                
                required_bmc_components = [
                    "key_partners", "key_activities", "key_resources", 
                    "value_propositions", "customer_relationships", "customer_segments",
                    "channels", "cost_structure", "revenue_streams"
                ]
                
                for canvas in active_canvases:
                    canvas_components = canvas.get("components", {})
                    
                    missing_components = []
                    for required_component in required_bmc_components:
                        if required_component not in canvas_components or not canvas_components[required_component]:
                            missing_components.append(required_component)
                    
                    if missing_components:
                        issues.append(f"Canvas {canvas['canvas_id']} missing BMC components: {missing_components}")
                        result.affected_components.append(canvas["canvas_id"])
                
                result.details = {
                    "canvases_checked": len(active_canvases),
                    "required_bmc_components": len(required_bmc_components),
                    "component_coverage_issues": len(issues)
                }
                
            except Exception as e:
                issues.append(f"Failed to validate Canvas-BMC alignment: {str(e)}")
        else:
            issues.append("Canvas bridge not available")
        
        if issues:
            result.passed = False
            result.message = f"Canvas-BMC alignment issues: {len(issues)} problems"
            result.recommendations = [
                "Complete missing BMC components in canvases",
                "Review BMC framework requirements",
                "Validate business model completeness"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _validate_ontology_namespaces(self, rule_id: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Validate ontology namespaces are consistent across ADRs"""
        
        result = ValidationResult(
            check_id=rule_id,
            adr_scope=rule_config["adrs"],
            validation_scope=rule_config["scope"],
            level=rule_config["level"],
            passed=True,
            message="Ontology namespace consistency validated"
        )
        
        issues = []
        
        try:
            # Check namespace consistency across all ADR components
            namespace_usage = self._collect_namespace_usage()
            namespace_conflicts = self._detect_namespace_conflicts(namespace_usage)
            
            for conflict in namespace_conflicts:
                issues.append(f"Namespace conflict: {conflict['namespace']} used inconsistently across {conflict['adrs']}")
                result.affected_components.extend(conflict["components"])
            
            result.details = {
                "namespaces_found": len(namespace_usage),
                "namespace_conflicts": len(namespace_conflicts),
                "consistency_score": 1.0 - (len(namespace_conflicts) / len(namespace_usage)) if namespace_usage else 1.0
            }
            
        except Exception as e:
            issues.append(f"Failed to validate ontology namespaces: {str(e)}")
        
        if issues:
            result.passed = False
            result.message = f"Ontology namespace issues: {len(issues)} conflicts"
            result.recommendations = [
                "Standardize namespace usage across ADRs",
                "Update conflicting namespace references",
                "Review ontology design guidelines"
            ]
            result.details["issues"] = issues
        
        return result
    
    def _generate_consistency_report(self, validation_id: str, results: List[ValidationResult]) -> ADRConsistencyReport:
        """Generate comprehensive consistency report from validation results"""
        
        # Count issues by level
        critical_issues = sum(1 for r in results if r.level == ADRValidationLevel.CRITICAL and not r.passed)
        warning_issues = sum(1 for r in results if r.level == ADRValidationLevel.WARNING and not r.passed)
        info_issues = sum(1 for r in results if r.level == ADRValidationLevel.INFO and not r.passed)
        
        # Calculate overall score
        total_checks = len(results)
        passed_checks = sum(1 for r in results if r.passed)
        overall_score = passed_checks / total_checks if total_checks > 0 else 0.0
        
        # Collect top recommendations
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)
        
        # Deduplicate and prioritize recommendations
        unique_recommendations = list(dict.fromkeys(all_recommendations))[:10]  # Top 10
        
        # Schedule next validation
        from datetime import timedelta
        next_validation_delta = timedelta(hours=24) if critical_issues > 0 else timedelta(days=7)
        
        report = ADRConsistencyReport(
            validation_id=validation_id,
            timestamp=datetime.utcnow(),
            overall_score=overall_score,
            critical_issues=critical_issues,
            warning_issues=warning_issues, 
            info_issues=info_issues,
            results=results,
            recommendations=unique_recommendations,
            next_validation=datetime.utcnow() + next_validation_delta
        )
        
        return report
    
    # Helper methods for validation checks (simplified implementations)
    
    def _get_active_sow_contracts(self) -> List[Dict[str, Any]]:
        """Get active SOW contracts from SOW manager"""
        # Simplified - would query actual SOW manager
        return [{"contract_id": "DC_001", "type": "data_contract"}]
    
    def _get_kuzu_table_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get KuzuDB table schemas"""
        # Simplified - would query actual KuzuDB
        return {"SOW_DC_001": {"columns": ["id", "data", "timestamp"]}}
    
    def _validate_contract_table_schema(self, contract: Dict[str, Any], table_schema: Dict[str, Any]) -> List[str]:
        """Validate contract schema matches table schema"""
        # Simplified validation logic
        return []
    
    def _get_active_business_canvases(self) -> List[Dict[str, Any]]:
        """Get active business canvases"""
        # Simplified - would query canvas storage
        return [{"canvas_id": "CANVAS_001", "components": {}}]
    
    def _get_canvas_sow_contracts(self, canvas_id: str) -> List[Dict[str, Any]]:
        """Get SOW contracts for specific canvas"""
        # Simplified - would query contract mappings
        return []
    
    def _check_contract_canvas_semantics(self, contract: Dict[str, Any], canvas: Dict[str, Any]) -> List[str]:
        """Check semantic consistency between contract and canvas"""
        # Simplified semantic validation
        return []
    
    def _get_canvases_with_spatial_context(self) -> List[Dict[str, Any]]:
        """Get canvases that have spatial context"""
        return []
    
    def _check_kuzu_spatial_capabilities(self) -> Dict[str, Any]:
        """Check KuzuDB spatial capabilities"""
        return {"enabled": True, "extensions": []}
    
    def _validate_spatial_requirements_support(self, requirements: Dict[str, Any], capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Validate spatial requirements are supported"""
        return {"fully_supported": True, "missing_capabilities": []}
    
    def _get_all_concept_uris(self) -> List[str]:
        """Get all concept URIs in use across system"""
        return ["http://localhost:3030/dbc/ontology#OliveOilConcept"]
    
    def _is_uri_resolvable(self, uri: str) -> bool:
        """Check if URI is resolvable"""
        # Simplified - would make HTTP request
        return True
    
    def _get_active_business_domains(self) -> List[str]:
        """Get active business domains"""
        return ["supply_chain", "logistics"]
    
    def _get_domain_concepts(self, domain: str) -> List[str]:
        """Get concepts for business domain"""
        return ["concept1", "concept2"]
    
    def _check_concept_language_coverage(self, concept_uri: str, languages: List[str]) -> List[str]:
        """Check which languages are missing for concept"""
        return []  # No missing languages
    
    def _measure_sow_kuzu_integration_latency(self) -> float:
        """Measure SOW-KuzuDB integration latency"""
        return 100.0  # 100ms
    
    def _measure_skos_routing_latency(self) -> float:
        """Measure SKOS routing latency"""
        return 25.0  # 25ms
    
    def _measure_canvas_bridge_latency(self) -> float:
        """Measure canvas bridge latency"""
        return 500.0  # 500ms
    
    def _collect_namespace_usage(self) -> Dict[str, Any]:
        """Collect namespace usage across ADRs"""
        return {"http://localhost:3030/dbc/ontology#": ["ADR-012"]}
    
    def _detect_namespace_conflicts(self, namespace_usage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect namespace conflicts"""
        return []  # No conflicts detected