"""
Enhanced Discovery Agent using BAML for intelligent data source discovery.

Implements agentic behavior for both known source analysis and zero-start discovery,
with comprehensive metadata collection for downstream workflow prepopulation.
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from pathlib import Path

# Add project root to path for baml_client import
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from baml_client import b
from baml_client.types import (
    DiscoveryPath, DataSourceType, UpdateFrequency,
    DataSourceMetadata, KnownSourceRequest, ZeroStartDiscovery,
    DiscoveryResult, WorkflowPrepopulation
)

from ..models.enhanced_discovery import (
    DiscoveryPath as ModelDiscoveryPath,
    DataSourceMetadata as ModelDataSourceMetadata,
    DiscoveryResult as ModelDiscoveryResult,
    WorkflowPrepopulation as ModelWorkflowPrepopulation
)

logger = logging.getLogger(__name__)


class EnhancedDiscoveryAgent:
    """
    Intelligent Data Discovery Agent with BAML-powered agentic behavior.

    Provides two discovery paths:
    1. Known Sources: Deep metadata analysis of provided URLs
    2. Zero-Start: Internet research and source recommendation

    Automatically prepopulates downstream workflow steps with discovered metadata.
    """

    def __init__(self):
        self.session_id = f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Initialized Enhanced Discovery Agent: {self.session_id}")

    async def discover_known_sources(
        self,
        source_urls: List[str],
        canvas_data: Dict[str, Any],
        expected_source_type: Optional[str] = None,
        specific_datasets: Optional[List[str]] = None,
        collection_depth: str = "detailed"
    ) -> ModelDiscoveryResult:
        """
        Analyze known data sources and extract comprehensive metadata.

        Args:
            source_urls: List of known data source URLs to analyze
            canvas_data: Data from Value & Users canvas for context
            expected_source_type: Expected type of data source
            specific_datasets: Specific datasets within sources to focus on
            collection_depth: Level of analysis ("basic", "detailed", "comprehensive")

        Returns:
            DiscoveryResult with metadata and workflow prepopulation data
        """
        logger.info(f"Starting known source discovery for {len(source_urls)} sources")
        start_time = datetime.now()

        try:
            # Create BAML request
            request = KnownSourceRequest(
                source_urls=source_urls,
                expected_source_type=self._convert_source_type(expected_source_type),
                specific_datasets=specific_datasets,
                collection_depth=collection_depth
            )

            # Execute BAML discovery agent
            logger.info("Invoking BAML DiscoverKnownSources agent...")
            discovered_metadata = await b.DiscoverKnownSources(request)

            # Analyze source fitness for business context
            fitness_analyses = []
            for metadata in discovered_metadata:
                fitness = await b.AnalyzeSourceFitness(
                    source_metadata=metadata,
                    business_context=canvas_data
                )
                fitness_analyses.append(fitness)

            # Prepare workflow prepopulation data
            workflow_prep = await b.PrepareWorkflowData(
                discovered_sources=discovered_metadata,
                canvas_data=canvas_data
            )

            # Calculate discovery metrics
            duration = (datetime.now() - start_time).total_seconds()

            result = ModelDiscoveryResult(
                discovery_path=ModelDiscoveryPath.KNOWN_SOURCE,
                discovered_sources=self._convert_metadata_list(discovered_metadata),
                total_sources_found=len(discovered_metadata),
                search_queries_used=[f"Known source: {url}" for url in source_urls],
                discovery_duration_seconds=duration,
                recommended_next_steps=self._extract_next_steps(fitness_analyses),
                prefilled_operations_data=workflow_prep.operations_data,
                prefilled_governance_data=workflow_prep.governance_data
            )

            logger.info(f"Known source discovery completed in {duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error in known source discovery: {e}")
            raise

    async def discover_from_scratch(
        self,
        business_domain: str,
        use_case_description: str,
        required_data_types: List[str],
        canvas_data: Dict[str, Any],
        max_sources: int = 5,
        geographic_scope: Optional[str] = None,
        time_period_requirements: Optional[str] = None,
        preferred_source_types: Optional[List[str]] = None,
        exclude_paid_sources: bool = False,
        require_api_access: bool = False,
        search_strategy: str = "focused",
        include_academic: bool = True,
        include_government: bool = True,
        include_commercial: bool = True
    ) -> ModelDiscoveryResult:
        """
        Discover data sources from scratch using intelligent internet research.

        Args:
            business_domain: Business domain for the data pipeline
            use_case_description: Detailed description of the intended use case
            required_data_types: Types of data needed
            canvas_data: Data from Value & Users canvas for context
            max_sources: Maximum number of sources to discover
            geographic_scope: Geographic limitations/requirements
            time_period_requirements: Time period constraints
            preferred_source_types: Preferred types of data sources
            exclude_paid_sources: Whether to exclude paid/premium sources
            require_api_access: Whether API access is required
            search_strategy: Search approach ("comprehensive", "focused", "quick")
            include_academic: Include academic/research sources
            include_government: Include government data sources
            include_commercial: Include commercial data sources

        Returns:
            DiscoveryResult with discovered sources and workflow prepopulation
        """
        logger.info(f"Starting zero-start discovery for domain: {business_domain}")
        start_time = datetime.now()

        try:
            # Create BAML discovery request
            request = ZeroStartDiscovery(
                business_domain=business_domain,
                use_case_description=use_case_description,
                required_data_types=required_data_types,
                geographic_scope=geographic_scope,
                time_period_requirements=time_period_requirements,
                max_sources_to_find=max_sources,
                preferred_source_types=self._convert_source_types(preferred_source_types),
                exclude_paid_sources=exclude_paid_sources,
                require_api_access=require_api_access,
                search_strategy=search_strategy,
                include_academic_sources=include_academic,
                include_government_sources=include_government,
                include_commercial_sources=include_commercial
            )

            # Execute BAML zero-start discovery
            logger.info("Invoking BAML DiscoverFromScratch agent...")
            discovery_result = await b.DiscoverFromScratch(request)

            # Prepare workflow prepopulation data with additional context
            workflow_prep = await b.PrepareWorkflowData(
                discovered_sources=discovery_result.discovered_sources,
                canvas_data={**canvas_data,
                           "discovery_strategy": search_strategy,
                           "business_domain": business_domain,
                           "use_case": use_case_description}
            )

            # Convert BAML result to model format
            result = ModelDiscoveryResult(
                discovery_path=ModelDiscoveryPath.ZERO_START,
                discovered_sources=self._convert_metadata_list(discovery_result.discovered_sources),
                total_sources_found=discovery_result.total_sources_found,
                search_queries_used=discovery_result.search_queries_used,
                discovery_duration_seconds=discovery_result.discovery_duration_seconds,
                recommended_next_steps=discovery_result.recommended_next_steps,
                prefilled_operations_data=discovery_result.prefilled_operations_data,
                prefilled_governance_data=discovery_result.prefilled_governance_data
            )

            duration = (datetime.now() - start_time).total_seconds()
            result.discovery_duration_seconds = duration

            logger.info(f"Zero-start discovery completed in {duration:.2f}s, found {len(result.discovered_sources)} sources")
            return result

        except Exception as e:
            logger.error(f"Error in zero-start discovery: {e}")
            raise

    async def analyze_source_portfolio(
        self,
        discovered_sources: List[ModelDataSourceMetadata],
        canvas_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the portfolio of discovered sources for complementarity and gaps.

        Args:
            discovered_sources: List of discovered data source metadata
            canvas_data: Business context from Value & Users canvas

        Returns:
            Portfolio analysis with recommendations
        """
        logger.info(f"Analyzing portfolio of {len(discovered_sources)} sources")

        try:
            # Convert to BAML format and analyze each source
            baml_sources = [self._convert_to_baml_metadata(src) for src in discovered_sources]

            analyses = []
            for source in baml_sources:
                fitness = await b.AnalyzeSourceFitness(
                    source_metadata=source,
                    business_context=canvas_data
                )
                analyses.append({
                    'source_name': source.name,
                    'fitness_analysis': fitness
                })

            # Aggregate portfolio insights
            portfolio_analysis = {
                'total_sources': len(discovered_sources),
                'source_types': list(set(src.source_type for src in discovered_sources)),
                'average_quality_score': sum(src.data_quality_score or 0.0 for src in discovered_sources) / len(discovered_sources),
                'average_relevance_score': sum(src.relevance_score for src in discovered_sources) / len(discovered_sources),
                'authentication_required': sum(1 for src in discovered_sources if src.authentication_required),
                'api_available': sum(1 for src in discovered_sources if 'api' in src.access_method.lower()),
                'source_analyses': analyses,
                'coverage_gaps': self._identify_coverage_gaps(discovered_sources, canvas_data),
                'integration_complexity': self._assess_integration_complexity(discovered_sources),
                'risk_factors': self._identify_risk_factors(discovered_sources)
            }

            logger.info("Portfolio analysis completed")
            return portfolio_analysis

        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            raise

    def _convert_source_type(self, source_type: Optional[str]) -> Optional[DataSourceType]:
        """Convert string source type to BAML enum"""
        if not source_type:
            return None

        type_mapping = {
            'api': DataSourceType.API,
            'database': DataSourceType.DATABASE,
            'file_system': DataSourceType.FILE_SYSTEM,
            'web_scraping': DataSourceType.WEB_SCRAPING,
            'stream': DataSourceType.STREAM,
            'cloud_storage': DataSourceType.CLOUD_STORAGE
        }
        return type_mapping.get(source_type.lower())

    def _convert_source_types(self, source_types: Optional[List[str]]) -> Optional[List[DataSourceType]]:
        """Convert list of string source types to BAML enums"""
        if not source_types:
            return None
        return [self._convert_source_type(st) for st in source_types if self._convert_source_type(st)]

    def _convert_metadata_list(self, baml_metadata: List[DataSourceMetadata]) -> List[ModelDataSourceMetadata]:
        """Convert BAML metadata list to model format"""
        result = []
        for metadata in baml_metadata:
            # Convert BAML metadata to model metadata
            model_metadata = ModelDataSourceMetadata(
                name=metadata.name,
                url=metadata.url,
                description=metadata.description,
                source_type=metadata.source_type.value,
                access_method=metadata.access_method,
                authentication_required=metadata.authentication_required,
                authentication_method=metadata.authentication_method,
                rate_limits=metadata.rate_limits or {},
                data_formats=metadata.data_formats or [],
                schema_available=metadata.schema_available,
                schema_url=metadata.schema_url,
                sample_data_url=metadata.sample_data_url,
                data_volume_estimate=metadata.data_volume_estimate,
                update_frequency=metadata.update_frequency.value if metadata.update_frequency else None,
                historical_data_available=metadata.historical_data_available,
                historical_range=metadata.historical_range,
                data_quality_score=metadata.data_quality_score,
                completeness_estimate=metadata.completeness_estimate,
                accuracy_indicators=metadata.accuracy_indicators or [],
                known_data_issues=metadata.known_data_issues or [],
                license_type=metadata.license_type,
                terms_of_use_url=metadata.terms_of_use_url,
                privacy_considerations=metadata.privacy_considerations or [],
                compliance_standards=metadata.compliance_standards or [],
                relevance_score=metadata.relevance_score,
                business_domains=metadata.business_domains or [],
                use_cases=metadata.use_cases or [],
                discovered_at=datetime.now(),
                discovery_method=metadata.discovery_method,
                confidence_score=metadata.confidence_score
            )
            result.append(model_metadata)
        return result

    def _convert_to_baml_metadata(self, model_metadata: ModelDataSourceMetadata) -> DataSourceMetadata:
        """Convert model metadata to BAML format"""
        return DataSourceMetadata(
            name=model_metadata.name,
            url=model_metadata.url,
            description=model_metadata.description,
            source_type=DataSourceType(model_metadata.source_type),
            access_method=model_metadata.access_method,
            authentication_required=model_metadata.authentication_required,
            authentication_method=model_metadata.authentication_method,
            rate_limits=model_metadata.rate_limits,
            data_formats=model_metadata.data_formats,
            schema_available=model_metadata.schema_available,
            schema_url=model_metadata.schema_url,
            sample_data_url=model_metadata.sample_data_url,
            data_volume_estimate=model_metadata.data_volume_estimate,
            update_frequency=UpdateFrequency(model_metadata.update_frequency) if model_metadata.update_frequency else None,
            historical_data_available=model_metadata.historical_data_available,
            historical_range=model_metadata.historical_range,
            data_quality_score=model_metadata.data_quality_score,
            completeness_estimate=model_metadata.completeness_estimate,
            accuracy_indicators=model_metadata.accuracy_indicators,
            known_data_issues=model_metadata.known_data_issues,
            license_type=model_metadata.license_type,
            terms_of_use_url=model_metadata.terms_of_use_url,
            privacy_considerations=model_metadata.privacy_considerations,
            compliance_standards=model_metadata.compliance_standards,
            relevance_score=model_metadata.relevance_score,
            business_domains=model_metadata.business_domains,
            use_cases=model_metadata.use_cases,
            discovery_method=model_metadata.discovery_method,
            confidence_score=model_metadata.confidence_score
        )

    def _extract_next_steps(self, fitness_analyses: List[Dict[str, str]]) -> List[str]:
        """Extract recommended next steps from fitness analyses"""
        next_steps = set()
        for analysis in fitness_analyses:
            if 'recommended_actions' in analysis:
                actions = analysis['recommended_actions'].split(',')
                next_steps.update(action.strip() for action in actions)
        return list(next_steps)

    def _identify_coverage_gaps(self, sources: List[ModelDataSourceMetadata], canvas_data: Dict[str, Any]) -> List[str]:
        """Identify potential gaps in data coverage"""
        gaps = []

        # Check for temporal gaps
        has_real_time = any(src.update_frequency == 'REAL_TIME' for src in sources if src.update_frequency)
        has_historical = any(src.historical_data_available for src in sources)

        if not has_real_time and canvas_data.get('real_time_requirements'):
            gaps.append("No real-time data sources identified")
        if not has_historical and canvas_data.get('historical_analysis_needed'):
            gaps.append("Limited historical data availability")

        # Check for data type gaps
        available_formats = set()
        for src in sources:
            available_formats.update(src.data_formats)

        required_formats = canvas_data.get('required_data_formats', [])
        missing_formats = set(required_formats) - available_formats
        if missing_formats:
            gaps.append(f"Missing data formats: {', '.join(missing_formats)}")

        return gaps

    def _assess_integration_complexity(self, sources: List[ModelDataSourceMetadata]) -> str:
        """Assess overall integration complexity"""
        complexity_factors = 0

        # Authentication complexity
        auth_methods = set(src.authentication_method for src in sources if src.authentication_method)
        complexity_factors += len(auth_methods)

        # Data format diversity
        all_formats = set()
        for src in sources:
            all_formats.update(src.data_formats)
        complexity_factors += len(all_formats)

        # Rate limit considerations
        rate_limited_sources = sum(1 for src in sources if src.rate_limits)
        complexity_factors += rate_limited_sources

        if complexity_factors <= 3:
            return "Low"
        elif complexity_factors <= 7:
            return "Medium"
        else:
            return "High"

    def _identify_risk_factors(self, sources: List[ModelDataSourceMetadata]) -> List[str]:
        """Identify potential risk factors in the source portfolio"""
        risks = []

        # Quality risks
        low_quality_sources = [src for src in sources if src.data_quality_score and src.data_quality_score < 0.7]
        if low_quality_sources:
            risks.append(f"Low data quality in {len(low_quality_sources)} sources")

        # Compliance risks
        unknown_licenses = [src for src in sources if not src.license_type]
        if unknown_licenses:
            risks.append(f"Unknown licensing terms for {len(unknown_licenses)} sources")

        # Availability risks
        no_sla_sources = [src for src in sources if not src.rate_limits and 'api' in src.access_method.lower()]
        if no_sla_sources:
            risks.append("API sources without clear SLA/rate limit information")

        return risks