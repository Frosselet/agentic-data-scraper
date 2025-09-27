"""
Canvas Validation Engine

Provides semantic validation for Data Business Canvas using BAML agents
and existing SOW schemas. Ensures canvas data quality and consistency
before feeding into downstream discovery agents.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

import sys
from pathlib import Path

# Add project src to path for absolute imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from agentic_data_scraper.agents.sow_interpreter import SOWInterpreterAgent, DataContract
from agentic_data_scraper.schemas.sow import SemanticStatementOfWork, BusinessChallenge
from agentic_data_scraper.semantic.skos_router import SKOSSemanticRouter

logger = logging.getLogger(__name__)


class CanvasValidationEngine:
    """
    Validates Data Business Canvas using BAML agents and semantic routing.

    Provides:
    - Business logic validation
    - SOW schema compliance checking
    - Semantic term validation via SKOS
    - Cross-section consistency analysis
    - Completeness scoring
    """

    def __init__(self):
        self.sow_agent = None
        self.skos_router = None
        self.validation_cache = {}

    async def initialize(self, kuzu_db_path: Optional[str] = None):
        """Initialize validation agents and semantic router"""
        try:
            # Initialize SOW interpreter for validation
            self.sow_agent = SOWInterpreterAgent(
                agent_id="canvas_validator",
                timeout_seconds=60
            )

            # Initialize SKOS router for semantic validation
            if kuzu_db_path:
                self.skos_router = SKOSSemanticRouter(kuzu_db_path)
            else:
                # Default path
                db_path = Path("data/kuzu_dbc.db")
                db_path.parent.mkdir(exist_ok=True)
                self.skos_router = SKOSSemanticRouter(str(db_path))

            logger.info("Canvas validation engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize validation engine: {e}")
            raise

    async def validate_canvas(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive canvas validation with semantic analysis

        Args:
            canvas_data: Complete canvas data structure

        Returns:
            Validation results with scores, issues, and recommendations
        """

        if not self.sow_agent or not self.skos_router:
            await self.initialize()

        validation_start = datetime.utcnow()

        # Run parallel validations
        validation_tasks = [
            self._validate_structure(canvas_data),
            self._validate_business_logic(canvas_data),
            self._validate_semantic_consistency(canvas_data),
            self._validate_sow_compatibility(canvas_data),
            self._validate_completeness(canvas_data)
        ]

        results = await asyncio.gather(*validation_tasks, return_exceptions=True)

        # Compile validation results
        validation_report = {
            "overall_score": 0.0,
            "validation_timestamp": validation_start.isoformat(),
            "validation_duration_ms": int((datetime.utcnow() - validation_start).total_seconds() * 1000),
            "sections": {
                "structure": results[0] if not isinstance(results[0], Exception) else {"score": 0.0, "errors": [str(results[0])]},
                "business_logic": results[1] if not isinstance(results[1], Exception) else {"score": 0.0, "errors": [str(results[1])]},
                "semantic_consistency": results[2] if not isinstance(results[2], Exception) else {"score": 0.0, "errors": [str(results[2])]},
                "sow_compatibility": results[3] if not isinstance(results[3], Exception) else {"score": 0.0, "errors": [str(results[3])]},
                "completeness": results[4] if not isinstance(results[4], Exception) else {"score": 0.0, "errors": [str(results[4])]}
            },
            "recommendations": [],
            "blocking_issues": [],
            "warnings": []
        }

        # Calculate overall score
        section_scores = [
            section.get("score", 0.0)
            for section in validation_report["sections"].values()
            if isinstance(section, dict)
        ]
        validation_report["overall_score"] = sum(section_scores) / len(section_scores) if section_scores else 0.0

        # Collect recommendations and issues
        for section_name, section_result in validation_report["sections"].items():
            if isinstance(section_result, dict):
                validation_report["recommendations"].extend(
                    section_result.get("recommendations", [])
                )
                validation_report["blocking_issues"].extend(
                    section_result.get("blocking_issues", [])
                )
                validation_report["warnings"].extend(
                    section_result.get("warnings", [])
                )

        # Overall validation status
        validation_report["is_valid"] = (
            validation_report["overall_score"] >= 0.7 and
            len(validation_report["blocking_issues"]) == 0
        )

        return validation_report

    async def _validate_structure(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate canvas data structure and required fields"""

        score = 1.0
        issues = []
        warnings = []
        recommendations = []

        # Required top-level sections
        required_sections = [
            "value_propositions", "customer_segments", "customer_relationships",
            "channels", "key_activities", "key_resources", "key_partners",
            "cost_structure", "revenue_streams", "data_sources",
            "data_governance", "technology_infrastructure", "metadata"
        ]

        missing_sections = [
            section for section in required_sections
            if section not in canvas_data
        ]

        if missing_sections:
            score -= 0.5
            issues.extend([f"Missing required section: {section}" for section in missing_sections])

        # Check critical subsections
        critical_fields = [
            ("value_propositions", "data_insights"),
            ("customer_segments", "primary_users"),
            ("data_sources", "external_sources"),
            ("data_governance", "quality_standards"),
            ("metadata", "business_domain")
        ]

        for section, field in critical_fields:
            if section in canvas_data:
                if field not in canvas_data[section]:
                    score -= 0.1
                    warnings.append(f"Missing critical field: {section}.{field}")
                elif not canvas_data[section][field]:
                    score -= 0.05
                    warnings.append(f"Empty critical field: {section}.{field}")

        # Metadata validation
        if "metadata" in canvas_data:
            metadata = canvas_data["metadata"]

            if not metadata.get("business_domain"):
                score -= 0.2
                issues.append("Business domain not specified in metadata")

            if not metadata.get("primary_language"):
                score -= 0.1
                warnings.append("Primary language not specified")

        # Generate recommendations
        if score < 0.9:
            recommendations.append("Ensure all required sections are populated")
        if len(warnings) > 3:
            recommendations.append("Address field completeness warnings")

        return {
            "score": max(0.0, score),
            "blocking_issues": issues,
            "warnings": warnings,
            "recommendations": recommendations
        }

    async def _validate_business_logic(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business logic consistency across canvas sections"""

        score = 1.0
        issues = []
        warnings = []
        recommendations = []

        # Value proposition alignment
        value_insights = canvas_data.get("value_propositions", {}).get("data_insights", [])
        primary_users = canvas_data.get("customer_segments", {}).get("primary_users", [])

        if value_insights and not primary_users:
            score -= 0.3
            issues.append("Data insights specified but no primary users defined")
        elif primary_users and not value_insights:
            score -= 0.2
            warnings.append("Primary users defined but no specific data insights")

        # Resource-activity alignment
        key_activities = canvas_data.get("key_activities", {})
        key_resources = canvas_data.get("key_resources", {})

        data_collection_activities = key_activities.get("data_collection", [])
        data_assets = key_resources.get("data_assets", [])

        if data_collection_activities and not data_assets:
            score -= 0.2
            warnings.append("Data collection activities defined but no data assets specified")

        # Technology-requirement alignment
        real_time_feeds = canvas_data.get("data_sources", {}).get("real_time_feeds", [])
        data_platforms = canvas_data.get("technology_infrastructure", {}).get("data_platforms", [])

        if real_time_feeds:
            has_streaming_platform = any(
                "stream" in platform.lower() or "real-time" in platform.lower() or
                "kafka" in platform.lower() or "kinesis" in platform.lower()
                for platform in data_platforms
            )
            if not has_streaming_platform:
                score -= 0.2
                warnings.append("Real-time data feeds specified but no streaming platform mentioned")

        # Cost-benefit alignment
        cost_structure = canvas_data.get("cost_structure", {})
        revenue_streams = canvas_data.get("revenue_streams", {})

        all_costs = (
            cost_structure.get("data_acquisition", []) +
            cost_structure.get("infrastructure", []) +
            cost_structure.get("operational", [])
        )

        all_revenues = (
            revenue_streams.get("direct_revenue", []) +
            revenue_streams.get("cost_savings", []) +
            revenue_streams.get("strategic_value", [])
        )

        if all_costs and not all_revenues:
            score -= 0.1
            warnings.append("Costs identified but no corresponding value streams")

        # Generate recommendations
        if score < 0.8:
            recommendations.append("Review business logic consistency across sections")
        if len(warnings) > 2:
            recommendations.append("Align related sections for better coherence")

        return {
            "score": max(0.0, score),
            "blocking_issues": issues,
            "warnings": warnings,
            "recommendations": recommendations
        }

    async def _validate_semantic_consistency(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate semantic consistency using SKOS routing"""

        score = 1.0
        issues = []
        warnings = []
        recommendations = []

        if not self.skos_router:
            return {
                "score": 0.5,
                "blocking_issues": ["SKOS router not available"],
                "warnings": [],
                "recommendations": ["Initialize semantic routing for term validation"]
            }

        try:
            # Extract business domain and language
            business_domain = canvas_data.get("metadata", {}).get("business_domain", "")
            primary_language = canvas_data.get("metadata", {}).get("primary_language", "en")

            # Validate business terms across sections
            business_terms = []

            # Collect terms from various sections
            for section_name, section_data in canvas_data.items():
                if section_name == "metadata":
                    continue

                business_terms.extend(self._extract_business_terms(section_data))

            # Validate terms using SKOS routing
            validated_terms = 0
            total_terms = len(business_terms)

            for term in business_terms[:10]:  # Limit to avoid performance issues
                try:
                    routing_result = self.skos_router.route_term_to_preferred(
                        term, primary_language, "en"
                    )

                    if routing_result.get("translation_confidence", 0) > 0.7:
                        validated_terms += 1
                    elif routing_result.get("needs_ai_fallback"):
                        warnings.append(f"Term '{term}' not found in SKOS vocabulary")

                except Exception as e:
                    logger.debug(f"SKOS validation error for term '{term}': {e}")

            # Calculate semantic score
            if total_terms > 0:
                semantic_coverage = validated_terms / min(total_terms, 10)
                score = 0.3 + (0.7 * semantic_coverage)  # Base score + semantic coverage
            else:
                score = 0.5  # Neutral score for no terms

            # Generate recommendations
            if score < 0.7:
                recommendations.append("Consider adding domain-specific terms to SKOS vocabulary")
            if len(warnings) > 3:
                recommendations.append("Review business terminology for consistency")

        except Exception as e:
            logger.error(f"Semantic validation error: {e}")
            score = 0.5
            warnings.append("Semantic validation partially failed")

        return {
            "score": max(0.0, score),
            "blocking_issues": issues,
            "warnings": warnings,
            "recommendations": recommendations
        }

    def _extract_business_terms(self, data: Any) -> List[str]:
        """Extract business terms from canvas data for semantic validation"""
        terms = []

        if isinstance(data, dict):
            for value in data.values():
                terms.extend(self._extract_business_terms(value))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str) and len(item.split()) <= 3:  # Short business terms
                    terms.append(item.strip())
                else:
                    terms.extend(self._extract_business_terms(item))

        return [term for term in terms if term and len(term) > 2]

    async def _validate_sow_compatibility(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compatibility with SOW schema requirements"""

        score = 1.0
        issues = []
        warnings = []
        recommendations = []

        try:
            # Convert canvas to SOW text for validation
            sow_text = self._canvas_to_sow_text(canvas_data)

            # Process with SOW interpreter
            data_contract = await self.sow_agent._process(
                sow_document=sow_text,
                business_domain=canvas_data.get("metadata", {}).get("business_domain", "general")
            )

            # Validate data contract completeness
            required_contract_fields = [
                "source_requirements", "validation_rules", "quality_thresholds",
                "security_requirements", "business_context"
            ]

            for field in required_contract_fields:
                field_value = getattr(data_contract, field, None)
                if not field_value:
                    score -= 0.15
                    warnings.append(f"SOW contract missing: {field}")

            # Check quality thresholds
            quality_thresholds = getattr(data_contract, "quality_thresholds", {})
            if not quality_thresholds or len(quality_thresholds) < 2:
                score -= 0.1
                warnings.append("Insufficient quality thresholds in generated SOW")

            # Validate business context inference
            business_context = getattr(data_contract, "business_context", "")
            expected_domain = canvas_data.get("metadata", {}).get("business_domain", "")

            if expected_domain and expected_domain not in business_context:
                score -= 0.1
                warnings.append("Business context mismatch between canvas and SOW")

            # Generate recommendations
            if score < 0.8:
                recommendations.append("Enhance canvas data to improve SOW generation quality")
            if len(warnings) > 2:
                recommendations.append("Review data governance and quality sections")

        except Exception as e:
            logger.error(f"SOW compatibility validation error: {e}")
            score = 0.3
            issues.append("SOW compatibility check failed")

        return {
            "score": max(0.0, score),
            "blocking_issues": issues,
            "warnings": warnings,
            "recommendations": recommendations
        }

    def _canvas_to_sow_text(self, canvas_data: Dict[str, Any]) -> str:
        """Convert canvas data to SOW text for validation"""
        sow_sections = []

        # Business objectives
        sow_sections.append("## Business Objectives")
        business_outcomes = canvas_data.get("value_propositions", {}).get("business_outcomes", [])
        sow_sections.extend(business_outcomes)

        # Data requirements
        sow_sections.append("\n## Data Requirements")

        # Internal sources
        internal_sources = canvas_data.get("data_sources", {}).get("internal_sources", [])
        if internal_sources:
            sow_sections.append("### Internal Data Sources:")
            sow_sections.extend(internal_sources)

        # External sources
        external_sources = canvas_data.get("data_sources", {}).get("external_sources", [])
        if external_sources:
            sow_sections.append("### External Data Sources:")
            sow_sections.extend(external_sources)

        # Quality standards
        quality_standards = canvas_data.get("data_governance", {}).get("quality_standards", [])
        if quality_standards:
            sow_sections.append("\n## Quality Standards")
            sow_sections.extend(quality_standards)

        # Compliance requirements
        compliance_reqs = canvas_data.get("data_governance", {}).get("compliance_requirements", [])
        if compliance_reqs:
            sow_sections.append("\n## Compliance Requirements")
            sow_sections.extend(compliance_reqs)

        # Technical requirements
        data_platforms = canvas_data.get("technology_infrastructure", {}).get("data_platforms", [])
        if data_platforms:
            sow_sections.append("\n## Technical Requirements")
            sow_sections.extend(data_platforms)

        return "\n".join(sow_sections)

    async def _validate_completeness(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate and validate canvas completeness"""

        total_fields = 0
        completed_fields = 0
        recommendations = []

        def count_fields(obj, path=""):
            nonlocal total_fields, completed_fields

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "metadata":
                        continue
                    count_fields(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                total_fields += 1
                if obj:  # Non-empty list
                    completed_fields += 1
            else:
                total_fields += 1
                if obj:  # Non-empty value
                    completed_fields += 1

        count_fields(canvas_data)

        completion_score = completed_fields / total_fields if total_fields > 0 else 0.0

        # Generate recommendations based on completion
        if completion_score < 0.5:
            recommendations.append("Complete critical sections before proceeding to data discovery")
        elif completion_score < 0.8:
            recommendations.append("Add more detail to improve data discovery quality")
        else:
            recommendations.append("Canvas is well-completed and ready for data discovery")

        return {
            "score": completion_score,
            "completed_fields": completed_fields,
            "total_fields": total_fields,
            "blocking_issues": [],
            "warnings": [],
            "recommendations": recommendations
        }

    def close(self):
        """Clean up resources"""
        if self.skos_router:
            self.skos_router.close()