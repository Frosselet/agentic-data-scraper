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

# Add project src to path for absolute imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from agentic_data_scraper.agents.sow_interpreter import SOWInterpreterAgent, DataContract
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
        self.validator = CanvasValidationEngine()

    def _initialize_canvas(self) -> Dict[str, Any]:
        """Initialize empty canvas structure"""
        return {
            # Core 9 Business Model Elements
            "value_propositions": {
                "data_insights": [],
                "business_outcomes": [],
                "competitive_advantages": []
            },
            "customer_segments": {
                "primary_users": [],
                "secondary_users": [],
                "user_personas": []
            },
            "customer_relationships": {
                "engagement_model": "",
                "feedback_mechanisms": [],
                "support_channels": []
            },
            "channels": {
                "delivery_methods": [],
                "distribution_channels": [],
                "access_interfaces": []
            },
            "key_activities": {
                "data_collection": [],
                "data_processing": [],
                "insight_generation": []
            },
            "key_resources": {
                "data_assets": [],
                "technical_resources": [],
                "human_resources": []
            },
            "key_partners": {
                "data_providers": [],
                "technology_partners": [],
                "service_providers": []
            },
            "cost_structure": {
                "data_acquisition": [],
                "infrastructure": [],
                "operational": []
            },
            "revenue_streams": {
                "direct_revenue": [],
                "cost_savings": [],
                "strategic_value": []
            },

            # Additional 3 Data-Specific Elements
            "data_sources": {
                "internal_sources": [],
                "external_sources": [],
                "real_time_feeds": [],
                "batch_sources": []
            },
            "data_governance": {
                "quality_standards": [],
                "compliance_requirements": [],
                "access_controls": [],
                "retention_policies": []
            },
            "technology_infrastructure": {
                "data_platforms": [],
                "analytics_tools": [],
                "integration_capabilities": [],
                "security_measures": []
            },

            # Metadata
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "version": "1.0",
                "completion_status": 0.0,
                "business_domain": "",
                "primary_language": "en"
            }
        }

    async def initialize_agents(self):
        """Initialize BAML agents and semantic routing"""
        try:
            # Initialize SKOS router for multilingual support
            db_path = Path("data/kuzu_dbc.db")
            self.skos_router = SKOSSemanticRouter(str(db_path))

            # Initialize SOW interpreter agent
            self.sow_agent = SOWInterpreterAgent()

            # Initialize canvas validator
            await self.validator.initialize(str(db_path))

            logger.info("Successfully initialized BAML agents, SKOS router, and validator")

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

        # Progress tracking
        progress = self._calculate_completion_progress()
        st.progress(progress)
        st.write(f"Canvas Completion: {progress:.1%}")

        # Main canvas tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Value & Users",
            "🔧 Operations & Resources",
            "📊 Data & Governance",
            "📋 Review & Export"
        ])

        with tab1:
            self._render_value_users_section()

        with tab2:
            self._render_operations_resources_section()

        with tab3:
            self._render_data_governance_section()

        with tab4:
            self._render_review_export_section()

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
            if st.button("🔍 Prepare Discovery"):
                discovery_context = self._prepare_discovery_context()
                st.session_state["discovery_context"] = discovery_context
                st.success("Discovery context prepared! Ready for data source discovery.")

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
            "business_domain": self.canvas_data["metadata"]["business_domain"],
            "primary_language": self.canvas_data["metadata"]["primary_language"],
            "value_propositions": self.canvas_data["value_propositions"]["data_insights"],
            "target_users": (self.canvas_data["customer_segments"]["primary_users"] +
                           self.canvas_data["customer_segments"]["secondary_users"]),
            "external_data_needs": self.canvas_data["data_sources"]["external_sources"],
            "quality_requirements": self.canvas_data["data_governance"]["quality_standards"],
            "compliance_constraints": self.canvas_data["data_governance"]["compliance_requirements"],
            "preferred_delivery_methods": self.canvas_data["channels"]["delivery_methods"],
            "budget_constraints": (self.canvas_data["cost_structure"]["data_acquisition"] +
                                 self.canvas_data["cost_structure"]["infrastructure"]),
            "technical_capabilities": self.canvas_data["technology_infrastructure"]["data_platforms"],
            "canvas_completion": self._calculate_completion_progress(),
            "generated_at": datetime.utcnow().isoformat()
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