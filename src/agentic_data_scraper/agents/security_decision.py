"""
Security Decision Agent - Handles human-in-the-loop security decisions.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .base import BaseAgent
import asyncio
import logging

class SecurityDecision(BaseModel):
    """Security decision with risk assessment and recommendations."""
    
    risk_level: str = Field(
        description="Risk level assessment (LOW, MEDIUM, HIGH, CRITICAL)"
    )
    decision_required: str = Field(
        description="Specific decision that needs to be made"
    )
    context: str = Field(
        description="Context and background for the security decision"
    )
    recommended_action: str = Field(
        description="Recommended security action to take"
    )
    human_approval_needed: bool = Field(
        description="Whether human approval is required for this decision"
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Identified risk factors"
    )
    mitigation_strategies: List[str] = Field(
        default_factory=list,
        description="Recommended mitigation strategies"
    )
    compliance_considerations: List[str] = Field(
        default_factory=list,
        description="Regulatory compliance considerations"
    )
    monitoring_requirements: List[str] = Field(
        default_factory=list,
        description="Additional monitoring requirements"
    )
    approval_criteria: Optional[str] = Field(
        default=None,
        description="Criteria for human approval decision"
    )

class SecurityDecisionAgent(BaseAgent):
    """
    Agent specialized in security decision-making with human-in-the-loop capabilities.
    
    Assesses operational security risks, determines when human approval is needed,
    and provides comprehensive security recommendations.
    """
    
    def __init__(
        self,
        agent_id: str = "security_decision",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 300
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.risk_assessment_criteria = self._initialize_risk_criteria()
        self.compliance_frameworks = self._initialize_compliance_frameworks()
        
    def _initialize_risk_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk assessment criteria."""
        return {
            "data_sensitivity": {
                "public": {"base_risk": 0.1, "factors": []},
                "internal": {"base_risk": 0.3, "factors": ["access_control"]},
                "confidential": {"base_risk": 0.6, "factors": ["encryption", "audit_logging"]},
                "restricted": {"base_risk": 0.8, "factors": ["encryption", "audit_logging", "access_approval"]},
                "pii": {"base_risk": 0.9, "factors": ["encryption", "anonymization", "consent_tracking"]},
                "financial": {"base_risk": 0.9, "factors": ["encryption", "fraud_detection", "audit_trail"]}
            },
            "operation_types": {
                "data_reading": {"base_risk": 0.2, "human_threshold": 0.7},
                "data_writing": {"base_risk": 0.4, "human_threshold": 0.6},
                "data_transformation": {"base_risk": 0.3, "human_threshold": 0.7},
                "external_api_access": {"base_risk": 0.5, "human_threshold": 0.6},
                "authentication": {"base_risk": 0.6, "human_threshold": 0.5},
                "data_export": {"base_risk": 0.7, "human_threshold": 0.4},
                "cross_border_transfer": {"base_risk": 0.8, "human_threshold": 0.3}
            },
            "environment_factors": {
                "production": {"multiplier": 1.5, "human_threshold_adjustment": -0.1},
                "staging": {"multiplier": 1.2, "human_threshold_adjustment": 0.0},
                "development": {"multiplier": 1.0, "human_threshold_adjustment": 0.1},
                "external_service": {"multiplier": 1.3, "human_threshold_adjustment": -0.1},
                "new_integration": {"multiplier": 1.4, "human_threshold_adjustment": -0.2}
            }
        }
    
    def _initialize_compliance_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance framework requirements."""
        return {
            "gdpr": {
                "name": "General Data Protection Regulation",
                "applicable_data": ["pii", "personal_data", "eu_citizen_data"],
                "requirements": [
                    "explicit_consent",
                    "data_minimization",
                    "purpose_limitation",
                    "right_to_erasure",
                    "data_portability",
                    "breach_notification"
                ],
                "human_approval_triggers": [
                    "processing_sensitive_personal_data",
                    "automated_decision_making",
                    "cross_border_data_transfer",
                    "new_processing_purpose"
                ]
            },
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "applicable_data": ["phi", "health_data", "medical_records"],
                "requirements": [
                    "administrative_safeguards",
                    "physical_safeguards", 
                    "technical_safeguards",
                    "breach_notification",
                    "business_associate_agreements"
                ],
                "human_approval_triggers": [
                    "phi_access",
                    "phi_transmission",
                    "new_healthcare_integration"
                ]
            },
            "sox": {
                "name": "Sarbanes-Oxley Act",
                "applicable_data": ["financial_data", "trading_records", "audit_trails"],
                "requirements": [
                    "internal_controls",
                    "audit_trail_integrity",
                    "management_assessment",
                    "external_auditor_attestation"
                ],
                "human_approval_triggers": [
                    "financial_data_modification",
                    "audit_trail_changes",
                    "control_system_changes"
                ]
            },
            "pci_dss": {
                "name": "Payment Card Industry Data Security Standard",
                "applicable_data": ["payment_card_data", "cardholder_data", "sensitive_authentication_data"],
                "requirements": [
                    "network_security",
                    "cardholder_data_protection",
                    "vulnerability_management",
                    "access_control",
                    "monitoring",
                    "information_security_policy"
                ],
                "human_approval_triggers": [
                    "cardholder_data_access",
                    "payment_processing_changes",
                    "new_payment_integration"
                ]
            }
        }
    
    async def _process(
        self,
        operation_context: str,
        risk_assessment: str,
        data_sensitivity: str = "internal",
        environment: str = "production",
        compliance_frameworks: List[str] = None,
        **kwargs
    ) -> SecurityDecision:
        """
        Analyze security implications and generate decision recommendations.
        
        Args:
            operation_context: Description of the operation being evaluated
            risk_assessment: Initial risk assessment description
            data_sensitivity: Sensitivity level of data involved
            environment: Environment where operation will occur
            compliance_frameworks: Applicable compliance frameworks
            
        Returns:
            SecurityDecision: Comprehensive security decision with recommendations
        """
        self.logger.info(f"Analyzing security decision for: {operation_context}")
        
        compliance_frameworks = compliance_frameworks or []
        
        # Calculate risk score
        risk_score = await self._calculate_risk_score(
            operation_context, risk_assessment, data_sensitivity, environment
        )
        
        # Determine risk level
        risk_level = await self._determine_risk_level(risk_score)
        
        # Identify risk factors
        risk_factors = await self._identify_risk_factors(
            operation_context, data_sensitivity, compliance_frameworks
        )
        
        # Generate mitigation strategies
        mitigation_strategies = await self._generate_mitigation_strategies(
            risk_factors, risk_level, data_sensitivity
        )
        
        # Check compliance requirements
        compliance_considerations = await self._assess_compliance_requirements(
            operation_context, data_sensitivity, compliance_frameworks
        )
        
        # Determine if human approval is needed
        human_approval_needed = await self._requires_human_approval(
            risk_score, risk_level, operation_context, compliance_frameworks
        )
        
        # Generate recommended action
        recommended_action = await self._generate_recommended_action(
            risk_level, mitigation_strategies, human_approval_needed
        )
        
        # Generate monitoring requirements
        monitoring_requirements = await self._generate_monitoring_requirements(
            risk_level, data_sensitivity, compliance_frameworks
        )
        
        # Generate approval criteria if human approval needed
        approval_criteria = None
        if human_approval_needed:
            approval_criteria = await self._generate_approval_criteria(
                risk_factors, compliance_considerations
            )
        
        return SecurityDecision(
            risk_level=risk_level,
            decision_required=await self._format_decision_requirement(operation_context),
            context=await self._format_context(operation_context, risk_assessment, data_sensitivity),
            recommended_action=recommended_action,
            human_approval_needed=human_approval_needed,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            compliance_considerations=compliance_considerations,
            monitoring_requirements=monitoring_requirements,
            approval_criteria=approval_criteria
        )
    
    async def _calculate_risk_score(
        self,
        operation_context: str,
        risk_assessment: str,
        data_sensitivity: str,
        environment: str
    ) -> float:
        """Calculate numerical risk score based on various factors."""
        
        base_score = 0.0
        
        # Data sensitivity risk
        sensitivity_config = self.risk_assessment_criteria["data_sensitivity"].get(
            data_sensitivity.lower(), {"base_risk": 0.5}
        )
        base_score += sensitivity_config["base_risk"]
        
        # Operation type risk
        operation_type = await self._classify_operation_type(operation_context)
        operation_config = self.risk_assessment_criteria["operation_types"].get(
            operation_type, {"base_risk": 0.3}
        )
        base_score += operation_config["base_risk"]
        
        # Environment multiplier
        env_config = self.risk_assessment_criteria["environment_factors"].get(
            environment.lower(), {"multiplier": 1.0}
        )
        base_score *= env_config["multiplier"]
        
        # Risk assessment context adjustments
        if "high" in risk_assessment.lower():
            base_score *= 1.3
        elif "critical" in risk_assessment.lower():
            base_score *= 1.5
        elif "low" in risk_assessment.lower():
            base_score *= 0.8
        
        # Contextual risk factors
        if "new" in operation_context.lower():
            base_score *= 1.2
        if "external" in operation_context.lower():
            base_score *= 1.1
        if "authentication" in operation_context.lower():
            base_score *= 1.2
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    async def _classify_operation_type(self, operation_context: str) -> str:
        """Classify operation type from context."""
        
        context_lower = operation_context.lower()
        
        if any(keyword in context_lower for keyword in ["fetch", "read", "get", "retrieve"]):
            return "data_reading"
        elif any(keyword in context_lower for keyword in ["write", "store", "save", "update"]):
            return "data_writing"
        elif any(keyword in context_lower for keyword in ["transform", "process", "convert"]):
            return "data_transformation"
        elif any(keyword in context_lower for keyword in ["api", "external", "service"]):
            return "external_api_access"
        elif any(keyword in context_lower for keyword in ["auth", "login", "credential"]):
            return "authentication"
        elif any(keyword in context_lower for keyword in ["export", "transfer", "send"]):
            return "data_export"
        elif any(keyword in context_lower for keyword in ["cross-border", "international"]):
            return "cross_border_transfer"
        else:
            return "data_reading"  # Default to least risky
    
    async def _determine_risk_level(self, risk_score: float) -> str:
        """Determine categorical risk level from numerical score."""
        
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    async def _identify_risk_factors(
        self,
        operation_context: str,
        data_sensitivity: str,
        compliance_frameworks: List[str]
    ) -> List[str]:
        """Identify specific risk factors for the operation."""
        
        risk_factors = []
        
        # Data sensitivity risks
        if data_sensitivity.lower() in ["pii", "financial", "restricted"]:
            risk_factors.append(f"High sensitivity data: {data_sensitivity}")
        
        # Operation-specific risks
        context_lower = operation_context.lower()
        
        if "external" in context_lower:
            risk_factors.append("External service dependency")
        if "new" in context_lower:
            risk_factors.append("New or untested integration")
        if "authentication" in context_lower:
            risk_factors.append("Authentication and credential management")
        if "api" in context_lower:
            risk_factors.append("Third-party API access")
        if "cross-border" in context_lower or "international" in context_lower:
            risk_factors.append("Cross-border data transfer")
        
        # Compliance-based risks
        for framework in compliance_frameworks:
            if framework.lower() in self.compliance_frameworks:
                risk_factors.append(f"Regulatory compliance: {framework.upper()}")
        
        return risk_factors
    
    async def _generate_mitigation_strategies(
        self,
        risk_factors: List[str],
        risk_level: str,
        data_sensitivity: str
    ) -> List[str]:
        """Generate appropriate mitigation strategies."""
        
        strategies = []
        
        # Base strategies by risk level
        if risk_level in ["HIGH", "CRITICAL"]:
            strategies.extend([
                "Implement comprehensive audit logging",
                "Enable real-time monitoring and alerting",
                "Apply principle of least privilege",
                "Require multi-factor authentication"
            ])
        
        if risk_level == "CRITICAL":
            strategies.extend([
                "Implement break-glass emergency procedures",
                "Require dual approval for critical operations",
                "Enable continuous compliance monitoring"
            ])
        
        # Data sensitivity specific strategies
        if data_sensitivity.lower() in ["pii", "financial", "restricted"]:
            strategies.extend([
                "Implement end-to-end encryption",
                "Apply data anonymization where possible",
                "Implement data loss prevention controls"
            ])
        
        # Risk factor specific strategies
        for factor in risk_factors:
            if "external service" in factor.lower():
                strategies.append("Implement service mesh with security policies")
            elif "new integration" in factor.lower():
                strategies.append("Conduct thorough security testing and validation")
            elif "authentication" in factor.lower():
                strategies.extend([
                    "Use secure credential storage (e.g., AWS Secrets Manager)",
                    "Implement credential rotation policies"
                ])
            elif "cross-border" in factor.lower():
                strategies.append("Ensure compliance with data residency requirements")
        
        return list(set(strategies))  # Remove duplicates
    
    async def _assess_compliance_requirements(
        self,
        operation_context: str,
        data_sensitivity: str,
        compliance_frameworks: List[str]
    ) -> List[str]:
        """Assess compliance requirements and considerations."""
        
        considerations = []
        
        for framework_name in compliance_frameworks:
            framework = self.compliance_frameworks.get(framework_name.lower())
            if not framework:
                continue
            
            # Check if data type matches framework scope
            applicable_data = framework["applicable_data"]
            if any(data_type in data_sensitivity.lower() for data_type in applicable_data):
                considerations.append(f"{framework['name']} applies to this data type")
                
                # Add specific requirements
                for requirement in framework["requirements"]:
                    considerations.append(f"{framework_name.upper()}: {requirement}")
        
        # General compliance considerations
        if data_sensitivity.lower() in ["pii", "personal_data"]:
            considerations.append("Data subject rights must be respected")
            considerations.append("Consent management may be required")
        
        if "cross-border" in operation_context.lower():
            considerations.append("International data transfer regulations apply")
        
        return considerations
    
    async def _requires_human_approval(
        self,
        risk_score: float,
        risk_level: str,
        operation_context: str,
        compliance_frameworks: List[str]
    ) -> bool:
        """Determine if human approval is required."""
        
        # Always require approval for critical risk
        if risk_level == "CRITICAL":
            return True
        
        # High risk requires approval unless explicitly low-risk operation
        if risk_level == "HIGH":
            low_risk_operations = ["read", "fetch", "get"]
            if not any(op in operation_context.lower() for op in low_risk_operations):
                return True
        
        # Check compliance framework triggers
        for framework_name in compliance_frameworks:
            framework = self.compliance_frameworks.get(framework_name.lower())
            if framework:
                triggers = framework.get("human_approval_triggers", [])
                for trigger in triggers:
                    if trigger.replace("_", " ") in operation_context.lower():
                        return True
        
        # Risk score threshold
        operation_type = await self._classify_operation_type(operation_context)
        operation_config = self.risk_assessment_criteria["operation_types"].get(
            operation_type, {"human_threshold": 0.7}
        )
        
        return risk_score >= operation_config["human_threshold"]
    
    async def _generate_recommended_action(
        self,
        risk_level: str,
        mitigation_strategies: List[str],
        human_approval_needed: bool
    ) -> str:
        """Generate recommended action based on analysis."""
        
        if human_approval_needed:
            if risk_level == "CRITICAL":
                return (
                    "REQUIRE IMMEDIATE HUMAN APPROVAL: Critical security risk identified. "
                    "Implementation blocked pending security review and explicit approval. "
                    f"Apply all mitigation strategies: {', '.join(mitigation_strategies[:3])}"
                )
            elif risk_level == "HIGH":
                return (
                    "REQUIRE HUMAN APPROVAL: High security risk requires review. "
                    "Proceed only after security team approval and implementation of "
                    f"required mitigations: {', '.join(mitigation_strategies[:2])}"
                )
            else:
                return (
                    "REQUIRE APPROVAL: Security review needed before proceeding. "
                    "Implement recommended mitigations and obtain approval."
                )
        else:
            if risk_level == "MEDIUM":
                return (
                    "PROCEED WITH CAUTION: Implement required security measures before deployment. "
                    f"Key mitigations: {', '.join(mitigation_strategies[:2])}"
                )
            else:
                return (
                    "PROCEED: Low risk operation. Apply standard security practices and monitor. "
                    f"Recommended: {', '.join(mitigation_strategies[:1]) if mitigation_strategies else 'Standard monitoring'}"
                )
    
    async def _generate_monitoring_requirements(
        self,
        risk_level: str,
        data_sensitivity: str,
        compliance_frameworks: List[str]
    ) -> List[str]:
        """Generate monitoring and alerting requirements."""
        
        monitoring = []
        
        # Base monitoring by risk level
        if risk_level in ["HIGH", "CRITICAL"]:
            monitoring.extend([
                "Real-time security event monitoring",
                "Automated anomaly detection",
                "Immediate alert on suspicious activity",
                "Daily security posture reporting"
            ])
        elif risk_level == "MEDIUM":
            monitoring.extend([
                "Regular security log review",
                "Weekly security reports",
                "Automated threshold-based alerts"
            ])
        else:
            monitoring.append("Standard audit logging and monthly reviews")
        
        # Data sensitivity specific monitoring
        if data_sensitivity.lower() in ["pii", "financial", "restricted"]:
            monitoring.extend([
                "Data access audit trails",
                "Data modification tracking",
                "Breach detection and notification procedures"
            ])
        
        # Compliance specific monitoring
        if "gdpr" in [f.lower() for f in compliance_frameworks]:
            monitoring.extend([
                "Data processing activity monitoring",
                "Consent tracking and validation",
                "Data subject request handling"
            ])
        
        if "sox" in [f.lower() for f in compliance_frameworks]:
            monitoring.extend([
                "Financial data integrity monitoring",
                "Internal control effectiveness tracking"
            ])
        
        return list(set(monitoring))
    
    async def _generate_approval_criteria(
        self,
        risk_factors: List[str],
        compliance_considerations: List[str]
    ) -> str:
        """Generate criteria for human approval decision."""
        
        criteria_parts = []
        
        criteria_parts.append("Human approval should consider:")
        
        if risk_factors:
            criteria_parts.append(f"• Risk factors: {', '.join(risk_factors[:3])}")
        
        if compliance_considerations:
            criteria_parts.append(f"• Compliance: {', '.join(compliance_considerations[:2])}")
        
        criteria_parts.extend([
            "• Business justification and necessity",
            "• Adequacy of proposed security measures",
            "• Availability of monitoring and incident response",
            "• Alignment with organizational security policies"
        ])
        
        return "\\n".join(criteria_parts)
    
    async def _format_decision_requirement(self, operation_context: str) -> str:
        """Format the specific decision requirement."""
        return f"Security approval for: {operation_context}"
    
    async def _format_context(
        self,
        operation_context: str,
        risk_assessment: str,
        data_sensitivity: str
    ) -> str:
        """Format comprehensive context for the decision."""
        
        return (
            f"Operation: {operation_context}\\n"
            f"Risk Assessment: {risk_assessment}\\n"
            f"Data Sensitivity: {data_sensitivity}\\n"
            f"Evaluation performed by automated security decision agent"
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "risk_assessment": [
                "multi_factor_risk_scoring",
                "contextual_risk_analysis", 
                "operation_type_classification",
                "data_sensitivity_evaluation"
            ],
            "compliance_frameworks": list(self.compliance_frameworks.keys()),
            "decision_types": [
                "human_approval_required",
                "automated_approval",
                "conditional_approval",
                "rejection_recommended"
            ],
            "mitigation_strategies": [
                "encryption",
                "access_control",
                "audit_logging",
                "monitoring",
                "authentication",
                "authorization"
            ],
            "output_format": "SecurityDecision"
        })
        return base_capabilities