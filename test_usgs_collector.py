#!/usr/bin/env python3
"""
Test USGS Collector to identify actual parsing issue
"""

import asyncio
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_usgs_collector():
    """Test the actual USGS collector"""
    
    print("🔍 Testing USGS Collector")
    print("=" * 50)
    
    try:
        from agentic_data_scraper.collectors.usgs_collector import USGSSemanticCollector
        
        # Initialize collector
        collector = USGSSemanticCollector(
            kuzu_temp_db="./test_usgs.kuzu",
            sites=["05331000"]  # Single site for testing
        )
        
        print("✅ Collector initialized successfully")
        
        # Test just the raw data extraction
        print("\n🔍 Testing extract_raw_data()...")
        try:
            raw_data = await collector.extract_raw_data()
            print(f"✅ extract_raw_data() successful, got {len(raw_data)} records")
            
            if raw_data:
                sample = raw_data[0]
                print(f"Sample record keys: {list(sample.keys())}")
                print(f"Site code: {sample.get('site_code', 'N/A')}")
                print(f"Parameter code: {sample.get('parameter_code', 'N/A')}")
                print(f"Collection method: {sample.get('collection_method', 'N/A')}")
                
                # Check if it's using mock data
                if sample.get("collection_method") == "simulated_real_time_gauge":
                    print("⚠️  Using mock data fallback")
                else:
                    print("✅ Using real API data")
            
            return "success"
            
        except Exception as e:
            print(f"❌ extract_raw_data() failed: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return "extract_failed"
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return "import_failed"
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return "init_failed"

async def test_full_collection():
    """Test the full semantic collection process"""
    
    print("\n" + "=" * 50)
    print("🔍 Testing Full Semantic Collection")
    print("=" * 50)
    
    try:
        from agentic_data_scraper.collectors.usgs_collector import USGSSemanticCollector
        
        # Initialize collector
        collector = USGSSemanticCollector(
            kuzu_temp_db="./test_full_usgs.kuzu",
            sites=["05331000"]  # Single site for testing
        )
        
        print("✅ Collector initialized for full test")
        
        # Test the full semantic collection
        print("\n🔍 Testing collect_semantically_enriched_data()...")
        try:
            enriched_data = await collector.collect_semantically_enriched_data()
            print(f"✅ Full collection successful, got {len(enriched_data)} enriched records")
            
            if enriched_data:
                sample = enriched_data[0]
                print(f"Sample enriched record:")
                print(f"  Source ID: {sample.source_id}")
                print(f"  Record ID: {sample.record_id}")
                print(f"  Timestamp: {sample.timestamp}")
                print(f"  Quality metrics: {sample.quality_metrics}")
            
            return "success"
            
        except Exception as e:
            print(f"❌ Full collection failed: {e}")
            import traceback
            traceback.print_exc()
            return "collection_failed"
            
    except Exception as e:
        print(f"❌ Full test setup failed: {e}")
        return "setup_failed"

if __name__ == "__main__":
    async def main():
        print("Starting USGS Collector Tests...")
        
        # Test 1: Raw data extraction
        result1 = await test_usgs_collector()
        print(f"Raw extraction test result: {result1}")
        
        # Test 2: Full semantic collection
        result2 = await test_full_collection()
        print(f"Full collection test result: {result2}")
        
        print("\n" + "=" * 50)
        print("🎯 USGS Collector Test Summary Complete")
        print("=" * 50)
        
    asyncio.run(main())