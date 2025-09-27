"""
Discovery Flow - Canvas to Data Discovery Integration

Streamlit interface that seamlessly connects the Data Business Canvas
with the BAML Data Discovery Agent for intelligent source recommendation.

Flow:
1. Load/Create Data Business Canvas
2. Review canvas context and add user suggestions
3. Run BAML-powered data discovery
4. Review and refine discovery results
5. Export results for SOW and pipeline generation
"""

import streamlit as st
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

import sys
from pathlib import Path

# Add project src to path for absolute imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from agentic_data_scraper.agents.data_discovery import DataDiscoveryAgent, DiscoveryContext, DataSource
from agentic_data_scraper.semantic.skos_router import SKOSSemanticRouter
from agentic_data_scraper.ui.data_business_canvas import DataBusinessCanvas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscoveryFlow:
    """
    Integrated flow from Data Business Canvas to intelligent data discovery.

    Provides a seamless user experience where business context captured in
    the canvas directly drives AI-powered source discovery and recommendation.
    """

    def __init__(self):
        self.canvas = DataBusinessCanvas()
        self.discovery_agent = None
        self.skos_router = None
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state"""
        if "flow_step" not in st.session_state:
            st.session_state["flow_step"] = 1

        if "canvas_loaded" not in st.session_state:
            st.session_state["canvas_loaded"] = False

        if "discovery_results" not in st.session_state:
            st.session_state["discovery_results"] = []

        if "user_suggestions" not in st.session_state:
            st.session_state["user_suggestions"] = []

        if "discovery_context" not in st.session_state:
            st.session_state["discovery_context"] = None

    async def initialize_agents(self):
        """Initialize discovery agents and semantic routing"""
        try:
            # Initialize SKOS router
            db_path = Path("data/kuzu_dbc.db")
            self.skos_router = SKOSSemanticRouter(str(db_path))

            # Initialize discovery agent with semantic routing
            self.discovery_agent = DataDiscoveryAgent(
                skos_router=self.skos_router,
                timeout_seconds=300
            )

            # Initialize canvas agents
            await self.canvas.initialize_agents()

            logger.info("Discovery flow agents initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize discovery flow: {e}")
            st.error(f"Failed to initialize discovery services: {e}")

    def render_discovery_flow(self):
        """Render the complete discovery flow interface"""
        st.set_page_config(
            page_title="Data Discovery Flow",
            page_icon="🔍",
            layout="wide"
        )

        st.title("🔍 Data Discovery Flow")
        st.markdown("""
        **From Business Canvas to Intelligent Data Discovery**

        This flow takes your business context and uses AI to find and recommend
        the most relevant data sources for your needs.
        """)

        # Progress indicator
        self._render_progress_indicator()

        # Current step content
        if st.session_state["flow_step"] == 1:
            self._render_canvas_step()
        elif st.session_state["flow_step"] == 2:
            self._render_context_review_step()
        elif st.session_state["flow_step"] == 3:
            self._render_discovery_step()
        elif st.session_state["flow_step"] == 4:
            self._render_results_step()

    def _render_progress_indicator(self):
        """Render progress indicator for the flow"""
        steps = [
            "📊 Canvas Setup",
            "🎯 Context Review",
            "🔍 Discovery",
            "📋 Results"
        ]

        cols = st.columns(len(steps))
        for i, step in enumerate(steps):
            with cols[i]:
                if i + 1 < st.session_state["flow_step"]:
                    st.success(f"✅ {step}")
                elif i + 1 == st.session_state["flow_step"]:
                    st.info(f"🔄 {step}")
                else:
                    st.write(f"⏸️ {step}")

        st.divider()

    def _render_canvas_step(self):
        """Step 1: Canvas Setup"""
        st.header("📊 Step 1: Data Business Canvas")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Canvas Options")

            canvas_option = st.radio(
                "How would you like to proceed?",
                [
                    "Create new canvas",
                    "Load existing canvas",
                    "Use sample canvas"
                ]
            )

            if canvas_option == "Create new canvas":
                st.info("👆 Create your canvas using the interface above, then proceed to the next step.")

                if st.button("🔗 Open Canvas Builder", type="primary"):
                    st.switch_page("pages/data_business_canvas.py")

            elif canvas_option == "Load existing canvas":
                uploaded_file = st.file_uploader(
                    "Upload Canvas JSON file",
                    type="json",
                    help="Upload a previously saved Data Business Canvas file"
                )

                if uploaded_file is not None:
                    try:
                        canvas_data = json.load(uploaded_file)
                        self.canvas.canvas_data = canvas_data
                        st.session_state["canvas_loaded"] = True
                        st.success("✅ Canvas loaded successfully!")

                        # Show summary
                        completion = self.canvas._calculate_completion_progress()
                        st.metric("Canvas Completion", f"{completion:.1%}")

                    except Exception as e:
                        st.error(f"Failed to load canvas: {e}")

            elif canvas_option == "Use sample canvas":
                if st.button("📄 Load Sample Canvas"):
                    self.canvas.canvas_data = self._create_sample_canvas()
                    st.session_state["canvas_loaded"] = True
                    st.success("✅ Sample canvas loaded!")

        with col2:
            st.subheader("Canvas Status")

            if st.session_state["canvas_loaded"]:
                st.success("✅ Canvas Ready")

                completion = self.canvas._calculate_completion_progress()
                st.metric("Completion", f"{completion:.1%}")

                domain = self.canvas.canvas_data.get("metadata", {}).get("business_domain", "Not set")
                st.write(f"**Domain:** {domain}")

                if st.button("➡️ Next Step", type="primary"):
                    st.session_state["flow_step"] = 2
                    st.rerun()

            else:
                st.warning("⏸️ Canvas needed")
                st.write("Complete canvas setup to proceed")

        # Show canvas preview if loaded
        if st.session_state["canvas_loaded"]:
            st.subheader("📖 Canvas Preview")

            with st.expander("View Canvas Summary"):
                self._render_canvas_summary()

    def _render_context_review_step(self):
        """Step 2: Context Review and User Suggestions"""
        st.header("🎯 Step 2: Discovery Context Review")

        if not st.session_state["canvas_loaded"]:
            st.error("⚠️ Canvas not loaded. Please return to Step 1.")
            if st.button("⬅️ Back to Canvas"):
                st.session_state["flow_step"] = 1
                st.rerun()
            return

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🧠 Discovery Context")

            # Show parsed context from canvas
            discovery_context = self._prepare_discovery_context()
            st.session_state["discovery_context"] = discovery_context

            st.write("**Business Domain:**", discovery_context.business_domain)
            st.write("**Primary Language:**", discovery_context.primary_language)

            with st.expander("📋 External Data Needs"):
                for need in discovery_context.external_data_needs:
                    st.write(f"• {need}")

            with st.expander("🎯 Value Propositions"):
                for prop in discovery_context.value_propositions:
                    st.write(f"• {prop}")

            st.subheader("💭 Your Data Source Ideas")
            st.write("Do you have specific data sources in mind? Our AI will consider these alongside its discoveries.")

            # User suggestions input
            suggestion_input = st.text_area(
                "Enter data source suggestions (one per line):",
                value="\n".join(st.session_state["user_suggestions"]),
                height=120,
                help="e.g., 'World Bank commodity prices', 'USDA agricultural data', 'European trade statistics'"
            )

            # Update user suggestions
            new_suggestions = [s.strip() for s in suggestion_input.split('\n') if s.strip()]
            st.session_state["user_suggestions"] = new_suggestions

            if new_suggestions:
                st.info(f"📝 {len(new_suggestions)} suggestions will be considered during discovery")

        with col2:
            st.subheader("🚀 Ready to Discover?")

            st.metric("Data Needs", len(discovery_context.external_data_needs))
            st.metric("User Ideas", len(st.session_state["user_suggestions"]))

            if st.button("🔍 Start Discovery", type="primary"):
                st.session_state["flow_step"] = 3
                st.rerun()

            if st.button("⬅️ Back to Canvas"):
                st.session_state["flow_step"] = 1
                st.rerun()

    def _render_discovery_step(self):
        """Step 3: Run Discovery"""
        st.header("🔍 Step 3: Intelligent Data Discovery")

        if not st.session_state["discovery_context"]:
            st.error("⚠️ Discovery context not ready. Please return to previous steps.")
            return

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🤖 BAML Discovery Agent")

            if not st.session_state["discovery_results"]:
                st.info("Click 'Run Discovery' to start the AI-powered search for relevant data sources.")

                discovery_settings = st.expander("⚙️ Discovery Settings")
                with discovery_settings:
                    max_sources = st.slider("Max Sources to Find", 10, 100, 50)
                    min_quality = st.slider("Minimum Quality Score", 0.0, 1.0, 0.6, 0.1)

                if st.button("🚀 Run Discovery", type="primary"):
                    with st.spinner("🔍 Discovering data sources..."):
                        results = asyncio.run(self._run_discovery(max_sources, min_quality))

                        if results:
                            st.session_state["discovery_results"] = results
                            st.success(f"✅ Discovery complete! Found {len(results)} relevant sources.")
                            st.rerun()
                        else:
                            st.warning("No sources found meeting the criteria. Try adjusting the settings.")

            else:
                st.success(f"✅ Discovery completed! Found {len(st.session_state['discovery_results'])} sources.")

                if st.button("🔄 Run Again"):
                    st.session_state["discovery_results"] = []
                    st.rerun()

        with col2:
            st.subheader("📊 Discovery Status")

            if st.session_state["discovery_results"]:
                results = st.session_state["discovery_results"]

                st.metric("Sources Found", len(results))

                avg_quality = sum(s.quality_score for s in results) / len(results)
                st.metric("Avg Quality", f"{avg_quality:.1%}")

                avg_relevance = sum(s.relevance_score for s in results) / len(results)
                st.metric("Avg Relevance", f"{avg_relevance:.1%}")

                if st.button("➡️ Review Results", type="primary"):
                    st.session_state["flow_step"] = 4
                    st.rerun()

            else:
                st.info("🔮 AI discovery ready")

            if st.button("⬅️ Back to Context"):
                st.session_state["flow_step"] = 2
                st.rerun()

    def _render_results_step(self):
        """Step 4: Review Results"""
        st.header("📋 Step 4: Discovery Results")

        if not st.session_state["discovery_results"]:
            st.error("⚠️ No discovery results available.")
            return

        results = st.session_state["discovery_results"]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🎯 Discovered Data Sources")

            # Sort options
            sort_by = st.selectbox(
                "Sort by:",
                ["Combined Score", "Quality Score", "Relevance Score", "Title"]
            )

            if sort_by == "Combined Score":
                sorted_results = sorted(results, key=lambda s: (s.quality_score + s.relevance_score) / 2, reverse=True)
            elif sort_by == "Quality Score":
                sorted_results = sorted(results, key=lambda s: s.quality_score, reverse=True)
            elif sort_by == "Relevance Score":
                sorted_results = sorted(results, key=lambda s: s.relevance_score, reverse=True)
            else:
                sorted_results = sorted(results, key=lambda s: s.title)

            # Display results
            for i, source in enumerate(sorted_results):
                with st.expander(f"#{i+1} {source.title} ({'⭐' * int(source.quality_score * 5)})"):
                    col_info, col_scores = st.columns([3, 1])

                    with col_info:
                        st.write(f"**URL:** {source.url}")
                        st.write(f"**Description:** {source.description}")
                        st.write(f"**Type:** {source.source_type}")
                        st.write(f"**Formats:** {', '.join(source.data_formats)}")
                        st.write(f"**Access:** {source.access_method}")
                        st.write(f"**Updates:** {source.update_frequency}")

                    with col_scores:
                        st.metric("Quality", f"{source.quality_score:.1%}")
                        st.metric("Relevance", f"{source.relevance_score:.1%}")

        with col2:
            st.subheader("💾 Export Results")

            if st.button("📄 Download JSON", type="primary"):
                export_data = asyncio.run(self.discovery_agent.export_discovery_results(results))
                st.download_button(
                    label="💾 Save Discovery Results",
                    data=export_data,
                    file_name=f"discovery_results_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

            if st.button("📋 Generate SOW"):
                st.info("SOW generation with discovered sources would be implemented here")

            if st.button("🏗️ Build Pipeline"):
                st.info("Pipeline generation would be implemented here")

            st.divider()

            st.subheader("🔄 Next Steps")

            if st.button("⬅️ Back to Discovery"):
                st.session_state["flow_step"] = 3
                st.rerun()

            if st.button("🔄 Start Over"):
                # Reset session state
                for key in ["flow_step", "canvas_loaded", "discovery_results", "user_suggestions", "discovery_context"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    def _create_sample_canvas(self) -> Dict[str, Any]:
        """Create a sample canvas for demonstration"""
        return {
            "value_propositions": {
                "data_insights": [
                    "Agricultural commodity price trends and volatility analysis",
                    "Supply chain risk assessment for key food commodities",
                    "Trade flow optimization recommendations"
                ],
                "business_outcomes": [
                    "15% reduction in commodity procurement costs",
                    "Improved supply chain resilience through diversification",
                    "Enhanced market timing for agricultural investments"
                ],
                "competitive_advantages": [
                    "Real-time market intelligence",
                    "Predictive analytics for commodity markets",
                    "Integrated global trade data analysis"
                ]
            },
            "customer_segments": {
                "primary_users": [
                    "Agricultural commodity traders",
                    "Food processing companies",
                    "Supply chain managers"
                ],
                "secondary_users": [
                    "Agricultural cooperatives",
                    "Investment firms focusing on commodities",
                    "Government agricultural agencies"
                ],
                "user_personas": [
                    "Sarah (Commodity Trader): Needs real-time price data and market trends",
                    "Mike (Supply Chain Manager): Requires supply risk assessments and alternative sourcing"
                ]
            },
            "data_sources": {
                "internal_sources": [
                    "Historical trading data",
                    "Supplier contracts and pricing",
                    "Inventory management systems"
                ],
                "external_sources": [
                    "Government agricultural statistics",
                    "International commodity exchanges data",
                    "Weather and climate data",
                    "Trade flow statistics",
                    "Economic indicators"
                ],
                "real_time_feeds": [
                    "Commodity exchange prices",
                    "Weather monitoring systems"
                ],
                "batch_sources": [
                    "Monthly agricultural reports",
                    "Quarterly trade statistics"
                ]
            },
            "data_governance": {
                "quality_standards": [
                    "95% data accuracy for pricing information",
                    "Daily updates for market data",
                    "Complete geographic coverage for major commodities"
                ],
                "compliance_requirements": [
                    "Financial data regulations compliance",
                    "Agricultural data sharing agreements"
                ]
            },
            "technology_infrastructure": {
                "data_platforms": [
                    "Cloud data warehouse",
                    "Real-time streaming platform",
                    "API gateway for data access"
                ]
            },
            "metadata": {
                "business_domain": "agriculture",
                "primary_language": "en",
                "created_at": datetime.utcnow().isoformat()
            }
        }

    def _prepare_discovery_context(self) -> DiscoveryContext:
        """Prepare discovery context from canvas data"""
        canvas_data = self.canvas._prepare_discovery_context()

        return DiscoveryContext(
            business_domain=canvas_data["business_domain"],
            primary_language=canvas_data["primary_language"],
            value_propositions=canvas_data["value_propositions"],
            target_users=canvas_data["target_users"],
            external_data_needs=canvas_data["external_data_needs"],
            quality_requirements=canvas_data["quality_requirements"],
            compliance_constraints=canvas_data["compliance_constraints"],
            technical_capabilities=canvas_data["technical_capabilities"],
            budget_constraints=canvas_data["budget_constraints"],
            semantic_mappings=canvas_data.get("semantic_mappings", {})
        )

    async def _run_discovery(self, max_sources: int, min_quality: float) -> List[DataSource]:
        """Run the discovery agent"""
        try:
            if not self.discovery_agent:
                await self.initialize_agents()

            discovery_context = st.session_state["discovery_context"]
            user_suggestions = st.session_state["user_suggestions"]

            # Convert discovery context to dict for the agent
            context_dict = {
                "business_domain": discovery_context.business_domain,
                "primary_language": discovery_context.primary_language,
                "value_propositions": discovery_context.value_propositions,
                "target_users": discovery_context.target_users,
                "external_data_needs": discovery_context.external_data_needs,
                "quality_requirements": discovery_context.quality_requirements,
                "compliance_constraints": discovery_context.compliance_constraints,
                "technical_capabilities": discovery_context.technical_capabilities,
                "budget_constraints": discovery_context.budget_constraints,
                "semantic_mappings": discovery_context.semantic_mappings
            }

            # Run discovery
            result = await self.discovery_agent._process(
                canvas_context=context_dict,
                user_suggestions=user_suggestions,
                max_sources=max_sources,
                min_quality_score=min_quality
            )

            return result

        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            st.error(f"Discovery failed: {e}")
            return []

    def _render_canvas_summary(self):
        """Render a summary of the loaded canvas"""
        canvas_data = self.canvas.canvas_data

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Value Propositions:**")
            for insight in canvas_data.get("value_propositions", {}).get("data_insights", [])[:3]:
                st.write(f"• {insight}")

        with col2:
            st.write("**External Data Needs:**")
            for need in canvas_data.get("data_sources", {}).get("external_sources", [])[:3]:
                st.write(f"• {need}")

        with col3:
            st.write("**Quality Requirements:**")
            for req in canvas_data.get("data_governance", {}).get("quality_standards", [])[:3]:
                st.write(f"• {req}")


def main():
    """Main Streamlit app entry point"""

    # Initialize discovery flow
    if "discovery_flow" not in st.session_state:
        st.session_state["discovery_flow"] = DiscoveryFlow()

    flow = st.session_state["discovery_flow"]

    # Initialize agents if not done
    if flow.discovery_agent is None:
        with st.spinner("Initializing discovery agents..."):
            asyncio.run(flow.initialize_agents())

    # Render the interface
    flow.render_discovery_flow()


if __name__ == "__main__":
    main()