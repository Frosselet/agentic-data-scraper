"""
Simple Discovery Interface - Standalone Streamlit App

A simplified version of the discovery flow that avoids complex imports
and focuses on demonstrating the core functionality.
"""

import streamlit as st
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Configure page
st.set_page_config(
    page_title="Data Discovery Demo",
    page_icon="🔍",
    layout="wide"
)

def main():
    """Main Streamlit app"""

    st.title("🔍 Data Discovery Flow - Demo")
    st.markdown("""
    **From Business Canvas to Intelligent Data Discovery**

    This demo shows how business context drives AI-powered data source discovery.
    """)

    # Sidebar for navigation
    st.sidebar.title("Demo Steps")
    step = st.sidebar.radio(
        "Choose a step:",
        ["📊 Business Context", "🤖 Discovery Results", "📋 Recommendations"]
    )

    if step == "📊 Business Context":
        show_business_context()
    elif step == "🤖 Discovery Results":
        show_discovery_results()
    elif step == "📋 Recommendations":
        show_recommendations()

def show_business_context():
    """Show business context step"""

    st.header("📊 Step 1: Business Context")

    st.subheader("Sample Canvas Data")
    st.info("This shows the business context captured from a Data Business Canvas")

    # Sample business context
    context = {
        "business_domain": "agriculture",
        "primary_language": "en",
        "value_propositions": [
            "Agricultural commodity price trends and volatility analysis",
            "Supply chain risk assessment for key food commodities",
            "Trade flow optimization recommendations"
        ],
        "external_data_needs": [
            "Government agricultural statistics",
            "International commodity exchanges data",
            "Weather and climate data",
            "Trade flow statistics"
        ],
        "quality_requirements": [
            "95% data accuracy for pricing information",
            "Daily updates for market data",
            "Complete geographic coverage"
        ]
    }

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Business Domain", context["business_domain"].title())
        st.metric("Primary Language", context["primary_language"].upper())

        st.subheader("🎯 Value Propositions")
        for i, prop in enumerate(context["value_propositions"]):
            st.write(f"{i+1}. {prop}")

    with col2:
        st.subheader("📊 Data Needs")
        for need in context["external_data_needs"]:
            st.write(f"• {need}")

        st.subheader("✅ Quality Requirements")
        for req in context["quality_requirements"]:
            st.write(f"• {req}")

    # Store context in session state
    st.session_state["business_context"] = context

    st.success("✅ Business context ready for discovery!")

def show_discovery_results():
    """Show mock discovery results"""

    st.header("🤖 Step 2: AI Discovery Results")

    if "business_context" not in st.session_state:
        st.warning("⚠️ Please complete Step 1 first")
        return

    st.info("Discovery agents found relevant data sources using multiple strategies")

    # Mock discovered sources
    discovered_sources = [
        {
            "title": "USDA National Agricultural Statistics Service",
            "url": "https://nass.usda.gov/api",
            "description": "Comprehensive US agricultural statistics including crop production, prices, and farm demographics",
            "source_type": "api",
            "access_method": "public",
            "data_formats": ["json", "csv"],
            "update_frequency": "monthly",
            "quality_score": 0.92,
            "relevance_score": 0.89,
            "strategy": "government_portals"
        },
        {
            "title": "World Bank Commodity Price Data",
            "url": "https://www.worldbank.org/en/research/commodity-markets",
            "description": "Global commodity price data and market analysis from the World Bank",
            "source_type": "api",
            "access_method": "public",
            "data_formats": ["json", "csv"],
            "update_frequency": "daily",
            "quality_score": 0.95,
            "relevance_score": 0.91,
            "strategy": "international_organizations"
        },
        {
            "title": "FAO Food Price Monitoring",
            "url": "https://www.fao.org/worldfoodsituation/foodpricesindex/en/",
            "description": "Food and Agriculture Organization global food price indices and monitoring data",
            "source_type": "portal",
            "access_method": "public",
            "data_formats": ["csv", "excel"],
            "update_frequency": "monthly",
            "quality_score": 0.88,
            "relevance_score": 0.85,
            "strategy": "international_organizations"
        },
        {
            "title": "Chicago Mercantile Exchange Data",
            "url": "https://www.cmegroup.com/market-data.html",
            "description": "Real-time and historical commodity futures and options data",
            "source_type": "api",
            "access_method": "subscription",
            "data_formats": ["json", "xml"],
            "update_frequency": "real-time",
            "quality_score": 0.96,
            "relevance_score": 0.93,
            "strategy": "commercial_apis"
        },
        {
            "title": "NOAA Climate Data",
            "url": "https://www.ncei.noaa.gov/data/",
            "description": "Weather and climate data affecting agricultural production",
            "source_type": "portal",
            "access_method": "public",
            "data_formats": ["csv", "json"],
            "update_frequency": "daily",
            "quality_score": 0.90,
            "relevance_score": 0.78,
            "strategy": "government_portals"
        }
    ]

    st.metric("Sources Discovered", len(discovered_sources))

    # Show discovery strategies
    st.subheader("🔍 Discovery Strategies Used")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info("**Government Portals**\n2 sources")
    with col2:
        st.info("**International Orgs**\n2 sources")
    with col3:
        st.info("**Commercial APIs**\n1 source")
    with col4:
        st.info("**Academic Sources**\n0 sources")

    # Show discovered sources
    st.subheader("📊 Discovered Sources")

    for i, source in enumerate(discovered_sources):
        with st.expander(f"#{i+1} {source['title']} ⭐{source['quality_score']:.1%}"):
            col_info, col_scores = st.columns([2, 1])

            with col_info:
                st.write(f"**URL:** {source['url']}")
                st.write(f"**Description:** {source['description']}")
                st.write(f"**Type:** {source['source_type']} | **Access:** {source['access_method']}")
                st.write(f"**Formats:** {', '.join(source['data_formats'])}")
                st.write(f"**Updates:** {source['update_frequency']}")
                st.write(f"**Strategy:** {source['strategy']}")

            with col_scores:
                st.metric("Quality Score", f"{source['quality_score']:.1%}")
                st.metric("Relevance Score", f"{source['relevance_score']:.1%}")

    # Store results
    st.session_state["discovered_sources"] = discovered_sources

    st.success(f"✅ {len(discovered_sources)} high-quality sources discovered!")

def show_recommendations():
    """Show intelligent recommendations"""

    st.header("📋 Step 3: Executive Recommendations")

    if "discovered_sources" not in st.session_state:
        st.warning("⚠️ Please complete Steps 1 and 2 first")
        return

    sources = st.session_state["discovered_sources"]

    st.info("AI analysis provides executive-level recommendations with risk assessment")

    # Mock recommendations with scoring
    recommendations = []
    for source in sources:
        # Calculate mock recommendation score
        business_value = (source['relevance_score'] * 0.6 +
                         (0.9 if source['access_method'] == 'public' else 0.5) * 0.4)

        technical_score = (source['quality_score'] * 0.5 +
                          (0.9 if 'json' in source['data_formats'] else 0.7) * 0.3 +
                          (0.9 if source['source_type'] == 'api' else 0.6) * 0.2)

        risk_score = (0.2 if source['access_method'] == 'public' else
                     0.4 if source['access_method'] == 'registration' else 0.7)

        cost_benefit = (0.9 if source['access_method'] == 'public' else 0.4)

        recommendation_score = (business_value * 0.35 + technical_score * 0.25 +
                              (1.0 - risk_score) * 0.25 + cost_benefit * 0.15)

        recommendations.append({
            "source": source,
            "recommendation_score": recommendation_score,
            "business_impact": "high" if recommendation_score > 0.8 else "medium" if recommendation_score > 0.6 else "low",
            "implementation_effort": "low" if technical_score > 0.8 else "medium" if technical_score > 0.6 else "high",
            "risk_level": "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high"
        })

    # Sort by recommendation score
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)

    # Show top recommendation
    top_rec = recommendations[0]

    st.subheader("🏆 Top Recommendation")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Recommendation Score", f"{top_rec['recommendation_score']:.1%}")
    with col2:
        st.metric("Business Impact", top_rec['business_impact'].upper())
    with col3:
        st.metric("Implementation", top_rec['implementation_effort'].upper() + " effort")
    with col4:
        st.metric("Risk Level", top_rec['risk_level'].upper())

    st.write(f"**{top_rec['source']['title']}**")
    st.write(top_rec['source']['description'])

    # Key benefits and concerns
    col_benefits, col_concerns = st.columns(2)

    with col_benefits:
        st.subheader("💡 Key Benefits")
        if top_rec['source']['access_method'] == 'public':
            st.write("• No licensing costs")
        if 'json' in top_rec['source']['data_formats']:
            st.write("• API-friendly format")
        if top_rec['source']['quality_score'] > 0.9:
            st.write("• High data quality")
        st.write("• Strong business alignment")

    with col_concerns:
        st.subheader("⚠️ Considerations")
        if top_rec['source']['update_frequency'] == 'monthly':
            st.write("• Monthly update frequency")
        if top_rec['source']['source_type'] == 'portal':
            st.write("• Manual data access")
        st.write("• Requires integration setup")

    # Next steps
    st.subheader("📋 Recommended Next Steps")
    st.write("1. Verify data source accessibility and current status")
    st.write("2. Review API documentation and usage terms")
    st.write("3. Design integration architecture")
    st.write("4. Develop proof of concept")
    st.write("5. Create data quality monitoring")

    # Executive summary
    st.subheader("📊 Executive Summary")

    high_value_sources = len([r for r in recommendations if r['business_impact'] == 'high'])
    low_effort_sources = len([r for r in recommendations if r['implementation_effort'] == 'low'])

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric("Total Sources", len(recommendations))
        st.metric("High Value", high_value_sources)

    with summary_col2:
        st.metric("Low Effort", low_effort_sources)
        avg_score = sum(r['recommendation_score'] for r in recommendations) / len(recommendations)
        st.metric("Avg Score", f"{avg_score:.1%}")

    with summary_col3:
        st.metric("Timeline", "2-4 weeks")
        st.metric("Est. Cost", "Low")

    # Strategic recommendations
    st.subheader("🎯 Strategic Recommendations")
    st.write(f"1. **Quick Win**: Start with {top_rec['source']['title']} for immediate value")
    st.write(f"2. **Parallel Development**: {low_effort_sources} sources have low implementation effort")
    st.write("3. **Risk Management**: All recommended sources are low-to-medium risk")
    st.write("4. **Cost Optimization**: Prioritize public sources to minimize licensing costs")

    # Export option
    if st.button("📄 Export Recommendations", type="primary"):
        export_data = {
            "executive_summary": {
                "total_sources": len(recommendations),
                "high_value_sources": high_value_sources,
                "average_score": avg_score,
                "top_recommendation": top_rec['source']['title']
            },
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }

        st.download_button(
            label="💾 Download JSON Report",
            data=json.dumps(export_data, indent=2),
            file_name=f"discovery_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

    st.success("🎉 Analysis complete! Ready for implementation.")

if __name__ == "__main__":
    main()