#!/usr/bin/env python3
"""
Debug USGS API Response Issue
Isolate and identify the exact parsing problem
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
import httpx

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def debug_usgs_api():
    """Debug the exact USGS API response structure"""
    
    print("🔍 USGS API Debug Session")
    print("=" * 50)
    
    # USGS API parameters (single site for simplicity)
    base_url = "https://waterdata.usgs.gov/nwis/iv"
    params = {
        "sites": "05331000",  # Single site: Mississippi River at St. Paul, MN
        "parameterCd": "00065,00060",  # Stage and discharge only
        "period": "PT1H",  # Last 1 hour (smaller dataset)
        "format": "json"
    }
    
    print(f"API URL: {base_url}")
    print(f"Parameters: {params}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(base_url, params=params)
            
            print(f"Response Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {response.headers.get('content-length')}")
            print()
            
            # Get raw response text
            response_text = response.text
            print(f"Raw Response (first 500 chars):")
            print("-" * 30)
            print(response_text[:500])
            print("-" * 30)
            print()
            
            # Try to parse JSON
            print("🔍 JSON Parsing Test:")
            try:
                data = response.json()
                print(f"✅ JSON parsing successful")
                print(f"Data type: {type(data)}")
                print(f"Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print()
                
                # Examine structure step by step
                print("🔍 Structure Analysis:")
                
                if isinstance(data, dict):
                    # Check for 'value' key
                    if "value" in data:
                        value_data = data["value"]
                        print(f"✅ Found 'value' key, type: {type(value_data)}")
                        
                        # Check for 'timeSeries' in value
                        if isinstance(value_data, dict) and "timeSeries" in value_data:
                            time_series_data = value_data["timeSeries"]
                            print(f"✅ Found 'timeSeries' key, type: {type(time_series_data)}")
                            print(f"Number of time series: {len(time_series_data) if isinstance(time_series_data, list) else 'Not a list'}")
                            
                            # Examine first time series entry
                            if isinstance(time_series_data, list) and len(time_series_data) > 0:
                                first_ts = time_series_data[0]
                                print(f"First time series type: {type(first_ts)}")
                                
                                if isinstance(first_ts, dict):
                                    print(f"First time series keys: {list(first_ts.keys())}")
                                    
                                    # Check sourceInfo
                                    if "sourceInfo" in first_ts:
                                        source_info = first_ts["sourceInfo"]
                                        print(f"sourceInfo type: {type(source_info)}")
                                        
                                        if isinstance(source_info, dict):
                                            print(f"sourceInfo keys: {list(source_info.keys())}")
                                            
                                            # Check siteCode structure
                                            if "siteCode" in source_info:
                                                site_code = source_info["siteCode"]
                                                print(f"siteCode type: {type(site_code)}")
                                                print(f"siteCode content: {site_code}")
                                                
                                                # This is where the error might occur
                                                if isinstance(site_code, list) and len(site_code) > 0:
                                                    site_code_entry = site_code[0]
                                                    print(f"First siteCode entry type: {type(site_code_entry)}")
                                                    print(f"First siteCode entry: {site_code_entry}")
                                                    
                                                    if isinstance(site_code_entry, dict):
                                                        value = site_code_entry.get("value", "")
                                                        print(f"✅ Successfully extracted site code: {value}")
                                                    else:
                                                        print(f"❌ ERROR: siteCode[0] is not a dict, it's {type(site_code_entry)}")
                                                        print(f"Content: {site_code_entry}")
                                                        return "siteCode_entry_not_dict"
                                                else:
                                                    print(f"❌ ERROR: siteCode is not a non-empty list")
                                                    print(f"siteCode: {site_code}")
                                                    return "siteCode_not_list"
                                            else:
                                                print(f"❌ ERROR: No 'siteCode' in sourceInfo")
                                                return "no_siteCode"
                                        else:
                                            print(f"❌ ERROR: sourceInfo is not a dict, it's {type(source_info)}")
                                            print(f"sourceInfo content: {source_info}")
                                            return "sourceInfo_not_dict"
                                    else:
                                        print(f"❌ ERROR: No 'sourceInfo' in first time series")
                                        return "no_sourceInfo"
                                else:
                                    print(f"❌ ERROR: First time series is not a dict, it's {type(first_ts)}")
                                    print(f"Content: {first_ts}")
                                    return "timeSeries_entry_not_dict"
                            else:
                                print(f"❌ ERROR: timeSeries is empty or not a list")
                                return "timeSeries_empty"
                        else:
                            print(f"❌ ERROR: No 'timeSeries' in value data or value is not a dict")
                            print(f"value keys: {list(value_data.keys()) if isinstance(value_data, dict) else 'Not a dict'}")
                            return "no_timeSeries"
                    else:
                        print(f"❌ ERROR: No 'value' key in response")
                        print(f"Available keys: {list(data.keys())}")
                        return "no_value_key"
                else:
                    print(f"❌ ERROR: Response data is not a dict, it's {type(data)}")
                    print(f"Data content: {data}")
                    return "response_not_dict"
                    
                print("✅ Structure analysis completed successfully")
                return "success"
                
            except json.JSONDecodeError as json_err:
                print(f"❌ JSON parsing failed: {json_err}")
                print(f"Response text: {response_text}")
                return "json_decode_error"
                
        except Exception as e:
            print(f"❌ HTTP request failed: {e}")
            return "http_error"

async def test_problematic_line():
    """Test the exact line that's causing the 'str' object has no attribute 'get' error"""
    
    print("\n" + "=" * 50)
    print("🔍 Testing Problematic Code Pattern")
    print("=" * 50)
    
    # Let's test the exact pattern from the code
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                "https://waterdata.usgs.gov/nwis/iv",
                params={
                    "sites": "05331000",
                    "parameterCd": "00065",
                    "period": "PT1H", 
                    "format": "json"
                }
            )
            
            data = response.json()
            
            if "value" in data and "timeSeries" in data["value"]:
                for time_series in data["value"]["timeSeries"]:
                    print(f"time_series type: {type(time_series)}")
                    
                    if not isinstance(time_series, dict):
                        print(f"❌ ERROR: time_series is not a dict!")
                        continue
                    
                    # This is the exact line from the original code (line 162)
                    site_info = time_series.get("sourceInfo", {})
                    print(f"site_info type: {type(site_info)}")
                    print(f"site_info: {site_info}")
                    
                    if not isinstance(site_info, dict):
                        print(f"❌ ERROR: site_info is not a dict!")
                        continue
                    
                    # This is the exact line from the original code (line 167) that might fail
                    site_code_list = site_info.get("siteCode", [])
                    print(f"siteCode list type: {type(site_code_list)}")
                    print(f"siteCode list: {site_code_list}")
                    
                    if isinstance(site_code_list, list) and len(site_code_list) > 0:
                        site_code_entry = site_code_list[0]
                        print(f"site_code_entry type: {type(site_code_entry)}")
                        print(f"site_code_entry: {site_code_entry}")
                        
                        # This is where the error likely occurs - trying to call .get() on a string
                        if isinstance(site_code_entry, str):
                            print(f"❌ FOUND THE ISSUE: siteCode[0] is a STRING, not a dict!")
                            print(f"Attempting to call .get() on string: '{site_code_entry}'")
                            try:
                                # This would cause the error
                                value = site_code_entry.get("value", "")
                                print(f"This line should not execute")
                            except AttributeError as e:
                                print(f"✅ CONFIRMED ERROR: {e}")
                                return "found_string_get_error"
                        elif isinstance(site_code_entry, dict):
                            value = site_code_entry.get("value", "")
                            print(f"✅ Successfully extracted: {value}")
                        else:
                            print(f"❌ Unexpected type for siteCode[0]: {type(site_code_entry)}")
        
        except Exception as e:
            print(f"❌ Error in test: {e}")
            return "test_error"
    
    return "test_completed"

if __name__ == "__main__":
    async def main():
        print("Starting USGS API Debug...")
        
        # Test 1: Full structure analysis
        result1 = await debug_usgs_api()
        print(f"Structure analysis result: {result1}")
        
        # Test 2: Test the specific problematic pattern
        result2 = await test_problematic_line()
        print(f"Problematic line test result: {result2}")
        
        print("\n" + "=" * 50)
        print("🎯 Debug Summary Complete")
        print("=" * 50)
        
    asyncio.run(main())