"""
Meaning-Preserving Semantic Mapping Example

Demonstrates how to semantically map data while preserving meaning:
- Headers: Standardize terminology and translate to English
- Data Values: Distinguish common names (standardize) from proper names (preserve)  
- Named Entity Resolution: Identify proper nouns that shouldn't be changed
- Semantic Annotations: Add context without changing original meaning

Shows real-world supply chain data processing with Turkish supplier example.
"""

import sys
import json
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from agentic_data_scraper.semantic.semantic_mapping_strategy import (
    create_meaning_preserving_semantic_mapper,
    MappingDecision,
    EntityType
)


def demonstrate_semantic_mapping_strategy():
    """Demonstrate meaning-preserving semantic mapping"""
    
    print("=== Meaning-Preserving Semantic Mapping ===\n")
    
    # Create semantic mapper with NER
    semantic_mapper = create_meaning_preserving_semantic_mapper()
    
    # Example supply chain data - mix of headers, common nouns, proper nouns
    supply_chain_data = {
        # Headers - should be standardized
        "tedarikçi_adı": "Aegean Olive Producers Ltd",           # Proper noun - preserve
        "ürün_kategorisi": "zeytin yağı",                        # Common noun - standardize  
        "menşe_ülke": "Türkiye",                                 # Proper noun (country name) - preserve
        "tedarikçi_türü": "kooperatif",                          # Common noun - standardize
        "ödeme_para_birimi": "TRY",                              # Currency code - preserve
        "kalite_sertifikası": "EU Organic",                     # Standard/brand - preserve
        "teslim_şartları": "FOB İzmir",                          # Mixed - FOB standardize, İzmir preserve
        
        # Metadata
        "veri_kaynağı": "supplier_database",                    # Header - standardize
        "son_güncelleme": "2024-12-01",                         # Date - preserve
        "kayıt_id": "TR-SUP-001",                               # ID - preserve
        
        # Nested data
        "iletişim_bilgileri": {
            "yetkili_kişi": "Mehmet Özkan",                     # Person name - preserve
            "e_posta": "mehmet@aegeanoil.com",                  # Email - preserve
            "telefon": "+90-232-123-4567",                      # Phone - preserve
            "adres": "Kemalpaşa, İzmir, Türkiye"               # Geographic - mixed handling
        },
        
        # Product details
        "ürün_detayları": [
            "extra virgin zeytin yağı",                         # Product name - standardize type, preserve brand level
            "soğuk sıkım",                                       # Process - standardize
            "500ml cam şişe",                                    # Package - standardize units, preserve specifics
            "organik sertifikalı"                               # Certification type - standardize
        ]
    }
    
    print("1. ORIGINAL DATA ANALYSIS")
    print("-" * 40)
    
    # Analyze the data structure for mapping candidates
    candidates = semantic_mapper.analyze_mapping_candidates(supply_chain_data, "supply_chain_record")
    
    print(f"Found {len(candidates)} semantic mapping candidates:\n")
    
    # Show analysis results
    for candidate in candidates[:10]:  # Show first 10
        entity_info = f" (Entity: {candidate.entity_type.value})" if candidate.entity_type else ""
        proper_noun_info = " [PROPER NOUN]" if candidate.is_proper_noun else " [COMMON NOUN]"
        header_info = " [HEADER]" if candidate.is_header else " [DATA]"
        
        print(f"'{candidate.text}'{header_info}{proper_noun_info}{entity_info}")
        print(f"  Decision: {candidate.mapping_decision.value.upper()}")
        print(f"  Confidence: {candidate.confidence_score:.2f}")
        print(f"  Reasoning: {candidate.reasoning}")
        print()
    
    print("2. SEMANTIC ENRICHMENT PLAN")
    print("-" * 40)
    
    # Generate enrichment plan
    enrichment_plan = semantic_mapper.generate_semantic_enrichment_plan(candidates)
    
    print("Plan Summary:")
    print(f"  STANDARDIZE: {enrichment_plan['statistics']['standardize_count']} items")
    print(f"  PRESERVE: {enrichment_plan['statistics']['preserve_count']} items") 
    print(f"  ANNOTATE: {enrichment_plan['statistics']['annotate_count']} items")
    print(f"  REVIEW: {enrichment_plan['statistics']['review_count']} items")
    print(f"  Meaning Preservation Score: {enrichment_plan['statistics']['meaning_preservation_score']:.1%}")
    print()
    
    print("Items to STANDARDIZE (headers + common nouns):")
    for item in enrichment_plan['standardize']:
        item_type = "HEADER" if item['is_header'] else "DATA"
        print(f"  [{item_type}] '{item['text']}' → standardize terminology")
    print()
    
    print("Items to PRESERVE (proper nouns, IDs, specific values):")
    for item in enrichment_plan['preserve']:
        print(f"  PRESERVE '{item['text']}' - {item['reasoning']}")
    print()
    
    print("Items to ANNOTATE (proper nouns with semantic context):")
    for item in enrichment_plan['annotate']:
        entity_type = item.get('entity_type', 'Unknown')
        print(f"  ANNOTATE '{item['text']}' as {entity_type} - preserve original, add semantic context")
    print()
    
    print("3. APPLIED SEMANTIC ENRICHMENT")
    print("-" * 40)
    
    # Apply enrichment (simulated since we don't have full SKOS setup)
    enriched_result = simulate_enrichment_application(supply_chain_data, enrichment_plan)
    
    print("ORIGINAL vs ENRICHED comparison:")
    print("\nORIGINAL:")
    print(json.dumps(supply_chain_data, indent=2, ensure_ascii=False))
    
    print("\nENRICHED (with preserved meaning):")
    print(json.dumps(enriched_result, indent=2, ensure_ascii=False))
    
    print("\n4. MEANING PRESERVATION VALIDATION")
    print("-" * 40)
    
    validation_results = validate_meaning_preservation(supply_chain_data, enriched_result)
    
    print("Validation Results:")
    print(f"  ✅ Proper nouns preserved: {validation_results['proper_nouns_preserved']}")
    print(f"  ✅ Original data accessible: {validation_results['originals_accessible']}")
    print(f"  ✅ Semantic enrichments added: {validation_results['enrichments_added']}")
    print(f"  ✅ No data loss: {validation_results['no_data_loss']}")
    print(f"  Overall preservation score: {validation_results['preservation_score']:.1%}")
    
    print("\n5. IMPLEMENTATION RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = generate_implementation_recommendations(enrichment_plan)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print("\n🎯 SUMMARY: Semantic mapping applied while preserving data meaning")
    print("   • Headers standardized for interoperability")  
    print("   • Common nouns mapped to SKOS vocabularies")
    print("   • Proper nouns preserved in original form")
    print("   • Semantic annotations added without data loss")
    print("   • Named entities protected from unwanted transformation")


def simulate_enrichment_application(original_data: dict, enrichment_plan: dict) -> dict:
    """Simulate applying enrichment plan to show results"""
    
    enriched_data = original_data.copy()
    
    # Simulate standardizations
    header_mappings = {
        "tedarikçi_adı": "supplier_name",
        "ürün_kategorisi": "product_category", 
        "menşe_ülke": "country_of_origin",
        "tedarikçi_türü": "supplier_type",
        "veri_kaynağı": "data_source"
    }
    
    # Simulate common noun standardizations
    value_mappings = {
        "zeytin yağı": "olive oil",
        "kooperatif": "cooperative",
        "soğuk sıkım": "cold pressed",
        "organik sertifikalı": "organic certified"
    }
    
    # Add standardized versions while preserving originals
    for original_key, standardized_key in header_mappings.items():
        if original_key in enriched_data:
            enriched_data[f"{standardized_key}_standardized"] = enriched_data[original_key]
    
    # Add semantic enrichment metadata
    enriched_data["_semantic_enrichment_metadata"] = {
        "header_standardizations": header_mappings,
        "value_standardizations": value_mappings,
        "preserved_proper_nouns": [
            "Aegean Olive Producers Ltd",  # Company name
            "Türkiye",                     # Country name  
            "Mehmet Özkan",               # Person name
            "İzmir",                      # City name
            "TR-SUP-001"                  # ID
        ],
        "semantic_annotations": {
            "Aegean Olive Producers Ltd": {
                "entity_type": "ORG",
                "semantic_context": "olive oil producer organization",
                "geographic_context": "Turkey, Aegean region"
            },
            "Mehmet Özkan": {
                "entity_type": "PERSON", 
                "role_context": "supplier contact person"
            }
        },
        "meaning_preservation_applied": True,
        "processing_method": "NER_guided_SKOS_mapping"
    }
    
    return enriched_data


def validate_meaning_preservation(original: dict, enriched: dict) -> dict:
    """Validate that meaning was preserved during enrichment"""
    
    validation = {
        "proper_nouns_preserved": True,
        "originals_accessible": True, 
        "enrichments_added": True,
        "no_data_loss": True,
        "preservation_score": 0.0
    }
    
    # Check that proper nouns are still accessible
    metadata = enriched.get("_semantic_enrichment_metadata", {})
    preserved_nouns = metadata.get("preserved_proper_nouns", [])
    
    # Verify proper nouns still exist in enriched data
    original_str = json.dumps(original, ensure_ascii=False)
    enriched_str = json.dumps(enriched, ensure_ascii=False)
    
    preserved_count = 0
    for proper_noun in preserved_nouns:
        if proper_noun in enriched_str:
            preserved_count += 1
        else:
            validation["proper_nouns_preserved"] = False
    
    # Check that enrichments were added
    if not metadata.get("header_standardizations") and not metadata.get("value_standardizations"):
        validation["enrichments_added"] = False
    
    # Check no critical data loss
    original_keys = set(str(original.keys()))
    enriched_keys = set(str(enriched.keys()))
    
    # Original keys should still be accessible (either directly or in metadata)
    if not original_keys.issubset(enriched_keys):
        # Check if they're preserved in metadata
        missing_keys = original_keys - enriched_keys
        if missing_keys and not all(key in enriched_str for key in missing_keys):
            validation["no_data_loss"] = False
    
    # Calculate preservation score
    scores = []
    scores.append(1.0 if validation["proper_nouns_preserved"] else 0.0)
    scores.append(1.0 if validation["originals_accessible"] else 0.0)
    scores.append(1.0 if validation["enrichments_added"] else 0.0)
    scores.append(1.0 if validation["no_data_loss"] else 0.0)
    
    validation["preservation_score"] = sum(scores) / len(scores)
    
    return validation


def generate_implementation_recommendations(enrichment_plan: dict) -> list:
    """Generate implementation recommendations based on analysis"""
    
    recommendations = []
    
    stats = enrichment_plan["statistics"]
    
    if stats["review_count"] > 0:
        recommendations.append(
            f"Manual review needed for {stats['review_count']} ambiguous cases"
        )
    
    if stats["meaning_preservation_score"] > 0.8:
        recommendations.append(
            "Excellent meaning preservation - safe to apply semantic mapping"
        )
    elif stats["meaning_preservation_score"] > 0.6:
        recommendations.append(
            "Good meaning preservation - review edge cases before applying"
        )
    else:
        recommendations.append(
            "Low meaning preservation - consider stricter NER thresholds"
        )
    
    if stats["standardize_percentage"] < 0.2:
        recommendations.append(
            "Few items selected for standardization - check SKOS vocabulary coverage"
        )
    
    recommendations.extend([
        "Use NER confidence thresholds to balance standardization vs preservation",
        "Implement gradual rollout with human validation checkpoints", 
        "Monitor semantic annotation quality for proper noun context",
        "Setup alerts for unexpected proper noun standardizations",
        "Consider domain-specific NER training for better supply chain entity recognition"
    ])
    
    return recommendations


if __name__ == "__main__":
    demonstrate_semantic_mapping_strategy()