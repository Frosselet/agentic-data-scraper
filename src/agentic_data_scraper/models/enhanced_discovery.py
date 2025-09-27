"""
Enhanced Data Discovery Models

Defines the dual-path discovery mechanism and metadata collection
for bridging Value & Users to Operations & Resources workflow steps.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
import datetime


class DiscoveryPath(str, Enum):
    """Discovery path selection"""
    KNOWN_SOURCE = "known_source"
    ZERO_START = "zero_start"


class DataSourceType(str, Enum):
    """Data source types for classification"""
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    WEB_SCRAPING = "web_scraping"
    STREAM = "stream"
    CLOUD_STORAGE = "cloud_storage"


class UpdateFrequency(str, Enum):
    """Data update frequencies"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    STATIC = "static"


@dataclass
class DataSourceMetadata:
    """Comprehensive metadata for discovered data sources"""
    # Basic identification
    name: str
    url: str
    description: str
    source_type: DataSourceType

    # Technical metadata (for Operations & Resources)
    access_method: str  # REST API, SQL connection, file download, etc.
    authentication_required: bool
    authentication_method: Optional[str] = None  # API key, OAuth, etc.
    rate_limits: Optional[Dict[str, Any]] = None
    data_formats: List[str] = None  # JSON, CSV, XML, etc.

    # Data characteristics (for Data & Governance)
    schema_available: bool = False
    schema_url: Optional[str] = None
    sample_data_url: Optional[str] = None
    data_volume_estimate: Optional[str] = None
    update_frequency: Optional[UpdateFrequency] = None
    historical_data_available: bool = False
    historical_range: Optional[str] = None

    # Quality indicators (for Data & Governance)
    data_quality_score: Optional[float] = None  # 0.0 to 1.0
    completeness_estimate: Optional[float] = None
    accuracy_indicators: List[str] = None
    known_data_issues: List[str] = None

    # Governance metadata (for Data & Governance)
    license_type: Optional[str] = None
    terms_of_use_url: Optional[str] = None
    privacy_considerations: List[str] = None
    compliance_standards: List[str] = None  # GDPR, CCPA, etc.

    # Business context (from Value & Users)
    relevance_score: float = 0.0  # How well it matches user requirements
    business_domains: List[str] = None
    use_cases: List[str] = None

    # Discovery metadata
    discovered_at: datetime.datetime
    discovery_method: str  # manual, web_crawl, recommendation_engine
    confidence_score: float = 0.0  # Discovery confidence 0.0 to 1.0


@dataclass
class KnownSourceRequest:
    """Request for metadata collection of known data sources"""
    source_urls: List[str]
    expected_source_type: Optional[DataSourceType] = None
    specific_datasets: Optional[List[str]] = None  # Specific datasets within source
    collection_depth: Literal["basic", "detailed", "comprehensive"] = "detailed"


@dataclass
class ZeroStartDiscovery:
    """Configuration for zero-start data discovery"""
    # From Value & Users canvas
    business_domain: str
    use_case_description: str
    required_data_types: List[str]
    geographic_scope: Optional[str] = None
    time_period_requirements: Optional[str] = None

    # Discovery preferences
    max_sources_to_find: int = 5
    preferred_source_types: List[DataSourceType] = None
    exclude_paid_sources: bool = False
    require_api_access: bool = False

    # Search strategy
    search_strategy: Literal["comprehensive", "focused", "quick"] = "focused"
    include_academic_sources: bool = True
    include_government_sources: bool = True
    include_commercial_sources: bool = True


@dataclass
class DiscoveryResult:
    """Result of data discovery process"""
    discovery_path: DiscoveryPath
    discovered_sources: List[DataSourceMetadata]
    total_sources_found: int
    search_queries_used: List[str] = None
    discovery_duration_seconds: float = 0.0

    # Recommendations for next workflow steps
    recommended_next_steps: List[str] = None
    prefilled_operations_data: Dict[str, Any] = None  # For Operations & Resources
    prefilled_governance_data: Dict[str, Any] = None  # For Data & Governance


@dataclass
class WorkflowPrepopulation:
    """Data to prepopulate in downstream workflow steps"""

    # For Operations & Resources step
    operations_data: Dict[str, Any]  # {
        # "data_sources": [...],
        # "access_methods": [...],
        # "authentication_requirements": [...],
        # "estimated_volumes": [...],
        # "update_frequencies": [...]
    # }

    # For Data & Governance step
    governance_data: Dict[str, Any]  # {
        # "data_quality_assessments": [...],
        # "compliance_requirements": [...],
        # "privacy_considerations": [...],
        # "license_constraints": [...]
    # }

    # For Review and Export step
    review_data: Dict[str, Any]  # {
        # "source_summaries": [...],
        # "integration_complexity": [...],
        # "risk_assessments": [...],
        # "implementation_recommendations": [...]
    # }