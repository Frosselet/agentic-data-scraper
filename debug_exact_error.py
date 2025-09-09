#!/usr/bin/env python3
"""
Debug the exact line causing 'str' object has no attribute 'get' error
"""

import asyncio
import httpx
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def debug_exact_parsing_error():
    """Debug the exact line that's failing"""
    
    print("🔍 Debugging Exact Parsing Error")
    print("=" * 50)
    
    # Use the exact same parameters as the collector
    base_url = "https://waterdata.usgs.gov/nwis/iv"
    sites = ["05331000"]
    parameter_codes = ["00065", "00060", "00010"]
    
    params = {
        "sites": ",".join(sites),
        "parameterCd": ",".join(parameter_codes),
        "period": "P1D",  # Last 24 hours (same as collector)
        "format": "json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Got response, status: {response.status_code}")
            print(f"Data structure valid: {isinstance(data, dict)}")
            
            if "value" in data and "timeSeries" in data["value"]:
                time_series_list = data["value"]["timeSeries"]
                print(f"Number of time series: {len(time_series_list)}")
                
                for i, time_series in enumerate(time_series_list):
                    print(f"\n--- Processing time_series {i} ---")
                    print(f"time_series type: {type(time_series)}")
                    
                    if not isinstance(time_series, dict):
                        print(f"❌ ERROR: time_series is not a dict!")
                        continue
                    
                    print(f"time_series keys: {list(time_series.keys())}")
                    
                    # The exact line from the collector (line 162)
                    site_info = time_series.get("sourceInfo", {})
                    print(f"site_info type: {type(site_info)}")
                    
                    if not isinstance(site_info, dict):
                        print(f"❌ ERROR: sourceInfo is not dict, it's {type(site_info)}")
                        continue
                    
                    print(f"site_info keys: {list(site_info.keys())}")
                    
                    # The exact line from the collector (line 167)
                    site_code_data = site_info.get("siteCode", [])
                    print(f"siteCode data type: {type(site_code_data)}")
                    print(f"siteCode data: {site_code_data}")
                    
                    if isinstance(site_code_data, list) and len(site_code_data) > 0:
                        site_code_entry = site_code_data[0]
                        print(f"First siteCode entry type: {type(site_code_entry)}")
                        print(f"First siteCode entry content: {site_code_entry}")
                        
                        # This is the problematic line - line 167 in the collector
                        # site_code = site_info.get("siteCode", [{}])[0].get("value", "")
                        
                        if isinstance(site_code_entry, dict):
                            value = site_code_entry.get("value", "")
                            print(f"✅ Successfully extracted site code: {value}")
                        else:
                            print(f"❌ FOUND THE ISSUE: Trying to call .get() on {type(site_code_entry)}")
                            print(f"Content: {site_code_entry}")
                            
                            # This would be the error
                            try:
                                value = site_code_entry.get("value", "")
                                print("This should not work")
                            except AttributeError as e:
                                print(f"✅ CONFIRMED ERROR: {e}")
                                return "found_exact_error"
                    
                    # Check variable info too
                    print(f"\n--- Checking variable info for time_series {i} ---")
                    variable_info = time_series.get("variable", {})
                    print(f"variable_info type: {type(variable_info)}")
                    
                    if isinstance(variable_info, dict):
                        variable_code_data = variable_info.get("variableCode", [])
                        print(f"variableCode data type: {type(variable_code_data)}")
                        print(f"variableCode data: {variable_code_data}")
                        
                        if isinstance(variable_code_data, list) and len(variable_code_data) > 0:
                            variable_code_entry = variable_code_data[0]
                            print(f"First variableCode entry type: {type(variable_code_entry)}")
                            
                            if isinstance(variable_code_entry, dict):
                                param_value = variable_code_entry.get("value", "")
                                print(f"✅ Successfully extracted param code: {param_value}")
                            else:
                                print(f"❌ ISSUE: variableCode entry is {type(variable_code_entry)}")
                                return "variable_code_issue"
                    
                    # Check values data
                    print(f"\n--- Checking values data for time_series {i} ---")
                    values_data = time_series.get("values", [])
                    print(f"values_data type: {type(values_data)}")
                    print(f"values_data length: {len(values_data) if isinstance(values_data, list) else 'not a list'}")
                    
                    if isinstance(values_data, list) and len(values_data) > 0:
                        first_values = values_data[0]
                        print(f"First values entry type: {type(first_values)}")
                        
                        if isinstance(first_values, dict):
                            values_array = first_values.get("value", [])
                            print(f"values_array type: {type(values_array)}")
                            print(f"values_array length: {len(values_array) if isinstance(values_array, list) else 'not a list'}")
                            
                            if isinstance(values_array, list) and len(values_array) > 0:
                                first_value_entry = values_array[0]
                                print(f"First value entry type: {type(first_value_entry)}")
                                
                                if isinstance(first_value_entry, dict):
                                    value = first_value_entry.get("value", "")
                                    datetime_val = first_value_entry.get("dateTime", "")
                                    print(f"✅ Successfully extracted measurement: {value} at {datetime_val}")
                                else:
                                    print(f"❌ ISSUE: value entry is {type(first_value_entry)}")
                                    return "value_entry_issue"
            
            print("\n✅ All parsing completed successfully - no 'str' object errors found")
            return "success"
            
        except Exception as e:
            print(f"❌ Error in debugging: {e}")
            import traceback
            traceback.print_exc()
            return "debug_error"

if __name__ == "__main__":
    async def main():
        result = await debug_exact_parsing_error()
        print(f"\nDebug result: {result}")
    
    asyncio.run(main())