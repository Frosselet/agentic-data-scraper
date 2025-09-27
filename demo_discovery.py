#!/usr/bin/env python3
"""
Demo Script - Canvas-to-Discovery Flow

Shows the system in action with a realistic example.
"""

import sys
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


async def demo_discovery_flow():
    """Demonstrate the complete discovery flow"""

    print("🎯 DEMO: Canvas-to-Discovery Flow")
    print("=" * 50)

    # Step 1: Business Canvas Context
    print("\n📊 STEP 1: Business Canvas Context")
    print("-" * 30)

    sample_canvas = {
        "business_domain": "agriculture",
        "primary_language": "en",
        "value_propositions": [
            "Agricultural commodity price trends and volatility analysis",
            "Supply chain risk assessment for key food commodities",
            "Trade flow optimization recommendations"
        ],
        "target_users": [
            "Agricultural commodity traders",
            "Food processing companies",
            "Supply chain managers"
        ],
        "external_data_needs": [
            "Government agricultural statistics",
            "International commodity exchanges data",
            "Weather and climate data",
            "Trade flow statistics",
            "Economic indicators"
        ],
        "quality_requirements": [
            "95% data accuracy for pricing information",
            "Daily updates for market data",
            "Complete geographic coverage for major commodities"
        ],
        "compliance_constraints": [
            "Financial data regulations compliance",
            "Agricultural data sharing agreements"
        ],
        "technical_capabilities": [
            "Cloud data warehouse",
            "Real-time streaming platform",
            "API gateway for data access"
        ],
        "budget_constraints": [
            "Cost-effective solutions preferred",
            "Subscription costs under $50k annually"
        ],
        "semantic_mappings": {}
    }

    print("✅ Business Domain:", sample_canvas["business_domain"])
    print("✅ Key Value Propositions:")
    for prop in sample_canvas["value_propositions"][:2]:
        print(f"   • {prop}")
    print("✅ External Data Needs:")
    for need in sample_canvas["external_data_needs"][:3]:
        print(f"   • {need}")

    # Step 2: User adds suggestions
    print("\n💭 STEP 2: User Suggestions")
    print("-" * 30)

    user_suggestions = [
        "USDA National Agricultural Statistics Service",
        "World Bank commodity price data",
        "FAO agricultural production statistics",
        "Chicago Mercantile Exchange data"
    ]

    print("User adds these data source ideas:")
    for suggestion in user_suggestions:
        print(f"   • {suggestion}")

    # Step 3: AI Discovery
    print("\n🤖 STEP 3: BAML Discovery Agent")
    print("-" * 30)

    try:
        from agentic_data_scraper.agents.data_discovery import DataDiscoveryAgent

        print("🔍 Initializing BAML Discovery Agent...")
        discovery_agent = DataDiscoveryAgent(skos_router=None)  # Skip SKOS for demo

        print("🎯 Running intelligent discovery...")
        print("   Strategy 1: Government portals (data.gov, etc.)")
        print("   Strategy 2: International organizations (World Bank, FAO, etc.)")
        print("   Strategy 3: Specialized agriculture portals")
        print("   Strategy 4: Academic sources")

        # Run discovery
        discovered_sources = await discovery_agent._process(
            canvas_context=sample_canvas,
            user_suggestions=user_suggestions,
            max_sources=8,
            min_quality_score=0.6
        )

        print(f"\n✅ Discovery Complete: {len(discovered_sources)} high-quality sources found")

        # Show top 3 sources
        print("\n🏆 TOP DISCOVERED SOURCES:")
        for i, source in enumerate(discovered_sources[:3]):
            print(f"\n#{i+1} {source.title}")
            print(f"   URL: {source.url}")
            print(f"   Type: {source.source_type} | Access: {source.access_method}")
            print(f"   Quality: {source.quality_score:.1%} | Relevance: {source.relevance_score:.1%}")
            print(f"   Formats: {', '.join(source.data_formats)}")
            print(f"   Updates: {source.update_frequency}")

    except Exception as e:
        print(f"❌ Discovery simulation failed: {e}")
        discovered_sources = []

    # Step 4: Recommendation Engine
    print(f"\n🧠 STEP 4: Recommendation Engine")
    print("-" * 30)

    if discovered_sources:
        try:
            from agentic_data_scraper.agents.source_recommender import SourceRecommendationEngine
            from agentic_data_scraper.agents.data_discovery import DiscoveryContext

            print("📊 Analyzing sources with multi-criteria framework...")
            print("   • Business value assessment (35%)")
            print("   • Technical feasibility (25%)")
            print("   • Risk assessment (25%)")
            print("   • Cost-benefit analysis (15%)")

            # Create recommendation engine
            recommender = SourceRecommendationEngine()

            # Create context
            context = DiscoveryContext(
                business_domain=sample_canvas["business_domain"],
                primary_language=sample_canvas["primary_language"],
                value_propositions=sample_canvas["value_propositions"],
                target_users=sample_canvas["target_users"],
                external_data_needs=sample_canvas["external_data_needs"],
                quality_requirements=sample_canvas["quality_requirements"],
                compliance_constraints=sample_canvas["compliance_constraints"],
                technical_capabilities=sample_canvas["technical_capabilities"],
                budget_constraints=sample_canvas["budget_constraints"],
                semantic_mappings=sample_canvas["semantic_mappings"]
            )

            # Generate recommendations
            recommendations, executive_summary = await recommender._process(
                discovered_sources=discovered_sources,
                discovery_context=context
            )

            print(f"\n✅ Analysis Complete: {len(recommendations)} sources analyzed")

            # Show top recommendation
            if recommendations:
                top_rec = recommendations[0]
                print(f"\n🏆 TOP RECOMMENDATION:")
                print(f"   Source: {top_rec.source.title}")
                print(f"   Recommendation Score: {top_rec.recommendation_score:.1%}")
                print(f"   Business Impact: {top_rec.business_impact.upper()}")
                print(f"   Implementation Effort: {top_rec.implementation_effort.upper()}")
                print(f"   Risk Level: {top_rec.risk_level.upper()}")

                print(f"\n💡 Key Benefits:")
                for benefit in top_rec.key_benefits[:3]:
                    print(f"   • {benefit}")

                print(f"\n⚠️ Considerations:")
                for concern in top_rec.potential_concerns[:2]:
                    print(f"   • {concern}")

                print(f"\n📋 Next Steps:")
                for step in top_rec.next_steps[:3]:
                    print(f"   • {step}")

            # Executive Summary
            print(f"\n📊 EXECUTIVE SUMMARY")
            print("-" * 20)
            print(f"Total Sources Discovered: {executive_summary.total_sources_discovered}")
            print(f"Recommended Sources: {executive_summary.recommended_sources}")
            print(f"Implementation Timeline: {executive_summary.estimated_implementation_timeline}")
            print(f"Cost Estimate: {executive_summary.estimated_total_cost}")

            print(f"\n🎯 Strategic Recommendations:")
            for rec in executive_summary.strategic_recommendations[:2]:
                print(f"   • {rec}")

        except Exception as e:
            print(f"❌ Recommendation simulation failed: {e}")

    print(f"\n🎉 DEMO COMPLETE!")
    print("=" * 50)
    print("To see the interactive version:")
    print("  agentic-data-scraper canvas discover")
    print("\nOr just the canvas builder:")
    print("  agentic-data-scraper canvas start")


if __name__ == "__main__":
    print("🚀 Starting Canvas-to-Discovery Demo...")
    asyncio.run(demo_discovery_flow())