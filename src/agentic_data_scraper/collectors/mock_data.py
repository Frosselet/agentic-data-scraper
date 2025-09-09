"""
Mock Data Generator for Mississippi River Navigation System
Generates realistic vessel, weather, and market data for demonstration
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import math

class MockDataGenerator:
    """Generates realistic mock data for Mississippi River navigation demonstrations"""
    
    def __init__(self):
        # Realistic vessel names for inland waterways
        self.vessel_names = [
            "AMERICAN SPIRIT", "GRAIN TRADER", "MISSISSIPPI QUEEN", "RIVER TRANSPORT",
            "CARGO MASTER", "INLAND NAVIGATOR", "BARGE COMMANDER", "COMMERCE STAR",
            "MIGHTY MISSISSIPPI", "RIVER HAWK", "DELTA PRINCESS", "GREAT LAKES TRADER",
            "HARVEST MOON", "COMMODITY EXPRESS", "INLAND EMPIRE", "WATERWAY WARRIOR"
        ]
        
        # Major Mississippi River ports with realistic coordinates
        self.river_ports = {
            "minneapolis": {"lat": 44.9778, "lon": -93.2650, "mile": 847.9, "name": "Minneapolis, MN"},
            "st_paul": {"lat": 44.9537, "lon": -93.0900, "mile": 847.9, "name": "St. Paul, MN"},
            "dubuque": {"lat": 42.5006, "lon": -90.6648, "mile": 647.9, "name": "Dubuque, IA"},
            "davenport": {"lat": 41.5236, "lon": -90.5776, "mile": 518.0, "name": "Davenport, IA"},
            "st_louis": {"lat": 38.6270, "lon": -90.1994, "mile": 180.0, "name": "St. Louis, MO"},
            "cape_girardeau": {"lat": 37.3059, "lon": -89.5181, "mile": 55.0, "name": "Cape Girardeau, MO"},
            "memphis": {"lat": 35.1495, "lon": -90.0490, "mile": 734.8, "name": "Memphis, TN"},
            "vicksburg": {"lat": 32.3526, "lon": -90.8779, "mile": 435.7, "name": "Vicksburg, MS"},
            "baton_rouge": {"lat": 30.4515, "lon": -91.1871, "mile": 228.4, "name": "Baton Rouge, LA"},
            "new_orleans": {"lat": 29.9511, "lon": -90.0715, "mile": 90.0, "name": "New Orleans, LA"}
        }
        
        # Vessel types with AIS codes
        self.vessel_types = {
            31: {"name": "Towing vessel", "category": "towboat", "typical_speed": 8},
            32: {"name": "Towing vessel", "category": "towboat", "typical_speed": 8},
            70: {"name": "Cargo vessel", "category": "cargo", "typical_speed": 10},
            71: {"name": "Hazardous cargo", "category": "hazmat", "typical_speed": 9},
            80: {"name": "Tanker", "category": "tanker", "typical_speed": 9}
        }
        
        # Commodity types for cargo estimation
        self.commodities = [
            "corn", "soybeans", "wheat", "coal", "petroleum", "fertilizer", 
            "steel", "sand", "gravel", "chemicals", "containers"
        ]
        
    def generate_mock_ais_data(self, vessel_count: int = 25) -> List[Dict[str, Any]]:
        """Generate mock AIS vessel data for Mississippi River system"""
        
        vessels = []
        
        for i in range(vessel_count):
            # Generate realistic vessel
            mmsi = f"36{random.randint(7000000, 7999999)}"  # US MMSI range
            vessel_name = random.choice(self.vessel_names)
            vessel_type = random.choice(list(self.vessel_types.keys()))
            
            # Generate position along Mississippi River
            origin_port = random.choice(list(self.river_ports.values()))
            dest_port = random.choice(list(self.river_ports.values()))
            
            # Interpolate position between origin and destination
            progress = random.uniform(0.1, 0.9)
            lat = origin_port["lat"] + (dest_port["lat"] - origin_port["lat"]) * progress
            lon = origin_port["lon"] + (dest_port["lon"] - origin_port["lon"]) * progress
            
            # Add some realistic variation to position
            lat += random.uniform(-0.05, 0.05)
            lon += random.uniform(-0.05, 0.05)
            
            # Generate realistic vessel characteristics
            vessel_info = self.vessel_types[vessel_type]
            base_speed = vessel_info["typical_speed"]
            speed = max(0, base_speed + random.uniform(-2, 3))
            heading = random.randint(0, 359)
            
            # Generate realistic vessel dimensions
            if vessel_type in [31, 32]:  # Towboats
                length = random.randint(35, 60)
                width = random.randint(10, 15)
                draught = random.uniform(2.5, 4.5)
            else:  # Cargo vessels
                length = random.randint(150, 300)
                width = random.randint(20, 35)
                draught = random.uniform(3.0, 8.0)
            
            # Navigation status
            nav_statuses = [0, 1, 5, 8]  # underway, anchored, moored, sailing
            nav_status = random.choice(nav_statuses)
            
            # Generate timestamp (recent)
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, 30))
            
            vessel_data = {
                "mmsi": mmsi,
                "imo": f"IMO{random.randint(1000000, 9999999)}",
                "shipname": vessel_name,
                "callsign": f"W{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000, 9999)}",
                "shiptype": vessel_type,
                "length": length,
                "width": width,
                "draught": round(draught, 1),
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "sog": round(speed, 1),  # Speed over ground
                "cog": heading,         # Course over ground
                "heading": heading,
                "navstat": nav_status,
                "destination": dest_port["name"],
                "eta": (datetime.now() + timedelta(hours=random.randint(6, 72))).isoformat(),
                "timestamp": timestamp.isoformat(),
                "last_pos_update": timestamp.isoformat()
            }
            
            vessels.append(vessel_data)
        
        return vessels
    
    def generate_mock_usgs_data(self, sites: List[str]) -> Dict[str, Any]:
        """Generate mock USGS water data"""
        
        # Site information for major Mississippi River gauges
        site_info = {
            "05331000": {
                "name": "MISSISSIPPI RIVER AT ST. PAUL, MN",
                "lat": 44.9537, "lon": -93.0900, "river_mile": 847.9
            },
            "05420500": {
                "name": "MISSISSIPPI RIVER AT CLINTON, IA", 
                "lat": 41.5236, "lon": -90.5776, "river_mile": 518.0
            },
            "07010000": {
                "name": "MISSISSIPPI RIVER AT ST. LOUIS, MO",
                "lat": 38.6270, "lon": -90.1994, "river_mile": 180.0
            },
            "07289000": {
                "name": "MISSISSIPPI RIVER AT VICKSBURG, MS",
                "lat": 32.3526, "lon": -90.8779, "river_mile": 435.7
            },
            "07374000": {
                "name": "MISSISSIPPI RIVER AT BATON ROUGE, LA",
                "lat": 30.4515, "lon": -91.1871, "river_mile": 228.4
            }
        }
        
        time_series = []
        
        for site_code in sites:
            if site_code not in site_info:
                continue
                
            site = site_info[site_code]
            
            # Generate realistic water level data
            base_stage = random.uniform(8, 25)  # feet
            stage_values = []
            
            # Generate 24 hours of hourly data
            for hour in range(24):
                timestamp = datetime.now() - timedelta(hours=23-hour)
                
                # Add realistic variation
                stage = base_stage + random.uniform(-2, 2)
                stage = max(2.0, stage)  # Minimum stage
                
                stage_values.append({
                    "value": f"{stage:.2f}",
                    "dateTime": timestamp.isoformat(),
                    "qualifiers": [{"qualifierCode": "A"}]
                })
            
            # Generate discharge data
            base_discharge = random.uniform(50000, 300000)  # cfs
            discharge_values = []
            
            for hour in range(24):
                timestamp = datetime.now() - timedelta(hours=23-hour)
                discharge = base_discharge + random.uniform(-20000, 20000)
                discharge = max(10000, discharge)  # Minimum discharge
                
                discharge_values.append({
                    "value": f"{discharge:.0f}",
                    "dateTime": timestamp.isoformat(), 
                    "qualifiers": [{"qualifierCode": "A"}]
                })
            
            # Water level time series
            time_series.append({
                "sourceInfo": {
                    "siteName": site["name"],
                    "siteCode": [{"value": site_code}],
                    "geoLocation": {
                        "geogLocation": {
                            "latitude": site["lat"],
                            "longitude": site["lon"]
                        }
                    }
                },
                "variable": {
                    "variableName": "Gage height, ft",
                    "variableCode": [{"value": "00065"}]
                },
                "values": [{"value": stage_values}]
            })
            
            # Discharge time series  
            time_series.append({
                "sourceInfo": {
                    "siteName": site["name"],
                    "siteCode": [{"value": site_code}],
                    "geoLocation": {
                        "geogLocation": {
                            "latitude": site["lat"],
                            "longitude": site["lon"]
                        }
                    }
                },
                "variable": {
                    "variableName": "Discharge, cubic feet per second",
                    "variableCode": [{"value": "00060"}]
                },
                "values": [{"value": discharge_values}]
            })
        
        return {
            "value": {
                "timeSeries": time_series
            }
        }
    
    def generate_mock_commodity_data(self) -> List[Dict[str, Any]]:
        """Generate mock USDA commodity price data"""
        
        locations = ["St. Louis, MO", "New Orleans, LA", "Minneapolis, MN", "Memphis, TN", "Baton Rouge, LA"]
        
        price_data = []
        
        for commodity in ["corn", "soybeans", "wheat"]:
            for location in locations:
                # Generate realistic commodity prices
                base_prices = {"corn": 4.50, "soybeans": 12.80, "wheat": 6.20}
                base_price = base_prices[commodity]
                
                # Add location differential
                location_diff = random.uniform(-0.50, 0.50)
                price = base_price + location_diff + random.uniform(-0.25, 0.25)
                
                record = {
                    "commodity_name": commodity.title(),
                    "location_desc": location,
                    "avg_price": round(price, 2),
                    "price_unit": "USD per bushel",
                    "report_date": datetime.now().isoformat(),
                    "report_type": "Daily Cash",
                    "grade": "No. 2"
                }
                
                price_data.append(record)
        
        return {"results": price_data}
    
    def generate_mock_weather_data(self) -> str:
        """Generate mock NOAA weather forecast XML"""
        
        locations = [
            {"name": "St. Louis, MO", "lat": 38.6270, "lon": -90.1994},
            {"name": "Memphis, TN", "lat": 35.1495, "lon": -90.0490},
            {"name": "New Orleans, LA", "lat": 29.9511, "lon": -90.0715}
        ]
        
        xml_forecasts = []
        
        for location in locations:
            stage = random.uniform(10, 30)
            flow = random.uniform(100000, 400000)
            precip = random.uniform(0, 2.5)
            
            forecast = f"""
    <forecast>
        <location>{location['name']}</location>
        <forecast_time>{datetime.now().isoformat()}</forecast_time>
        <valid_time>{(datetime.now() + timedelta(hours=24)).isoformat()}</valid_time>
        <stage>{stage:.1f}</stage>
        <flow>{flow:.0f}</flow>
        <precipitation>{precip:.2f}</precipitation>
    </forecast>"""
            
            xml_forecasts.append(forecast)
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<weather_forecasts>
{''.join(xml_forecasts)}
</weather_forecasts>"""
        
        return xml_content


# Global instance for easy import
mock_generator = MockDataGenerator()