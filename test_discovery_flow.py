#!/usr/bin/env python3
"""
Test script for complete Canvas-to-Discovery flow

Tests the integrated flow from Data Business Canvas context through
intelligent data discovery to executive recommendations.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_discovery_agent_import():
    """Test discovery agent imports"""
    print("🧪 Testing Discovery Agent Imports")

    try:
        from agentic_data_scraper.agents.data_discovery import (
            DataDiscoveryAgent, DataSource, DiscoveryContext
        )
        print("✅ DataDiscoveryAgent imports successfully")

        from agentic_data_scraper.agents.source_recommender import (
            SourceRecommendationEngine, SourceRecommendation, ExecutiveSummary
        )
        print("✅ SourceRecommendationEngine imports successfully")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_discovery_context():
    """Test discovery context creation"""
    print("\n🧪 Testing Discovery Context Creation")

    try:
        from agentic_data_scraper.agents.data_discovery import DiscoveryContext

        # Create sample context from canvas
        sample_context = DiscoveryContext(
            business_domain="agriculture",
            primary_language="en",
            value_propositions=[
                "Agricultural commodity price trends and volatility analysis",
                "Supply chain risk assessment for key food commodities"
            ],
            target_users=[
                "Agricultural commodity traders",
                "Food processing companies"
            ],
            external_data_needs=[
                "Government agricultural statistics",
                "International commodity exchanges data",
                "Weather and climate data"
            ],
            quality_requirements=[
                "95% data accuracy for pricing information",
                "Daily updates for market data"
            ],
            compliance_constraints=[
                "Financial data regulations compliance"
            ],
            technical_capabilities=[
                "Cloud data warehouse",
                "Real-time streaming platform"
            ],
            budget_constraints=[
                "Cost-effective solutions preferred"
            ],
            semantic_mappings={}
        )

        print(f"✅ Discovery context created with {len(sample_context.external_data_needs)} data needs")
        return True, sample_context

    except Exception as e:
        print(f"❌ Context creation failed: {e}")
        return False, None


async def test_discovery_agent():
    """Test data discovery agent functionality"""
    print("\n🧪 Testing Data Discovery Agent")

    try:
        from agentic_data_scraper.agents.data_discovery import DataDiscoveryAgent

        # Create discovery agent (without SKOS router for testing)
        agent = DataDiscoveryAgent(skos_router=None)

        # Create test context
        context_dict = {
            "business_domain": "agriculture",
            "primary_language": "en",
            "value_propositions": ["Agricultural commodity price analysis"],
            "target_users": ["Commodity traders"],
            "external_data_needs": ["Government agricultural statistics", "Commodity prices"],
            "quality_requirements": ["95% accuracy", "Daily updates"],
            "compliance_constraints": ["Financial regulations"],
            "technical_capabilities": ["Cloud platform", "API access"],
            "budget_constraints": ["Cost-effective"],
            "semantic_mappings": {}
        }

        # Run discovery
        discovered_sources = await agent._process(
            canvas_context=context_dict,
            user_suggestions=["USDA agricultural data", "World Bank commodity prices"],
            max_sources=10,
            min_quality_score=0.6
        )

        print(f"✅ Discovery completed: {len(discovered_sources)} sources found")

        # Validate source structure
        if discovered_sources:
            source = discovered_sources[0]
            print(f"   Sample source: {source.title}")
            print(f"   Quality score: {source.quality_score:.1%}")
            print(f"   Relevance score: {source.relevance_score:.1%}")

        return True, discovered_sources

    except Exception as e:
        print(f"❌ Discovery agent test failed: {e}")
        return False, []


async def test_recommendation_engine():
    """Test source recommendation engine"""
    print("\n🧪 Testing Source Recommendation Engine")

    try:
        from agentic_data_scraper.agents.source_recommender import SourceRecommendationEngine
        from agentic_data_scraper.agents.data_discovery import DiscoveryContext, DataSource

        # Create recommendation engine
        engine = SourceRecommendationEngine()

        # Create sample discovered sources
        sample_sources = [
            DataSource(
                url="https://data.gov/agriculture",
                title="USDA Agricultural Data Portal",
                description="Government agricultural statistics and commodity data",
                source_type="portal",
                data_formats=["csv", "json"],
                update_frequency="monthly",
                access_method="public",
                quality_score=0.9,
                relevance_score=0.8,
                business_domains=["agriculture"],
                geographic_coverage="national",
                discovered_at=datetime.utcnow().isoformat(),
                metadata={"strategy": "government_portals", "verified": True}
            ),
            DataSource(
                url="https://worldbank.org/commodity-api",
                title="World Bank Commodity Price API",
                description="International commodity price data and market indicators",
                source_type="api",
                data_formats=["json"],
                update_frequency="daily",
                access_method="api_key",
                quality_score=0.95,
                relevance_score=0.9,
                business_domains=["agriculture", "finance"],
                geographic_coverage="global",
                discovered_at=datetime.utcnow().isoformat(),
                metadata={"strategy": "international_organizations", "verified": True}
            )
        ]

        # Create discovery context
        context = DiscoveryContext(
            business_domain="agriculture",
            primary_language="en",
            value_propositions=["Commodity price analysis"],
            target_users=["Traders"],
            external_data_needs=["Price data", "Market statistics"],
            quality_requirements=["95% accuracy"],
            compliance_constraints=[],
            technical_capabilities=["API integration"],
            budget_constraints=["Cost-effective"],
            semantic_mappings={}
        )

        # Generate recommendations
        recommendations, executive_summary = await engine._process(
            discovered_sources=sample_sources,
            discovery_context=context
        )

        print(f"✅ Recommendations generated: {len(recommendations)} sources analyzed")
        print(f"   Top recommendation: {recommendations[0].source.title}")
        print(f"   Recommendation score: {recommendations[0].recommendation_score:.1%}")
        print(f"   Business impact: {recommendations[0].business_impact}")
        print(f"   Implementation effort: {recommendations[0].implementation_effort}")

        print(f"✅ Executive summary generated")
        print(f"   Key findings: {len(executive_summary.key_findings)}")
        print(f"   Strategic recommendations: {len(executive_summary.strategic_recommendations)}")

        return True, recommendations, executive_summary

    except Exception as e:
        print(f"❌ Recommendation engine test failed: {e}")
        return False, [], None


def test_cli_integration():
    """Test CLI integration for discovery flow"""
    print("\n🧪 Testing CLI Integration")

    try:
        from agentic_data_scraper.cli.canvas_cli import app

        # Check if discover command exists
        commands = []
        for command in app.commands.values():
            commands.append(command.name)

        if "discover" in commands:
            print("✅ Discovery flow command available in CLI")
        else:
            print("❌ Discovery command not found in CLI")
            return False

        print("✅ CLI integration verified")
        return True

    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False


async def test_complete_flow():
    """Test the complete canvas-to-discovery flow"""
    print("\n🧪 Testing Complete Canvas-to-Discovery Flow")

    try:
        # Step 1: Canvas Context (simulated)
        print("📊 Step 1: Canvas context prepared")

        # Step 2: Discovery
        success, discovered_sources = await test_discovery_agent()
        if not success:
            return False

        # Step 3: Recommendations
        success, recommendations, summary = await test_recommendation_engine()
        if not success:
            return False

        # Step 4: Export
        if recommendations:
            from agentic_data_scraper.agents.source_recommender import SourceRecommendationEngine

            engine = SourceRecommendationEngine()
            export_data = await engine.export_recommendations(
                recommendations, summary, format="json"
            )

            print("✅ Export functionality verified")
            print(f"   Export size: {len(export_data)} characters")

        print("🎉 Complete flow test passed!")
        return True

    except Exception as e:
        print(f"❌ Complete flow test failed: {e}")
        return False


def test_data_structures():
    """Test data structure compatibility"""
    print("\n🧪 Testing Data Structure Compatibility")

    try:
        from agentic_data_scraper.agents.data_discovery import DataSource
        from agentic_data_scraper.agents.source_recommender import SourceRecommendation
        from dataclasses import asdict

        # Test DataSource serialization
        source = DataSource(
            url="https://example.com",
            title="Test Source",
            description="Test description",
            source_type="api",
            data_formats=["json"],
            update_frequency="daily",
            access_method="public",
            quality_score=0.8,
            relevance_score=0.9,
            business_domains=["test"],
            geographic_coverage="global",
            discovered_at=datetime.utcnow().isoformat(),
            metadata={"test": True}
        )

        source_dict = asdict(source)
        print("✅ DataSource serialization works")

        # Test JSON compatibility
        json_str = json.dumps(source_dict, indent=2)
        reloaded = json.loads(json_str)
        print("✅ JSON serialization/deserialization works")

        return True

    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Discovery Flow Test Suite\n")

    success = True

    # Test imports
    success &= test_discovery_agent_import()

    # Test context creation
    context_success, context = test_discovery_context()
    success &= context_success

    # Test data structures
    success &= test_data_structures()

    # Test CLI integration
    success &= test_cli_integration()

    # Test discovery agent
    discovery_success, sources = await test_discovery_agent()
    success &= discovery_success

    # Test recommendation engine
    rec_success, recs, summary = await test_recommendation_engine()
    success &= rec_success

    # Test complete flow
    flow_success = await test_complete_flow()
    success &= flow_success

    print(f"\n{'🎉 ALL TESTS PASSED!' if success else '❌ SOME TESTS FAILED'}")

    # Summary
    if success:
        print("\n📊 Test Summary:")
        print("✅ Data discovery agent functional")
        print("✅ Source recommendation engine operational")
        print("✅ Canvas-to-discovery integration working")
        print("✅ CLI commands available")
        print("✅ Data structures compatible")
        print("✅ Export functionality ready")
        print("\n🚀 Ready for production testing!")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)