#!/usr/bin/env python3
"""
Debug the collector line by line to find the exact issue
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List, Any
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def debug_collector_parsing_step_by_step():
    """Replicate the exact collector logic step by step"""
    
    print("🔍 Debugging Collector Parsing Step by Step")
    print("=" * 60)
    
    # Exact same setup as USGSSemanticCollector
    default_sites = [
        "05331000",  # Mississippi River at St. Paul, MN
        "05420500",  # Mississippi River at Clinton, IA  
        "05587450",  # Mississippi River below Alton, IL
        "07010000",  # Mississippi River at St. Louis, MO
        "07289000",  # Mississippi River at Vicksburg, MS
        "07373420",  # Mississippi River near St. Francisville, LA
        "07374000",  # Mississippi River at Baton Rouge, LA
        "07374525",  # Mississippi River at Belle Chasse, LA
    ]
    
    base_url = "https://waterdata.usgs.gov/nwis/iv"
    parameter_codes = ["00065", "00060", "00010"]  # Stage, discharge, temperature
    
    raw_records = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Build USGS API request - EXACT same as collector
        params = {
            "sites": ",".join(default_sites),
            "parameterCd": ",".join(parameter_codes), 
            "period": "P1D",  # Last 24 hours
            "format": "json"
        }
        
        print(f"Making request to: {base_url}")
        print(f"With params: {params}")
        print()
        
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            
            print(f"Response status: {response.status_code}")
            print(f"Response content-type: {response.headers.get('content-type')}")
            
            response_text = response.text
            print(f"Response text length: {len(response_text)}")
            
            try:
                data = response.json()
                print(f"✅ JSON parsing successful")
            except json.JSONDecodeError as json_err:
                print(f"❌ JSON decode failed: {json_err}")
                return "json_error"
            
            # Ensure data is a dictionary - EXACT same check as collector
            if not isinstance(data, dict):
                print(f"❌ Expected dict, got {type(data)}")
                return "not_dict"
            
            print(f"✅ Data is dict with keys: {list(data.keys())}")
            
            # EXACT same check as collector line 154
            if "value" in data and "timeSeries" in data["value"]:
                time_series_list = data["value"]["timeSeries"]
                print(f"✅ Found timeSeries with {len(time_series_list)} entries")
                
                # EXACT same loop as collector line 155
                for ts_index, time_series in enumerate(time_series_list):
                    print(f"\n--- Processing time_series {ts_index} ---")
                    
                    # EXACT same validation as collector line 157
                    if not isinstance(time_series, dict):
                        print(f"❌ Skipping invalid time_series (type: {type(time_series)})")
                        continue
                    
                    print(f"time_series keys: {list(time_series.keys())}")
                    
                    # EXACT same line as collector line 162 
                    site_info = time_series.get("sourceInfo", {})
                    print(f"site_info type: {type(site_info)}")
                    
                    # EXACT same validation as collector line 163
                    if not isinstance(site_info, dict):
                        print(f"❌ Invalid sourceInfo type: {type(site_info)}")
                        continue
                    
                    print(f"site_info keys: {list(site_info.keys())}")
                    
                    # EXACT same logic as collector line 167 - THIS IS THE SUSPICIOUS LINE
                    print(f"\n🔍 CRITICAL PARSING LINE 167:")
                    site_code_raw = site_info.get("siteCode", [])
                    print(f"  site_info.get('siteCode', []) = {site_code_raw}")
                    print(f"  Type: {type(site_code_raw)}")
                    
                    if isinstance(site_code_raw, list) and len(site_code_raw) > 0:
                        site_code_first = site_code_raw[0]
                        print(f"  site_code_raw[0] = {site_code_first}")
                        print(f"  Type: {type(site_code_first)}")
                        
                        # THIS IS THE PROBLEMATIC CALL - line 167 original code:
                        # site_code = site_info.get("siteCode", [{}])[0].get("value", "")
                        
                        if isinstance(site_code_first, dict):
                            site_code = site_code_first.get("value", "")
                            print(f"  ✅ site_code_first.get('value', '') = '{site_code}'")
                        elif isinstance(site_code_first, str):
                            print(f"  ❌ FOUND THE ISSUE! site_code_first is a STRING: '{site_code_first}'")
                            print(f"     Trying to call .get() on string would fail!")
                            try:
                                # This would cause the error
                                bad_call = site_code_first.get("value", "")
                            except AttributeError as e:
                                print(f"     ✅ CONFIRMED ERROR: {e}")
                                return "found_string_get_error"
                        else:
                            print(f"  ❌ Unexpected type: {type(site_code_first)}")
                            return "unexpected_type"
                    else:
                        print(f"  ❌ siteCode not a non-empty list")
                    
                    # Continue with variable info - EXACT same logic as collector line 169
                    print(f"\n🔍 CHECKING VARIABLE INFO:")
                    variable_info = time_series.get("variable", {})
                    print(f"  variable_info type: {type(variable_info)}")
                    
                    if not isinstance(variable_info, dict):
                        print(f"  ❌ Invalid variable info type: {type(variable_info)}")
                        continue
                    
                    # EXACT same logic as collector line 174 - ANOTHER SUSPICIOUS LINE
                    variable_code_raw = variable_info.get("variableCode", [])
                    print(f"  variable_info.get('variableCode', []) = {variable_code_raw}")
                    print(f"  Type: {type(variable_code_raw)}")
                    
                    if isinstance(variable_code_raw, list) and len(variable_code_raw) > 0:
                        variable_code_first = variable_code_raw[0]
                        print(f"  variable_code_raw[0] = {variable_code_first}")
                        print(f"  Type: {type(variable_code_first)}")
                        
                        if isinstance(variable_code_first, dict):
                            param_code = variable_code_first.get("value", "")
                            print(f"  ✅ param_code = '{param_code}'")
                        elif isinstance(variable_code_first, str):
                            print(f"  ❌ ANOTHER STRING ISSUE! variable_code_first is: '{variable_code_first}'")
                            return "found_variable_string_error"
                        else:
                            print(f"  ❌ Unexpected variable code type: {type(variable_code_first)}")
                    
                    # Continue with a few values to check the pattern
                    values_data = time_series.get("values", [])
                    if isinstance(values_data, list) and len(values_data) > 0:
                        values_array = values_data[0].get("value", []) if isinstance(values_data[0], dict) else []
                        print(f"  Found {len(values_array)} value entries")
                        
                        # Process first few values
                        for val_idx, value_entry in enumerate(values_array[:3]):  # Just first 3
                            if isinstance(value_entry, dict):
                                val = value_entry.get("value", "")
                                dt = value_entry.get("dateTime", "")
                                print(f"    Value {val_idx}: {val} at {dt}")
                            else:
                                print(f"    ❌ Value {val_idx} is {type(value_entry)}, not dict")
                
                print(f"\n✅ Processed all {len(time_series_list)} time series without string .get() errors")
                return "success"
                
            else:
                print(f"❌ No value.timeSeries found")
                return "no_timeseries"
                
        except Exception as e:
            print(f"❌ Exception during processing: {e}")
            import traceback
            traceback.print_exc()
            return "processing_error"

if __name__ == "__main__":
    async def main():
        result = await debug_collector_parsing_step_by_step()
        print(f"\n🎯 Final result: {result}")
    
    asyncio.run(main())