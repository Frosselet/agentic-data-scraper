"""
Data Business Canvas - Streamlit Implementation

Implements the 9+3 Data Business Canvas framework from ADR-012 as an interactive
Streamlit application for gathering real business context that feeds into BAML
discovery agents and semantic SOW generation.

Key Features:
- Interactive 9+3 canvas framework implementation
- Real business data collection (no simulation/dummy values)
- SKOS semantic routing for multilingual support
- Integration with existing BAML agents and schemas
- Structured output for downstream data discovery
"""

import streamlit as st
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

import sys
from pathlib import Path

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))  # For baml_client

from agentic_data_scraper.agents.sow_interpreter import SOWInterpreterAgent, DataContract
from agentic_data_scraper.agents.executive_target_scorer import ExecutiveTargetScorerAgent
from agentic_data_scraper.models.executive_targets import (
    ExecutiveTarget, AlignmentScore, TargetParsingResult, TargetCategory, TargetPriority
)
from agentic_data_scraper.semantic.skos_router import SKOSSemanticRouter
from agentic_data_scraper.schemas.sow import (
    SemanticStatementOfWork, BusinessChallenge
)
from agentic_data_scraper.ui.canvas_validator import CanvasValidationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataBusinessCanvas:
    """
    Data Business Canvas implementation following ADR-012 framework.

    The 9+3 framework consists of:
    Core 9 Elements:
    1. Value Propositions - What data value we create
    2. Customer Segments - Who benefits from data insights
    3. Customer Relationships - How we engage data consumers
    4. Channels - How insights are delivered
    5. Key Activities - Core data operations
    6. Key Resources - Essential data assets
    7. Key Partners - External data/service providers
    8. Cost Structure - Data operation costs
    9. Revenue Streams - Value monetization

    Additional 3 Elements:
    10. Data Sources - Where data originates
    11. Data Governance - Compliance and quality control
    12. Technology Infrastructure - Technical enablers
    """

    def __init__(self):
        self.canvas_data = self._initialize_canvas()
        self.skos_router = None
        self.sow_agent = None
        self.executive_scorer = None
        self.validator = CanvasValidationEngine()

    def cleanup(self):
        """Cleanup database connections and resources"""
        try:
            if self.skos_router:
                # Store database path before closing
                db_path = getattr(self.skos_router, 'kuzu_db_path', None)
                self.skos_router.close()
                self.skos_router = None

                # Clean up session-specific database files
                if db_path and 'kuzu_dbc_' in db_path:
                    import os
                    try:
                        if os.path.exists(db_path):
                            os.remove(db_path)
                        # Also remove WAL files
                        wal_file = f"{db_path}.wal"
                        if os.path.exists(wal_file):
                            os.remove(wal_file)
                        logger.info(f"Cleaned up session database: {db_path}")
                    except Exception as cleanup_error:
                        logger.warning(f"Could not remove session database files: {cleanup_error}")

            logger.info("DataBusinessCanvas cleanup completed")
        except Exception as e:
            logger.warning(f"Error during DataBusinessCanvas cleanup: {e}")

    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()

    def _initialize_canvas(self) -> Dict[str, Any]:
        """Initialize canvas with European Energy Trading example"""
        return {
            # Core 9 Business Model Elements
            "value_propositions": {
                "data_insights": [
                    "Real-time European energy price forecasting to anticipate commodity transport costs",
                    "Cross-border energy flow analysis for regional price arbitrage opportunities",
                    "Renewable generation variability prediction for energy cost volatility assessment",
                    "Day-ahead vs real-time price deviation analysis for trading strategy optimization"
                ],
                "business_outcomes": [
                    "15% improvement in commodity transport cost prediction accuracy",
                    "Reduced exposure to energy price volatility through advanced warning systems",
                    "Enhanced trading profitability via energy-informed commodity positioning",
                    "Competitive advantage through superior energy market intelligence"
                ],
                "competitive_advantages": [
                    "Proprietary ENTSO-E data integration capabilities",
                    "Multi-country energy flow correlation analysis",
                    "Real-time energy price impact modeling for commodity markets",
                    "Advanced renewable energy forecasting algorithms"
                ]
            },
            "customer_segments": {
                "primary_users": [
                    "Commodity traders focusing on energy-sensitive products",
                    "Agricultural traders tracking transport and processing costs",
                    "Industrial commodity analysts monitoring energy cost impacts"
                ],
                "secondary_users": [
                    "Supply chain managers optimizing energy-dependent logistics",
                    "Risk management teams hedging energy cost exposure",
                    "Portfolio managers integrating energy signals into commodity strategies"
                ],
                "user_personas": [
                    "Senior Commodity Trader: Needs instant energy price alerts affecting transport costs",
                    "Energy Analyst: Requires detailed cross-border flow analysis and forecasting models",
                    "Risk Manager: Demands energy volatility metrics for commodity exposure assessment"
                ]
            },
            "customer_relationships": {
                "engagement_model": "On-demand analysis",
                "feedback_mechanisms": [
                    "Weekly trader feedback sessions on price prediction accuracy",
                    "Monthly business review meetings with trading desk heads",
                    "Quarterly model enhancement workshops with quantitative analysts"
                ],
                "support_channels": [
                    "24/7 technical support during market hours",
                    "Dedicated energy analyst for complex query resolution",
                    "Emergency hotline for critical energy market events"
                ]
            },
            "channels": {
                "delivery_methods": [
                    "Real-time API feeds for trading system integration",
                    "Interactive web dashboard for visual analysis",
                    "Mobile alerts for critical energy price movements",
                    "Scheduled email reports with daily energy-commodity correlations"
                ],
                "distribution_channels": [
                    "Direct API integration with trading platforms",
                    "Bloomberg terminal integration for seamless workflow",
                    "Microsoft Teams/Slack notifications for instant alerts",
                    "Custom Excel plugins for analyst workflow integration"
                ],
                "access_interfaces": [
                    "RESTful API with JSON responses",
                    "WebSocket connections for real-time streaming",
                    "Jupyter notebook integration for quantitative analysis",
                    "Power BI/Tableau connectors for visualization"
                ]
            },
            "key_activities": {
                "data_collection": [
                    "ENTSO-E Transparency Platform automated data harvesting",
                    "Multi-country energy market data normalization and validation",
                    "Cross-border electricity flow data quality assurance",
                    "Renewable generation forecast data aggregation from TSOs"
                ],
                "data_processing": [
                    "Real-time energy price calculation and standardization",
                    "Cross-border flow impact analysis on regional pricing",
                    "Energy volatility modeling and risk metrics computation",
                    "Commodity-energy correlation analysis and signal generation"
                ],
                "insight_generation": [
                    "Energy cost impact forecasting for commodity transport",
                    "Regional energy arbitrage opportunity identification",
                    "Renewable intermittency impact assessment on grid stability",
                    "Energy-commodity price elasticity analysis and reporting"
                ]
            },
            "key_resources": {
                "data_assets": [
                    "ENTSO-E historical data warehouse (5+ years of market data)",
                    "Real-time energy flow monitoring across 35+ European countries",
                    "Proprietary energy-commodity correlation models",
                    "Validated renewable generation forecasting algorithms"
                ],
                "technical_resources": [
                    "High-frequency data processing infrastructure on AWS",
                    "Machine learning pipeline for energy price prediction",
                    "Real-time stream processing using Apache Kafka and Flink",
                    "Automated data quality monitoring and alerting systems"
                ],
                "human_resources": [
                    "Senior energy market analysts with 10+ years experience",
                    "Quantitative developers specializing in time-series analysis",
                    "DevOps engineers maintaining 99.9% uptime for critical feeds",
                    "Domain experts in European energy regulation and market structure"
                ]
            },
            "key_partners": {
                "data_providers": [
                    "ENTSO-E (European Network of Transmission System Operators)",
                    "Individual TSOs for granular regional data access",
                    "Weather data providers for renewable generation forecasting",
                    "Economic data vendors for macro-energy correlations"
                ],
                "technology_partners": [
                    "AWS for cloud infrastructure and managed services",
                    "Confluent for enterprise Kafka streaming platform",
                    "DataDog for comprehensive monitoring and observability",
                    "Auth0 for secure API authentication and access control"
                ],
                "service_providers": [
                    "European energy market consultancy for regulatory updates",
                    "Financial data vendors for commodity price benchmarking",
                    "Cybersecurity firm for energy infrastructure protection",
                    "Legal advisors for cross-border data compliance"
                ]
            },
            "cost_structure": {
                "data_acquisition": [
                    "ENTSO-E API access and premium data subscriptions: €25K/year",
                    "Individual TSO data licensing agreements: €40K/year",
                    "Weather and economic data subscriptions: €30K/year"
                ],
                "infrastructure": [
                    "AWS cloud infrastructure (compute, storage, networking): €80K/year",
                    "Data streaming and processing platform licenses: €35K/year",
                    "Monitoring and observability tools: €15K/year"
                ],
                "operational": [
                    "Energy analyst salaries and benefits: €400K/year",
                    "Technical development team: €300K/year",
                    "Compliance and legal advisory: €50K/year"
                ]
            },
            "revenue_streams": {
                "direct_revenue": [
                    "Premium energy intelligence subscriptions: €500K/year projected",
                    "Custom analysis and consulting services: €200K/year",
                    "API access licensing to fintech partners: €150K/year"
                ],
                "cost_savings": [
                    "Reduced commodity transport cost prediction errors: €2M/year value",
                    "Improved energy hedging strategies: €1.5M/year savings",
                    "Optimized logistics timing based on energy costs: €800K/year"
                ],
                "strategic_value": [
                    "Competitive advantage in energy-sensitive commodity trading",
                    "Risk mitigation through superior energy market intelligence",
                    "Market leadership in European energy-commodity correlation analysis"
                ]
            },

            # Additional 3 Data-Specific Elements
            "data_sources": {
                "internal_sources": [
                    "Historical commodity trading positions and performance",
                    "Internal energy cost allocation models",
                    "Proprietary transport route optimization algorithms"
                ],
                "external_sources": [
                    "ENTSO-E Transparency Platform (transparency.entsoe.eu)",
                    "Individual TSO websites and APIs across 35 European countries",
                    "European Power Exchange (EPEX SPOT) market data",
                    "Weather APIs for renewable generation forecasting"
                ],
                "real_time_feeds": [
                    "Live energy price feeds from major European exchanges",
                    "Real-time cross-border electricity flow data",
                    "Renewable generation output streaming data",
                    "Grid frequency and stability metrics"
                ],
                "batch_sources": [
                    "Daily energy market settlement reports",
                    "Weekly renewable capacity auction results",
                    "Monthly transmission capacity allocation data",
                    "Quarterly European energy regulatory updates"
                ]
            },
            "data_governance": {
                "quality_standards": [
                    "99.5% data completeness for critical energy price feeds",
                    "Sub-5-minute latency for real-time market data updates",
                    "Automated validation against multiple TSO sources",
                    "Statistical outlier detection for anomalous price movements"
                ],
                "compliance_requirements": [
                    "GDPR compliance for any personal data handling",
                    "REMIT (Regulation on Energy Market Integrity and Transparency)",
                    "MiFID II transparency requirements for financial instrument data",
                    "Data residency requirements for EU energy market information"
                ],
                "access_controls": [
                    "Role-based access control with trader, analyst, and admin levels",
                    "API key management with usage quotas and rate limiting",
                    "Audit logging for all data access and modification events",
                    "Multi-factor authentication for sensitive energy market data"
                ],
                "retention_policies": [
                    "7-year retention for energy market historical data",
                    "Real-time data cached for 90 days for performance optimization",
                    "Forecast model training data retained for 3 years",
                    "User activity logs retained for 2 years for compliance"
                ]
            },
            "technology_infrastructure": {
                "data_platforms": [
                    "Apache Kafka for real-time energy data streaming",
                    "Amazon S3 for historical energy market data lake storage",
                    "ClickHouse for high-performance time-series analytics",
                    "Apache Airflow for energy data pipeline orchestration"
                ],
                "analytics_tools": [
                    "Python/Pandas for energy market data analysis",
                    "TensorFlow for renewable generation forecasting models",
                    "Apache Spark for large-scale energy correlation analysis",
                    "Jupyter Lab for interactive energy market research"
                ],
                "integration_capabilities": [
                    "REST APIs for energy data access and delivery",
                    "WebSocket connections for real-time price streaming",
                    "FIX protocol integration for trading system connectivity",
                    "SFTP/FTP for secure batch data exchange with partners"
                ],
                "security_measures": [
                    "End-to-end encryption for all energy market data transmission",
                    "VPN access for secure connection to European TSO systems",
                    "Regular penetration testing of energy data infrastructure",
                    "24/7 security monitoring with automated threat detection"
                ]
            },

            # Executive Targets (+E Framework Extension)
            "executive_targets": {
                "enterprise_id": "euro-energy-traders",
                "enterprise_name": "European Energy Trading Analytics",
                "raw_targets": [
                    "Achieve 20% improvement in energy cost prediction accuracy for commodity transport within Q2 2025 to reduce logistics budget overruns by €3M annually",
                    "Establish real-time European energy intelligence platform serving 50+ commodity traders with 99.5% uptime by end of 2025",
                    "Generate €1.5M in new revenue from premium energy-commodity correlation analytics subscriptions by Q4 2025",
                    "Reduce commodity position risk exposure by 15% through advanced energy volatility forecasting and hedging recommendations"
                ],
                "targets": [],
                "alignment_scores": {},
                "enterprise_context": {
                    "fiscal_year": "2025",
                    "quarter": "Q1",
                    "industry_context": "European commodity trading with focus on energy-sensitive products and transport optimization",
                    "competitive_priorities": [
                        "Energy market intelligence leadership",
                        "Real-time decision support capabilities",
                        "Risk mitigation through superior forecasting",
                        "Cost optimization via energy-informed trading"
                    ]
                }
            },

            # Metadata
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "version": "1.0",
                "completion_status": 0.9,  # Canvas is 90% complete
                "business_domain": "European Energy Trading and Commodity Analytics",
                "primary_language": "en"
            }
        }

    async def initialize_agents(self):
        """Initialize BAML agents and semantic routing"""
        try:
            # Initialize SKOS router for multilingual support with unique DB per session
            import time
            import os
            session_id = str(time.time()).replace('.', '_')
            db_path = Path(f"data/kuzu_dbc_{session_id}_{os.getpid()}.db")
            self.skos_router = SKOSSemanticRouter(str(db_path))

            # Initialize SOW interpreter agent
            self.sow_agent = SOWInterpreterAgent()

            # Initialize executive target scorer
            enterprise_name = self.canvas_data["executive_targets"]["enterprise_name"] or "Enterprise"
            enterprise_id = self.canvas_data["executive_targets"]["enterprise_id"] or "default"
            self.executive_scorer = ExecutiveTargetScorerAgent(
                enterprise_id=enterprise_id,
                enterprise_name=enterprise_name
            )

            # Initialize canvas validator
            await self.validator.initialize(str(db_path))

            logger.info("Successfully initialized BAML agents, SKOS router, executive scorer, and validator")

        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            st.error(f"Failed to initialize backend services: {e}")

    def render_canvas_interface(self):
        """Render the complete Data Business Canvas interface"""
        st.set_page_config(
            page_title="Data Business Canvas",
            page_icon="📊",
            layout="wide"
        )

        st.title("🎯 Data Business Canvas")
        st.markdown("""
        **Build your data strategy foundation step-by-step.**

        This canvas helps you define the business context that will guide our AI agents
        in discovering and recommending the most relevant data sources for your needs.
        """)

        # Persona Selection
        st.subheader("👤 Select Your Role")

        col1, col2, col3 = st.columns(3)

        with col1:
            business_owner = st.button(
                "👔 Business Owner\n(The WHAT)",
                help="I need data to solve my business problem",
                use_container_width=True
            )
            if business_owner:
                self.canvas_data["metadata"]["selected_persona"] = "business_owner"
                st.rerun()

        with col2:
            business_analyst = st.button(
                "📋 Business Analyst\n(The BRIDGE)",
                help="I translate business needs into technical requirements",
                use_container_width=True
            )
            if business_analyst:
                self.canvas_data["metadata"]["selected_persona"] = "business_analyst"
                st.rerun()

        with col3:
            data_engineer = st.button(
                "🔧 Data Engineer/DevOps\n(The HOW)",
                help="I build and implement the data pipeline",
                use_container_width=True
            )
            if data_engineer:
                self.canvas_data["metadata"]["selected_persona"] = "data_engineer"
                st.rerun()

        # Show selected persona
        current_persona = self.canvas_data["metadata"].get("selected_persona", "business_owner")
        persona_names = {
            "business_owner": "👔 Business Owner",
            "business_analyst": "📋 Business Analyst",
            "data_engineer": "🔧 Data Engineer/DevOps"
        }

        st.info(f"**Current Role:** {persona_names[current_persona]}")

        # Progress tracking
        progress = self._calculate_completion_progress()
        st.progress(progress)
        st.write(f"Canvas Completion: {progress:.1%}")

        # THE COMPLETE DATA BUSINESS CANVAS - All sections visible in canvas layout
        current_persona = self.canvas_data["metadata"].get("selected_persona", "business_owner")

        # Permission legend at top
        self._render_permission_legend(current_persona)

        st.markdown("---")
        st.markdown("# 📊 Data Business Canvas")
        st.markdown("**Complete 9+3 Framework - All sections visible simultaneously**")

        # CANVAS LAYOUT: Traditional Business Model Canvas structure + Data extensions
        self._render_full_canvas_layout(current_persona)

    def _render_permission_legend(self, current_persona: str):
        """Render permission legend showing what the current persona can edit"""
        st.markdown("### 🔐 Your Permissions")

        col1, col2, col3 = st.columns(3)

        persona_colors = {
            "business_owner": "#e8f4f8",    # Light blue
            "business_analyst": "#f0f8e8",   # Light green
            "data_engineer": "#f8f0e8"       # Light orange
        }

        with col1:
            if current_persona == "business_owner":
                st.markdown(f"""
                <div style="background-color: {persona_colors['business_owner']}; padding: 10px; border-radius: 5px; border-left: 5px solid #2196F3;">
                <strong>👔 YOU CAN EDIT:</strong><br>
                • Executive Targets<br>
                • Value Propositions<br>
                • Customer Segments<br>
                • Proposals to BA
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("**👔 Business Owner**: Executive targets, value propositions")

        with col2:
            if current_persona == "business_analyst":
                st.markdown(f"""
                <div style="background-color: {persona_colors['business_analyst']}; padding: 10px; border-radius: 5px; border-left: 5px solid #4CAF50;">
                <strong>📋 YOU CAN EDIT:</strong><br>
                • Operations & Resources<br>
                • Technical Analysis<br>
                • Cost-Benefit Analysis<br>
                • Data Requirements
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("**📋 Business Analyst**: Operations, resources, technical analysis")

        with col3:
            if current_persona == "data_engineer":
                st.markdown(f"""
                <div style="background-color: {persona_colors['data_engineer']}; padding: 10px; border-radius: 5px; border-left: 5px solid #FF9800;">
                <strong>🔧 YOU CAN EDIT:</strong><br>
                • Data Sources<br>
                • Data Governance<br>
                • Technical Implementation<br>
                • Delivery & Operations
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("**🔧 Data Engineer**: Data sources, governance, implementation")

    def _render_full_canvas_layout(self, current_persona: str):
        """Render the complete Business Model Canvas layout in traditional grid format"""

        # EXECUTIVE TARGETS - Special section at top (Business Owner)
        with st.container():
            self._render_canvas_section(
                "⭐ Executive Target Alignment Analysis",
                self._render_executive_targets_section,
                current_persona, "business_owner", full_width=True
            )

        st.markdown("---")

        # ROW 1: Key Partners | Key Activities | Value Propositions | Customer Relationships | Customer Segments
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

        with col1:
            self._render_canvas_section(
                "🤝 Key Partners",
                self._render_key_partners_section,
                current_persona, "business_analyst"
            )

        with col2:
            self._render_canvas_section(
                "⚙️ Key Activities",
                self._render_key_activities_section,
                current_persona, "business_analyst"
            )

        with col3:
            self._render_canvas_section(
                "💡 Value Propositions",
                self._render_value_propositions_section,
                current_persona, "business_owner"
            )

        with col4:
            self._render_canvas_section(
                "🤝 Customer Relationships",
                self._render_customer_relationships_section,
                current_persona, "business_owner"
            )

        with col5:
            self._render_canvas_section(
                "👥 Customer Segments",
                self._render_customer_segments_section,
                current_persona, "business_owner"
            )

        # ROW 2: Key Resources | [spans across] | Channels
        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            self._render_canvas_section(
                "🔑 Key Resources",
                self._render_key_resources_section,
                current_persona, "business_analyst"
            )

        with col3:
            self._render_canvas_section(
                "📺 Channels",
                self._render_channels_section,
                current_persona, "business_owner"
            )

        # ROW 3: Cost Structure | Revenue Streams
        col1, col2 = st.columns([1, 1])

        with col1:
            self._render_canvas_section(
                "💰 Cost Structure",
                self._render_cost_structure_section,
                current_persona, "business_analyst"
            )

        with col2:
            self._render_canvas_section(
                "💵 Revenue Streams",
                self._render_revenue_streams_section,
                current_persona, "business_owner"
            )

        st.markdown("---")
        st.markdown("## 📊 Data-Specific Extensions (+3)")

        # DATA EXTENSIONS ROW: Data Sources | Data Governance | Technology Infrastructure
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            self._render_canvas_section(
                "📊 Data Sources",
                self._render_data_sources_section,
                current_persona, "data_engineer"
            )

        with col2:
            self._render_canvas_section(
                "🔒 Data Governance",
                self._render_data_governance_section,
                current_persona, "data_engineer"
            )

        with col3:
            self._render_canvas_section(
                "🔧 Technology Infrastructure",
                self._render_technology_infrastructure_section,
                current_persona, "data_engineer"
            )

        # EXPORT SECTION (Always accessible)
        st.markdown("---")
        with st.container():
            st.subheader("📋 Export & Analysis")
            self._render_export_handoff_section()

    def _render_canvas_section(self, title: str, render_func, current_persona: str, owner_persona: str, full_width: bool = False):
        """Render a single canvas section with proper permission indicators"""
        permission = "edit" if current_persona == owner_persona else "view"

        # Color coding based on owner persona
        colors = {
            "business_owner": {"bg": "#e3f2fd", "border": "#2196F3"},
            "business_analyst": {"bg": "#e8f5e8", "border": "#4CAF50"},
            "data_engineer": {"bg": "#fff3e0", "border": "#FF9800"}
        }

        color_scheme = colors[owner_persona]

        # Create container with visual styling
        if permission == "edit":
            container_style = f"""
            <div style="
                border: 3px solid {color_scheme['border']};
                background-color: {color_scheme['bg']};
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                min-height: 200px;
            ">
            """
        else:
            container_style = f"""
            <div style="
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                min-height: 200px;
            ">
            """

        st.markdown(container_style, unsafe_allow_html=True)

        # Section header with permission indicator
        st.write(f"**{title}**")
        if permission == "edit":
            st.write("✏️ *You can edit*")
        else:
            st.write("👀 *View only*")

        # Render section content
        try:
            render_func()
        except Exception as e:
            st.error(f"Error rendering {title}: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    def _get_section_permission(self, current_persona: str, section: str) -> str:
        """Get permission level for a section based on current persona"""
        permissions = {
            "business_owner": {
                "executive_targets": "edit",
                "value_users": "edit",
                "operations_resources": "view",
                "data_governance": "view"
            },
            "business_analyst": {
                "executive_targets": "view",
                "value_users": "view",
                "operations_resources": "edit",
                "data_governance": "view"
            },
            "data_engineer": {
                "executive_targets": "view",
                "value_users": "view",
                "operations_resources": "view",
                "data_governance": "edit"
            }
        }
        return permissions.get(current_persona, {}).get(section, "view")

    def _render_section_with_permissions(self, title: str, render_func, permission: str, owner_persona: str):
        """Render a section with visual permission indicators"""
        # Define colors for each persona
        persona_colors = {
            "business_owner": "#e3f2fd",    # Light blue
            "business_analyst": "#e8f5e8",   # Light green
            "data_engineer": "#fff3e0"       # Light orange
        }

        border_colors = {
            "business_owner": "#2196F3",    # Blue
            "business_analyst": "#4CAF50",   # Green
            "data_engineer": "#FF9800"       # Orange
        }

        # Create container with colored border based on owner
        if permission == "edit":
            # Thick border for edit access
            container_style = f"""
            <div style="border: 3px solid {border_colors[owner_persona]};
                       background-color: {persona_colors[owner_persona]};
                       padding: 15px; border-radius: 10px; margin: 10px 0;">
            """
            permission_badge = "✏️ **YOU CAN EDIT**"
        else:
            # Thin border for view-only
            container_style = f"""
            <div style="border: 1px solid #ddd;
                       background-color: #f9f9f9;
                       padding: 15px; border-radius: 10px; margin: 10px 0;">
            """
            permission_badge = "👀 **VIEW ONLY**"

        st.markdown(container_style, unsafe_allow_html=True)

        # Header with permission indicator
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(title)
        with col2:
            if permission == "edit":
                st.success(permission_badge)
            else:
                st.info(permission_badge)

        # Render the section content
        try:
            if callable(render_func):
                result = render_func()
                # Handle cases where render_func returns a tuple (multiple functions)
                if isinstance(result, tuple):
                    pass  # Functions were executed
        except Exception as e:
            st.error(f"Error rendering section: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # === CANVAS SECTION RENDERING METHODS ===

    def _render_value_propositions_section(self):
        """Value Propositions section of the canvas"""
        insights = self.canvas_data.get("value_propositions", {}).get("data_insights", [])
        for insight in insights[:3]:  # Show first 3
            st.write(f"• {insight}")

    def _render_customer_segments_section(self):
        """Customer Segments section of the canvas"""
        primary_users = self.canvas_data.get("customer_segments", {}).get("primary_users", [])
        for user in primary_users[:3]:  # Show first 3
            st.write(f"• {user}")

    def _render_customer_relationships_section(self):
        """Customer Relationships section of the canvas"""
        engagement = self.canvas_data.get("customer_relationships", {}).get("engagement_model", [])
        for item in engagement[:3]:  # Show first 3
            st.write(f"• {item}")

    def _render_channels_section(self):
        """Channels section of the canvas"""
        delivery_methods = self.canvas_data.get("channels", {}).get("delivery_methods", [])
        for method in delivery_methods[:3]:  # Show first 3
            st.write(f"• {method}")

    def _render_key_activities_section(self):
        """Key Activities section of the canvas"""
        data_collection = self.canvas_data.get("key_activities", {}).get("data_collection", [])
        for activity in data_collection[:3]:  # Show first 3
            st.write(f"• {activity}")

    def _render_key_resources_section(self):
        """Key Resources section of the canvas"""
        data_assets = self.canvas_data.get("key_resources", {}).get("data_assets", [])
        for asset in data_assets[:3]:  # Show first 3
            st.write(f"• {asset}")

    def _render_key_partners_section(self):
        """Key Partners section of the canvas"""
        data_providers = self.canvas_data.get("key_partners", {}).get("data_providers", [])
        for provider in data_providers[:3]:  # Show first 3
            st.write(f"• {provider}")

    def _render_cost_structure_section(self):
        """Cost Structure section of the canvas"""
        data_acquisition = self.canvas_data.get("cost_structure", {}).get("data_acquisition", [])
        for cost in data_acquisition[:3]:  # Show first 3
            st.write(f"• {cost}")

    def _render_revenue_streams_section(self):
        """Revenue Streams section of the canvas"""
        direct_revenue = self.canvas_data.get("revenue_streams", {}).get("direct_revenue", [])
        for revenue in direct_revenue[:3]:  # Show first 3
            st.write(f"• {revenue}")

    def _render_data_sources_section(self):
        """Data Sources section of the canvas"""
        internal_sources = self.canvas_data.get("data_sources", {}).get("internal_sources", [])
        external_sources = self.canvas_data.get("data_sources", {}).get("external_sources", [])

        if internal_sources:
            st.write("**Internal:**")
            for source in internal_sources[:2]:
                st.write(f"• {source}")

        if external_sources:
            st.write("**External:**")
            for source in external_sources[:2]:
                st.write(f"• {source}")

    def _render_data_governance_section(self):
        """Data Governance section of the canvas"""
        quality_standards = self.canvas_data.get("data_governance", {}).get("quality_standards", [])
        compliance = self.canvas_data.get("data_governance", {}).get("compliance_requirements", [])

        if quality_standards:
            st.write("**Quality:**")
            for standard in quality_standards[:2]:
                st.write(f"• {standard}")

        if compliance:
            st.write("**Compliance:**")
            for req in compliance[:2]:
                st.write(f"• {req}")

    def _render_technology_infrastructure_section(self):
        """Technology Infrastructure section of the canvas"""
        data_platforms = self.canvas_data.get("technology_infrastructure", {}).get("data_platforms", [])
        analytics_tools = self.canvas_data.get("technology_infrastructure", {}).get("analytics_tools", [])

        if data_platforms:
            st.write("**Platforms:**")
            for platform in data_platforms[:2]:
                st.write(f"• {platform}")

        if analytics_tools:
            st.write("**Tools:**")
            for tool in analytics_tools[:2]:
                st.write(f"• {tool}")

    # === BUSINESS OWNER PERSONA METHODS ===

    def _render_business_strategy_section(self):
        """Business Owner: Value propositions, challenges, and customer focus"""
        st.header("🎯 Business Strategy")

        # This combines the old value_users_section content
        self._render_value_users_section()

    def _render_ba_proposal_section(self):
        """Business Owner can propose ideas to BA"""
        st.header("📋 Proposals for Business Analyst")

        st.info("""
        **💡 You can propose ideas to the Business Analyst below.**
        The BA will review and refine these into technical requirements.
        """)

        proposal_text = st.text_area(
            "Data Requirements Proposals",
            value=self.canvas_data.get("ba_proposals", {}).get("data_requirements", ""),
            height=100,
            help="Suggest what data sources or processing you think might be needed",
            placeholder="Example: We might need customer transaction data from our CRM, external market data, and real-time website analytics..."
        )
        self.canvas_data.setdefault("ba_proposals", {})["data_requirements"] = proposal_text

        cost_proposal = st.text_area(
            "Budget & Timeline Proposals",
            value=self.canvas_data.get("ba_proposals", {}).get("budget_timeline", ""),
            height=100,
            help="Share your budget constraints and timeline expectations",
            placeholder="Example: Budget around $50K, need initial results within 3 months..."
        )
        self.canvas_data.setdefault("ba_proposals", {})["budget_timeline"] = cost_proposal

    # === BUSINESS ANALYST PERSONA METHODS ===

    def _render_business_review_section(self):
        """BA reviews business owner input"""
        st.header("📋 Business Requirements Review")

        # Show business owner's input in read-only format
        st.subheader("👔 Business Owner Input")

        if self.canvas_data["executive_targets"].get("targets"):
            st.write("**Executive Targets:**")
            for target in self.canvas_data["executive_targets"]["targets"]:
                st.write(f"• {target.get('description', 'No description')}")
        else:
            st.info("No executive targets defined yet")

        # Show proposals from business owner
        ba_proposals = self.canvas_data.get("ba_proposals", {})
        if ba_proposals.get("data_requirements"):
            st.write("**Data Requirements Proposals:**")
            st.write(ba_proposals["data_requirements"])

        if ba_proposals.get("budget_timeline"):
            st.write("**Budget & Timeline Proposals:**")
            st.write(ba_proposals["budget_timeline"])

    def _render_data_requirements_section(self):
        """BA defines technical data requirements"""
        st.header("🔍 Data Requirements Analysis")

        # This will use existing data sources section
        self._render_data_governance_section()

    def _render_technical_analysis_section(self):
        """BA bridges business and technical"""
        st.header("📊 Technical Analysis")

        # This will use parts of operations section
        self._render_operations_resources_section()

    def _render_cost_benefit_section(self):
        """BA analyzes costs and benefits"""
        st.header("💰 Cost-Benefit Analysis")

        st.subheader("📈 Expected Benefits")
        benefits = st.text_area(
            "Quantify expected business benefits",
            value=self.canvas_data.get("ba_analysis", {}).get("benefits", ""),
            height=100,
            help="Revenue increase, cost savings, efficiency gains, etc."
        )
        self.canvas_data.setdefault("ba_analysis", {})["benefits"] = benefits

        st.subheader("💸 Investment Requirements")
        costs = st.text_area(
            "Estimate total investment needed",
            value=self.canvas_data.get("ba_analysis", {}).get("costs", ""),
            height=100,
            help="Technology, personnel, external data, etc."
        )
        self.canvas_data.setdefault("ba_analysis", {})["costs"] = costs

    # === DATA ENGINEER PERSONA METHODS ===

    def _render_requirements_review_section(self):
        """Data Engineer reviews BA requirements"""
        st.header("📋 Requirements Review")

        # Show BA analysis in read-only
        st.subheader("📋 BA Analysis")

        ba_analysis = self.canvas_data.get("ba_analysis", {})
        if ba_analysis.get("benefits"):
            st.write("**Expected Benefits:**")
            st.write(ba_analysis["benefits"])

        if ba_analysis.get("costs"):
            st.write("**Investment Requirements:**")
            st.write(ba_analysis["costs"])

    def _render_technical_implementation_section(self):
        """Data Engineer designs the technical solution"""
        st.header("🔧 Technical Implementation")

        st.subheader("🏗️ Architecture Design")
        architecture = st.text_area(
            "Technical architecture and data flow",
            value=self.canvas_data.get("tech_implementation", {}).get("architecture", ""),
            height=150,
            help="Data sources → Processing → Storage → APIs"
        )
        self.canvas_data.setdefault("tech_implementation", {})["architecture"] = architecture

        st.subheader("⚙️ Technology Stack")
        tech_stack = st.text_area(
            "Tools and technologies to be used",
            value=self.canvas_data.get("tech_implementation", {}).get("tech_stack", ""),
            height=100,
            help="Cloud services, databases, processing frameworks, etc."
        )
        self.canvas_data.setdefault("tech_implementation", {})["tech_stack"] = tech_stack

    def _render_delivery_operations_section(self):
        """Data Engineer plans delivery and operations"""
        st.header("📈 Delivery & Operations")

        st.subheader("🗓️ Delivery Timeline")
        timeline = st.text_area(
            "Implementation phases and milestones",
            value=self.canvas_data.get("delivery_ops", {}).get("timeline", ""),
            height=100,
            help="Phase 1: Data ingestion, Phase 2: Processing, etc."
        )
        self.canvas_data.setdefault("delivery_ops", {})["timeline"] = timeline

        st.subheader("🔧 Operations Plan")
        operations = st.text_area(
            "Monitoring, maintenance, and support",
            value=self.canvas_data.get("delivery_ops", {}).get("operations", ""),
            height=100,
            help="Monitoring dashboards, alerting, backup procedures, etc."
        )
        self.canvas_data.setdefault("delivery_ops", {})["operations"] = operations

    def _render_export_handoff_section(self):
        """Export and handoff functionality for all personas"""
        st.write("**Export current canvas state for handoff between personas**")

        if st.button("📤 Export Canvas for Handoff"):
            canvas_json = json.dumps(self.canvas_data, indent=2, default=str)
            st.download_button(
                label="Download Canvas JSON",
                data=canvas_json,
                file_name=f"data_canvas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    def _render_value_users_section(self):
        """Render Value Propositions and Customer segments"""
        st.header("🎯 Value Propositions & Customer Segments")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💡 Value Propositions")
            st.write("What specific data insights and business value will you create?")

            # Data insights
            st.write("**Data Insights You'll Generate:**")
            insights = st.text_area(
                "List the key insights your data will provide",
                value="\n".join(self.canvas_data["value_propositions"]["data_insights"]),
                height=100,
                help="e.g., Customer behavior patterns, Supply chain optimization opportunities, Risk assessment metrics"
            )
            self.canvas_data["value_propositions"]["data_insights"] = [
                i.strip() for i in insights.split('\n') if i.strip()
            ]

            # Business outcomes
            st.write("**Expected Business Outcomes:**")
            outcomes = st.text_area(
                "What business outcomes will these insights drive?",
                value="\n".join(self.canvas_data["value_propositions"]["business_outcomes"]),
                height=100,
                help="e.g., 15% cost reduction, Faster decision making, New revenue opportunities"
            )
            self.canvas_data["value_propositions"]["business_outcomes"] = [
                o.strip() for o in outcomes.split('\n') if o.strip()
            ]

            # Competitive advantages
            st.write("**Competitive Advantages:**")
            advantages = st.text_area(
                "How will this data give you a competitive edge?",
                value="\n".join(self.canvas_data["value_propositions"]["competitive_advantages"]),
                height=100,
                help="e.g., Better market timing, Unique insights, Operational efficiency"
            )
            self.canvas_data["value_propositions"]["competitive_advantages"] = [
                a.strip() for a in advantages.split('\n') if a.strip()
            ]

        with col2:
            st.subheader("👥 Customer Segments")
            st.write("Who are the primary users and beneficiaries of your data insights?")

            # Primary users
            st.write("**Primary Users:**")
            primary_users = st.text_area(
                "Who will directly use the data and insights?",
                value="\n".join(self.canvas_data["customer_segments"]["primary_users"]),
                height=100,
                help="e.g., Operations managers, Financial analysts, Executive team"
            )
            self.canvas_data["customer_segments"]["primary_users"] = [
                u.strip() for u in primary_users.split('\n') if u.strip()
            ]

            # Secondary users
            st.write("**Secondary Users:**")
            secondary_users = st.text_area(
                "Who else will benefit from or consume these insights?",
                value="\n".join(self.canvas_data["customer_segments"]["secondary_users"]),
                height=100,
                help="e.g., External partners, Customers, Regulatory bodies"
            )
            self.canvas_data["customer_segments"]["secondary_users"] = [
                u.strip() for u in secondary_users.split('\n') if u.strip()
            ]

            # User personas
            st.write("**Key User Personas:**")
            personas = st.text_area(
                "Describe 2-3 key user personas with their specific needs",
                value="\n".join(self.canvas_data["customer_segments"]["user_personas"]),
                height=120,
                help="e.g., 'Sarah (Supply Chain Manager): Needs real-time inventory visibility to prevent stockouts'"
            )
            self.canvas_data["customer_segments"]["user_personas"] = [
                p.strip() for p in personas.split('\n') if p.strip()
            ]

        # Engagement and channels
        st.subheader("🤝 Customer Relationships & Channels")

        col3, col4 = st.columns(2)

        with col3:
            st.write("**Engagement Model:**")
            engagement = st.selectbox(
                "How will you engage with data consumers?",
                ["Self-service dashboards", "Regular reports", "On-demand analysis",
                 "Embedded insights", "API access", "Other"],
                index=0 if not self.canvas_data["customer_relationships"]["engagement_model"]
                else ["Self-service dashboards", "Regular reports", "On-demand analysis",
                      "Embedded insights", "API access", "Other"].index(
                    self.canvas_data["customer_relationships"]["engagement_model"])
            )
            self.canvas_data["customer_relationships"]["engagement_model"] = engagement

            feedback = st.text_area(
                "Feedback Mechanisms:",
                value="\n".join(self.canvas_data["customer_relationships"]["feedback_mechanisms"]),
                height=80,
                help="How will users provide feedback on data quality and insights?"
            )
            self.canvas_data["customer_relationships"]["feedback_mechanisms"] = [
                f.strip() for f in feedback.split('\n') if f.strip()
            ]

        with col4:
            st.write("**Delivery Channels:**")
            channels = st.text_area(
                "How will insights be delivered to users?",
                value="\n".join(self.canvas_data["channels"]["delivery_methods"]),
                height=80,
                help="e.g., Web dashboards, Mobile apps, Email reports, API endpoints"
            )
            self.canvas_data["channels"]["delivery_methods"] = [
                c.strip() for c in channels.split('\n') if c.strip()
            ]

            interfaces = st.text_area(
                "Access Interfaces:",
                value="\n".join(self.canvas_data["channels"]["access_interfaces"]),
                height=80,
                help="e.g., Business intelligence tools, Custom applications, Direct database access"
            )
            self.canvas_data["channels"]["access_interfaces"] = [
                i.strip() for i in interfaces.split('\n') if i.strip()
            ]

    def _render_operations_resources_section(self):
        """Render Operations, Resources, Partners, and Economics"""
        st.header("🔧 Operations, Resources & Economics")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚙️ Key Activities")
            st.write("What are the core data operations you need to perform?")

            # Data collection activities
            st.write("**Data Collection:**")
            collection = st.text_area(
                "How will you collect and ingest data?",
                value="\n".join(self.canvas_data["key_activities"]["data_collection"]),
                height=80,
                help="e.g., Web scraping, API integration, File uploads, Real-time streaming"
            )
            self.canvas_data["key_activities"]["data_collection"] = [
                c.strip() for c in collection.split('\n') if c.strip()
            ]

            # Data processing activities
            st.write("**Data Processing:**")
            processing = st.text_area(
                "What processing and transformation is needed?",
                value="\n".join(self.canvas_data["key_activities"]["data_processing"]),
                height=80,
                help="e.g., Data cleaning, Normalization, Aggregation, Enrichment"
            )
            self.canvas_data["key_activities"]["data_processing"] = [
                p.strip() for p in processing.split('\n') if p.strip()
            ]

            # Insight generation
            st.write("**Insight Generation:**")
            insights = st.text_area(
                "How will you generate actionable insights?",
                value="\n".join(self.canvas_data["key_activities"]["insight_generation"]),
                height=80,
                help="e.g., Statistical analysis, Machine learning, Trend analysis, Benchmarking"
            )
            self.canvas_data["key_activities"]["insight_generation"] = [
                i.strip() for i in insights.split('\n') if i.strip()
            ]

        with col2:
            st.subheader("🏗️ Key Resources")
            st.write("What essential resources do you need?")

            # Data assets
            st.write("**Data Assets:**")
            assets = st.text_area(
                "What are your critical data assets?",
                value="\n".join(self.canvas_data["key_resources"]["data_assets"]),
                height=80,
                help="e.g., Customer database, Transaction history, Market data feeds"
            )
            self.canvas_data["key_resources"]["data_assets"] = [
                a.strip() for a in assets.split('\n') if a.strip()
            ]

            # Technical resources
            st.write("**Technical Resources:**")
            technical = st.text_area(
                "What technical infrastructure is required?",
                value="\n".join(self.canvas_data["key_resources"]["technical_resources"]),
                height=80,
                help="e.g., Cloud computing, Data storage, Analytics platforms, APIs"
            )
            self.canvas_data["key_resources"]["technical_resources"] = [
                t.strip() for t in technical.split('\n') if t.strip()
            ]

            # Human resources
            st.write("**Human Resources:**")
            human = st.text_area(
                "What human capabilities are needed?",
                value="\n".join(self.canvas_data["key_resources"]["human_resources"]),
                height=80,
                help="e.g., Data scientists, Analysts, Domain experts, IT support"
            )
            self.canvas_data["key_resources"]["human_resources"] = [
                h.strip() for h in human.split('\n') if h.strip()
            ]

        # Partners and Economics
        st.subheader("🤝 Key Partners")
        col3, col4 = st.columns(2)

        with col3:
            st.write("**Data Providers:**")
            providers = st.text_area(
                "Who provides external data?",
                value="\n".join(self.canvas_data["key_partners"]["data_providers"]),
                height=80,
                help="e.g., Government agencies, Market data vendors, Industry associations"
            )
            self.canvas_data["key_partners"]["data_providers"] = [
                p.strip() for p in providers.split('\n') if p.strip()
            ]

            st.write("**Technology Partners:**")
            tech_partners = st.text_area(
                "What technology partnerships are needed?",
                value="\n".join(self.canvas_data["key_partners"]["technology_partners"]),
                height=80,
                help="e.g., Cloud providers, Software vendors, Integration specialists"
            )
            self.canvas_data["key_partners"]["technology_partners"] = [
                t.strip() for t in tech_partners.split('\n') if t.strip()
            ]

        with col4:
            st.subheader("💰 Economics")

            st.write("**Cost Structure:**")
            costs = st.text_area(
                "What are your main cost drivers?",
                value="\n".join(self.canvas_data["cost_structure"]["data_acquisition"] +
                              self.canvas_data["cost_structure"]["infrastructure"] +
                              self.canvas_data["cost_structure"]["operational"]),
                height=100,
                help="e.g., Data licenses, Cloud infrastructure, Personnel, Compliance"
            )
            all_costs = [c.strip() for c in costs.split('\n') if c.strip()]
            # Simple distribution - can be enhanced
            self.canvas_data["cost_structure"]["data_acquisition"] = all_costs[:len(all_costs)//3]
            self.canvas_data["cost_structure"]["infrastructure"] = all_costs[len(all_costs)//3:2*len(all_costs)//3]
            self.canvas_data["cost_structure"]["operational"] = all_costs[2*len(all_costs)//3:]

            st.write("**Revenue/Value Streams:**")
            revenue = st.text_area(
                "How does this data create financial value?",
                value="\n".join(self.canvas_data["revenue_streams"]["direct_revenue"] +
                              self.canvas_data["revenue_streams"]["cost_savings"] +
                              self.canvas_data["revenue_streams"]["strategic_value"]),
                height=100,
                help="e.g., Cost savings, Revenue growth, Risk reduction, Strategic advantages"
            )
            all_revenue = [r.strip() for r in revenue.split('\n') if r.strip()]
            # Simple distribution - can be enhanced
            self.canvas_data["revenue_streams"]["direct_revenue"] = all_revenue[:len(all_revenue)//3]
            self.canvas_data["revenue_streams"]["cost_savings"] = all_revenue[len(all_revenue)//3:2*len(all_revenue)//3]
            self.canvas_data["revenue_streams"]["strategic_value"] = all_revenue[2*len(all_revenue)//3:]

    def _render_data_governance_section(self):
        """Render Data Sources, Governance, and Technology"""
        st.header("📊 Data Sources, Governance & Technology")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🗃️ Data Sources")
            st.write("Where does your data come from?")

            # Internal sources
            st.write("**Internal Data Sources:**")
            internal = st.text_area(
                "What internal data sources do you have?",
                value="\n".join(self.canvas_data["data_sources"]["internal_sources"]),
                height=80,
                help="e.g., CRM system, ERP database, Transaction logs, User activity"
            )
            self.canvas_data["data_sources"]["internal_sources"] = [
                i.strip() for i in internal.split('\n') if i.strip()
            ]

            # External sources
            st.write("**External Data Sources:**")
            external = st.text_area(
                "What external data sources do you need?",
                value="\n".join(self.canvas_data["data_sources"]["external_sources"]),
                height=80,
                help="e.g., Industry reports, Government databases, Market feeds, Social media"
            )
            self.canvas_data["data_sources"]["external_sources"] = [
                e.strip() for e in external.split('\n') if e.strip()
            ]

            # Data frequency
            col_rt, col_batch = st.columns(2)
            with col_rt:
                st.write("**Real-time Feeds:**")
                realtime = st.text_area(
                    "What data needs real-time updates?",
                    value="\n".join(self.canvas_data["data_sources"]["real_time_feeds"]),
                    height=60
                )
                self.canvas_data["data_sources"]["real_time_feeds"] = [
                    r.strip() for r in realtime.split('\n') if r.strip()
                ]

            with col_batch:
                st.write("**Batch Sources:**")
                batch = st.text_area(
                    "What data can be processed in batches?",
                    value="\n".join(self.canvas_data["data_sources"]["batch_sources"]),
                    height=60
                )
                self.canvas_data["data_sources"]["batch_sources"] = [
                    b.strip() for b in batch.split('\n') if b.strip()
                ]

        with col2:
            st.subheader("🛡️ Data Governance")
            st.write("How will you ensure data quality and compliance?")

            # Quality standards
            st.write("**Quality Standards:**")
            quality = st.text_area(
                "What data quality standards are required?",
                value="\n".join(self.canvas_data["data_governance"]["quality_standards"]),
                height=80,
                help="e.g., 95% accuracy, Complete records, Timely updates, Consistent formats"
            )
            self.canvas_data["data_governance"]["quality_standards"] = [
                q.strip() for q in quality.split('\n') if q.strip()
            ]

            # Compliance requirements
            st.write("**Compliance Requirements:**")
            compliance = st.text_area(
                "What regulatory compliance is needed?",
                value="\n".join(self.canvas_data["data_governance"]["compliance_requirements"]),
                height=80,
                help="e.g., GDPR, HIPAA, SOX, Industry-specific regulations"
            )
            self.canvas_data["data_governance"]["compliance_requirements"] = [
                c.strip() for c in compliance.split('\n') if c.strip()
            ]

            # Access controls
            st.write("**Access Controls:**")
            access = st.text_area(
                "Who should have access to what data?",
                value="\n".join(self.canvas_data["data_governance"]["access_controls"]),
                height=80,
                help="e.g., Role-based access, Data classification, Audit trails"
            )
            self.canvas_data["data_governance"]["access_controls"] = [
                a.strip() for a in access.split('\n') if a.strip()
            ]

        # Technology Infrastructure
        st.subheader("🔧 Technology Infrastructure")

        col3, col4 = st.columns(2)

        with col3:
            st.write("**Data Platforms:**")
            platforms = st.text_area(
                "What data platforms will you use?",
                value="\n".join(self.canvas_data["technology_infrastructure"]["data_platforms"]),
                height=80,
                help="e.g., Cloud data warehouses, Data lakes, Streaming platforms"
            )
            self.canvas_data["technology_infrastructure"]["data_platforms"] = [
                p.strip() for p in platforms.split('\n') if p.strip()
            ]

            st.write("**Analytics Tools:**")
            analytics = st.text_area(
                "What analytics and BI tools are needed?",
                value="\n".join(self.canvas_data["technology_infrastructure"]["analytics_tools"]),
                height=80,
                help="e.g., Business intelligence tools, Statistical software, ML platforms"
            )
            self.canvas_data["technology_infrastructure"]["analytics_tools"] = [
                a.strip() for a in analytics.split('\n') if a.strip()
            ]

        with col4:
            st.write("**Integration Capabilities:**")
            integration = st.text_area(
                "How will systems be integrated?",
                value="\n".join(self.canvas_data["technology_infrastructure"]["integration_capabilities"]),
                height=80,
                help="e.g., APIs, ETL tools, Data pipelines, Message queues"
            )
            self.canvas_data["technology_infrastructure"]["integration_capabilities"] = [
                i.strip() for i in integration.split('\n') if i.strip()
            ]

            st.write("**Security Measures:**")
            security = st.text_area(
                "What security measures are required?",
                value="\n".join(self.canvas_data["technology_infrastructure"]["security_measures"]),
                height=80,
                help="e.g., Encryption, Access controls, Monitoring, Backup systems"
            )
            self.canvas_data["technology_infrastructure"]["security_measures"] = [
                s.strip() for s in security.split('\n') if s.strip()
            ]

        # Business domain and language selection with semantic routing
        st.subheader("🌐 Context Settings & Semantic Routing")
        col5, col6, col7 = st.columns(3)

        with col5:
            domain = st.selectbox(
                "Primary Business Domain:",
                ["agriculture", "trading", "supply_chain", "healthcare", "finance",
                 "manufacturing", "retail", "logistics", "energy", "other"],
                index=["agriculture", "trading", "supply_chain", "healthcare", "finance",
                       "manufacturing", "retail", "logistics", "energy", "other"].index(
                    self.canvas_data["metadata"]["business_domain"])
                if self.canvas_data["metadata"]["business_domain"] else 0
            )
            self.canvas_data["metadata"]["business_domain"] = domain

        with col6:
            language = st.selectbox(
                "Primary Language:",
                ["en", "tr", "es", "fr", "de", "pt", "it", "other"],
                index=["en", "tr", "es", "fr", "de", "pt", "it", "other"].index(
                    self.canvas_data["metadata"]["primary_language"])
                if self.canvas_data["metadata"]["primary_language"] else 0
            )
            self.canvas_data["metadata"]["primary_language"] = language

        with col7:
            if st.button("🌍 Semantic Route Terms"):
                with st.spinner("Running semantic term routing..."):
                    routing_results = asyncio.run(self._semantic_route_terms())
                    st.success(f"Routed {routing_results['routed_terms']} terms")

                    if routing_results.get("new_terms"):
                        with st.expander("🔍 View Semantic Mappings"):
                            for original, mapped in routing_results["new_terms"].items():
                                st.write(f"**{original}** → {mapped}")

        # Semantic term input assistant
        st.subheader("🧠 Semantic Term Assistant")
        col8, col9 = st.columns(2)

        with col8:
            term_input = st.text_input(
                "Enter business term for semantic validation:",
                help="Enter a term to check its semantic mapping"
            )

            if term_input and st.button("🔍 Check Term"):
                if self.skos_router:
                    routing_result = self.skos_router.route_term_to_preferred(
                        term_input, language, "en"
                    )

                    if routing_result.get("preferred_label"):
                        st.success(f"✅ Found: **{routing_result['preferred_label']}**")
                        st.write(f"Confidence: {routing_result['translation_confidence']:.1%}")
                        st.write(f"Method: {routing_result['method']}")

                        if routing_result.get("definition"):
                            st.info(f"💡 {routing_result['definition']}")
                    else:
                        st.warning("⚠️ Term not found in semantic vocabulary")
                        if st.button("➕ Add to Custom Vocabulary"):
                            # Placeholder for adding custom terms
                            st.info("Custom term addition would be implemented here")

        with col9:
            # Display current semantic mappings if any
            if "semantic_mappings" in self.canvas_data.get("metadata", {}):
                st.write("**Current Semantic Mappings:**")
                mappings = self.canvas_data["metadata"]["semantic_mappings"]
                for term, mapping in mappings.items():
                    st.write(f"• {term} → {mapping}")
            else:
                st.info("No semantic mappings yet. Use 'Semantic Route Terms' to create mappings.")

    def _render_review_export_section(self):
        """Render review, validation, and export functionality"""
        st.header("📋 Review & Export")

        # Canvas summary
        st.subheader("📊 Canvas Summary")

        completion = self._calculate_completion_progress()
        st.metric("Completion Progress", f"{completion:.1%}")

        # Enhanced BAML-powered validation
        col_val1, col_val2 = st.columns(2)

        with col_val1:
            if st.button("🔍 Quick Validate", type="secondary"):
                validation_results = self._validate_canvas_basic()
                self._display_validation_results(validation_results, "basic")

        with col_val2:
            if st.button("🧠 BAML Validate", type="primary"):
                with st.spinner("Running BAML semantic validation..."):
                    validation_results = asyncio.run(self._validate_canvas_advanced())
                self._display_validation_results(validation_results, "advanced")

        # Export options
        st.subheader("💾 Export Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export JSON"):
                json_data = self._export_to_json()
                st.download_button(
                    label="💾 Download JSON",
                    data=json_data,
                    file_name=f"data_business_canvas_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📋 Generate SOW Draft"):
                if asyncio.run(self._generate_sow_draft()):
                    st.success("SOW draft generated successfully!")

        with col3:
            if st.button("🔍 Enhanced Data Discovery"):
                discovery_context = self._prepare_discovery_context()
                st.session_state["discovery_context"] = discovery_context
                st.success("Discovery context prepared! Proceeding to enhanced discovery...")
                st.switch_page("pages/enhanced_data_discovery.py")

                # Show what will be passed to discovery agents
                with st.expander("🔍 View Discovery Context"):
                    st.json(discovery_context)

        # Canvas visualization
        st.subheader("🎨 Canvas Visualization")
        self._render_canvas_visualization()

    def _calculate_completion_progress(self) -> float:
        """Calculate canvas completion percentage"""
        total_fields = 0
        completed_fields = 0

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

        count_fields(self.canvas_data)

        return completed_fields / total_fields if total_fields > 0 else 0.0

    def _validate_canvas_basic(self) -> Dict[str, Any]:
        """Basic canvas validation for completeness and consistency"""
        issues = []

        # Check critical sections
        critical_sections = [
            ("value_propositions.data_insights", "Data insights"),
            ("customer_segments.primary_users", "Primary users"),
            ("data_sources.external_sources", "External data sources"),
            ("data_governance.quality_standards", "Quality standards")
        ]

        for path, description in critical_sections:
            value = self._get_nested_value(self.canvas_data, path)
            if not value:
                issues.append(f"Missing {description}")

        # Business domain validation
        if not self.canvas_data["metadata"]["business_domain"]:
            issues.append("Business domain not specified")

        # Check for consistency
        if (self.canvas_data["data_sources"]["real_time_feeds"] and
            not any("real-time" in platform.lower()
                   for platform in self.canvas_data["technology_infrastructure"]["data_platforms"])):
            issues.append("Real-time data sources specified but no streaming platform mentioned")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "completion_score": self._calculate_completion_progress(),
            "validation_type": "basic"
        }

    async def _validate_canvas_advanced(self) -> Dict[str, Any]:
        """Advanced BAML-powered canvas validation"""
        try:
            if not self.validator.sow_agent:
                await self.validator.initialize()

            # Run comprehensive validation
            validation_results = await self.validator.validate_canvas(self.canvas_data)
            validation_results["validation_type"] = "advanced"

            return validation_results

        except Exception as e:
            logger.error(f"Advanced validation failed: {e}")
            return {
                "is_valid": False,
                "overall_score": 0.0,
                "blocking_issues": [f"Validation engine error: {e}"],
                "warnings": [],
                "recommendations": ["Retry validation or use quick validate"],
                "validation_type": "advanced_failed"
            }

    def _display_validation_results(self, results: Dict[str, Any], validation_type: str):
        """Display validation results in Streamlit interface"""

        if validation_type == "basic":
            # Basic validation display
            if results["is_valid"]:
                st.success("✅ Basic validation passed!")
                st.write(f"**Completion:** {results['completion_score']:.1%}")
            else:
                st.warning("⚠️ Canvas needs attention:")
                for issue in results["issues"]:
                    st.write(f"• {issue}")

        elif validation_type == "advanced":
            # Advanced validation display
            overall_score = results.get("overall_score", 0.0)

            if results.get("is_valid"):
                st.success("✅ BAML validation passed!")
            else:
                st.warning("⚠️ BAML validation found issues")

            # Overall score
            st.metric("Overall Validation Score", f"{overall_score:.1%}")

            # Section scores
            if "sections" in results:
                st.write("**Section Scores:**")
                cols = st.columns(len(results["sections"]))
                for i, (section_name, section_data) in enumerate(results["sections"].items()):
                    if isinstance(section_data, dict) and "score" in section_data:
                        cols[i].metric(
                            section_name.replace("_", " ").title(),
                            f"{section_data['score']:.1%}"
                        )

            # Blocking issues
            if results.get("blocking_issues"):
                st.error("🚫 **Blocking Issues:**")
                for issue in results["blocking_issues"]:
                    st.write(f"• {issue}")

            # Warnings
            if results.get("warnings"):
                with st.expander("⚠️ Warnings"):
                    for warning in results["warnings"]:
                        st.write(f"• {warning}")

            # Recommendations
            if results.get("recommendations"):
                with st.expander("💡 Recommendations"):
                    for rec in results["recommendations"]:
                        st.write(f"• {rec}")

            # Performance metrics
            if "validation_duration_ms" in results:
                st.caption(f"Validation completed in {results['validation_duration_ms']}ms")

        elif validation_type == "advanced_failed":
            st.error("❌ Advanced validation failed")
            for issue in results.get("blocking_issues", []):
                st.write(f"• {issue}")
            st.info("💡 Try using Quick Validate instead")

    def _get_nested_value(self, obj, path):
        """Get nested value from object using dot notation"""
        keys = path.split('.')
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return None
        return obj

    def _export_to_json(self) -> str:
        """Export canvas to JSON format"""
        self.canvas_data["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        self.canvas_data["metadata"]["completion_status"] = self._calculate_completion_progress()

        return json.dumps(self.canvas_data, indent=2, ensure_ascii=False)

    async def _generate_sow_draft(self) -> bool:
        """Generate SOW draft using canvas data"""
        try:
            if not self.sow_agent:
                await self.initialize_agents()

            # Convert canvas to SOW format
            sow_text = self._canvas_to_sow_text()

            # Process with SOW interpreter agent
            data_contract = await self.sow_agent._process(
                sow_document=sow_text,
                business_domain=self.canvas_data["metadata"]["business_domain"]
            )

            # Store in session state for next steps
            st.session_state["generated_sow"] = data_contract

            return True

        except Exception as e:
            logger.error(f"Failed to generate SOW draft: {e}")
            st.error(f"Failed to generate SOW: {e}")
            return False

    def _canvas_to_sow_text(self) -> str:
        """Convert canvas data to SOW text format"""
        sow_sections = []

        # Business objectives
        sow_sections.append("## Business Objectives")
        sow_sections.extend(self.canvas_data["value_propositions"]["business_outcomes"])

        # Data requirements
        sow_sections.append("\n## Data Requirements")
        sow_sections.append("### Internal Data Sources:")
        sow_sections.extend(self.canvas_data["data_sources"]["internal_sources"])
        sow_sections.append("### External Data Sources:")
        sow_sections.extend(self.canvas_data["data_sources"]["external_sources"])

        # Quality standards
        sow_sections.append("\n## Quality Standards")
        sow_sections.extend(self.canvas_data["data_governance"]["quality_standards"])

        # Compliance requirements
        sow_sections.append("\n## Compliance Requirements")
        sow_sections.extend(self.canvas_data["data_governance"]["compliance_requirements"])

        # Technical requirements
        sow_sections.append("\n## Technical Requirements")
        sow_sections.extend(self.canvas_data["technology_infrastructure"]["data_platforms"])

        return "\n".join(sow_sections)

    async def _semantic_route_terms(self) -> Dict[str, Any]:
        """Perform semantic routing on business terms in the canvas"""
        if not self.skos_router:
            await self.initialize_agents()

        source_language = self.canvas_data["metadata"]["primary_language"]
        target_language = "en"  # Standardize to English

        # Extract business terms from canvas
        all_terms = []
        routed_terms = {}
        new_mappings = {}

        # Collect terms from various sections
        term_sources = [
            ("value_propositions", "data_insights"),
            ("customer_segments", "primary_users"),
            ("data_sources", "external_sources"),
            ("key_activities", "data_collection"),
            ("key_resources", "data_assets"),
            ("key_partners", "data_providers")
        ]

        for section, field in term_sources:
            if section in self.canvas_data and field in self.canvas_data[section]:
                section_terms = self.canvas_data[section][field]
                if isinstance(section_terms, list):
                    all_terms.extend(section_terms)

        # Route terms through SKOS
        for term in all_terms[:20]:  # Limit for performance
            if isinstance(term, str) and len(term.strip()) > 2:
                term_clean = term.strip()

                try:
                    routing_result = self.skos_router.route_term_to_preferred(
                        term_clean, source_language, target_language
                    )

                    if (routing_result.get("preferred_label") and
                        routing_result.get("translation_confidence", 0) > 0.7):

                        routed_terms[term_clean] = routing_result["preferred_label"]
                        new_mappings[term_clean] = {
                            "preferred_label": routing_result["preferred_label"],
                            "confidence": routing_result["translation_confidence"],
                            "method": routing_result["method"],
                            "concept_uri": routing_result.get("concept_uri")
                        }

                except Exception as e:
                    logger.debug(f"Semantic routing failed for term '{term_clean}': {e}")

        # Store semantic mappings in canvas metadata
        if "semantic_mappings" not in self.canvas_data["metadata"]:
            self.canvas_data["metadata"]["semantic_mappings"] = {}

        self.canvas_data["metadata"]["semantic_mappings"].update(new_mappings)

        return {
            "routed_terms": len(routed_terms),
            "total_terms": len(all_terms),
            "new_terms": routed_terms,
            "mappings": new_mappings
        }

    def _prepare_discovery_context(self) -> Dict[str, Any]:
        """Prepare context for data discovery agents"""
        return {
            "business_domain": self.canvas_data.get("metadata", {}).get("business_domain", ""),
            "primary_language": self.canvas_data.get("metadata", {}).get("primary_language", "en"),
            "value_propositions": self.canvas_data.get("value_propositions", {}).get("data_insights", []),
            "target_users": (
                self.canvas_data.get("customer_segments", {}).get("primary_users", []) +
                self.canvas_data.get("customer_segments", {}).get("secondary_users", [])
            ),
            "external_data_needs": self.canvas_data.get("data_sources", {}).get("external_sources", []),
            "quality_requirements": self.canvas_data.get("data_governance", {}).get("quality_standards", []),
            "compliance_constraints": self.canvas_data.get("data_governance", {}).get("compliance_requirements", []),
            "preferred_delivery_methods": self.canvas_data.get("channels", {}).get("delivery_methods", []),
            "budget_constraints": (
                self.canvas_data.get("cost_structure", {}).get("data_acquisition", []) +
                self.canvas_data.get("cost_structure", {}).get("infrastructure", [])
            ),
            "technical_capabilities": self.canvas_data.get("technology_infrastructure", {}).get("data_platforms", []),
            "canvas_completion": self._calculate_completion_progress(),
            "generated_at": datetime.utcnow().isoformat(),
            # Add executive context integration
            "executive_targets": self.canvas_data.get("executive_targets", {}).get("targets", []),
            "enterprise_context": self.canvas_data.get("executive_targets", {}).get("enterprise_context", {}),
            "strategic_alignment_available": len(self.canvas_data.get("executive_targets", {}).get("alignment_scores", {})) > 0
        }

    def _render_canvas_visualization(self):
        """Render visual representation of the canvas"""
        st.write("**Canvas Overview:**")

        # Create a simple visual summary
        sections = {
            "Value & Users": len([
                item for sublist in [
                    self.canvas_data["value_propositions"]["data_insights"],
                    self.canvas_data["customer_segments"]["primary_users"]
                ] for item in sublist
            ]),
            "Operations": len([
                item for sublist in [
                    self.canvas_data["key_activities"]["data_collection"],
                    self.canvas_data["key_resources"]["data_assets"]
                ] for item in sublist
            ]),
            "Data Sources": len([
                item for sublist in [
                    self.canvas_data["data_sources"]["internal_sources"],
                    self.canvas_data["data_sources"]["external_sources"]
                ] for item in sublist
            ]),
            "Governance": len([
                item for sublist in [
                    self.canvas_data["data_governance"]["quality_standards"],
                    self.canvas_data["data_governance"]["compliance_requirements"]
                ] for item in sublist
            ])
        }

        # Display as metrics
        cols = st.columns(len(sections))
        for i, (section, count) in enumerate(sections.items()):
            cols[i].metric(section, count)

    def _render_executive_targets_section(self):
        """Render Executive Targets (+E) Framework Section"""
        st.header("⭐ Executive Target Alignment Analysis")

        st.markdown("""
        **📋 How This Works:**
        1. **Review** your Data Business Canvas below (what you're proposing to build)
        2. **Submit** your Executive Targets (what business leadership wants to achieve)
        3. **AI Analysis** scores how well your canvas aligns with executive targets
        4. **Get insights** on strategic fit, gaps, and improvement recommendations
        """)

        # Show the current canvas first so users understand what they're scoring against
        st.subheader("📊 Your Data Business Canvas (What Gets Scored)")

        with st.expander("📈 Current Canvas Summary", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**💡 Value Propositions:**")
                for insight in self.canvas_data.get("value_propositions", {}).get("data_insights", []):
                    st.write(f"• {insight}")

                st.write("**👥 Target Users:**")
                for user in self.canvas_data.get("customer_segments", {}).get("primary_users", []):
                    st.write(f"• {user}")

                st.write("**🔧 Key Activities:**")
                for activity in self.canvas_data.get("key_activities", {}).get("data_collection", [])[:3]:
                    st.write(f"• {activity}")

            with col2:
                st.write("**💰 Revenue Streams:**")
                for revenue in self.canvas_data.get("revenue_streams", {}).get("direct_revenue", []):
                    st.write(f"• {revenue}")

                st.write("**🎯 Business Outcomes:**")
                for outcome in self.canvas_data.get("value_propositions", {}).get("business_outcomes", []):
                    st.write(f"• {outcome}")

                completion = self._calculate_completion_progress()
                st.metric("Canvas Completion", f"{completion:.0%}")

        st.markdown("---")

        st.subheader("🎯 Executive Target Analysis")
        st.markdown("""
        **What to submit:** Your executive/business targets (strategic goals, business objectives, performance targets)

        **What gets analyzed:** How well your proposed Data Business Canvas (above) supports achieving these targets
        """)

        # Simple text input for executive targets
        st.subheader("🎯 Executive Targets (Natural Text)")

        # Default example for demonstration
        default_targets = """EXECUTIVE TARGETS - TECH STARTUP EXAMPLE

1. Increase monthly recurring revenue (MRR) by 40% through AI-powered customer segmentation and personalized pricing strategies by Q2 2024. Owner: Sarah Chen, VP Sales. Success metrics: $2M MRR target, 25% increase in customer lifetime value.

2. Reduce customer acquisition cost (CAC) by 30% using predictive analytics to optimize marketing spend and channel performance within 6 months. Owner: Michael Rodriguez, CMO. Success metrics: CAC below $150, 20% improvement in conversion rates.

3. Launch predictive maintenance SaaS platform to capture 15% market share in manufacturing IoT space by end of fiscal year. Owner: Alex Kim, Chief Product Officer. Success metrics: 100+ enterprise customers, $5M ARR from new product line.

4. Improve customer satisfaction (NPS) from 65 to 80+ through real-time behavioral analytics and proactive support automation. Owner: Jennifer Wu, Head of Customer Experience. Success metrics: NPS 80+, 50% reduction in support tickets.

5. Achieve SOC2 Type II compliance and implement zero-trust security architecture to enable enterprise sales by Q3 2024. Owner: David Park, CTO. Success metrics: SOC2 certification, 50+ enterprise prospects qualified."""

        executive_targets_text = st.text_area(
            "Paste your executive targets here:",
            value=self.canvas_data["executive_targets"].get("raw_text", default_targets),
            height=200,
            help="""
            Examples:
            • Increase revenue by 30% through data-driven customer insights by Q2 2024
            • Reduce operational costs by 15% using predictive analytics within 6 months
            • Launch new AI-powered product features by end of fiscal year
            • Improve customer satisfaction scores by 25% through personalized experiences

            Just paste your targets naturally - the agent will parse everything automatically.
            """,
            placeholder="Paste your executive targets here..."
        )

        # Store the raw text
        self.canvas_data["executive_targets"]["raw_text"] = executive_targets_text

        # Executive targets submission and analysis
        st.info("💡 **Executive Targets** = Business goals, strategic objectives, and performance targets from leadership")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Submit Executive Targets", type="secondary"):
                if executive_targets_text.strip():
                    # Simple text processing to show targets
                    target_lines = []
                    current_target = []

                    for line in executive_targets_text.split('\n'):
                        line = line.strip()
                        if not line:
                            continue

                        # Check if line starts with a number (new target)
                        if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                            if current_target:
                                target_lines.append('\n'.join(current_target))
                                current_target = []
                            current_target.append(line)
                        else:
                            if current_target:  # continuation of current target
                                current_target.append(line)

                    # Add the last target
                    if current_target:
                        target_lines.append('\n'.join(current_target))

                    # Store raw targets for preview
                    self.canvas_data["executive_targets"]["raw_targets"] = target_lines
                    st.success(f"✅ {len(target_lines)} targets submitted and ready for AI parsing!")
                    st.rerun()
                else:
                    st.warning("Please enter your executive targets first")

        with col2:
            targets_count = len(self.canvas_data["executive_targets"].get("raw_targets", []))
            st.metric("Targets Ready", targets_count)

        # Show submitted targets preview
        if self.canvas_data["executive_targets"].get("raw_targets"):
            st.subheader("📋 Submitted Targets Preview")

            for i, target in enumerate(self.canvas_data["executive_targets"]["raw_targets"]):
                with st.expander(f"Target {i+1}", expanded=False):
                    st.write(target)

        # Step 2: Parse with AI
        st.subheader("🤖 Step 2: AI Alignment Analysis")
        st.info("💡 **Analysis Process:** AI scores how well your Data Business Canvas (above) supports achieving your Executive Targets")

        if self.canvas_data["executive_targets"].get("raw_targets"):
            col1, col2 = st.columns(2)

            with col1:
                # Check canvas completion before allowing target analysis
                canvas_completion = self._calculate_completion_progress()
                canvas_ready = canvas_completion >= 0.3  # Require at least 30% completion

                if canvas_ready:
                    if st.button("🤖 Analyze Canvas-Target Alignment", type="primary"):
                        with st.spinner("AI agent parsing targets and analyzing strategic alignment..."):
                            success = asyncio.run(self._parse_submitted_targets())
                        if success:
                            st.success("✅ Targets parsed and analyzed!")
                            st.rerun()
                        else:
                            st.error("❌ Parsing failed. Check the logs for details.")
                else:
                    st.button("🤖 Analyze Canvas-Target Alignment", type="primary", disabled=True,
                             help=f"Please complete more of your Data Business Canvas first (Currently {canvas_completion:.1%} complete, need at least 30%)")
                    st.warning("⚠️ **Complete your Data Business Canvas first!** The AI needs to understand your proposed data solution before it can analyze how well your executive targets align with it.")

            with col2:
                if st.button("🔄 Re-score Alignment"):
                    if self.canvas_data["executive_targets"].get("targets"):
                        with st.spinner("Re-analyzing strategic alignment..."):
                            asyncio.run(self._score_all_targets_alignment())
                        st.success("✅ Alignment scores updated!")
                        st.rerun()
                    else:
                        st.warning("Parse targets first")
        else:
            st.info("👆 Please submit your targets first using Step 1")

        # Display existing targets with alignment
        if self.canvas_data["executive_targets"]["targets"]:
            st.subheader("📊 Current Executive Targets & Strategic Alignment")

            for i, target_data in enumerate(self.canvas_data["executive_targets"]["targets"]):
                with st.expander(f"🎯 {target_data.get('title', f'Target {i+1}')} ({target_data.get('category', 'Unknown').title()})", expanded=True):

                    # Target details
                    target_col1, target_col2, target_col3 = st.columns([2, 1, 1])

                    with target_col1:
                        st.write(f"**Description:** {target_data.get('description', 'No description')}")
                        st.write(f"**Owner:** {target_data.get('owner', 'Unknown')} ({target_data.get('owner_role', 'Unknown role')})")

                        if target_data.get('success_metrics'):
                            st.write("**Success Metrics:**")
                            for metric in target_data.get('success_metrics', []):
                                st.write(f"• {metric}")

                    with target_col2:
                        st.metric("Priority", target_data.get('priority', 'medium').upper())
                        st.metric("Deadline", target_data.get('deadline', 'Not set'))
                        if target_data.get('target_value'):
                            st.metric("Target Value", target_data.get('target_value'))

                    with target_col3:
                        # Real-time alignment scoring
                        target_id = target_data.get('id')
                        if target_id in self.canvas_data["executive_targets"]["alignment_scores"]:
                            alignment = self.canvas_data["executive_targets"]["alignment_scores"][target_id]

                            # Overall alignment score with color coding
                            score = alignment.get('overall_score', 0.0)
                            color = "🟢" if score > 0.7 else "🟡" if score > 0.4 else "🔴"
                            st.metric(f"Alignment {color}", f"{score:.1%}")

                            st.metric("Confidence", f"{alignment.get('confidence', 0.0):.1%}")

                            # Quick dimension scores
                            st.write("**Key Dimensions:**")
                            st.write(f"Strategic Fit: {alignment.get('strategic_fit', 0.0):.1%}")
                            st.write(f"Impact Potential: {alignment.get('impact_potential', 0.0):.1%}")
                            st.write(f"Timeline Feasibility: {alignment.get('timeline_feasibility', 0.0):.1%}")
                        else:
                            st.info("🔄 Score alignment to see metrics")

                    # Action buttons
                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        if st.button(f"🔄 Score Alignment", key=f"score_{i}"):
                            if self.canvas_data["value_propositions"]["data_insights"]:
                                with st.spinner("Scoring strategic alignment..."):
                                    asyncio.run(self._score_target_alignment(target_data))
                            else:
                                st.warning("Please complete Value Propositions section first")

                    with action_col2:
                        if st.button(f"📝 View Details", key=f"detail_{i}"):
                            self._show_target_details(target_data)

                    with action_col3:
                        if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                            self.canvas_data["executive_targets"]["targets"].pop(i)
                            st.rerun()

        else:
            st.info("No executive targets added yet. Add your first target above to begin strategic alignment analysis.")

        # Canvas Section Alignment Indicators
        st.subheader("📈 Canvas Section Alignment Overview")

        if self.canvas_data["executive_targets"]["targets"]:
            self._render_section_alignment_indicators()
        else:
            st.info("Add executive targets to see section-by-section alignment analysis")

    async def _parse_submitted_targets(self):
        """Parse the submitted targets using the executive scorer agent"""
        try:
            if not self.executive_scorer:
                await self.initialize_agents()

            # Clear existing parsed targets
            self.canvas_data["executive_targets"]["targets"] = []
            self.canvas_data["executive_targets"]["alignment_scores"] = {}

            # Get submitted targets
            raw_targets = self.canvas_data["executive_targets"].get("raw_targets", [])
            if not raw_targets:
                st.error("No targets to parse. Please submit targets first.")
                return False

            # Enterprise context
            enterprise_context = {
                "enterprise_name": self.canvas_data["metadata"].get("business_domain", "Your Enterprise"),
                "business_domain": self.canvas_data["metadata"]["business_domain"],
            }

            # Parse each target individually
            parsed_count = 0
            for i, target_text in enumerate(raw_targets):
                if not target_text.strip():
                    continue

                try:
                    st.write(f"Parsing target {i+1}...")

                    # Parse target with BAML agent
                    parsing_result = await self.executive_scorer.parse_executive_target(
                        target_description=target_text,
                        enterprise_context=enterprise_context,
                        owner=None,  # Let agent extract from text
                        owner_role=None,  # Let agent extract from text
                        deadline=None  # Let agent extract from text
                    )

                    # Create executive target
                    executive_target = await self.executive_scorer.create_executive_target_from_parsing(
                        parsing_result=parsing_result,
                        target_description=target_text,
                        owner=parsing_result.owner or "Executive Team",
                        owner_role=parsing_result.owner_role or "Leadership",
                        deadline=parsing_result.deadline,
                        custom_properties={}
                    )

                    # Convert to dict for storage
                    target_dict = {
                        "id": executive_target.id,
                        "title": executive_target.title,
                        "description": executive_target.description,
                        "category": parsing_result.category.value if parsing_result.category else "strategic",
                        "priority": parsing_result.priority.value if parsing_result.priority else "high",
                        "owner": executive_target.owner,
                        "owner_role": executive_target.owner_role,
                        "deadline": parsing_result.deadline.isoformat() if parsing_result.deadline else None,
                        "success_metrics": executive_target.success_metrics,
                        "target_value": executive_target.target_value,
                        "business_domain": executive_target.business_domain,
                        "stakeholders": executive_target.stakeholders,
                    }

                    # Add to canvas
                    self.canvas_data["executive_targets"]["targets"].append(target_dict)
                    parsed_count += 1

                    st.write(f"✅ Target {i+1} parsed successfully")

                except Exception as target_error:
                    st.error(f"❌ Failed to parse target {i+1}: {str(target_error)}")
                    logger.error(f"Target {i+1} parsing error: {target_error}")

            if parsed_count > 0:
                # Score alignment for all successfully parsed targets
                st.write("Analyzing strategic alignment...")
                await self._score_all_targets_alignment()
                st.write(f"✅ Successfully parsed {parsed_count} targets")
                return True
            else:
                st.error("❌ No targets could be parsed")
                return False

        except Exception as e:
            st.error(f"❌ Error during parsing: {str(e)}")
            logger.error(f"Target parsing error: {e}")
            return False

    async def _parse_and_analyze_targets(self, targets_text: str):
        """Parse multiple targets from text and analyze strategic alignment"""
        try:
            if not self.executive_scorer:
                await self.initialize_agents()

            # Clear existing targets
            self.canvas_data["executive_targets"]["targets"] = []
            self.canvas_data["executive_targets"]["alignment_scores"] = {}

            # Split targets by lines that start with numbers (simple splitting)
            target_lines = []
            current_target = []

            for line in targets_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Check if line starts with a number (new target)
                if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                    if current_target:
                        target_lines.append('\n'.join(current_target))
                        current_target = []
                    current_target.append(line)
                else:
                    if current_target:  # continuation of current target
                        current_target.append(line)

            # Add the last target
            if current_target:
                target_lines.append('\n'.join(current_target))

            # Parse each target individually using existing method
            enterprise_context = {
                "enterprise_name": self.canvas_data["metadata"].get("business_domain", "Your Enterprise"),
                "business_domain": self.canvas_data["metadata"]["business_domain"],
            }

            for i, target_text in enumerate(target_lines):
                if not target_text.strip():
                    continue

                try:
                    # Parse target with BAML agent
                    parsing_result = await self.executive_scorer.parse_executive_target(
                        target_description=target_text,
                        enterprise_context=enterprise_context,
                        owner=None,  # Let agent extract from text
                        owner_role=None,  # Let agent extract from text
                        deadline=None  # Let agent extract from text
                    )

                    # Create executive target
                    executive_target = await self.executive_scorer.create_executive_target_from_parsing(
                        parsing_result=parsing_result,
                        target_description=target_text,
                        owner=parsing_result.owner or "Executive Team",
                        owner_role=parsing_result.owner_role or "Leadership",
                        deadline=parsing_result.deadline,
                        custom_properties={}
                    )

                    # Convert to dict for storage
                    target_dict = {
                        "id": executive_target.id,
                        "title": executive_target.title,
                        "description": executive_target.description,
                        "category": parsing_result.category.value if parsing_result.category else "strategic",
                        "priority": parsing_result.priority.value if parsing_result.priority else "high",
                        "owner": executive_target.owner,
                        "owner_role": executive_target.owner_role,
                        "deadline": parsing_result.deadline.isoformat() if parsing_result.deadline else None,
                        "success_metrics": executive_target.success_metrics,
                        "target_value": executive_target.target_value,
                        "business_domain": executive_target.business_domain,
                        "stakeholders": executive_target.stakeholders,
                    }

                    # Add to canvas
                    self.canvas_data["executive_targets"]["targets"].append(target_dict)

                except Exception as target_error:
                    st.warning(f"Could not parse target {i+1}: {str(target_error)}")
                    logger.warning(f"Target {i+1} parsing error: {target_error}")

            # Score alignment for all targets
            await self._score_all_targets_alignment()

            return True

        except Exception as e:
            st.error(f"Error parsing targets: {str(e)}")
            logger.error(f"Target parsing error: {e}")
            return False

    async def _score_all_targets_alignment(self):
        """Score strategic alignment for all targets against canvas"""
        try:
            if not self.executive_scorer:
                await self.initialize_agents()

            for target_data in self.canvas_data["executive_targets"]["targets"]:
                await self._score_target_alignment(target_data)

        except Exception as e:
            st.error(f"Error scoring alignment: {str(e)}")
            logger.error(f"Alignment scoring error: {e}")

    async def _parse_and_add_target(self, description: str, owner: str, owner_role: str, deadline, category: str, priority: str):
        """Parse target description and add to canvas"""
        try:
            if not self.executive_scorer:
                await self.initialize_agents()

            enterprise_context = {
                "enterprise_name": self.canvas_data["executive_targets"]["enterprise_name"],
                "business_domain": self.canvas_data["metadata"]["business_domain"],
                "fiscal_year": self.canvas_data["executive_targets"]["enterprise_context"]["fiscal_year"],
                "quarter": self.canvas_data["executive_targets"]["enterprise_context"]["quarter"],
                "industry_context": self.canvas_data["executive_targets"]["enterprise_context"]["industry_context"]
            }

            # Parse with BAML agent
            parsing_result = await self.executive_scorer.parse_executive_target(
                target_description=description,
                enterprise_context=enterprise_context,
                owner=owner,
                owner_role=owner_role,
                deadline=deadline
            )

            # Create executive target
            executive_target = await self.executive_scorer.create_executive_target_from_parsing(
                parsing_result=parsing_result,
                target_description=description,
                owner=owner or "Executive Team",
                owner_role=owner_role or "Leadership",
                deadline=deadline,
                custom_properties={
                    "category_override": category,
                    "priority_override": priority
                }
            )

            # Convert to dict for storage
            target_dict = {
                "id": executive_target.id,
                "title": executive_target.title,
                "description": executive_target.description,
                "category": category,  # Use user selection
                "priority": priority,  # Use user selection
                "owner": executive_target.owner,
                "owner_role": executive_target.owner_role,
                "deadline": deadline.isoformat() if deadline else None,
                "success_metrics": executive_target.success_metrics,
                "target_value": executive_target.target_value,
                "business_domain": executive_target.business_domain,
                "stakeholders": executive_target.stakeholders,
                "custom_properties": executive_target.custom_properties,
                "tags": executive_target.tags,
                "created_at": datetime.now().isoformat(),
                "parsing_confidence": parsing_result.confidence
            }

            # Add to canvas
            self.canvas_data["executive_targets"]["targets"].append(target_dict)

            st.success(f"✅ Executive target parsed and added with {parsing_result.confidence:.1%} confidence!")

            # Show parsing insights
            if parsing_result.key_themes:
                st.info(f"🔍 Key themes identified: {', '.join(parsing_result.key_themes[:3])}")

            st.rerun()

        except Exception as e:
            logger.error(f"Error parsing target: {e}")
            st.error(f"Failed to parse target: {e}")

    async def _score_target_alignment(self, target_data: Dict[str, Any]):
        """Score alignment between target and current canvas"""
        try:
            if not self.executive_scorer:
                await self.initialize_agents()

            # Recreate executive target object
            executive_target = ExecutiveTarget(
                id=target_data["id"],
                title=target_data["title"],
                description=target_data["description"],
                category=TargetCategory(target_data["category"]),
                priority=TargetPriority(target_data["priority"]),
                owner=target_data["owner"],
                owner_role=target_data["owner_role"],
                deadline=datetime.fromisoformat(target_data["deadline"]).date() if target_data.get("deadline") else None,
                success_metrics=target_data.get("success_metrics", []),
                target_value=target_data.get("target_value"),
                business_domain=target_data.get("business_domain", ""),
                stakeholders=target_data.get("stakeholders", [])
            )

            # Prepare canvas data for alignment
            canvas_data = self._prepare_canvas_for_alignment()

            enterprise_context = {
                "enterprise_name": self.canvas_data["executive_targets"]["enterprise_name"],
                "business_domain": self.canvas_data["metadata"]["business_domain"],
                "fiscal_year": self.canvas_data["executive_targets"]["enterprise_context"]["fiscal_year"],
                "industry_context": self.canvas_data["executive_targets"]["enterprise_context"]["industry_context"]
            }

            # Score alignment
            alignment_score = await self.executive_scorer.score_strategic_alignment(
                target=executive_target,
                canvas_data=canvas_data,
                enterprise_context=enterprise_context
            )

            # Store alignment score
            self.canvas_data["executive_targets"]["alignment_scores"][target_data["id"]] = {
                "overall_score": alignment_score.overall_score,
                "confidence": alignment_score.confidence,
                "strategic_fit": alignment_score.strategic_fit,
                "impact_potential": alignment_score.impact_potential,
                "timeline_feasibility": alignment_score.timeline_feasibility,
                "resource_efficiency": alignment_score.resource_efficiency,
                "risk_assessment": alignment_score.risk_assessment,
                "dependency_analysis": alignment_score.dependency_analysis,
                "reasoning": alignment_score.reasoning,
                "key_factors": alignment_score.key_factors,
                "risk_factors": alignment_score.risk_factors,
                "recommendations": alignment_score.recommendations,
                "scored_at": alignment_score.scored_at.isoformat()
            }

            st.success(f"✅ Alignment scored: {alignment_score.overall_score:.1%} overall alignment!")

            # Show key insights
            if alignment_score.recommendations:
                with st.expander("💡 Strategic Recommendations"):
                    for rec in alignment_score.recommendations[:3]:
                        st.write(f"• {rec}")

            st.rerun()

        except Exception as e:
            logger.error(f"Error scoring alignment: {e}")
            st.error(f"Failed to score alignment: {e}")

    def _prepare_canvas_for_alignment(self) -> Dict[str, Any]:
        """Prepare canvas data for alignment scoring"""
        return {
            "value_propositions": self.canvas_data["value_propositions"]["data_insights"],
            "key_activities": (
                self.canvas_data["key_activities"]["data_collection"] +
                self.canvas_data["key_activities"]["data_processing"] +
                self.canvas_data["key_activities"]["insight_generation"]
            ),
            "key_resources": (
                self.canvas_data["key_resources"]["data_assets"] +
                self.canvas_data["key_resources"]["technical_resources"] +
                self.canvas_data["key_resources"]["human_resources"]
            ),
            "key_partnerships": (
                self.canvas_data["key_partners"]["data_providers"] +
                self.canvas_data["key_partners"]["technology_partners"] +
                self.canvas_data["key_partners"]["service_providers"]
            ),
            "customer_segments": (
                self.canvas_data["customer_segments"]["primary_users"] +
                self.canvas_data["customer_segments"]["secondary_users"]
            ),
            "customer_relationships": [self.canvas_data["customer_relationships"]["engagement_model"]],
            "channels": (
                self.canvas_data["channels"]["delivery_methods"] +
                self.canvas_data["channels"]["distribution_channels"]
            ),
            "cost_structure": (
                self.canvas_data["cost_structure"]["data_acquisition"] +
                self.canvas_data["cost_structure"]["infrastructure"] +
                self.canvas_data["cost_structure"]["operational"]
            ),
            "revenue_streams": (
                self.canvas_data["revenue_streams"]["direct_revenue"] +
                self.canvas_data["revenue_streams"]["cost_savings"] +
                self.canvas_data["revenue_streams"]["strategic_value"]
            ),
            "data_assets": self.canvas_data["data_sources"]["internal_sources"],
            "intelligence_capabilities": self.canvas_data["technology_infrastructure"]["analytics_tools"],
            "competitive_advantages": self.canvas_data["value_propositions"]["competitive_advantages"],
            "business_domain": self.canvas_data["metadata"]["business_domain"],
            "use_case_description": " | ".join(self.canvas_data["value_propositions"]["data_insights"][:3]),
            "timeline": "Current fiscal year implementation",
            "budget": " | ".join(self.canvas_data["cost_structure"]["data_acquisition"][:2])
        }

    def _show_target_details(self, target_data: Dict[str, Any]):
        """Show detailed target information"""
        st.subheader(f"Target Details: {target_data.get('title')}")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**ID:** {target_data.get('id')}")
            st.write(f"**Category:** {target_data.get('category', 'Unknown').title()}")
            st.write(f"**Priority:** {target_data.get('priority', 'medium').upper()}")
            st.write(f"**Created:** {target_data.get('created_at', 'Unknown')}")

            if target_data.get('parsing_confidence'):
                st.write(f"**Parsing Confidence:** {target_data.get('parsing_confidence'):.1%}")

        with col2:
            if target_data.get('stakeholders'):
                st.write("**Stakeholders:**")
                for stakeholder in target_data['stakeholders']:
                    st.write(f"• {stakeholder}")

            if target_data.get('tags'):
                st.write("**Tags:**")
                st.write(f"{', '.join(target_data['tags'])}")

        # Show alignment details if available
        target_id = target_data.get('id')
        if target_id in self.canvas_data["executive_targets"]["alignment_scores"]:
            alignment = self.canvas_data["executive_targets"]["alignment_scores"][target_id]

            st.subheader("📊 Alignment Analysis")

            # Dimensional scores
            dimensions = {
                "Strategic Fit": alignment.get('strategic_fit', 0.0),
                "Impact Potential": alignment.get('impact_potential', 0.0),
                "Timeline Feasibility": alignment.get('timeline_feasibility', 0.0),
                "Resource Efficiency": alignment.get('resource_efficiency', 0.0),
                "Risk Assessment": alignment.get('risk_assessment', 0.0),
                "Dependency Analysis": alignment.get('dependency_analysis', 0.0)
            }

            for dim, score in dimensions.items():
                st.progress(score, text=f"{dim}: {score:.1%}")

            # Reasoning and recommendations
            if alignment.get('reasoning'):
                st.write("**Strategic Reasoning:**")
                st.write(alignment['reasoning'])

            if alignment.get('recommendations'):
                st.write("**Recommendations:**")
                for rec in alignment['recommendations']:
                    st.write(f"• {rec}")

    def _render_section_alignment_indicators(self):
        """Render alignment indicators for each canvas section"""
        if not self.canvas_data["executive_targets"]["targets"]:
            return

        # Calculate section-level alignment scores
        section_scores = self._calculate_section_alignments()

        # Create visual indicators
        cols = st.columns(4)
        sections = [
            ("🎯 Value & Users", section_scores.get('value_users', 0.0)),
            ("🔧 Operations & Resources", section_scores.get('operations_resources', 0.0)),
            ("📊 Data & Governance", section_scores.get('data_governance', 0.0)),
            ("📋 Overall Canvas", section_scores.get('overall', 0.0))
        ]

        for i, (section_name, score) in enumerate(sections):
            with cols[i]:
                # Color-coded alignment indicator
                color = "🟢" if score > 0.7 else "🟡" if score > 0.4 else "🔴"
                st.metric(
                    f"{color} {section_name}",
                    f"{score:.1%}",
                    help=f"Strategic alignment score for {section_name.split(' ', 1)[1]}"
                )

        # Detailed breakdown
        with st.expander("📊 View Detailed Section Analysis"):
            st.write("**Section-by-section alignment with executive targets:**")

            for section, score in section_scores.items():
                if section != 'overall':
                    status = "Strong" if score > 0.7 else "Moderate" if score > 0.4 else "Weak"
                    st.write(f"• **{section.replace('_', ' ').title()}:** {score:.1%} ({status} alignment)")

            # Show improvement recommendations
            low_sections = [s for s, score in section_scores.items() if score < 0.5 and s != 'overall']
            if low_sections:
                st.warning("💡 **Improvement Opportunities:**")
                for section in low_sections:
                    st.write(f"• Consider strengthening {section.replace('_', ' ')} to better align with executive targets")

    def _calculate_section_alignments(self) -> Dict[str, float]:
        """Calculate alignment scores for each canvas section"""
        if not self.canvas_data["executive_targets"]["alignment_scores"]:
            return {"value_users": 0.0, "operations_resources": 0.0, "data_governance": 0.0, "overall": 0.0}

        # Get average alignment scores across all targets
        alignments = list(self.canvas_data["executive_targets"]["alignment_scores"].values())

        if not alignments:
            return {"value_users": 0.0, "operations_resources": 0.0, "data_governance": 0.0, "overall": 0.0}

        # Calculate section-specific scores based on alignment dimensions
        value_users_score = sum(a.get('strategic_fit', 0.0) for a in alignments) / len(alignments)
        operations_score = sum(a.get('resource_efficiency', 0.0) for a in alignments) / len(alignments)
        data_governance_score = sum(a.get('risk_assessment', 0.0) for a in alignments) / len(alignments)
        overall_score = sum(a.get('overall_score', 0.0) for a in alignments) / len(alignments)

        return {
            "value_users": value_users_score,
            "operations_resources": operations_score,
            "data_governance": data_governance_score,
            "overall": overall_score
        }


def main():
    """Main Streamlit app entry point"""

    # Initialize canvas
    if "canvas" not in st.session_state:
        st.session_state["canvas"] = DataBusinessCanvas()

    canvas = st.session_state["canvas"]

    # Initialize agents if not done
    if canvas.skos_router is None:
        with st.spinner("Initializing semantic agents..."):
            asyncio.run(canvas.initialize_agents())

    # Render the interface
    canvas.render_canvas_interface()


if __name__ == "__main__":
    main()