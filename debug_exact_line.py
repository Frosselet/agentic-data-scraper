#!/usr/bin/env python3
"""
Add specific debug logging to catch the exact line causing the error
"""

import asyncio
import sys
import logging
from pathlib import Path
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def debug_extract_raw_data():
    """Debug the exact line in extract_raw_data that's failing"""
    
    print("🔍 Debugging extract_raw_data with detailed logging")
    print("=" * 60)
    
    try:
        from agentic_data_scraper.collectors.usgs_collector import USGSSemanticCollector
        
        # Initialize collector
        collector = USGSSemanticCollector(
            kuzu_temp_db="./debug_usgs.kuzu",
            sites=["05331000"]  # Single site for testing
        )
        
        print("✅ Collector initialized")
        
        # Monkey patch the extract method to add debug output
        original_extract = collector.extract_raw_data
        
        async def debug_extract_wrapper():
            print("\n🔍 Starting extract_raw_data execution...")
            try:
                result = await original_extract()
                print(f"✅ extract_raw_data completed successfully with {len(result)} records")
                return result
            except Exception as e:
                print(f"❌ extract_raw_data failed with error: {e}")
                print(f"Error type: {type(e)}")
                print("Full traceback:")
                traceback.print_exc()
                raise e
        
        # Replace with debug version
        collector.extract_raw_data = debug_extract_wrapper
        
        # Test the extraction
        result = await collector.extract_raw_data()
        print(f"Final result: {len(result)} records")
        
        if result and result[0].get("collection_method") == "real_time_api":
            print("✅ Successfully used real API data!")
        else:
            print("⚠️  Fell back to mock data")
        
        return "success"
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        traceback.print_exc()
        return "failed"

if __name__ == "__main__":
    async def main():
        result = await debug_extract_raw_data()
        print(f"\nDebug result: {result}")
    
    asyncio.run(main())