"""
Executive Target Scorer Agent

BAML-powered intelligent agent for enterprise-specific executive target alignment,
with dynamic target parsing and contextual alignment scoring.
"""

import asyncio
import logging
import sys
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from pathlib import Path

# Add project root to path for baml_client import
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from baml_client import b
from baml_client.types import (
    TargetCategory, TargetPriority, ExecutiveTarget, AlignmentScore,
    TargetParsingResult, DataBusinessCanvas
)

from ..models.executive_targets import (
    ExecutiveTarget as ModelExecutiveTarget,
    AlignmentScore as ModelAlignmentScore,
    TargetParsingResult as ModelTargetParsingResult,
    TargetAlignment, EnterpriseTargetRegistry, AlignmentFeedback
)

logger = logging.getLogger(__name__)


class ExecutiveTargetScorerAgent:
    """
    Enterprise-adaptive Executive Target Scorer with BAML-powered intelligence.

    Provides dynamic target parsing, contextual alignment scoring, and continuous
    feedback for maintaining optimal strategic alignment between data initiatives
    and executive objectives.
    """

    def __init__(self, enterprise_id: str, enterprise_name: str):
        self.enterprise_id = enterprise_id
        self.enterprise_name = enterprise_name
        self.session_id = f"scorer_{enterprise_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Initialized Executive Target Scorer: {self.session_id}")

    async def parse_executive_target(
        self,
        target_description: str,
        enterprise_context: Dict[str, str],
        owner: Optional[str] = None,
        owner_role: Optional[str] = None,
        deadline: Optional[date] = None
    ) -> ModelTargetParsingResult:
        """
        Parse natural language executive target description into structured format.

        Args:
            target_description: Natural language description of the target
            enterprise_context: Enterprise-specific context for parsing
            owner: Executive responsible for the target
            owner_role: Role/title of the owner
            deadline: Target deadline if known

        Returns:
            Structured parsing result with extracted entities and inferences
        """
        logger.info(f"Parsing executive target: {target_description[:100]}...")

        try:
            # Execute BAML target parsing agent
            parsing_result = await b.ParseExecutiveTarget(
                target_description=target_description,
                enterprise_context=enterprise_context
            )

            # Convert to model format
            model_result = ModelTargetParsingResult(
                key_themes=parsing_result.key_themes,
                quantitative_targets=parsing_result.quantitative_targets,
                timeframes=parsing_result.timeframes,
                stakeholders=parsing_result.stakeholders,
                success_indicators=parsing_result.success_indicators,
                suggested_category=parsing_result.suggested_category.value if parsing_result.suggested_category else None,
                suggested_priority=parsing_result.suggested_priority.value if parsing_result.suggested_priority else None,
                complexity_score=parsing_result.complexity_score,
                required_data_types=parsing_result.required_data_types,
                suggested_metrics=parsing_result.suggested_metrics,
                potential_data_sources=parsing_result.potential_data_sources,
                confidence=parsing_result.confidence,
                parsing_method="baml_agent",
                parsed_at=datetime.now()
            )

            logger.info(f"Target parsing completed with {model_result.confidence:.2f} confidence")
            return model_result

        except Exception as e:
            logger.error(f"Error parsing executive target: {e}")
            raise

    async def create_executive_target_from_parsing(
        self,
        parsing_result: ModelTargetParsingResult,
        target_description: str,
        owner: Optional[str] = None,
        owner_role: Optional[str] = None,
        deadline: Optional[date] = None,
        custom_properties: Dict[str, Any] = None
    ) -> ModelExecutiveTarget:
        """
        Create structured executive target from parsing results.

        Args:
            parsing_result: Result from parse_executive_target
            target_description: Original target description
            owner: Executive responsible
            owner_role: Owner's role/title
            deadline: Target deadline
            custom_properties: Enterprise-specific properties

        Returns:
            Structured executive target ready for alignment scoring
        """
        try:
            # Generate title from key themes
            title = " | ".join(parsing_result.key_themes[:3]) if parsing_result.key_themes else "Strategic Target"

            target = ModelExecutiveTarget(
                title=title,
                description=target_description,
                category=parsing_result.suggested_category or "revenue",
                priority=parsing_result.suggested_priority or "medium",
                owner=owner or "Executive Team",
                owner_role=owner_role or "Leadership",
                deadline=deadline,
                success_metrics=parsing_result.success_indicators,
                target_value=parsing_result.quantitative_targets[0] if parsing_result.quantitative_targets else None,
                business_domain=self.enterprise_name,
                stakeholders=parsing_result.stakeholders,
                custom_properties=custom_properties or {},
                tags=parsing_result.key_themes
            )

            logger.info(f"Created executive target: {target.title}")
            return target

        except Exception as e:
            logger.error(f"Error creating executive target: {e}")
            raise

    async def score_strategic_alignment(
        self,
        target: ModelExecutiveTarget,
        canvas_data: Dict[str, Any],
        enterprise_context: Dict[str, str]
    ) -> ModelAlignmentScore:
        """
        Score strategic alignment between data initiative and executive target.

        Args:
            target: Executive target to align against
            canvas_data: Data Business Canvas data
            enterprise_context: Enterprise-specific context

        Returns:
            Multi-dimensional alignment score with detailed analysis
        """
        logger.info(f"Scoring alignment for target: {target.title}")

        try:
            # Convert target to BAML format
            baml_target = ExecutiveTarget(
                id=target.id,
                title=target.title,
                description=target.description,
                category=TargetCategory(target.category.upper()),
                priority=TargetPriority(target.priority.upper()),
                owner=target.owner,
                owner_role=target.owner_role,
                deadline=target.deadline.isoformat() if target.deadline else None,
                success_metrics=target.success_metrics,
                target_value=target.target_value,
                baseline_value=target.baseline_value,
                business_domain=target.business_domain,
                stakeholders=target.stakeholders,
                dependencies=target.dependencies,
                constraints=target.constraints,
                status=target.status
            )

            # Create BAML canvas representation
            baml_canvas = DataBusinessCanvas(
                value_propositions=canvas_data.get('value_propositions', []),
                key_activities=canvas_data.get('key_activities', []),
                key_resources=canvas_data.get('key_resources', []),
                key_partnerships=canvas_data.get('key_partnerships', []),
                customer_segments=canvas_data.get('customer_segments', []),
                customer_relationships=canvas_data.get('customer_relationships', []),
                channels=canvas_data.get('channels', []),
                cost_structure=canvas_data.get('cost_structure', []),
                revenue_streams=canvas_data.get('revenue_streams', []),
                data_assets=canvas_data.get('data_assets', []),
                intelligence_capabilities=canvas_data.get('intelligence_capabilities', []),
                competitive_advantages=canvas_data.get('competitive_advantages', []),
                business_domain=canvas_data.get('business_domain', ''),
                use_case_description=canvas_data.get('use_case_description', ''),
                timeline=canvas_data.get('timeline', ''),
                budget=canvas_data.get('budget', '')
            )

            # Execute BAML alignment scoring
            alignment_result = await b.ScoreStrategicAlignment(
                target=baml_target,
                canvas=baml_canvas,
                enterprise_context=enterprise_context
            )

            # Convert to model format
            model_score = ModelAlignmentScore(
                overall_score=alignment_result.overall_score,
                confidence=alignment_result.confidence,
                strategic_fit=alignment_result.strategic_fit,
                impact_potential=alignment_result.impact_potential,
                timeline_feasibility=alignment_result.timeline_feasibility,
                resource_efficiency=alignment_result.resource_efficiency,
                risk_assessment=alignment_result.risk_assessment,
                dependency_analysis=alignment_result.dependency_analysis,
                reasoning=alignment_result.reasoning,
                key_factors=alignment_result.key_factors,
                risk_factors=alignment_result.risk_factors,
                recommendations=alignment_result.recommendations,
                scored_at=datetime.now(),
                scorer_agent="ExecutiveTargetScorer",
                version="1.0"
            )

            logger.info(f"Alignment scoring completed: {model_score.overall_score:.2f} overall score")
            return model_score

        except Exception as e:
            logger.error(f"Error scoring strategic alignment: {e}")
            raise

    async def generate_alignment_feedback(
        self,
        target: ModelExecutiveTarget,
        canvas_data: Dict[str, Any],
        alignment_score: ModelAlignmentScore,
        market_changes: Dict[str, str] = None,
        progress_data: Dict[str, str] = None
    ) -> AlignmentFeedback:
        """
        Generate continuous feedback on alignment status with recommendations.

        Args:
            target: Executive target being monitored
            canvas_data: Current canvas state
            alignment_score: Latest alignment score
            market_changes: Recent market condition changes
            progress_data: Initiative progress metrics

        Returns:
            Structured feedback with recommendations and urgency assessment
        """
        logger.info(f"Generating alignment feedback for: {target.title}")

        try:
            # Convert alignment score to BAML format
            baml_score = AlignmentScore(
                overall_score=alignment_score.overall_score,
                confidence=alignment_score.confidence,
                strategic_fit=alignment_score.strategic_fit,
                impact_potential=alignment_score.impact_potential,
                timeline_feasibility=alignment_score.timeline_feasibility,
                resource_efficiency=alignment_score.resource_efficiency,
                risk_assessment=alignment_score.risk_assessment,
                dependency_analysis=alignment_score.dependency_analysis,
                reasoning=alignment_score.reasoning,
                key_factors=alignment_score.key_factors,
                risk_factors=alignment_score.risk_factors,
                recommendations=alignment_score.recommendations
            )

            # Convert target to BAML format
            baml_target = ExecutiveTarget(
                id=target.id,
                title=target.title,
                description=target.description,
                category=TargetCategory(target.category.upper()),
                priority=TargetPriority(target.priority.upper()),
                owner=target.owner,
                owner_role=target.owner_role,
                deadline=target.deadline.isoformat() if target.deadline else None,
                success_metrics=target.success_metrics,
                target_value=target.target_value,
                baseline_value=target.baseline_value,
                business_domain=target.business_domain,
                stakeholders=target.stakeholders,
                dependencies=target.dependencies,
                constraints=target.constraints,
                status=target.status
            )

            # Create BAML canvas
            baml_canvas = self._create_baml_canvas(canvas_data)

            # Execute BAML feedback generation
            feedback_result = await b.GenerateAlignmentFeedback(
                target=baml_target,
                canvas=baml_canvas,
                alignment_score=baml_score,
                market_changes=market_changes or {},
                progress_data=progress_data or {}
            )

            # Convert to structured feedback
            feedback = AlignmentFeedback(
                target_id=target.id,
                initiative_id=canvas_data.get('id', 'unknown'),
                feedback_type="progress_update",
                description=feedback_result.get('primary_concern', ''),
                impact_on_alignment=feedback_result.get('alignment_trend', 'stable'),
                suggested_actions=feedback_result.get('recommended_actions', '').split(','),
                urgency=feedback_result.get('urgency_level', 'medium'),
                external_factors=feedback_result.get('market_response', '').split(','),
                reported_by="ExecutiveTargetScorer",
                reported_at=datetime.now()
            )

            logger.info(f"Alignment feedback generated with {feedback.urgency} urgency")
            return feedback

        except Exception as e:
            logger.error(f"Error generating alignment feedback: {e}")
            raise

    async def create_target_template(
        self,
        target_examples: List[str],
        enterprise_domain: str,
        template_name: str
    ) -> Dict[str, str]:
        """
        Create reusable target template from enterprise examples.

        Args:
            target_examples: List of example target descriptions
            enterprise_domain: Enterprise business domain
            template_name: Name for the template

        Returns:
            Structured template for creating similar targets
        """
        logger.info(f"Creating target template: {template_name}")

        try:
            template_result = await b.CreateTargetTemplate(
                target_examples=target_examples,
                enterprise_domain=enterprise_domain,
                template_name=template_name
            )

            logger.info(f"Target template created: {template_name}")
            return template_result

        except Exception as e:
            logger.error(f"Error creating target template: {e}")
            raise

    def _create_baml_canvas(self, canvas_data: Dict[str, Any]) -> DataBusinessCanvas:
        """Convert canvas data to BAML format"""
        return DataBusinessCanvas(
            value_propositions=canvas_data.get('value_propositions', []),
            key_activities=canvas_data.get('key_activities', []),
            key_resources=canvas_data.get('key_resources', []),
            key_partnerships=canvas_data.get('key_partnerships', []),
            customer_segments=canvas_data.get('customer_segments', []),
            customer_relationships=canvas_data.get('customer_relationships', []),
            channels=canvas_data.get('channels', []),
            cost_structure=canvas_data.get('cost_structure', []),
            revenue_streams=canvas_data.get('revenue_streams', []),
            data_assets=canvas_data.get('data_assets', []),
            intelligence_capabilities=canvas_data.get('intelligence_capabilities', []),
            competitive_advantages=canvas_data.get('competitive_advantages', []),
            business_domain=canvas_data.get('business_domain', ''),
            use_case_description=canvas_data.get('use_case_description', ''),
            timeline=canvas_data.get('timeline', ''),
            budget=canvas_data.get('budget', '')
        )

    async def batch_score_targets(
        self,
        targets: List[ModelExecutiveTarget],
        canvas_data: Dict[str, Any],
        enterprise_context: Dict[str, str]
    ) -> List[TargetAlignment]:
        """
        Score alignment for multiple targets efficiently.

        Args:
            targets: List of executive targets
            canvas_data: Data Business Canvas data
            enterprise_context: Enterprise context

        Returns:
            List of target alignments with scores
        """
        logger.info(f"Batch scoring {len(targets)} targets")

        alignments = []
        for target in targets:
            try:
                score = await self.score_strategic_alignment(
                    target, canvas_data, enterprise_context
                )

                alignment = TargetAlignment(
                    target_id=target.id,
                    initiative_id=canvas_data.get('id', 'unknown'),
                    alignment_score=score,
                    contribution_type="direct" if score.overall_score > 0.7 else "indirect",
                    expected_impact=f"High impact potential: {score.impact_potential:.2f}",
                    timeline_match="aligned" if score.timeline_feasibility > 0.6 else "delayed"
                )

                alignments.append(alignment)

            except Exception as e:
                logger.error(f"Error scoring target {target.id}: {e}")
                continue

        logger.info(f"Batch scoring completed for {len(alignments)} targets")
        return alignments