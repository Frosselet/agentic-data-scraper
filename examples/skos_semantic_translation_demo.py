"""
SKOS Semantic Translation Demo

Demonstrates deterministic multilingual term translation using SKOS concepts
in KuzuDB. Shows practical application for supply chain crisis management
where consistent terminology is critical for AI-powered decision making.

Example: Turkish supplier data → English standardized terms for AI processing
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from agentic_data_scraper.semantic.skos_router import SKOSSemanticRouter, SKOSEnabledCollector
import json


def demo_skos_translation():
    """Demonstrate SKOS-based semantic translation for supply chain data"""
    
    print("=== SKOS Semantic Translation Demo ===\n")
    
    # Initialize SKOS router with KuzuDB
    db_path = project_root / "data" / "skos_demo.db"
    skos_router = SKOSSemanticRouter(str(db_path))
    
    print("✅ SKOS Router initialized with KuzuDB backend")
    print("✅ Supply chain vocabulary loaded (Turkish, English, French, Spanish)")
    print()
    
    # Example 1: Turkish supplier product data
    print("📦 Example 1: Turkish Supplier Product Translation")
    print("-" * 50)
    
    turkish_terms = [
        ("zeytin yağı", "tr"),
        ("tarife", "tr"), 
        ("gümrük vergisi", "tr"),
        ("tedarikçi", "tr")
    ]
    
    for term, lang in turkish_terms:
        result = skos_router.route_term_to_preferred(term, lang, "en")
        
        print(f"Original: '{term}' @{lang}")
        print(f"Preferred: '{result['preferred_label']}' @en")
        print(f"Confidence: {result['translation_confidence']:.1%}")
        print(f"Method: {result['method']}")
        print(f"Concept URI: {result.get('concept_uri', 'N/A')}")
        print()
    
    # Example 2: Crisis Supply Chain Data Processing
    print("🚨 Example 2: Crisis Supply Chain Data Processing")
    print("-" * 50)
    
    # Simulated crisis data from Turkish supplier
    crisis_supplier_data = {
        "supplier_id": "TR-AEGEAN-001",
        "supplier_name": "Aegean Olive Producers Cooperative",
        "location": "İzmir, Türkiye",
        "product_name_tr": "extra virgin zeytin yağı",
        "policy_term": "gümrük vergisi",
        "risk_status": "high_tariff_exposure",
        "supply_capacity": "2000 tons/month",
        "quality_certification": "EU Organic"
    }
    
    print("Original Crisis Data:")
    print(json.dumps(crisis_supplier_data, indent=2, ensure_ascii=False))
    print()
    
    # Process with SKOS-enabled collector
    skos_collector = SKOSEnabledCollector(skos_router)
    enriched_data = skos_collector.extract_with_semantic_routing(
        crisis_supplier_data,
        term_mappings={
            'product_name_tr': {'source_lang': 'tr', 'target_lang': 'en'},
            'policy_term': {'source_lang': 'tr', 'target_lang': 'en'}
        }
    )
    
    print("SKOS-Enriched Crisis Data:")
    print(json.dumps(enriched_data, indent=2, ensure_ascii=False))
    print()
    
    # Example 3: Multilingual Term Coverage
    print("🌍 Example 3: Multilingual Term Coverage")
    print("-" * 50)
    
    # Test same concept across languages
    olive_oil_variants = [
        ("olive oil", "en"),
        ("zeytin yağı", "tr"),
        ("huile d'olive", "fr"),
        ("aceite de oliva", "es")
    ]
    
    print("Testing multilingual routing for 'olive oil' concept:")
    for term, lang in olive_oil_variants:
        result = skos_router.route_term_to_preferred(term, lang, "en")
        status = "✅" if result['preferred_label'] else "❌"
        print(f"{status} '{term}' @{lang} → '{result.get('preferred_label', 'NOT_FOUND')}' @en")
    
    print()
    
    # Example 4: Deterministic vs AI Translation Comparison
    print("🤖 Example 4: Deterministic vs AI Translation Benefits")
    print("-" * 50)
    
    comparison_terms = ["zeytin yağı", "gümrük vergisi", "tedarikçi"]
    
    print("SKOS Deterministic Translation Results:")
    for term in comparison_terms:
        result = skos_router.route_term_to_preferred(term, "tr", "en")
        print(f"  • '{term}' → '{result['preferred_label']}' (Confidence: {result['translation_confidence']:.1%})")
    
    print("\nBenefits of SKOS over AI Translation:")
    print("  ✅ 100% deterministic results (no variance between runs)")
    print("  ✅ Domain-specific vocabulary precision")
    print("  ✅ No external API dependencies during crisis")
    print("  ✅ Instant in-memory routing via KuzuDB")
    print("  ✅ Semantic relationships preserved")
    print("  ❌ AI: Stochastic, context-dependent, external dependency")
    print()
    
    # Example 5: Custom Domain Vocabulary
    print("🔧 Example 5: Adding Custom Domain Vocabulary")
    print("-" * 50)
    
    # Add custom concept for specific supply chain scenario
    custom_concept = {
        'concept_uri': 'http://localhost:3030/dbc/ontology#CrisisResponseTimeConcept',
        'scheme_uri': 'http://localhost:3030/dbc/ontology#SupplyChainVocabulary',
        'pref_label_en': 'crisis response time',
        'pref_label_tr': 'kriz yanıt süresi',
        'pref_label_fr': 'temps de réponse de crise',
        'pref_label_es': 'tiempo de respuesta a crisis',
        'definition': 'Time required to implement alternative supply chain routes during disruption',
        'broader_concept': 'http://localhost:3030/dbc/ontology#SupplyChainMetricsConcept'
    }
    
    custom_alt_labels = [
        {'alt_label': 'crisis response time', 'language': 'en'},
        {'alt_label': 'emergency response time', 'language': 'en'},
        {'alt_label': 'kriz yanıt süresi', 'language': 'tr'},
        {'alt_label': 'acil durum yanıt süresi', 'language': 'tr'}
    ]
    
    try:
        skos_router.add_custom_concept(custom_concept, custom_alt_labels)
        print("✅ Added custom concept: Crisis Response Time")
        
        # Test the new concept
        test_result = skos_router.route_term_to_preferred("acil durum yanıt süresi", "tr", "en")
        print(f"✅ Custom term routing: 'acil durum yanıt süresi' @tr → '{test_result['preferred_label']}' @en")
        
    except Exception as e:
        print(f"⚠️ Custom concept already exists or error: {e}")
    
    print()
    
    # Clean up
    skos_router.close()
    print("🎯 Demo completed. SKOS semantic translation enables:")
    print("   • Deterministic multilingual term standardization")
    print("   • Crisis-ready supply chain vocabulary")
    print("   • AI-powered decision making with consistent terminology")
    print("   • Global supply chain semantic interoperability")


if __name__ == "__main__":
    demo_skos_translation()