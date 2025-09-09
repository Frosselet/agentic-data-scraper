"""
USGS Water Data Collector with Semantic Enrichment
Implements ET(K)L for hydrological data acquisition with real-time semantic processing
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

import httpx
import pandas as pd
from .semantic_collectors import SemanticCollectorBase, SemanticContext, StructuredRecord
from .mock_data import mock_generator

logger = logging.getLogger(__name__)


class USGSSemanticCollector(SemanticCollectorBase):
    """
    USGS Water Data collector with built-in semantic enrichment
    Collects gauge data and applies hydrological ontologies during acquisition
    """
    
    def __init__(self, kuzu_temp_db: str, sites: List[str] = None):
        
        # Define semantic context for USGS hydrological data
        semantic_context = SemanticContext(
            domain="hydrology",
            ontology_uri="http://hydrology.usgs.gov/ontology/",
            primary_concepts=["water_level", "flow_rate", "temperature", "gauge_station"],
            entity_types=["gauge_station", "waterway", "measurement", "location"],
            spatial_context="mississippi_river_system",
            temporal_context="real_time_monitoring",
            unit_mappings={
                "00065": "feet",  # Gauge height
                "00060": "cubic_feet_per_second",  # Discharge
                "00010": "celsius"  # Temperature
            }
        )
        
        super().__init__("usgs_water_data", kuzu_temp_db, semantic_context)
        
        # Mississippi River system gauge stations (major navigation points)
        self.default_sites = [
            "05331000",  # Mississippi River at St. Paul, MN
            "05420500",  # Mississippi River at Clinton, IA  
            "05587450",  # Mississippi River below Alton, IL
            "07010000",  # Mississippi River at St. Louis, MO
            "07289000",  # Mississippi River at Vicksburg, MS
            "07373420",  # Mississippi River near St. Francisville, LA
            "07374000",  # Mississippi River at Baton Rouge, LA
            "07374525",  # Mississippi River at Belle Chasse, LA
        ] if sites is None else sites
        
        self.base_url = "https://waterdata.usgs.gov/nwis/iv"
        self.parameter_codes = ["00065", "00060", "00010"]  # Stage, discharge, temperature
        
    def _initialize_domain_knowledge(self):
        """Initialize USGS-specific hydrological knowledge"""
        
        # USGS parameter code mappings with semantic context
        self.parameter_semantics = {
            "00065": {
                "name": "Gauge Height",
                "concept": "WaterLevel", 
                "ontology_uri": "http://hydrology.usgs.gov/ontology/WaterLevel",
                "unit": "feet",
                "navigation_critical": True,
                "quality_thresholds": {"min": 0, "max": 50, "typical_range": (5, 30)}
            },
            "00060": {
                "name": "Discharge",
                "concept": "FlowRate",
                "ontology_uri": "http://hydrology.usgs.gov/ontology/FlowRate", 
                "unit": "cubic_feet_per_second",
                "navigation_critical": True,
                "quality_thresholds": {"min": 0, "max": 1000000, "typical_range": (1000, 500000)}
            },
            "00010": {
                "name": "Temperature",
                "concept": "WaterTemperature",
                "ontology_uri": "http://hydrology.usgs.gov/ontology/WaterTemperature",
                "unit": "celsius", 
                "navigation_critical": False,
                "quality_thresholds": {"min": -5, "max": 40, "typical_range": (0, 35)}
            }
        }
        
        # Site-specific navigation knowledge
        self.site_navigation_context = {
            "05331000": {"river_mile": 847.9, "navigation_pool": "Pool 1", "lock_dam": "Lock and Dam 1"},
            "05420500": {"river_mile": 518.0, "navigation_pool": "Pool 13", "lock_dam": "Lock and Dam 13"},
            "05587450": {"river_mile": 202.3, "navigation_pool": "Pool 26", "lock_dam": "Lock and Dam 26"},
            "07010000": {"river_mile": 180.0, "navigation_pool": "Open River", "lock_dam": None},
            "07289000": {"river_mile": 435.7, "navigation_pool": "Open River", "lock_dam": None},
            "07373420": {"river_mile": 265.4, "navigation_pool": "Open River", "lock_dam": None},
            "07374000": {"river_mile": 228.4, "navigation_pool": "Open River", "lock_dam": None},
            "07374525": {"river_mile": 73.2, "navigation_pool": "Open River", "lock_dam": None}
        }
        
        # Navigation risk thresholds (site-specific)
        self.navigation_risk_thresholds = {
            "05331000": {"low_water": 4.0, "flood_stage": 14.0, "critical_low": 2.0},
            "05420500": {"low_water": 6.0, "flood_stage": 16.0, "critical_low": 4.0},
            "05587450": {"low_water": 8.0, "flood_stage": 21.0, "critical_low": 6.0},
            "07010000": {"low_water": 10.0, "flood_stage": 30.0, "critical_low": 8.0},
            "07289000": {"low_water": 12.0, "flood_stage": 43.0, "critical_low": 10.0},
            "07373420": {"low_water": 15.0, "flood_stage": 48.0, "critical_low": 12.0},
            "07374000": {"low_water": 18.0, "flood_stage": 35.0, "critical_low": 15.0},
            "07374525": {"low_water": 20.0, "flood_stage": 25.0, "critical_low": 17.0}
        }
    
    async def extract_raw_data(self) -> List[Dict[str, Any]]:
        """
        Extract raw USGS data with semantic awareness
        Real-time API calls with domain knowledge applied during extraction
        """
        
        raw_records = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Build USGS API request
            params = {
                "sites": ",".join(self.default_sites),
                "parameterCd": ",".join(self.parameter_codes),
                "period": "P1D",  # Last 24 hours
                "format": "json"
            }
            
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                # Debug: Check response content type and content
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response content-type: {response.headers.get('content-type')}")
                
                response_text = response.text
                logger.debug(f"Response text (first 200 chars): {response_text[:200]}")
                
                try:
                    data = response.json()
                    logger.debug(f"JSON parsing successful, data type: {type(data)}")
                except json.JSONDecodeError as json_err:
                    logger.error(f"JSON decode failed: {json_err}")
                    logger.error(f"Response text: {response_text[:500]}")
                    raise ValueError(f"Invalid JSON response from USGS API: {json_err}")
                
                # Ensure data is a dictionary
                if not isinstance(data, dict):
                    raise ValueError(f"Expected dict from USGS API, got {type(data)}: {str(data)[:200]}")
                
                logger.debug(f"Data has keys: {list(data.keys())}")
                
                if "value" in data and "timeSeries" in data["value"]:
                    logger.debug(f"Found timeSeries with {len(data['value']['timeSeries'])} entries")
                    for time_series in data["value"]["timeSeries"]:
                        # Validate time_series is a dictionary
                        if not isinstance(time_series, dict):
                            logger.warning(f"Skipping invalid time_series entry (type: {type(time_series)}): {str(time_series)[:100]}")
                            continue
                            
                        # Extract site and parameter information with semantic context
                        site_info = time_series.get("sourceInfo", {})
                        if not isinstance(site_info, dict):
                            logger.warning(f"Invalid sourceInfo type: {type(site_info)}")
                            continue
                            
                        # Extract site code with robust error handling
                        site_code_list = site_info.get("siteCode", [])
                        if isinstance(site_code_list, list) and len(site_code_list) > 0:
                            site_code_entry = site_code_list[0]
                            if isinstance(site_code_entry, dict):
                                site_code = site_code_entry.get("value", "")
                            else:
                                logger.warning(f"Unexpected siteCode entry type: {type(site_code_entry)}, content: {site_code_entry}")
                                site_code = str(site_code_entry) if site_code_entry else ""
                        else:
                            site_code = ""
                        
                        variable_info = time_series.get("variable", {})
                        if not isinstance(variable_info, dict):
                            logger.warning(f"Invalid variable info type: {type(variable_info)}")
                            continue
                            
                        # Extract parameter code with robust error handling
                        variable_code_list = variable_info.get("variableCode", [])
                        if isinstance(variable_code_list, list) and len(variable_code_list) > 0:
                            variable_code_entry = variable_code_list[0]
                            if isinstance(variable_code_entry, dict):
                                param_code = variable_code_entry.get("value", "")
                            else:
                                logger.warning(f"Unexpected variableCode entry type: {type(variable_code_entry)}, content: {variable_code_entry}")
                                param_code = str(variable_code_entry) if variable_code_entry else ""
                        else:
                            param_code = ""
                        
                        # Apply semantic knowledge during extraction
                        site_semantic_context = self._get_site_semantic_context(site_code)
                        param_semantic_context = self._get_parameter_semantic_context(param_code)
                        
                        # Extract values with semantic enrichment
                        values_data = time_series.get("values", [])
                        if not isinstance(values_data, list) or len(values_data) == 0:
                            logger.warning(f"No values data for site {site_code}, param {param_code}")
                            continue
                            
                        values_array = values_data[0].get("value", []) if isinstance(values_data[0], dict) else []
                        
                        for value_entry in values_array:
                            if not isinstance(value_entry, dict):
                                logger.warning(f"Skipping invalid value entry (type: {type(value_entry)})")
                                continue
                            # Build semantically-aware raw record
                            raw_record = {
                                # Core USGS data
                                "site_code": site_code,
                                "site_name": site_info.get("siteName", ""),
                                "parameter_code": param_code,
                                "parameter_name": variable_info.get("variableName", ""),
                                "value": value_entry.get("value", ""),
                                "datetime": value_entry.get("dateTime", ""),
                                # Extract quality code with robust error handling
                                "quality_code": self._extract_quality_code(value_entry),
                                
                                # Geospatial context
                                "latitude": float(site_info.get("geoLocation", {}).get("geogLocation", {}).get("latitude", 0)),
                                "longitude": float(site_info.get("geoLocation", {}).get("geogLocation", {}).get("longitude", 0)),
                                
                                # Semantic context applied during extraction
                                "semantic_site_context": site_semantic_context,
                                "semantic_parameter_context": param_semantic_context,
                                
                                # Navigation context applied immediately
                                "navigation_context": self.site_navigation_context.get(site_code, {}),
                                "risk_thresholds": self.navigation_risk_thresholds.get(site_code, {}),
                                
                                # Data provenance
                                "extraction_timestamp": datetime.now().isoformat(),
                                "data_source_api": self.base_url,
                                "collection_method": "real_time_api"
                            }
                            
                            raw_records.append(raw_record)
                
            except Exception as e:
                logger.error(f"Failed to extract USGS data: {e}")
                logger.info("Falling back to mock USGS data for demonstration")
                return await self._extract_mock_data()
        
        logger.info(f"Extracted {len(raw_records)} raw records with semantic context from USGS")
        return raw_records
    
    async def _extract_mock_data(self) -> List[Dict[str, Any]]:
        """Extract mock USGS data for demonstration purposes"""
        
        raw_records = []
        
        logger.info("Generating mock USGS data for demonstration")
        
        # Generate mock data using the mock generator
        mock_data = mock_generator.generate_mock_usgs_data(self.default_sites)
        
        # Process mock data through the same semantic enrichment pipeline
        if "value" in mock_data and "timeSeries" in mock_data["value"]:
            for time_series in mock_data["value"]["timeSeries"]:
                # Validate time_series is a dictionary
                if not isinstance(time_series, dict):
                    continue
                    
                # Extract site and parameter information with semantic context
                site_info = time_series.get("sourceInfo", {})
                if not isinstance(site_info, dict):
                    continue
                    
                # Extract site code with robust error handling (same as real API)
                site_code_list = site_info.get("siteCode", [])
                if isinstance(site_code_list, list) and len(site_code_list) > 0:
                    site_code_entry = site_code_list[0]
                    if isinstance(site_code_entry, dict):
                        site_code = site_code_entry.get("value", "")
                    else:
                        site_code = str(site_code_entry) if site_code_entry else ""
                else:
                    site_code = ""
                
                variable_info = time_series.get("variable", {})
                if not isinstance(variable_info, dict):
                    continue
                    
                # Extract parameter code with robust error handling (same as real API)
                variable_code_list = variable_info.get("variableCode", [])
                if isinstance(variable_code_list, list) and len(variable_code_list) > 0:
                    variable_code_entry = variable_code_list[0]
                    if isinstance(variable_code_entry, dict):
                        param_code = variable_code_entry.get("value", "")
                    else:
                        param_code = str(variable_code_entry) if variable_code_entry else ""
                else:
                    param_code = ""
                
                # Apply semantic knowledge during extraction (same as real API)
                site_semantic_context = self._get_site_semantic_context(site_code)
                param_semantic_context = self._get_parameter_semantic_context(param_code)
                
                # Extract values with semantic enrichment
                values_data = time_series.get("values", [])
                if not isinstance(values_data, list) or len(values_data) == 0:
                    continue
                    
                values_array = values_data[0].get("value", []) if isinstance(values_data[0], dict) else []
                
                for value_entry in values_array:
                    if not isinstance(value_entry, dict):
                        continue
                        
                    # Build semantically-aware raw record (identical to real API processing)
                    raw_record = {
                        # Core USGS data
                        "site_code": site_code,
                        "site_name": site_info.get("siteName", ""),
                        "parameter_code": param_code,
                        "parameter_name": variable_info.get("variableName", ""),
                        "value": value_entry.get("value", ""),
                        "datetime": value_entry.get("dateTime", ""),
                        # Extract quality code with robust error handling
                        "quality_code": self._extract_quality_code(value_entry),
                        
                        # Semantic context applied during extraction
                        "semantic_site_context": site_semantic_context,
                        "semantic_parameter_context": param_semantic_context,
                        
                        # Navigation-specific assessments
                        "navigation_criticality": param_semantic_context.get("navigation_criticality", "unknown"),
                        "flood_risk_assessment": self._assess_flood_risk(site_code, param_code, value_entry.get("value", "")),
                        "low_water_risk_assessment": self._assess_low_water_risk(site_code, param_code, value_entry.get("value", "")),
                        
                        # Data provenance
                        "extraction_timestamp": datetime.now().isoformat(),
                        "data_source_api": "mock_usgs_data",
                        "collection_method": "simulated_real_time_gauge"
                    }
                    
                    raw_records.append(raw_record)
        
        logger.info(f"Generated {len(raw_records)} mock USGS records with semantic context")
        return raw_records
    
    def structure_data(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure USGS data with hydrological domain knowledge
        Applies semantic transformations during structuring phase
        """
        
        try:
            # Parse and validate numeric value
            raw_value = raw_record.get("value", "")
            if raw_value in ["", "Ice", "Bkw", "Rat", "Eqp"]:  # USGS status codes
                numeric_value = None
                value_status = raw_value if raw_value else "missing"
            else:
                try:
                    numeric_value = float(raw_value)
                    value_status = "valid"
                except ValueError:
                    numeric_value = None
                    value_status = "invalid"
            
            # Parse timestamp with timezone awareness
            timestamp_str = raw_record.get("datetime", "")
            try:
                # Convert pandas Timestamp to Python datetime for JSON serialization
                timestamp = pd.to_datetime(timestamp_str).to_pydatetime()
            except ValueError:
                timestamp = datetime.now()
                
            # Apply semantic structure with domain knowledge
            structured_record = {
                # Standardized identifiers
                "site_id": raw_record["site_code"],
                "site_name_canonical": self._canonicalize_site_name(raw_record["site_name"]),
                "parameter_id": raw_record["parameter_code"],
                "measurement_timestamp": timestamp,
                
                # Measured value with semantic typing
                "measured_value": numeric_value,
                "measurement_unit": self._get_canonical_unit(raw_record["parameter_code"]),
                "measurement_status": value_status,
                "data_quality_code": raw_record.get("quality_code", ""),
                
                # Geospatial information with validation
                "latitude": self._validate_coordinate(raw_record["latitude"], "latitude"),
                "longitude": self._validate_coordinate(raw_record["longitude"], "longitude"),
                "spatial_reference_system": "EPSG:4326",  # WGS84
                
                # Navigation-specific semantic structure
                "river_mile": raw_record["navigation_context"].get("river_mile"),
                "navigation_pool": raw_record["navigation_context"].get("navigation_pool"),
                "associated_lock_dam": raw_record["navigation_context"].get("lock_dam"),
                
                # Semantic classifications applied during structuring
                "measurement_category": self._classify_measurement(raw_record["parameter_code"], numeric_value),
                "navigation_relevance": self._assess_navigation_relevance(raw_record["parameter_code"]),
                "data_freshness_minutes": self._calculate_data_freshness(timestamp),
                
                # Quality assessment with domain-specific rules
                "value_within_expected_range": self._validate_value_range(raw_record["parameter_code"], numeric_value),
                "seasonal_context": self._determine_seasonal_context(timestamp),
                
                # Provenance and lineage
                "source_system": "USGS_NWIS",
                "collection_timestamp": raw_record["extraction_timestamp"],
                "processing_stage": "structured_with_semantics"
            }
            
            return structured_record
            
        except Exception as e:
            logger.error(f"Failed to structure USGS record: {e}")
            return raw_record  # Fallback to raw data
    
    def _get_site_semantic_context(self, site_code: str) -> Dict[str, Any]:
        """Get semantic context for USGS site during extraction"""
        
        context = {
            "site_uri": f"http://hydrology.usgs.gov/site/{site_code}",
            "site_type": "gauge_station",
            "monitoring_purpose": "navigation_support",
            "data_steward": "USGS",
            "site_status": "active"
        }
        
        # Add navigation-specific context
        if site_code in self.site_navigation_context:
            nav_context = self.site_navigation_context[site_code]
            context.update({
                "navigation_mile": nav_context.get("river_mile"),
                "navigation_significance": "critical" if nav_context.get("lock_dam") else "important",
                "waterway_system": "Mississippi River",
                "navigation_district": self._determine_navigation_district(nav_context.get("river_mile"))
            })
        
        return context
    
    def _get_parameter_semantic_context(self, param_code: str) -> Dict[str, Any]:
        """Get semantic context for USGS parameter during extraction"""
        
        if param_code in self.parameter_semantics:
            param_info = self.parameter_semantics[param_code]
            return {
                "parameter_uri": param_info["ontology_uri"],
                "measurement_concept": param_info["concept"],
                "canonical_unit": param_info["unit"],
                "navigation_critical": param_info["navigation_critical"],
                "measurement_domain": "hydrology",
                "quality_thresholds": param_info["quality_thresholds"]
            }
        
        return {
            "parameter_uri": f"http://hydrology.usgs.gov/parameter/{param_code}",
            "measurement_concept": "UnknownHydrologicalParameter",
            "navigation_critical": False
        }
    
    def _canonicalize_site_name(self, site_name: str) -> str:
        """Canonicalize site name for consistent referencing"""
        
        # Standardize Mississippi River site names
        canonical_patterns = {
            "MISSISSIPPI RIVER": "Mississippi River",
            " AT ": " at ",
            " NEAR ": " near ",
            " BELOW ": " below ",
            " ABOVE ": " above "
        }
        
        canonical_name = site_name
        for pattern, replacement in canonical_patterns.items():
            canonical_name = canonical_name.replace(pattern, replacement)
        
        return canonical_name.title()
    
    def _get_canonical_unit(self, param_code: str) -> str:
        """Get canonical unit for parameter"""
        return self.parameter_semantics.get(param_code, {}).get("unit", "unknown")
    
    def _validate_coordinate(self, coord: float, coord_type: str) -> Optional[float]:
        """Validate coordinate values"""
        
        if coord_type == "latitude" and -90 <= coord <= 90:
            return coord
        elif coord_type == "longitude" and -180 <= coord <= 180:
            return coord
        else:
            logger.warning(f"Invalid {coord_type}: {coord}")
            return None
    
    def _classify_measurement(self, param_code: str, value: Optional[float]) -> str:
        """Classify measurement based on parameter and value"""
        
        if param_code == "00065":  # Water level/stage
            if value is None:
                return "missing_water_level"
            elif value < 5:
                return "low_water_level"
            elif value > 25:
                return "high_water_level" 
            else:
                return "normal_water_level"
                
        elif param_code == "00060":  # Discharge
            if value is None:
                return "missing_discharge"
            elif value < 10000:
                return "low_discharge"
            elif value > 500000:
                return "high_discharge"
            else:
                return "normal_discharge"
                
        elif param_code == "00010":  # Temperature
            return "water_temperature"
        
        return "unknown_measurement"
    
    def _assess_navigation_relevance(self, param_code: str) -> str:
        """Assess relevance of parameter for navigation"""
        
        navigation_critical_params = ["00065", "00060"]  # Stage and discharge
        
        if param_code in navigation_critical_params:
            return "critical"
        else:
            return "supplementary"
    
    def _calculate_data_freshness(self, timestamp: datetime) -> float:
        """Calculate data freshness in minutes"""
        try:
            # Handle timezone-aware timestamps from USGS
            now = datetime.now()
            if timestamp.tzinfo is not None:
                # If timestamp has timezone, make now timezone-aware too
                import pytz
                if now.tzinfo is None:
                    now = pytz.UTC.localize(now)
                # Convert timestamp to UTC for comparison
                timestamp_utc = timestamp.astimezone(pytz.UTC)
                now_utc = now.astimezone(pytz.UTC)
                return (now_utc - timestamp_utc).total_seconds() / 60
            else:
                # Both are timezone-naive
                return (now - timestamp).total_seconds() / 60
        except Exception as e:
            logger.warning(f"Could not calculate data freshness: {e}")
            return 0.0  # Return 0 minutes as fallback
    
    def _validate_value_range(self, param_code: str, value: Optional[float]) -> bool:
        """Validate if value is within expected range for parameter"""
        
        if value is None:
            return False
            
        thresholds = self.parameter_semantics.get(param_code, {}).get("quality_thresholds", {})
        
        min_val = thresholds.get("min", float('-inf'))
        max_val = thresholds.get("max", float('inf'))
        
        return min_val <= value <= max_val
    
    def _determine_seasonal_context(self, timestamp: datetime) -> str:
        """Determine seasonal context for measurement"""
        
        month = timestamp.month
        
        if month in [12, 1, 2]:
            return "winter"  # Ice risk, low flows
        elif month in [3, 4, 5]:
            return "spring"  # Snowmelt, floods
        elif month in [6, 7, 8]:
            return "summer"  # Low flows, navigation season
        else:
            return "fall"  # Harvest season, moderate flows
    
    def _determine_navigation_district(self, river_mile: Optional[float]) -> str:
        """Determine navigation district based on river mile"""
        
        if river_mile is None:
            return "unknown"
        elif river_mile >= 844:
            return "St. Paul District"
        elif river_mile >= 647:
            return "Rock Island District"
        elif river_mile >= 364:
            return "St. Louis District"
        elif river_mile >= 325:
            return "Memphis District"
        else:
            return "New Orleans District"
    
    def _extract_quality_code(self, value_entry: Dict[str, Any]) -> str:
        """Extract quality code with robust error handling"""
        
        qualifiers_list = value_entry.get("qualifiers", [])
        if isinstance(qualifiers_list, list) and len(qualifiers_list) > 0:
            qualifier_entry = qualifiers_list[0]
            if isinstance(qualifier_entry, dict):
                return qualifier_entry.get("qualifierCode", "")
            else:
                # Handle case where qualifier is a string or other type
                # Note: USGS often returns qualifiers as simple strings (e.g., "P" for provisional)
                return str(qualifier_entry) if qualifier_entry else ""
        return ""
    
    def _assess_flood_risk(self, site_code: str, param_code: str, value: str) -> str:
        """Assess flood risk based on water level measurements"""
        
        if param_code != "00065":  # Only assess for gauge height
            return "not_applicable"
        
        try:
            water_level = float(value)
            
            # Get site-specific flood thresholds (simplified)
            if site_code in self.navigation_risk_thresholds:
                flood_stage = self.navigation_risk_thresholds[site_code]["flood_stage"]
                
                if water_level >= flood_stage + 5:
                    return "critical"
                elif water_level >= flood_stage:
                    return "high"
                elif water_level >= flood_stage - 2:
                    return "moderate"
                else:
                    return "low"
            
            # Default assessment for unknown sites
            if water_level >= 30:
                return "high"
            elif water_level >= 25:
                return "moderate"
            else:
                return "low"
                
        except (ValueError, TypeError):
            return "unknown"
    
    def _assess_low_water_risk(self, site_code: str, param_code: str, value: str) -> str:
        """Assess low water navigation risk"""
        
        if param_code != "00065":  # Only assess for gauge height
            return "not_applicable"
        
        try:
            water_level = float(value)
            
            # Get site-specific low water thresholds
            if site_code in self.navigation_risk_thresholds:
                low_water = self.navigation_risk_thresholds[site_code]["low_water"]
                
                if water_level <= low_water - 2:
                    return "critical"
                elif water_level <= low_water:
                    return "high"
                elif water_level <= low_water + 2:
                    return "moderate" 
                else:
                    return "low"
            
            # Default assessment for unknown sites
            if water_level <= 5:
                return "critical"
            elif water_level <= 8:
                return "high"
            elif water_level <= 12:
                return "moderate"
            else:
                return "low"
                
        except (ValueError, TypeError):
            return "unknown"


# Usage example showing ET(K)L in action
if __name__ == "__main__":
    async def main():
        # Initialize USGS collector with semantic processing
        collector = USGSSemanticCollector(
            kuzu_temp_db="./temp_semantic_processing.kuzu",
            sites=["05331000", "07010000"]  # St. Paul and St. Louis
        )
        
        # Run ET(K)L collection
        print("Starting USGS semantic data collection...")
        enriched_records = await collector.collect_semantically_enriched_data()
        
        print(f"\nCollected {len(enriched_records)} semantically enriched records")
        
        # Show first record to demonstrate semantic enrichment
        if enriched_records:
            sample_record = enriched_records[0]
            print("\n=== Sample Semantically Enriched Record ===")
            print(f"Source: {sample_record.source_id}")
            print(f"Record ID: {sample_record.record_id}")
            print(f"Timestamp: {sample_record.timestamp}")
            
            print("\nStructured Data:")
            for key, value in sample_record.structured_data.items():
                print(f"  {key}: {value}")
            
            print("\nSemantic Annotations:")
            for key, value in sample_record.semantic_annotations.items():
                print(f"  {key}: {value}")
            
            print(f"\nQuality Score: {sample_record.quality_metrics.get('overall_quality', 'N/A')}")
        
        # Store in KuzuDB tables ready for graph analytics
        collector.store_in_kuzu_tables(enriched_records, "HydroReading")
        
        print("\nData successfully collected with semantic enrichment during acquisition!")
    
    # Run the example
    import asyncio
    asyncio.run(main())