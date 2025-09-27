"""
Enhanced Data Discovery Page

Implements the dual-path discovery mechanism that bridges Value & Users to Operations & Resources:
1. Known Sources: Deep metadata analysis of provided URLs
2. Zero-Start: Intelligent internet research and source recommendation

Automatically prepopulates downstream workflow steps with discovered metadata.
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from ...agents.enhanced_discovery_agent import EnhancedDiscoveryAgent
from ...models.enhanced_discovery import (
    DiscoveryPath, DataSourceType,
    ModelDiscoveryResult as DiscoveryResult
)

st.set_page_config(
    page_title="Enhanced Data Discovery",
    page_icon="🔍",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables for discovery workflow"""
    if 'discovery_agent' not in st.session_state:
        st.session_state.discovery_agent = EnhancedDiscoveryAgent()

    if 'discovery_result' not in st.session_state:
        st.session_state.discovery_result = None

    if 'canvas_data' not in st.session_state:
        # Load canvas data from previous step
        st.session_state.canvas_data = st.session_state.get('canvas_data', {})

def render_discovery_path_selection():
    """Render discovery path selection interface"""
    st.header("🔍 Enhanced Data Discovery")
    st.markdown("""
    **Bridge Value & Users → Operations & Resources**

    Choose your discovery approach based on your current knowledge of data sources:
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📍 Known Sources")
        st.markdown("""
        **You already know the data sources you want**
        - Deep metadata analysis of provided URLs
        - Technical capability assessment
        - Quality and governance evaluation
        - Integration planning preparation
        """)

        if st.button("🎯 Analyze Known Sources", use_container_width=True):
            st.session_state.discovery_path = DiscoveryPath.KNOWN_SOURCE
            st.rerun()

    with col2:
        st.markdown("### 🌐 Zero-Start Discovery")
        st.markdown("""
        **You need to find data sources from scratch**
        - Intelligent internet research
        - 3-5 curated source recommendations
        - Multi-criteria source evaluation
        - Comprehensive metadata collection
        """)

        if st.button("🚀 Discover From Scratch", use_container_width=True):
            st.session_state.discovery_path = DiscoveryPath.ZERO_START
            st.rerun()

def render_known_sources_interface():
    """Render interface for known sources discovery"""
    st.header("📍 Known Sources Analysis")

    with st.form("known_sources_form"):
        st.markdown("### Source Configuration")

        # Source URLs input
        source_urls_text = st.text_area(
            "Data Source URLs",
            placeholder="https://api.example.com/data\nhttps://data.gov/dataset/example\nhttps://source.org/api/v1",
            help="Enter one URL per line for the data sources you want to analyze",
            height=100
        )

        col1, col2 = st.columns(2)

        with col1:
            expected_type = st.selectbox(
                "Expected Source Type",
                options=["Unknown"] + [t.value for t in DataSourceType],
                help="If you know the type of source, select it to improve analysis"
            )

            collection_depth = st.selectbox(
                "Analysis Depth",
                options=["basic", "detailed", "comprehensive"],
                index=1,
                help="Level of metadata collection detail"
            )

        with col2:
            specific_datasets = st.text_area(
                "Specific Datasets (Optional)",
                placeholder="dataset1\ndataset2\nspecific_endpoint",
                help="If you need specific datasets within the sources",
                height=80
            )

        submitted = st.form_submit_button("🔍 Analyze Sources", use_container_width=True)

        if submitted and source_urls_text.strip():
            source_urls = [url.strip() for url in source_urls_text.strip().split('\n') if url.strip()]
            specific_datasets_list = [ds.strip() for ds in specific_datasets.split('\n') if ds.strip()] if specific_datasets else None

            with st.spinner("🔍 Analyzing known sources with BAML agents..."):
                try:
                    result = asyncio.run(
                        st.session_state.discovery_agent.discover_known_sources(
                            source_urls=source_urls,
                            canvas_data=st.session_state.canvas_data,
                            expected_source_type=expected_type if expected_type != "Unknown" else None,
                            specific_datasets=specific_datasets_list,
                            collection_depth=collection_depth
                        )
                    )
                    st.session_state.discovery_result = result
                    st.success(f"✅ Analysis complete! Found metadata for {len(result.discovered_sources)} sources")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")

def render_zero_start_interface():
    """Render interface for zero-start discovery"""
    st.header("🌐 Zero-Start Discovery")

    with st.form("zero_start_form"):
        st.markdown("### Business Requirements")

        col1, col2 = st.columns(2)

        with col1:
            business_domain = st.text_input(
                "Business Domain",
                value=st.session_state.canvas_data.get('domain', ''),
                placeholder="e.g., Healthcare, Finance, Retail, Manufacturing",
                help="The business domain for your data pipeline"
            )

            use_case = st.text_area(
                "Use Case Description",
                value=st.session_state.canvas_data.get('use_case', ''),
                placeholder="Describe what you plan to do with the data...",
                help="Detailed description of your intended use case",
                height=100
            )

            required_data_types = st.text_area(
                "Required Data Types",
                placeholder="customer data\nsales transactions\nmarket prices\nweather data",
                help="Enter one data type per line",
                height=80
            )

        with col2:
            geographic_scope = st.text_input(
                "Geographic Scope (Optional)",
                placeholder="e.g., United States, European Union, Global",
                help="Geographic limitations or requirements"
            )

            time_period = st.text_input(
                "Time Period Requirements (Optional)",
                placeholder="e.g., 2020-present, Historical 10 years, Real-time only",
                help="Time period constraints for the data"
            )

            max_sources = st.number_input(
                "Maximum Sources",
                min_value=1,
                max_value=10,
                value=5,
                help="Maximum number of sources to discover"
            )

        st.markdown("### Discovery Preferences")

        col3, col4 = st.columns(2)

        with col3:
            preferred_types = st.multiselect(
                "Preferred Source Types",
                options=[t.value for t in DataSourceType],
                help="Select preferred types of data sources"
            )

            search_strategy = st.selectbox(
                "Search Strategy",
                options=["focused", "comprehensive", "quick"],
                index=0,
                help="Discovery approach intensity"
            )

        with col4:
            exclude_paid = st.checkbox(
                "Exclude Paid Sources",
                help="Only include free/open data sources"
            )

            require_api = st.checkbox(
                "Require API Access",
                help="Only include sources with API access"
            )

            col5, col6, col7 = st.columns(3)
            with col5:
                include_academic = st.checkbox("Academic Sources", value=True)
            with col6:
                include_government = st.checkbox("Government Sources", value=True)
            with col7:
                include_commercial = st.checkbox("Commercial Sources", value=True)

        submitted = st.form_submit_button("🚀 Discover Sources", use_container_width=True)

        if submitted and business_domain and use_case and required_data_types:
            data_types_list = [dt.strip() for dt in required_data_types.split('\n') if dt.strip()]

            with st.spinner("🚀 Discovering sources with intelligent BAML agents..."):
                try:
                    result = asyncio.run(
                        st.session_state.discovery_agent.discover_from_scratch(
                            business_domain=business_domain,
                            use_case_description=use_case,
                            required_data_types=data_types_list,
                            canvas_data=st.session_state.canvas_data,
                            max_sources=max_sources,
                            geographic_scope=geographic_scope or None,
                            time_period_requirements=time_period or None,
                            preferred_source_types=preferred_types or None,
                            exclude_paid_sources=exclude_paid,
                            require_api_access=require_api,
                            search_strategy=search_strategy,
                            include_academic=include_academic,
                            include_government=include_government,
                            include_commercial=include_commercial
                        )
                    )
                    st.session_state.discovery_result = result
                    st.success(f"✅ Discovery complete! Found {len(result.discovered_sources)} sources")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error during discovery: {str(e)}")

def render_discovery_results():
    """Render discovery results and portfolio analysis"""
    result = st.session_state.discovery_result

    st.header("📊 Discovery Results")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Sources Found", len(result.discovered_sources))
    with col2:
        st.metric("Discovery Time", f"{result.discovery_duration_seconds:.1f}s")
    with col3:
        avg_relevance = sum(s.relevance_score for s in result.discovered_sources) / len(result.discovered_sources)
        st.metric("Avg Relevance", f"{avg_relevance:.2f}")
    with col4:
        api_sources = sum(1 for s in result.discovered_sources if 'api' in s.access_method.lower())
        st.metric("API Sources", api_sources)

    # Source details
    st.markdown("### 📋 Discovered Sources")

    for i, source in enumerate(result.discovered_sources, 1):
        with st.expander(f"{i}. {source.name} ({source.source_type})", expanded=(i <= 2)):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Description:** {source.description}")
                st.markdown(f"**URL:** {source.url}")
                st.markdown(f"**Access Method:** {source.access_method}")

                if source.data_formats:
                    st.markdown(f"**Data Formats:** {', '.join(source.data_formats)}")

                if source.update_frequency:
                    st.markdown(f"**Update Frequency:** {source.update_frequency}")

                if source.authentication_required:
                    st.markdown(f"**Authentication:** {source.authentication_method or 'Required'}")

            with col2:
                st.metric("Relevance Score", f"{source.relevance_score:.2f}")
                if source.data_quality_score:
                    st.metric("Quality Score", f"{source.data_quality_score:.2f}")
                st.metric("Confidence", f"{source.confidence_score:.2f}")

                if source.license_type:
                    st.markdown(f"**License:** {source.license_type}")

    # Portfolio analysis
    with st.spinner("🔍 Analyzing source portfolio..."):
        try:
            portfolio = asyncio.run(
                st.session_state.discovery_agent.analyze_source_portfolio(
                    result.discovered_sources,
                    st.session_state.canvas_data
                )
            )
            render_portfolio_analysis(portfolio)
        except Exception as e:
            st.warning(f"Portfolio analysis unavailable: {str(e)}")

    # Workflow prepopulation preview
    render_workflow_prepopulation_preview(result)

    # Next steps
    st.markdown("### 🎯 Recommended Next Steps")
    for step in result.recommended_next_steps:
        st.markdown(f"• {step}")

    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 New Discovery", use_container_width=True):
            del st.session_state.discovery_path
            del st.session_state.discovery_result
            st.rerun()

    with col2:
        if st.button("📋 Operations & Resources", use_container_width=True):
            # Store discovery data for next step
            st.session_state.operations_prepopulated_data = result.prefilled_operations_data
            st.switch_page("pages/operations_resources.py")

    with col3:
        if st.button("🏛️ Data & Governance", use_container_width=True):
            # Store discovery data for next step
            st.session_state.governance_prepopulated_data = result.prefilled_governance_data
            st.switch_page("pages/data_governance.py")

def render_portfolio_analysis(portfolio: Dict[str, Any]):
    """Render portfolio analysis results"""
    st.markdown("### 🎯 Portfolio Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Source Types", len(portfolio['source_types']))
        st.metric("API Available", portfolio['api_available'])

    with col2:
        st.metric("Auth Required", portfolio['authentication_required'])
        st.metric("Integration Complexity", portfolio['integration_complexity'])

    with col3:
        st.metric("Avg Quality", f"{portfolio['average_quality_score']:.2f}")
        st.metric("Avg Relevance", f"{portfolio['average_relevance_score']:.2f}")

    # Coverage gaps
    if portfolio['coverage_gaps']:
        st.markdown("**⚠️ Identified Gaps:**")
        for gap in portfolio['coverage_gaps']:
            st.markdown(f"• {gap}")

    # Risk factors
    if portfolio['risk_factors']:
        st.markdown("**🚨 Risk Factors:**")
        for risk in portfolio['risk_factors']:
            st.markdown(f"• {risk}")

def render_workflow_prepopulation_preview(result: DiscoveryResult):
    """Render preview of workflow prepopulation data"""
    st.markdown("### 🔗 Workflow Integration Preview")

    tab1, tab2 = st.tabs(["Operations & Resources", "Data & Governance"])

    with tab1:
        st.markdown("**Prepopulated Operations Data:**")
        if result.prefilled_operations_data:
            for key, value in result.prefilled_operations_data.items():
                st.markdown(f"• **{key}:** {value}")
        else:
            st.info("Operations data will be prepared after BAML processing")

    with tab2:
        st.markdown("**Prepopulated Governance Data:**")
        if result.prefilled_governance_data:
            for key, value in result.prefilled_governance_data.items():
                st.markdown(f"• **{key}:** {value}")
        else:
            st.info("Governance data will be prepared after BAML processing")

def main():
    """Main discovery page function"""
    initialize_session_state()

    # Check if canvas data is available
    if not st.session_state.canvas_data:
        st.warning("⚠️ No canvas data found. Please complete the Value & Users step first.")
        if st.button("📊 Go to Data Business Canvas"):
            st.switch_page("pages/data_business_canvas.py")
        return

    # Display discovery workflow based on state
    if 'discovery_path' not in st.session_state:
        render_discovery_path_selection()
    elif st.session_state.discovery_result is None:
        if st.session_state.discovery_path == DiscoveryPath.KNOWN_SOURCE:
            render_known_sources_interface()
        else:  # ZERO_START
            render_zero_start_interface()
    else:
        render_discovery_results()

if __name__ == "__main__":
    main()