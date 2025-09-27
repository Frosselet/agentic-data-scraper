#!/usr/bin/env python3
"""
Lambda Readiness Assessment for SKOS Taxonomy Browsing
======================================================

Comprehensive assessment of taxonomy browsing readiness for AWS Lambda deployment.
This module evaluates taxonomy completeness, navigation pattern effectiveness,
implementation guidance quality, and overall readiness for Lambda users.

Features:
- Taxonomy Completeness Assessment
- Navigation Pattern Effectiveness Analysis
- Implementation Guidance Quality Evaluation
- Lambda-specific Readiness Scoring
- Detailed Recommendations and Action Items
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our validation modules
try:
    from tests.validation.skos_taxonomy_validation import SKOSTaxonomyValidator, ValidationResult, TaxonomyMetrics
    from tests.validation.sparql_taxonomy_queries import TaxonomyBrowsingQueries
except ImportError as e:
    print(f"Error importing validation modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReadinessLevel(Enum):
    """Lambda readiness levels"""
    PRODUCTION_READY = "Production Ready"
    NEEDS_MINOR_IMPROVEMENTS = "Needs Minor Improvements"
    NEEDS_MAJOR_IMPROVEMENTS = "Needs Major Improvements"
    NOT_READY = "Not Ready"

@dataclass
class AssessmentCriteria:
    """Criteria for Lambda readiness assessment"""
    taxonomy_completeness_threshold: float = 75.0
    navigation_effectiveness_threshold: float = 80.0
    implementation_guidance_threshold: float = 70.0
    overall_readiness_threshold: float = 75.0

@dataclass
class ReadinessScore:
    """Individual readiness score component"""
    category: str
    score: float
    max_score: float
    percentage: float
    status: str
    recommendations: List[str] = field(default_factory=list)

@dataclass
class LambdaReadinessReport:
    """Complete Lambda readiness assessment report"""
    assessment_date: str
    overall_readiness_level: ReadinessLevel
    overall_score: float
    max_possible_score: float
    overall_percentage: float

    # Component scores
    taxonomy_completeness: ReadinessScore
    navigation_effectiveness: ReadinessScore
    implementation_guidance: ReadinessScore
    sparql_query_readiness: ReadinessScore

    # Detailed metrics
    taxonomy_metrics: Dict[str, Any]
    validation_results: List[Dict[str, Any]]
    query_results: Dict[str, Any]

    # Recommendations
    critical_issues: List[str] = field(default_factory=list)
    improvement_recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    # Lambda-specific assessments
    lambda_development_readiness: Dict[str, Any] = field(default_factory=dict)
    lambda_deployment_readiness: Dict[str, Any] = field(default_factory=dict)
    lambda_user_experience_readiness: Dict[str, Any] = field(default_factory=dict)

class LambdaReadinessAssessor:
    """Comprehensive Lambda readiness assessment"""

    def __init__(self, criteria: Optional[AssessmentCriteria] = None):
        self.criteria = criteria or AssessmentCriteria()
        self.taxonomy_validator = SKOSTaxonomyValidator()
        self.query_tester = TaxonomyBrowsingQueries()

    def assess_taxonomy_completeness(self, metrics: TaxonomyMetrics) -> ReadinessScore:
        """Assess taxonomy completeness for Lambda deployment"""
        recommendations = []

        # Component scores
        scheme_score = min(metrics.concept_schemes_count * 30, 100)  # Max at ~3-4 schemes
        concept_score = min(metrics.concepts_count * 8, 100)  # Max at ~12-15 concepts
        hierarchy_score = min(metrics.hierarchical_relationships_count * 4, 100)  # Max at ~25 relationships
        depth_score = min(metrics.max_hierarchy_depth * 25, 100)  # Max at 4 levels

        # Calculate weighted score
        total_score = (
            scheme_score * 0.25 +
            concept_score * 0.35 +
            hierarchy_score * 0.25 +
            depth_score * 0.15
        )

        # Generate recommendations
        if scheme_score < 80:
            recommendations.append("Add more ConceptSchemes to cover different domain areas")
        if concept_score < 80:
            recommendations.append("Expand concept coverage within existing schemes")
        if hierarchy_score < 80:
            recommendations.append("Strengthen hierarchical relationships between concepts")
        if depth_score < 80:
            recommendations.append("Develop deeper taxonomy hierarchies for better navigation")

        status = "Good" if total_score >= 80 else "Needs Improvement" if total_score >= 60 else "Poor"

        return ReadinessScore(
            category="Taxonomy Completeness",
            score=total_score,
            max_score=100.0,
            percentage=total_score,
            status=status,
            recommendations=recommendations
        )

    def assess_navigation_effectiveness(self, validation_results: List[ValidationResult]) -> ReadinessScore:
        """Assess navigation pattern effectiveness"""
        recommendations = []

        # Extract scores from validation results
        scores = {}
        for result in validation_results:
            scores[result.test_name] = result.score

        # Calculate component scores
        scheme_nav_score = scores.get("ConceptScheme Navigation", 0)
        hierarchy_score = scores.get("Hierarchical Browsing", 0)
        relation_score = scores.get("Related Concept Discovery", 0)

        # Weighted average
        total_score = (
            scheme_nav_score * 0.4 +
            hierarchy_score * 0.4 +
            relation_score * 0.2
        )

        # Generate recommendations based on individual scores
        if scheme_nav_score < 80:
            recommendations.append("Improve ConceptScheme metadata and cross-references")
        if hierarchy_score < 80:
            recommendations.append("Fix bidirectional relationships and reduce orphaned concepts")
        if relation_score < 80:
            recommendations.append("Add more cross-domain concept relationships")

        # Navigation-specific recommendations
        if total_score < 85:
            recommendations.extend([
                "Implement breadcrumb navigation support",
                "Add concept search and filtering capabilities",
                "Provide alternative navigation paths"
            ])

        status = "Excellent" if total_score >= 85 else "Good" if total_score >= 70 else "Needs Improvement"

        return ReadinessScore(
            category="Navigation Effectiveness",
            score=total_score,
            max_score=100.0,
            percentage=total_score,
            status=status,
            recommendations=recommendations
        )

    def assess_implementation_guidance(self, validation_results: List[ValidationResult],
                                     metrics: TaxonomyMetrics) -> ReadinessScore:
        """Assess quality of implementation guidance"""
        recommendations = []

        # Get examples and scope notes score
        guidance_result = next((r for r in validation_results if r.test_name == "Examples and Scope Notes"), None)
        guidance_score = guidance_result.score if guidance_result else 0

        # Additional Lambda-specific assessments
        example_coverage = (metrics.concepts_with_examples / metrics.concepts_count) * 100 if metrics.concepts_count else 0
        scope_coverage = (metrics.concepts_with_scope_notes / metrics.concepts_count) * 100 if metrics.concepts_count else 0

        # Lambda readiness factors
        lambda_factor = 1.0
        if guidance_result and guidance_result.details:
            lambda_readiness = guidance_result.details.get("lambda_readiness", 0)
            detail_quality = guidance_result.details.get("detail_quality", 0)

            # Boost score for Lambda-specific content
            lambda_factor = 1.0 + (lambda_readiness / 100 * 0.2)  # Up to 20% boost
            lambda_factor += (detail_quality / 100 * 0.1)  # Up to 10% boost

        total_score = min(guidance_score * lambda_factor, 100)

        # Generate recommendations
        if example_coverage < 60:
            recommendations.append("Add concrete examples to more concepts")
        if scope_coverage < 50:
            recommendations.append("Add detailed scope notes to key concepts")
        if total_score < 70:
            recommendations.extend([
                "Include more Lambda-specific implementation guidance",
                "Add architectural patterns and best practices",
                "Provide code snippets and configuration examples"
            ])

        status = "Excellent" if total_score >= 80 else "Good" if total_score >= 65 else "Needs Improvement"

        return ReadinessScore(
            category="Implementation Guidance",
            score=total_score,
            max_score=100.0,
            percentage=total_score,
            status=status,
            recommendations=recommendations
        )

    def assess_sparql_query_readiness(self, query_results: Dict[str, Any]) -> ReadinessScore:
        """Assess SPARQL query readiness for Lambda implementation"""
        recommendations = []

        # Extract metrics from query results
        total_queries = query_results.get("total_queries", 0)
        successful_queries = query_results.get("successful_queries", 0)
        failed_queries = query_results.get("failed_queries", 0)

        # Calculate success rate
        success_rate = (successful_queries / total_queries * 100) if total_queries else 0

        # Check expectation fulfillment
        query_details = query_results.get("query_results", [])
        expectation_met = sum(1 for q in query_details if q.get("meets_expectations", False))
        expectation_rate = (expectation_met / total_queries * 100) if total_queries else 0

        # Calculate complexity coverage
        use_cases_covered = len(set(q.get("use_case", "") for q in query_details if q.get("success", False)))
        complexity_score = min(use_cases_covered * 12.5, 100)  # Max at 8 use cases

        # Weighted total score
        total_score = (
            success_rate * 0.4 +
            expectation_rate * 0.4 +
            complexity_score * 0.2
        )

        # Generate recommendations
        if success_rate < 90:
            recommendations.append("Fix failing SPARQL queries")
        if expectation_rate < 80:
            recommendations.append("Improve taxonomy content to meet query expectations")
        if complexity_score < 80:
            recommendations.append("Add more diverse query patterns and use cases")

        # Lambda-specific SPARQL recommendations
        recommendations.extend([
            "Optimize queries for Lambda execution time limits",
            "Add query result caching strategies",
            "Implement query batching for large result sets"
        ])

        status = "Ready" if total_score >= 85 else "Needs Tuning" if total_score >= 70 else "Needs Work"

        return ReadinessScore(
            category="SPARQL Query Readiness",
            score=total_score,
            max_score=100.0,
            percentage=total_score,
            status=status,
            recommendations=recommendations
        )

    def assess_lambda_specific_readiness(self, overall_scores: Dict[str, ReadinessScore],
                                       metrics: TaxonomyMetrics) -> Dict[str, Dict[str, Any]]:
        """Assess Lambda-specific deployment readiness factors"""

        # Development Readiness
        development_readiness = {
            "code_generation_ready": overall_scores["implementation_guidance"].score >= 70,
            "api_pattern_ready": overall_scores["sparql_query_readiness"].score >= 80,
            "documentation_complete": overall_scores["implementation_guidance"].score >= 65,
            "score": (
                (80 if overall_scores["implementation_guidance"].score >= 70 else 40) +
                (80 if overall_scores["sparql_query_readiness"].score >= 80 else 40) +
                (40 if overall_scores["implementation_guidance"].score >= 65 else 20)
            ) / 2,
            "recommendations": [
                "Implement semantic reasoning caching for Lambda cold starts",
                "Create Lambda layers for RDFLib and ontology files",
                "Design stateless query execution patterns"
            ]
        }

        # Deployment Readiness
        deployment_readiness = {
            "performance_optimized": metrics.concepts_count < 100,  # Manageable size
            "memory_efficient": metrics.hierarchical_relationships_count < 200,  # Reasonable complexity
            "query_optimized": overall_scores["sparql_query_readiness"].score >= 75,
            "score": (
                (30 if metrics.concepts_count < 100 else 15) +
                (30 if metrics.hierarchical_relationships_count < 200 else 15) +
                (40 if overall_scores["sparql_query_readiness"].score >= 75 else 20)
            ),
            "recommendations": [
                "Pre-compute common taxonomy queries",
                "Implement concept indexes for fast lookup",
                "Use compressed ontology formats for Lambda deployment"
            ]
        }

        # User Experience Readiness
        ux_readiness = {
            "intuitive_navigation": overall_scores["navigation_effectiveness"].score >= 80,
            "comprehensive_examples": metrics.concepts_with_examples >= (metrics.concepts_count * 0.6),
            "clear_guidance": overall_scores["implementation_guidance"].score >= 70,
            "score": (
                (40 if overall_scores["navigation_effectiveness"].score >= 80 else 20) +
                (30 if metrics.concepts_with_examples >= (metrics.concepts_count * 0.6) else 15) +
                (30 if overall_scores["implementation_guidance"].score >= 70 else 15)
            ),
            "recommendations": [
                "Implement taxonomy browsing UI components",
                "Add concept search and filtering",
                "Provide interactive taxonomy exploration"
            ]
        }

        return {
            "development": development_readiness,
            "deployment": deployment_readiness,
            "user_experience": ux_readiness
        }

    def generate_overall_readiness_level(self, overall_score: float) -> ReadinessLevel:
        """Determine overall readiness level"""
        if overall_score >= 85:
            return ReadinessLevel.PRODUCTION_READY
        elif overall_score >= 75:
            return ReadinessLevel.NEEDS_MINOR_IMPROVEMENTS
        elif overall_score >= 60:
            return ReadinessLevel.NEEDS_MAJOR_IMPROVEMENTS
        else:
            return ReadinessLevel.NOT_READY

    def run_comprehensive_assessment(self) -> LambdaReadinessReport:
        """Run complete Lambda readiness assessment"""
        logger.info("Starting comprehensive Lambda readiness assessment...")

        # Run taxonomy validation
        logger.info("Running taxonomy validation...")
        success, validation_results = self.taxonomy_validator.run_all_tests()
        metrics = self.taxonomy_validator.metrics

        # Run SPARQL query tests
        logger.info("Running SPARQL query tests...")
        query_results = self.query_tester.run_all_queries()

        # Assess individual components
        logger.info("Assessing component readiness...")
        taxonomy_completeness = self.assess_taxonomy_completeness(metrics)
        navigation_effectiveness = self.assess_navigation_effectiveness(validation_results)
        implementation_guidance = self.assess_implementation_guidance(validation_results, metrics)
        sparql_readiness = self.assess_sparql_query_readiness(query_results)

        # Calculate overall score
        overall_scores = {
            "taxonomy_completeness": taxonomy_completeness,
            "navigation_effectiveness": navigation_effectiveness,
            "implementation_guidance": implementation_guidance,
            "sparql_query_readiness": sparql_readiness
        }

        overall_score = (
            taxonomy_completeness.score * 0.25 +
            navigation_effectiveness.score * 0.30 +
            implementation_guidance.score * 0.25 +
            sparql_readiness.score * 0.20
        )

        # Lambda-specific assessments
        lambda_specific = self.assess_lambda_specific_readiness(overall_scores, metrics)

        # Generate recommendations
        critical_issues = []
        improvement_recommendations = []
        next_steps = []

        # Collect recommendations from all components
        for score in overall_scores.values():
            improvement_recommendations.extend(score.recommendations)

        # Critical issues
        if overall_score < 60:
            critical_issues.append("Overall taxonomy readiness below acceptable threshold")
        if not success:
            critical_issues.append("Taxonomy validation tests failing")
        if query_results.get("failed_queries", 0) > 2:
            critical_issues.append("Multiple SPARQL queries failing")

        # Next steps based on readiness level
        readiness_level = self.generate_overall_readiness_level(overall_score)

        if readiness_level == ReadinessLevel.PRODUCTION_READY:
            next_steps = [
                "Deploy to Lambda staging environment",
                "Conduct user acceptance testing",
                "Implement monitoring and alerting"
            ]
        elif readiness_level == ReadinessLevel.NEEDS_MINOR_IMPROVEMENTS:
            next_steps = [
                "Address high-priority recommendations",
                "Expand test coverage",
                "Prepare for staging deployment"
            ]
        else:
            next_steps = [
                "Address critical issues first",
                "Expand taxonomy content",
                "Improve validation test results"
            ]

        return LambdaReadinessReport(
            assessment_date=datetime.now().isoformat(),
            overall_readiness_level=readiness_level,
            overall_score=overall_score,
            max_possible_score=100.0,
            overall_percentage=overall_score,
            taxonomy_completeness=taxonomy_completeness,
            navigation_effectiveness=navigation_effectiveness,
            implementation_guidance=implementation_guidance,
            sparql_query_readiness=sparql_readiness,
            taxonomy_metrics=asdict(metrics),
            validation_results=[asdict(vr) for vr in validation_results],
            query_results=query_results,
            critical_issues=critical_issues,
            improvement_recommendations=list(set(improvement_recommendations)),  # Remove duplicates
            next_steps=next_steps,
            lambda_development_readiness=lambda_specific["development"],
            lambda_deployment_readiness=lambda_specific["deployment"],
            lambda_user_experience_readiness=lambda_specific["user_experience"]
        )

def generate_html_report(report: LambdaReadinessReport, output_path: Path) -> None:
    """Generate HTML assessment report"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lambda Readiness Assessment Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
            .score {{ font-size: 24px; font-weight: bold; }}
            .ready {{ color: #27ae60; }}
            .minor {{ color: #f39c12; }}
            .major {{ color: #e74c3c; }}
            .not-ready {{ color: #c0392b; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; }}
            .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .critical {{ background: #f8d7da; }}
            .query-results {{ max-height: 400px; overflow-y: auto; background: #f8f9fa; padding: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>SKOS Taxonomy Browsing - Lambda Readiness Assessment</h1>
            <p><strong>Assessment Date:</strong> {report.assessment_date}</p>
            <p class="score {report.overall_readiness_level.value.lower().replace(' ', '-')}">
                Overall Readiness: {report.overall_readiness_level.value} ({report.overall_percentage:.1f}%)
            </p>
        </div>

        <div class="section">
            <h2>Component Scores</h2>
            <div class="metrics">
                <div class="metric-card">
                    <h3>Taxonomy Completeness</h3>
                    <p><strong>Score:</strong> {report.taxonomy_completeness.percentage:.1f}%</p>
                    <p><strong>Status:</strong> {report.taxonomy_completeness.status}</p>
                </div>
                <div class="metric-card">
                    <h3>Navigation Effectiveness</h3>
                    <p><strong>Score:</strong> {report.navigation_effectiveness.percentage:.1f}%</p>
                    <p><strong>Status:</strong> {report.navigation_effectiveness.status}</p>
                </div>
                <div class="metric-card">
                    <h3>Implementation Guidance</h3>
                    <p><strong>Score:</strong> {report.implementation_guidance.percentage:.1f}%</p>
                    <p><strong>Status:</strong> {report.implementation_guidance.status}</p>
                </div>
                <div class="metric-card">
                    <h3>SPARQL Query Readiness</h3>
                    <p><strong>Score:</strong> {report.sparql_query_readiness.percentage:.1f}%</p>
                    <p><strong>Status:</strong> {report.sparql_query_readiness.status}</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Lambda-Specific Readiness</h2>
            <div class="metrics">
                <div class="metric-card">
                    <h3>Development Readiness</h3>
                    <p><strong>Score:</strong> {report.lambda_development_readiness['score']:.1f}%</p>
                    <p>Code Generation: {'✅' if report.lambda_development_readiness['code_generation_ready'] else '❌'}</p>
                    <p>API Patterns: {'✅' if report.lambda_development_readiness['api_pattern_ready'] else '❌'}</p>
                </div>
                <div class="metric-card">
                    <h3>Deployment Readiness</h3>
                    <p><strong>Score:</strong> {report.lambda_deployment_readiness['score']:.1f}%</p>
                    <p>Performance: {'✅' if report.lambda_deployment_readiness['performance_optimized'] else '❌'}</p>
                    <p>Memory Efficient: {'✅' if report.lambda_deployment_readiness['memory_efficient'] else '❌'}</p>
                </div>
                <div class="metric-card">
                    <h3>User Experience Readiness</h3>
                    <p><strong>Score:</strong> {report.lambda_user_experience_readiness['score']:.1f}%</p>
                    <p>Navigation: {'✅' if report.lambda_user_experience_readiness['intuitive_navigation'] else '❌'}</p>
                    <p>Examples: {'✅' if report.lambda_user_experience_readiness['comprehensive_examples'] else '❌'}</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Taxonomy Metrics</h2>
            <div class="metrics">
                <div class="metric-card">
                    <p><strong>ConceptSchemes:</strong> {report.taxonomy_metrics['concept_schemes_count']}</p>
                    <p><strong>Concepts:</strong> {report.taxonomy_metrics['concepts_count']}</p>
                    <p><strong>Hierarchical Relationships:</strong> {report.taxonomy_metrics['hierarchical_relationships_count']}</p>
                    <p><strong>Related Relationships:</strong> {report.taxonomy_metrics['related_relationships_count']}</p>
                </div>
                <div class="metric-card">
                    <p><strong>Max Hierarchy Depth:</strong> {report.taxonomy_metrics['max_hierarchy_depth']}</p>
                    <p><strong>Avg Hierarchy Depth:</strong> {report.taxonomy_metrics['avg_hierarchy_depth']:.2f}</p>
                    <p><strong>Concepts with Examples:</strong> {report.taxonomy_metrics['concepts_with_examples']}</p>
                    <p><strong>Concepts with Scope Notes:</strong> {report.taxonomy_metrics['concepts_with_scope_notes']}</p>
                </div>
            </div>
        </div>

        {"<div class='section'><h2>Critical Issues</h2><div class='recommendations critical'><ul>" + "".join(f"<li>{issue}</li>" for issue in report.critical_issues) + "</ul></div></div>" if report.critical_issues else ""}

        <div class="section">
            <h2>Improvement Recommendations</h2>
            <div class="recommendations">
                <ul>
                    {"".join(f"<li>{rec}</li>" for rec in report.improvement_recommendations[:10])}
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>Next Steps</h2>
            <div class="recommendations">
                <ol>
                    {"".join(f"<li>{step}</li>" for step in report.next_steps)}
                </ol>
            </div>
        </div>

        <div class="section">
            <h2>SPARQL Query Results Summary</h2>
            <div class="query-results">
                <p><strong>Total Queries:</strong> {report.query_results.get('total_queries', 0)}</p>
                <p><strong>Successful:</strong> {report.query_results.get('successful_queries', 0)}</p>
                <p><strong>Failed:</strong> {report.query_results.get('failed_queries', 0)}</p>
            </div>
        </div>
    </body>
    </html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """Main assessment execution"""
    print("Lambda Readiness Assessment for SKOS Taxonomy Browsing")
    print("=" * 60)

    assessor = LambdaReadinessAssessor()
    report = assessor.run_comprehensive_assessment()

    # Print summary
    print(f"\nAssessment Complete!")
    print(f"Overall Readiness: {report.overall_readiness_level.value}")
    print(f"Overall Score: {report.overall_percentage:.1f}%")
    print()

    print("Component Scores:")
    print(f"  Taxonomy Completeness: {report.taxonomy_completeness.percentage:.1f}% ({report.taxonomy_completeness.status})")
    print(f"  Navigation Effectiveness: {report.navigation_effectiveness.percentage:.1f}% ({report.navigation_effectiveness.status})")
    print(f"  Implementation Guidance: {report.implementation_guidance.percentage:.1f}% ({report.implementation_guidance.status})")
    print(f"  SPARQL Query Readiness: {report.sparql_query_readiness.percentage:.1f}% ({report.sparql_query_readiness.status})")
    print()

    print("Lambda-Specific Readiness:")
    print(f"  Development: {report.lambda_development_readiness['score']:.1f}%")
    print(f"  Deployment: {report.lambda_deployment_readiness['score']:.1f}%")
    print(f"  User Experience: {report.lambda_user_experience_readiness['score']:.1f}%")
    print()

    if report.critical_issues:
        print("Critical Issues:")
        for issue in report.critical_issues:
            print(f"  ❌ {issue}")
        print()

    print("Next Steps:")
    for i, step in enumerate(report.next_steps, 1):
        print(f"  {i}. {step}")

    # Save reports
    reports_dir = Path("reports/taxonomy_validation")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON report
    json_path = reports_dir / f"lambda_readiness_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(asdict(report), f, indent=2, default=str)

    # Save HTML report
    html_path = reports_dir / f"lambda_readiness_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    generate_html_report(report, html_path)

    print(f"\nReports saved:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}")

    return report.overall_readiness_level in [ReadinessLevel.PRODUCTION_READY, ReadinessLevel.NEEDS_MINOR_IMPROVEMENTS]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)