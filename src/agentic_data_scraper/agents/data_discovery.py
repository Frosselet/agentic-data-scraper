"""
BAML-Powered Data Discovery Agent

Intelligent web-based data source discovery that uses business context from the
Data Business Canvas to find, evaluate, and recommend relevant data sources.

Key Features:
- Canvas context-aware discovery
- Multi-strategy source identification
- Quality and relevance scoring
- Metadata extraction and enrichment
- Integration with existing semantic routing
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
import json
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict

from .base import BaseAgent, AgentResult
from ..semantic.skos_router import SKOSSemanticRouter

logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    """Discovered data source with metadata"""
    url: str
    title: str
    description: str
    source_type: str  # 'api', 'download', 'portal', 'database', 'stream'
    data_formats: List[str]  # ['json', 'csv', 'xml', etc.]
    update_frequency: str  # 'real-time', 'daily', 'weekly', 'monthly', 'static'
    access_method: str  # 'public', 'registration', 'api_key', 'subscription', 'request'
    quality_score: float  # 0.0 to 1.0
    relevance_score: float  # 0.0 to 1.0 based on canvas context
    business_domains: List[str]
    geographic_coverage: str
    discovered_at: str
    metadata: Dict[str, Any]


@dataclass
class DiscoveryContext:
    """Context from Data Business Canvas for targeted discovery"""
    business_domain: str
    primary_language: str
    value_propositions: List[str]
    target_users: List[str]
    external_data_needs: List[str]
    quality_requirements: List[str]
    compliance_constraints: List[str]
    technical_capabilities: List[str]
    budget_constraints: List[str]
    semantic_mappings: Dict[str, Any]


class DataDiscoveryAgent(BaseAgent):
    """
    BAML-powered agent for intelligent data source discovery.

    Uses business context from Data Business Canvas to guide discovery,
    employs multiple search strategies, and provides quality assessments.
    """

    def __init__(
        self,
        agent_id: str = "data_discovery",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 600,
        skos_router: Optional[SKOSSemanticRouter] = None
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.skos_router = skos_router
        self.discovery_strategies = self._initialize_strategies()
        self.source_evaluators = self._initialize_evaluators()

    def _initialize_strategies(self) -> Dict[str, Any]:
        """Initialize discovery strategies"""
        return {
            "government_portals": {
                "enabled": True,
                "domains": [
                    "data.gov", "data.gov.uk", "data.europa.eu", "opendata.cz",
                    "datos.gob.es", "dados.gov.pt", "dati.gov.it", "data.gouv.fr"
                ],
                "keywords": ["open data", "government data", "public data"]
            },
            "international_organizations": {
                "enabled": True,
                "domains": [
                    "worldbank.org", "imf.org", "oecd.org", "who.int", "fao.org",
                    "wto.org", "un.org", "eurostat.ec.europa.eu"
                ],
                "keywords": ["statistics", "economic data", "development data"]
            },
            "industry_associations": {
                "enabled": True,
                "search_patterns": [
                    "{domain} association data",
                    "{domain} industry statistics",
                    "{domain} market data"
                ]
            },
            "academic_sources": {
                "enabled": True,
                "domains": [
                    "kaggle.com", "github.com", "zenodo.org", "figshare.com",
                    "dataverse.harvard.edu", "ieee.org"
                ],
                "keywords": ["research data", "dataset", "academic data"]
            },
            "commercial_apis": {
                "enabled": True,
                "search_patterns": [
                    "{domain} API documentation",
                    "{domain} data API",
                    "{domain} web service"
                ]
            },
            "specialized_portals": {
                "enabled": True,
                "domain_specific": {
                    "agriculture": ["fao.org", "usda.gov", "ec.europa.eu/agriculture"],
                    "finance": ["federalreserve.gov", "ecb.europa.eu", "bis.org"],
                    "health": ["who.int", "cdc.gov", "ecdc.europa.eu"],
                    "trade": ["wto.org", "tradingeconomics.com", "comtrade.un.org"]
                }
            }
        }

    def _initialize_evaluators(self) -> Dict[str, Any]:
        """Initialize source evaluation criteria"""
        return {
            "quality_factors": {
                "documentation_quality": 0.2,
                "update_frequency": 0.15,
                "data_completeness": 0.15,
                "accessibility": 0.15,
                "reliability": 0.15,
                "format_quality": 0.1,
                "metadata_richness": 0.1
            },
            "relevance_factors": {
                "business_domain_match": 0.3,
                "data_type_alignment": 0.25,
                "geographic_relevance": 0.2,
                "temporal_alignment": 0.15,
                "quality_threshold_match": 0.1
            }
        }

    async def _process(
        self,
        canvas_context: Dict[str, Any],
        user_suggestions: Optional[List[str]] = None,
        max_sources: int = 50,
        min_quality_score: float = 0.6,
        **kwargs
    ) -> List[DataSource]:
        """
        Discover data sources based on canvas context and user suggestions.

        Args:
            canvas_context: Business context from Data Business Canvas
            user_suggestions: Optional user-provided data source ideas
            max_sources: Maximum number of sources to discover
            min_quality_score: Minimum quality threshold for inclusion

        Returns:
            List of discovered and evaluated data sources
        """

        self.logger.info("Starting intelligent data discovery")

        # Parse canvas context
        discovery_context = self._parse_canvas_context(canvas_context)

        # Initialize semantic routing if available
        if self.skos_router and discovery_context.semantic_mappings:
            self.logger.info("Using semantic routing for enhanced discovery")

        # Generate search queries based on context
        search_queries = await self._generate_search_queries(discovery_context, user_suggestions)

        # Execute discovery strategies
        discovered_sources = []

        for strategy_name, strategy_config in self.discovery_strategies.items():
            if not strategy_config.get("enabled", True):
                continue

            self.logger.info(f"Executing discovery strategy: {strategy_name}")

            try:
                strategy_sources = await self._execute_strategy(
                    strategy_name, strategy_config, discovery_context, search_queries
                )
                discovered_sources.extend(strategy_sources)

            except Exception as e:
                self.logger.warning(f"Strategy {strategy_name} failed: {e}")

        # Remove duplicates and evaluate sources
        unique_sources = self._deduplicate_sources(discovered_sources)
        evaluated_sources = await self._evaluate_sources(unique_sources, discovery_context)

        # Filter by quality and relevance
        filtered_sources = [
            source for source in evaluated_sources
            if source.quality_score >= min_quality_score
        ]

        # Sort by combined score and limit results
        sorted_sources = sorted(
            filtered_sources,
            key=lambda s: (s.relevance_score + s.quality_score) / 2,
            reverse=True
        )[:max_sources]

        self.logger.info(f"Discovery completed: {len(sorted_sources)} high-quality sources found")

        return sorted_sources

    def _parse_canvas_context(self, canvas_data: Dict[str, Any]) -> DiscoveryContext:
        """Parse canvas data into discovery context"""
        return DiscoveryContext(
            business_domain=canvas_data.get("business_domain", ""),
            primary_language=canvas_data.get("primary_language", "en"),
            value_propositions=canvas_data.get("value_propositions", []),
            target_users=canvas_data.get("target_users", []),
            external_data_needs=canvas_data.get("external_data_needs", []),
            quality_requirements=canvas_data.get("quality_requirements", []),
            compliance_constraints=canvas_data.get("compliance_constraints", []),
            technical_capabilities=canvas_data.get("technical_capabilities", []),
            budget_constraints=canvas_data.get("budget_constraints", []),
            semantic_mappings=canvas_data.get("semantic_mappings", {})
        )

    async def _generate_search_queries(
        self,
        context: DiscoveryContext,
        user_suggestions: Optional[List[str]]
    ) -> List[str]:
        """Generate targeted search queries based on context"""

        queries = []

        # Base domain queries
        if context.business_domain:
            queries.extend([
                f"{context.business_domain} data sources",
                f"{context.business_domain} open data",
                f"{context.business_domain} API data",
                f"{context.business_domain} statistics"
            ])

        # External data needs queries
        for need in context.external_data_needs[:5]:  # Limit for performance
            if self.skos_router and context.semantic_mappings:
                # Use semantic routing to enhance queries
                standardized_need = await self._standardize_term(need, context.primary_language)
                if standardized_need != need:
                    queries.append(f"{standardized_need} data")

            queries.extend([
                f"{need} data source",
                f"{need} dataset",
                f"{need} API"
            ])

        # Value proposition queries
        for value_prop in context.value_propositions[:3]:
            # Extract key terms from value propositions
            key_terms = self._extract_key_terms(value_prop)
            for term in key_terms:
                queries.append(f"{term} data")

        # User suggestion queries
        if user_suggestions:
            for suggestion in user_suggestions:
                queries.extend([
                    suggestion,
                    f"{suggestion} data",
                    f"{suggestion} API"
                ])

        # Remove duplicates and return
        return list(set(queries))

    async def _standardize_term(self, term: str, language: str) -> str:
        """Standardize term using SKOS router if available"""
        if not self.skos_router:
            return term

        try:
            routing_result = self.skos_router.route_term_to_preferred(term, language, "en")
            if routing_result.get("preferred_label"):
                return routing_result["preferred_label"]
        except Exception as e:
            self.logger.debug(f"Term standardization failed for '{term}': {e}")

        return term

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key business terms from text"""
        # Simple keyword extraction - can be enhanced with NLP
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had"
        }

        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        key_terms = [word for word in words if word not in stop_words]

        # Return unique terms, prioritizing longer ones
        return list(set(key_terms))

    async def _execute_strategy(
        self,
        strategy_name: str,
        strategy_config: Dict[str, Any],
        context: DiscoveryContext,
        queries: List[str]
    ) -> List[DataSource]:
        """Execute specific discovery strategy"""

        sources = []

        if strategy_name == "government_portals":
            sources = await self._discover_government_sources(strategy_config, context, queries)
        elif strategy_name == "international_organizations":
            sources = await self._discover_international_sources(strategy_config, context, queries)
        elif strategy_name == "specialized_portals":
            sources = await self._discover_specialized_sources(strategy_config, context, queries)
        elif strategy_name == "academic_sources":
            sources = await self._discover_academic_sources(strategy_config, context, queries)
        else:
            # Generic web search strategy
            sources = await self._discover_web_sources(strategy_config, context, queries)

        return sources

    async def _discover_government_sources(
        self, config: Dict[str, Any], context: DiscoveryContext, queries: List[str]
    ) -> List[DataSource]:
        """Discover government open data sources"""
        sources = []

        for domain in config.get("domains", []):
            # Simulate discovery - in real implementation, would crawl/search these domains
            if context.business_domain in ["agriculture", "trade", "finance"]:
                sources.append(DataSource(
                    url=f"https://{domain}/dataset/{context.business_domain}",
                    title=f"{context.business_domain.title()} Open Data Portal",
                    description=f"Government open data portal for {context.business_domain} sector",
                    source_type="portal",
                    data_formats=["csv", "json", "xml"],
                    update_frequency="monthly",
                    access_method="public",
                    quality_score=0.8,
                    relevance_score=0.0,  # Will be calculated later
                    business_domains=[context.business_domain],
                    geographic_coverage="national",
                    discovered_at=datetime.utcnow().isoformat(),
                    metadata={
                        "strategy": "government_portals",
                        "domain": domain,
                        "verified": False
                    }
                ))

        return sources

    async def _discover_international_sources(
        self, config: Dict[str, Any], context: DiscoveryContext, queries: List[str]
    ) -> List[DataSource]:
        """Discover international organization data sources"""
        sources = []

        # Domain-specific international sources
        domain_mappings = {
            "agriculture": ["fao.org", "worldbank.org"],
            "finance": ["imf.org", "worldbank.org", "bis.org"],
            "trade": ["wto.org", "worldbank.org", "oecd.org"],
            "health": ["who.int", "worldbank.org"]
        }

        relevant_domains = domain_mappings.get(context.business_domain, ["worldbank.org"])

        for domain in relevant_domains:
            sources.append(DataSource(
                url=f"https://{domain}/data/{context.business_domain}",
                title=f"{domain.split('.')[0].upper()} {context.business_domain.title()} Data",
                description=f"International data from {domain} for {context.business_domain}",
                source_type="api",
                data_formats=["json", "csv"],
                update_frequency="quarterly",
                access_method="public",
                quality_score=0.9,
                relevance_score=0.0,
                business_domains=[context.business_domain],
                geographic_coverage="global",
                discovered_at=datetime.utcnow().isoformat(),
                metadata={
                    "strategy": "international_organizations",
                    "organization": domain,
                    "verified": False
                }
            ))

        return sources

    async def _discover_specialized_sources(
        self, config: Dict[str, Any], context: DiscoveryContext, queries: List[str]
    ) -> List[DataSource]:
        """Discover domain-specific specialized sources"""
        sources = []

        domain_specific = config.get("domain_specific", {})
        specialized_domains = domain_specific.get(context.business_domain, [])

        for domain in specialized_domains:
            sources.append(DataSource(
                url=f"https://{domain}/data",
                title=f"{context.business_domain.title()} Specialized Data Portal",
                description=f"Industry-specific data portal for {context.business_domain}",
                source_type="portal",
                data_formats=["csv", "json", "excel"],
                update_frequency="weekly",
                access_method="registration",
                quality_score=0.85,
                relevance_score=0.0,
                business_domains=[context.business_domain],
                geographic_coverage="varies",
                discovered_at=datetime.utcnow().isoformat(),
                metadata={
                    "strategy": "specialized_portals",
                    "specialization": context.business_domain,
                    "verified": False
                }
            ))

        return sources

    async def _discover_academic_sources(
        self, config: Dict[str, Any], context: DiscoveryContext, queries: List[str]
    ) -> List[DataSource]:
        """Discover academic and research data sources"""
        sources = []

        # Simulate academic source discovery
        for external_need in context.external_data_needs[:3]:
            sources.append(DataSource(
                url=f"https://kaggle.com/datasets/{external_need.lower().replace(' ', '-')}",
                title=f"{external_need} Research Dataset",
                description=f"Academic research dataset for {external_need}",
                source_type="download",
                data_formats=["csv", "json"],
                update_frequency="static",
                access_method="registration",
                quality_score=0.75,
                relevance_score=0.0,
                business_domains=[context.business_domain],
                geographic_coverage="varies",
                discovered_at=datetime.utcnow().isoformat(),
                metadata={
                    "strategy": "academic_sources",
                    "platform": "kaggle",
                    "verified": False
                }
            ))

        return sources

    async def _discover_web_sources(
        self, config: Dict[str, Any], context: DiscoveryContext, queries: List[str]
    ) -> List[DataSource]:
        """Generic web-based source discovery"""
        sources = []

        # Simulate web discovery results
        for i, query in enumerate(queries[:5]):  # Limit for demo
            sources.append(DataSource(
                url=f"https://example-data-source-{i}.com/api",
                title=f"Web Data Source for {query}",
                description=f"Web-discovered data source related to {query}",
                source_type="api",
                data_formats=["json"],
                update_frequency="daily",
                access_method="api_key",
                quality_score=0.65,
                relevance_score=0.0,
                business_domains=[context.business_domain],
                geographic_coverage="varies",
                discovered_at=datetime.utcnow().isoformat(),
                metadata={
                    "strategy": "web_search",
                    "query": query,
                    "verified": False
                }
            ))

        return sources

    def _deduplicate_sources(self, sources: List[DataSource]) -> List[DataSource]:
        """Remove duplicate sources based on URL"""
        seen_urls = set()
        unique_sources = []

        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)

        return unique_sources

    async def _evaluate_sources(
        self, sources: List[DataSource], context: DiscoveryContext
    ) -> List[DataSource]:
        """Evaluate and score sources for quality and relevance"""

        for source in sources:
            # Calculate quality score
            source.quality_score = await self._calculate_quality_score(source, context)

            # Calculate relevance score
            source.relevance_score = await self._calculate_relevance_score(source, context)

        return sources

    async def _calculate_quality_score(self, source: DataSource, context: DiscoveryContext) -> float:
        """Calculate quality score based on multiple factors"""
        factors = self.source_evaluators["quality_factors"]
        scores = {}

        # Documentation quality (simulated)
        scores["documentation_quality"] = 0.8 if source.source_type in ["api", "portal"] else 0.6

        # Update frequency
        frequency_scores = {
            "real-time": 1.0, "daily": 0.9, "weekly": 0.8,
            "monthly": 0.7, "quarterly": 0.5, "static": 0.3
        }
        scores["update_frequency"] = frequency_scores.get(source.update_frequency, 0.5)

        # Data completeness (simulated based on source type)
        scores["data_completeness"] = 0.9 if source.source_type == "api" else 0.7

        # Accessibility
        access_scores = {
            "public": 1.0, "registration": 0.8, "api_key": 0.7,
            "subscription": 0.5, "request": 0.3
        }
        scores["accessibility"] = access_scores.get(source.access_method, 0.5)

        # Reliability (based on source strategy)
        strategy_reliability = {
            "government_portals": 0.9,
            "international_organizations": 0.95,
            "specialized_portals": 0.8,
            "academic_sources": 0.75,
            "web_search": 0.6
        }
        scores["reliability"] = strategy_reliability.get(
            source.metadata.get("strategy", "web_search"), 0.6
        )

        # Format quality
        format_scores = {"json": 1.0, "csv": 0.9, "xml": 0.8, "excel": 0.7}
        avg_format_score = sum(format_scores.get(fmt, 0.5) for fmt in source.data_formats) / len(source.data_formats)
        scores["format_quality"] = avg_format_score

        # Metadata richness (simulated)
        scores["metadata_richness"] = 0.8 if len(source.metadata) > 3 else 0.6

        # Calculate weighted score
        total_score = sum(scores[factor] * weight for factor, weight in factors.items())

        return min(1.0, max(0.0, total_score))

    async def _calculate_relevance_score(self, source: DataSource, context: DiscoveryContext) -> float:
        """Calculate relevance score based on business context alignment"""
        factors = self.source_evaluators["relevance_factors"]
        scores = {}

        # Business domain match
        domain_match = 1.0 if context.business_domain in source.business_domains else 0.3
        scores["business_domain_match"] = domain_match

        # Data type alignment (check if external needs are mentioned in source)
        alignment_score = 0.0
        for need in context.external_data_needs:
            if any(need.lower() in source.title.lower() or
                   need.lower() in source.description.lower() for need in [need]):
                alignment_score += 0.2
        scores["data_type_alignment"] = min(1.0, alignment_score)

        # Geographic relevance (simplified)
        geo_scores = {"global": 1.0, "national": 0.8, "regional": 0.6, "local": 0.4, "varies": 0.7}
        scores["geographic_relevance"] = geo_scores.get(source.geographic_coverage, 0.5)

        # Temporal alignment (update frequency vs requirements)
        if "real-time" in " ".join(context.quality_requirements).lower():
            temporal_score = 1.0 if source.update_frequency in ["real-time", "daily"] else 0.5
        else:
            temporal_score = 0.8  # Good enough for most cases
        scores["temporal_alignment"] = temporal_score

        # Quality threshold match
        min_quality = 0.7  # Default threshold
        for req in context.quality_requirements:
            if "%" in req:
                try:
                    threshold = float(re.search(r'(\d+(?:\.\d+)?)%', req).group(1)) / 100
                    min_quality = max(min_quality, threshold)
                except:
                    pass

        scores["quality_threshold_match"] = 1.0 if source.quality_score >= min_quality else 0.5

        # Calculate weighted score
        total_score = sum(scores[factor] * weight for factor, weight in factors.items())

        return min(1.0, max(0.0, total_score))

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "discovery_strategies": list(self.discovery_strategies.keys()),
            "evaluation_factors": {
                "quality": list(self.source_evaluators["quality_factors"].keys()),
                "relevance": list(self.source_evaluators["relevance_factors"].keys())
            },
            "supported_source_types": ["api", "download", "portal", "database", "stream"],
            "supported_formats": ["json", "csv", "xml", "excel", "parquet"],
            "semantic_routing": self.skos_router is not None
        })
        return base_capabilities

    async def export_discovery_results(
        self, sources: List[DataSource], format: str = "json"
    ) -> str:
        """Export discovery results in specified format"""

        export_data = {
            "discovery_metadata": {
                "agent_id": self.agent_id,
                "discovery_timestamp": datetime.utcnow().isoformat(),
                "total_sources": len(sources),
                "avg_quality_score": sum(s.quality_score for s in sources) / len(sources) if sources else 0.0,
                "avg_relevance_score": sum(s.relevance_score for s in sources) / len(sources) if sources else 0.0
            },
            "sources": [asdict(source) for source in sources]
        }

        if format == "json":
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")