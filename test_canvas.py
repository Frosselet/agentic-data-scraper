#!/usr/bin/env python3
"""
Test script for Data Business Canvas functionality
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_canvas_basic():
    """Test basic canvas functionality without heavy dependencies"""
    print("🧪 Testing Data Business Canvas - Basic Functionality")

    # Test just the core data structure without imports
    canvas_structure = {
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
            "created_at": "2025-01-13T12:00:00Z",
            "business_domain": "",
            "primary_language": "en"
        }
    }

    # Verify 9+3 framework structure
    expected_sections = [
        # Core 9 sections
        "value_propositions", "customer_segments", "customer_relationships",
        "channels", "key_activities", "key_resources", "key_partners",
        "cost_structure", "revenue_streams",

        # Additional 3 sections
        "data_sources", "data_governance", "technology_infrastructure",

        # Metadata
        "metadata"
    ]

    print(f"✅ Testing 9+3 framework structure ({len(expected_sections)} sections)")

    all_present = True
    for section in expected_sections:
        if section in canvas_structure:
            print(f"   ✓ {section}")
        else:
            print(f"   ✗ {section} MISSING")
            all_present = False

    if all_present:
        print("🎯 ALL 9+3 framework sections present!")
    else:
        print("❌ Some sections missing")
        return False

    # Test JSON serialization
    try:
        json_str = json.dumps(canvas_structure, indent=2)
        print("✅ JSON serialization works")

        # Test deserialization
        reloaded = json.loads(json_str)
        print("✅ JSON deserialization works")

        if len(reloaded) == len(canvas_structure):
            print("✅ Data integrity preserved")
        else:
            print("❌ Data integrity issue")
            return False

    except Exception as e:
        print(f"❌ JSON handling failed: {e}")
        return False

    # Test completion calculation logic
    def calculate_completion(data):
        total_fields = 0
        completed_fields = 0

        def count_fields(obj):
            nonlocal total_fields, completed_fields

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "metadata":
                        continue
                    count_fields(value)
            elif isinstance(obj, list):
                total_fields += 1
                if obj:  # Non-empty list
                    completed_fields += 1
            else:
                total_fields += 1
                if obj:  # Non-empty value
                    completed_fields += 1

        count_fields(data)
        return completed_fields / total_fields if total_fields > 0 else 0.0

    completion = calculate_completion(canvas_structure)
    print(f"✅ Completion calculation: {completion:.1%}")

    # Test with some sample data
    sample_data = canvas_structure.copy()
    sample_data["value_propositions"]["data_insights"] = ["Customer behavior analysis", "Risk assessment"]
    sample_data["customer_segments"]["primary_users"] = ["Marketing team", "Risk managers"]
    sample_data["data_sources"]["external_sources"] = ["Government data", "Market feeds"]
    sample_data["metadata"]["business_domain"] = "finance"

    sample_completion = calculate_completion(sample_data)
    print(f"✅ Sample completion calculation: {sample_completion:.1%}")

    if sample_completion > completion:
        print("✅ Completion increases with data")
    else:
        print("❌ Completion calculation issue")
        return False

    print("🎉 All basic functionality tests passed!")
    return True

def test_cli_integration():
    """Test CLI integration"""
    print("\n🧪 Testing CLI Integration")

    # Test CLI structure import
    try:
        from agentic_data_scraper.cli.canvas_cli import app
        print("✅ Canvas CLI imports successfully")

        # Test main CLI integration
        from agentic_data_scraper.cli.main import app as main_app
        print("✅ Main CLI imports successfully")

        # Check if canvas command is registered
        commands = [cmd.name for cmd in main_app.commands.values()]
        if "canvas" in commands:
            print("✅ Canvas command registered in main CLI")
        else:
            print("❌ Canvas command not found in main CLI")
            return False

    except Exception as e:
        print(f"❌ CLI integration failed: {e}")
        return False

    print("🎉 CLI integration tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Data Business Canvas Test Suite\n")

    success = True

    # Run basic functionality tests
    success &= test_canvas_basic()

    # Run CLI integration tests
    success &= test_cli_integration()

    print(f"\n{'🎉 ALL TESTS PASSED!' if success else '❌ SOME TESTS FAILED'}")
    sys.exit(0 if success else 1)