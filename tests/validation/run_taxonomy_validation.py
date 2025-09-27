#!/usr/bin/env python3
"""
Comprehensive SKOS Taxonomy Validation Test Runner
=================================================

Complete validation suite runner for SKOS taxonomy browsing capability.
Executes all validation tests and generates comprehensive reports.

This is the main entry point for validating taxonomy browsing readiness
for AWS Lambda deployment.

Usage:
    python tests/validation/run_taxonomy_validation.py

Or run individual components:
    python tests/validation/run_taxonomy_validation.py --component skos
    python tests/validation/run_taxonomy_validation.py --component sparql
    python tests/validation/run_taxonomy_validation.py --component assessment
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tests.validation.skos_taxonomy_validation import SKOSTaxonomyValidator
    from tests.validation.sparql_taxonomy_queries import TaxonomyBrowsingQueries
    from tests.validation.lambda_readiness_assessment import LambdaReadinessAssessor
except ImportError as e:
    print(f"Error importing validation modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('taxonomy_validation.log')
    ]
)
logger = logging.getLogger(__name__)

class TaxonomyValidationRunner:
    """Comprehensive taxonomy validation test runner"""

    def __init__(self):
        self.results = {
            "start_time": datetime.now().isoformat(),
            "components_run": [],
            "skos_validation": None,
            "sparql_queries": None,
            "lambda_assessment": None,
            "overall_success": False,
            "summary": {}
        }

    def run_skos_validation(self) -> Dict[str, Any]:
        """Run SKOS taxonomy structure validation"""
        logger.info("=" * 60)
        logger.info("RUNNING SKOS TAXONOMY VALIDATION")
        logger.info("=" * 60)

        try:
            validator = SKOSTaxonomyValidator()
            success, validation_results = validator.run_all_tests()

            # Create results summary
            results = {
                "success": success,
                "total_tests": len(validation_results),
                "passed_tests": sum(1 for r in validation_results if r.passed),
                "failed_tests": sum(1 for r in validation_results if not r.passed),
                "metrics": validator.metrics,
                "validation_results": validation_results,
                "overall_score": sum(r.score for r in validation_results) / len(validation_results) if validation_results else 0
            }

            # Log summary
            logger.info(f"SKOS Validation Results:")
            logger.info(f"  Tests passed: {results['passed_tests']}/{results['total_tests']}")
            logger.info(f"  Overall score: {results['overall_score']:.1f}%")
            logger.info(f"  Taxonomy completeness: {validator.metrics.taxonomy_completeness_score:.1f}%")
            logger.info(f"  Navigation readiness: {validator.metrics.navigation_readiness_score:.1f}%")

            if not success:
                logger.warning("Some SKOS validation tests failed!")
                for result in validation_results:
                    if not result.passed:
                        logger.warning(f"  ❌ {result.test_name}: {result.message}")

            return results

        except Exception as e:
            logger.error(f"SKOS validation failed with error: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0
            }

    def run_sparql_queries(self) -> Dict[str, Any]:
        """Run SPARQL taxonomy browsing queries"""
        logger.info("=" * 60)
        logger.info("RUNNING SPARQL TAXONOMY QUERIES")
        logger.info("=" * 60)

        try:
            query_tester = TaxonomyBrowsingQueries()
            results = query_tester.run_all_queries()

            # Calculate success metrics
            total_queries = results.get("total_queries", 0)
            successful_queries = results.get("successful_queries", 0)
            failed_queries = results.get("failed_queries", 0)

            success_rate = (successful_queries / total_queries * 100) if total_queries else 0

            # Check expectation fulfillment
            query_details = results.get("query_results", [])
            expectation_met = sum(1 for q in query_details if q.get("meets_expectations", False))
            expectation_rate = (expectation_met / total_queries * 100) if total_queries else 0

            overall_success = success_rate >= 80 and expectation_rate >= 70

            # Log summary
            logger.info(f"SPARQL Query Results:")
            logger.info(f"  Total queries: {total_queries}")
            logger.info(f"  Successful: {successful_queries} ({success_rate:.1f}%)")
            logger.info(f"  Failed: {failed_queries}")
            logger.info(f"  Meeting expectations: {expectation_met} ({expectation_rate:.1f}%)")

            if failed_queries > 0:
                logger.warning("Some SPARQL queries failed!")
                for query_result in query_details:
                    if not query_result.get("success", False):
                        logger.warning(f"  ❌ {query_result['name']}: {query_result.get('message', 'Unknown error')}")

            # Add success metrics to results
            results.update({
                "overall_success": overall_success,
                "success_rate": success_rate,
                "expectation_rate": expectation_rate
            })

            return results

        except Exception as e:
            logger.error(f"SPARQL queries failed with error: {e}")
            return {
                "overall_success": False,
                "error": str(e),
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0
            }

    def run_lambda_assessment(self) -> Dict[str, Any]:
        """Run Lambda readiness assessment"""
        logger.info("=" * 60)
        logger.info("RUNNING LAMBDA READINESS ASSESSMENT")
        logger.info("=" * 60)

        try:
            assessor = LambdaReadinessAssessor()
            report = assessor.run_comprehensive_assessment()

            # Log summary
            logger.info(f"Lambda Readiness Assessment Results:")
            logger.info(f"  Overall readiness: {report.overall_readiness_level.value}")
            logger.info(f"  Overall score: {report.overall_percentage:.1f}%")
            logger.info(f"  Taxonomy completeness: {report.taxonomy_completeness.percentage:.1f}%")
            logger.info(f"  Navigation effectiveness: {report.navigation_effectiveness.percentage:.1f}%")
            logger.info(f"  Implementation guidance: {report.implementation_guidance.percentage:.1f}%")
            logger.info(f"  SPARQL readiness: {report.sparql_query_readiness.percentage:.1f}%")

            # Log critical issues
            if report.critical_issues:
                logger.warning("Critical issues found:")
                for issue in report.critical_issues:
                    logger.warning(f"  ❌ {issue}")

            success = report.overall_readiness_level.value in ["Production Ready", "Needs Minor Improvements"]

            return {
                "success": success,
                "report": report,
                "overall_score": report.overall_percentage,
                "readiness_level": report.overall_readiness_level.value,
                "critical_issues": report.critical_issues
            }

        except Exception as e:
            logger.error(f"Lambda assessment failed with error: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_score": 0,
                "readiness_level": "Error"
            }

    def run_all_components(self) -> bool:
        """Run all validation components"""
        logger.info("Starting comprehensive SKOS taxonomy validation...")
        logger.info(f"Start time: {self.results['start_time']}")

        overall_success = True

        # Run SKOS validation
        self.results["skos_validation"] = self.run_skos_validation()
        self.results["components_run"].append("skos_validation")
        if not self.results["skos_validation"]["success"]:
            overall_success = False

        # Run SPARQL queries
        self.results["sparql_queries"] = self.run_sparql_queries()
        self.results["components_run"].append("sparql_queries")
        if not self.results["sparql_queries"]["overall_success"]:
            overall_success = False

        # Run Lambda assessment
        self.results["lambda_assessment"] = self.run_lambda_assessment()
        self.results["components_run"].append("lambda_assessment")
        if not self.results["lambda_assessment"]["success"]:
            overall_success = False

        self.results["overall_success"] = overall_success
        self.results["end_time"] = datetime.now().isoformat()

        return overall_success

    def run_component(self, component: str) -> bool:
        """Run a specific validation component"""
        logger.info(f"Running component: {component}")

        if component == "skos":
            self.results["skos_validation"] = self.run_skos_validation()
            self.results["components_run"].append("skos_validation")
            return self.results["skos_validation"]["success"]

        elif component == "sparql":
            self.results["sparql_queries"] = self.run_sparql_queries()
            self.results["components_run"].append("sparql_queries")
            return self.results["sparql_queries"]["overall_success"]

        elif component == "assessment":
            self.results["lambda_assessment"] = self.run_lambda_assessment()
            self.results["components_run"].append("lambda_assessment")
            return self.results["lambda_assessment"]["success"]

        else:
            logger.error(f"Unknown component: {component}")
            return False

    def generate_summary(self) -> None:
        """Generate validation summary"""
        logger.info("=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)

        summary = {}

        # Overall status
        if self.results["overall_success"]:
            status = "✅ READY FOR LAMBDA DEPLOYMENT"
            logger.info(status)
        else:
            status = "❌ NOT READY FOR LAMBDA DEPLOYMENT"
            logger.error(status)

        summary["overall_status"] = status

        # Component summaries
        components = []

        if "skos_validation" in self.results["components_run"]:
            skos = self.results["skos_validation"]
            component_status = "✅ PASS" if skos["success"] else "❌ FAIL"
            score = skos.get("overall_score", 0)
            logger.info(f"SKOS Validation: {component_status} (Score: {score:.1f}%)")
            components.append({"name": "SKOS Validation", "status": component_status, "score": score})

        if "sparql_queries" in self.results["components_run"]:
            sparql = self.results["sparql_queries"]
            component_status = "✅ PASS" if sparql["overall_success"] else "❌ FAIL"
            success_rate = sparql.get("success_rate", 0)
            logger.info(f"SPARQL Queries: {component_status} (Success: {success_rate:.1f}%)")
            components.append({"name": "SPARQL Queries", "status": component_status, "score": success_rate})

        if "lambda_assessment" in self.results["components_run"]:
            assessment = self.results["lambda_assessment"]
            component_status = "✅ READY" if assessment["success"] else "❌ NOT READY"
            overall_score = assessment.get("overall_score", 0)
            readiness = assessment.get("readiness_level", "Unknown")
            logger.info(f"Lambda Assessment: {component_status} ({readiness}, {overall_score:.1f}%)")
            components.append({"name": "Lambda Assessment", "status": component_status, "score": overall_score})

        summary["components"] = components

        # Key metrics
        if self.results.get("skos_validation") and "metrics" in self.results["skos_validation"]:
            metrics = self.results["skos_validation"]["metrics"]
            logger.info(f"Key Metrics:")
            logger.info(f"  ConceptSchemes: {metrics.concept_schemes_count}")
            logger.info(f"  Concepts: {metrics.concepts_count}")
            logger.info(f"  Hierarchical relationships: {metrics.hierarchical_relationships_count}")
            logger.info(f"  Max hierarchy depth: {metrics.max_hierarchy_depth}")

        # Critical issues
        if (self.results.get("lambda_assessment") and
            "critical_issues" in self.results["lambda_assessment"] and
            self.results["lambda_assessment"]["critical_issues"]):

            logger.warning("Critical Issues:")
            for issue in self.results["lambda_assessment"]["critical_issues"]:
                logger.warning(f"  ❌ {issue}")

        # Recommendations
        logger.info("\nNext Steps:")
        if self.results["overall_success"]:
            logger.info("  1. Deploy to Lambda staging environment")
            logger.info("  2. Conduct user acceptance testing")
            logger.info("  3. Implement monitoring and alerting")
        else:
            logger.info("  1. Address failing validation tests")
            logger.info("  2. Expand taxonomy content and relationships")
            logger.info("  3. Improve implementation guidance")
            logger.info("  4. Re-run validation after improvements")

        self.results["summary"] = summary

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="SKOS Taxonomy Validation Suite")
    parser.add_argument(
        "--component",
        choices=["skos", "sparql", "assessment"],
        help="Run specific component (default: run all)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = TaxonomyValidationRunner()

    try:
        if args.component:
            success = runner.run_component(args.component)
        else:
            success = runner.run_all_components()

        runner.generate_summary()

        # Create reports directory
        reports_dir = Path("reports/taxonomy_validation")
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save results
        import json
        results_file = reports_dir / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Convert any complex objects to serializable format
        serializable_results = {}
        for key, value in runner.results.items():
            if key == "skos_validation" and value and "metrics" in value:
                # Convert metrics object to dict
                from dataclasses import asdict
                value["metrics"] = asdict(value["metrics"])
            if key == "lambda_assessment" and value and "report" in value:
                # Convert report object to dict
                from dataclasses import asdict
                value["report"] = asdict(value["report"])
            serializable_results[key] = value

        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)

        logger.info(f"\nResults saved to: {results_file}")

        return success

    except KeyboardInterrupt:
        logger.info("\nValidation interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)