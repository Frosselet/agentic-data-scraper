"""
AIS Vessel Data Collector with Semantic Enrichment
Implements ET(K)L for vessel tracking data with transportation ontology integration
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import math

import httpx
import pandas as pd
from .semantic_collectors import SemanticCollectorBase, SemanticContext, StructuredRecord
from .mock_data import mock_generator

logger = logging.getLogger(__name__)


class AISSemanticCollector(SemanticCollectorBase):
    """
    AIS Vessel Tracking collector with transportation semantic enrichment
    Applies maritime ontologies and navigation intelligence during data acquisition
    """
    
    def __init__(self, kuzu_temp_db: str, api_key: str, bbox: Dict[str, float] = None):
        
        # Define semantic context for AIS transportation data
        semantic_context = SemanticContext(
            domain="transportation",
            ontology_uri="http://transportation.dot.gov/ontology/",
            primary_concepts=["vessel", "position", "movement", "cargo", "navigation_status"],
            entity_types=["vessel", "port", "waterway", "cargo", "route"],
            spatial_context="mississippi_river_inland_waterways",
            temporal_context="real_time_tracking",
            unit_mappings={
                "speed": "knots",
                "heading": "degrees",
                "latitude": "decimal_degrees",
                "longitude": "decimal_degrees"
            }
        )
        
        super().__init__("ais_vessel_tracking", kuzu_temp_db, semantic_context)
        
        self.api_key = api_key
        
        # Default bounding box for Mississippi River system
        self.bbox = bbox or {
            "north": 47.9,   # Northern Minnesota
            "south": 29.0,   # New Orleans
            "east": -89.0,   # Eastern boundary
            "west": -95.2    # Western boundary (includes tributaries)
        }
        
        self.base_url = "https://api.vesselfinder.com/v1/ais"
        
    def _initialize_domain_knowledge(self):
        """Initialize AIS-specific transportation and maritime knowledge"""
        
        # AIS vessel type codes with semantic mappings
        self.vessel_type_semantics = {
            # Commercial vessels
            70: {"category": "cargo", "subcategory": "general_cargo", "navigation_relevance": "high"},
            71: {"category": "cargo", "subcategory": "hazardous_cargo", "navigation_relevance": "critical"},
            72: {"category": "cargo", "subcategory": "bulk_carrier", "navigation_relevance": "high"},
            73: {"category": "cargo", "subcategory": "bulk_carrier", "navigation_relevance": "high"},
            74: {"category": "cargo", "subcategory": "general_cargo", "navigation_relevance": "high"},
            
            # Tankers
            80: {"category": "tanker", "subcategory": "liquid_bulk", "navigation_relevance": "critical"},
            81: {"category": "tanker", "subcategory": "hazardous_liquid", "navigation_relevance": "critical"},
            82: {"category": "tanker", "subcategory": "liquid_bulk", "navigation_relevance": "critical"},
            
            # Towing vessels (critical for inland waterways)
            31: {"category": "towing", "subcategory": "towboat", "navigation_relevance": "critical"},
            32: {"category": "towing", "subcategory": "towboat", "navigation_relevance": "critical"},
            
            # Passenger vessels
            60: {"category": "passenger", "subcategory": "passenger_ship", "navigation_relevance": "medium"},
            61: {"category": "passenger", "subcategory": "passenger_ship", "navigation_relevance": "medium"},
            
            # Service vessels
            50: {"category": "service", "subcategory": "pilot_vessel", "navigation_relevance": "high"},
            51: {"category": "service", "subcategory": "search_rescue", "navigation_relevance": "high"},
            52: {"category": "service", "subcategory": "tug", "navigation_relevance": "high"},
            53: {"category": "service", "subcategory": "port_tender", "navigation_relevance": "medium"},
        }
        
        # Navigation status codes with semantic meaning
        self.navigation_status_semantics = {
            0: {"status": "under_way_using_engine", "mobility": "moving", "priority": "normal"},
            1: {"status": "at_anchor", "mobility": "anchored", "priority": "low"},
            2: {"status": "not_under_command", "mobility": "restricted", "priority": "high"},
            3: {"status": "restricted_maneuverability", "mobility": "restricted", "priority": "high"},
            4: {"status": "constrained_by_draught", "mobility": "restricted", "priority": "medium"},
            5: {"status": "moored", "mobility": "stationary", "priority": "low"},
            6: {"status": "aground", "mobility": "emergency", "priority": "critical"},
            7: {"status": "engaged_in_fishing", "mobility": "restricted", "priority": "medium"},
            8: {"status": "under_way_sailing", "mobility": "moving", "priority": "low"},
            15: {"status": "not_defined", "mobility": "unknown", "priority": "low"}
        }
        
        # Mississippi River commodity classification for cargo estimation
        self.river_commodity_patterns = {
            # Grain-related vessel names
            "grain": {"keywords": ["grain", "corn", "soy", "wheat", "agri"], "commodity_type": "agricultural"},
            "coal": {"keywords": ["coal", "energy"], "commodity_type": "energy"},
            "petroleum": {"keywords": ["oil", "fuel", "petroleum", "chemical"], "commodity_type": "energy"},
            "container": {"keywords": ["container", "intermodal"], "commodity_type": "manufactured"},
            "barge": {"keywords": ["barge", "tow"], "commodity_type": "bulk_carrier"}
        }
        
        # Major Mississippi River ports with semantic context
        self.river_ports_context = {
            "minneapolis": {"river_mile": 847.9, "port_type": "grain_terminal", "navigation_district": "St. Paul"},
            "st_paul": {"river_mile": 847.9, "port_type": "grain_terminal", "navigation_district": "St. Paul"},
            "dubuque": {"river_mile": 647.9, "port_type": "multi_commodity", "navigation_district": "Rock Island"},
            "st_louis": {"river_mile": 180.0, "port_type": "major_hub", "navigation_district": "St. Louis"},
            "memphis": {"river_mile": 734.8, "port_type": "multi_commodity", "navigation_district": "Memphis"},
            "vicksburg": {"river_mile": 435.7, "port_type": "grain_terminal", "navigation_district": "Vicksburg"},
            "baton_rouge": {"river_mile": 228.4, "port_type": "petroleum_chemical", "navigation_district": "New Orleans"},
            "new_orleans": {"river_mile": 90.0, "port_type": "major_hub", "navigation_district": "New Orleans"}
        }
        
    async def extract_raw_data(self) -> List[Dict[str, Any]]:
        """
        Extract AIS vessel data with maritime semantic awareness
        Real-time vessel positions with transportation ontology context
        """
        
        raw_records = []
        
        # Check if we should use mock data
        if not self.api_key or self.api_key == "demo_key":
            logger.info("Using mock AIS data for demonstration (no API key provided)")
            return await self._extract_mock_data()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Build AIS API request for Mississippi River bounding box
            params = {
                "userkey": self.api_key,
                "format": "json",
                "north": self.bbox["north"],
                "south": self.bbox["south"],
                "east": self.bbox["east"],
                "west": self.bbox["west"],
                "zoom": 10  # Detailed vessel data
            }
            
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Process vessel list with semantic context applied during extraction
                if isinstance(data, list):
                    for vessel_data in data:
                        # Apply semantic knowledge during extraction
                        vessel_semantic_context = self._get_vessel_semantic_context(vessel_data)
                        navigation_semantic_context = self._get_navigation_semantic_context(vessel_data)
                        spatial_semantic_context = self._get_spatial_semantic_context(vessel_data)
                        
                        # Build semantically-enriched raw record
                        raw_record = {
                            # Core AIS vessel data
                            "mmsi": vessel_data.get("mmsi", ""),
                            "imo": vessel_data.get("imo", ""),
                            "vessel_name": vessel_data.get("shipname", ""),
                            "call_sign": vessel_data.get("callsign", ""),
                            "vessel_type": vessel_data.get("shiptype", 0),
                            "length": vessel_data.get("length", 0),
                            "width": vessel_data.get("width", 0),
                            "draught": vessel_data.get("draught", 0),
                            
                            # Position and movement
                            "latitude": float(vessel_data.get("lat", 0)),
                            "longitude": float(vessel_data.get("lon", 0)),
                            "speed_over_ground": float(vessel_data.get("sog", 0)),
                            "course_over_ground": float(vessel_data.get("cog", 0)),
                            "heading": vessel_data.get("heading", 0),
                            "navigation_status": vessel_data.get("navstat", 15),
                            
                            # Voyage information
                            "destination": vessel_data.get("destination", ""),
                            "eta": vessel_data.get("eta", ""),
                            
                            # Timestamp information
                            "timestamp": vessel_data.get("timestamp", datetime.now().isoformat()),
                            "last_position_update": vessel_data.get("last_pos_update", ""),
                            
                            # Semantic context applied during extraction
                            "semantic_vessel_context": vessel_semantic_context,
                            "semantic_navigation_context": navigation_semantic_context,
                            "semantic_spatial_context": spatial_semantic_context,
                            
                            # Transportation domain knowledge
                            "estimated_cargo_category": self._estimate_cargo_category(vessel_data),
                            "mississippi_river_relevance": self._assess_river_relevance(vessel_data),
                            "navigation_priority": self._assess_navigation_priority(vessel_data),
                            
                            # Data provenance
                            "extraction_timestamp": datetime.now().isoformat(),
                            "data_source_api": self.base_url,
                            "collection_method": "real_time_ais"
                        }
                        
                        raw_records.append(raw_record)
                        
            except Exception as e:
                logger.error(f"Failed to extract AIS data: {e}")
                raise
        
        logger.info(f"Extracted {len(raw_records)} vessel records with semantic context from AIS")
        return raw_records
    
    async def _extract_mock_data(self) -> List[Dict[str, Any]]:
        """Extract mock AIS data for demonstration purposes"""
        
        raw_records = []
        
        # Generate realistic mock vessel data
        mock_vessels = mock_generator.generate_mock_ais_data(vessel_count=15)
        
        for vessel_data in mock_vessels:
            # Apply semantic knowledge during extraction (same as real API)
            vessel_semantic_context = self._get_vessel_semantic_context(vessel_data)
            navigation_semantic_context = self._get_navigation_semantic_context(vessel_data)
            spatial_semantic_context = self._get_spatial_semantic_context(vessel_data)
            
            # Build semantically-enriched raw record (identical to real API processing)
            raw_record = {
                # Core AIS vessel data
                "mmsi": vessel_data.get("mmsi", ""),
                "imo": vessel_data.get("imo", ""),
                "vessel_name": vessel_data.get("shipname", ""),
                "call_sign": vessel_data.get("callsign", ""),
                "vessel_type": vessel_data.get("shiptype", 0),
                "length": vessel_data.get("length", 0),
                "width": vessel_data.get("width", 0),
                "draught": vessel_data.get("draught", 0),
                
                # Position and movement
                "latitude": float(vessel_data.get("lat", 0)),
                "longitude": float(vessel_data.get("lon", 0)),
                "speed_over_ground": float(vessel_data.get("sog", 0)),
                "course_over_ground": float(vessel_data.get("cog", 0)),
                "heading": vessel_data.get("heading", 0),
                "navigation_status": vessel_data.get("navstat", 15),
                
                # Voyage information
                "destination": vessel_data.get("destination", ""),
                "eta": vessel_data.get("eta", ""),
                
                # Timestamp information
                "timestamp": vessel_data.get("timestamp", datetime.now().isoformat()),
                "last_position_update": vessel_data.get("last_pos_update", ""),
                
                # Semantic context applied during extraction
                "semantic_vessel_context": vessel_semantic_context,
                "semantic_navigation_context": navigation_semantic_context,
                "semantic_spatial_context": spatial_semantic_context,
                
                # Transportation domain knowledge
                "estimated_cargo_category": self._estimate_cargo_category(vessel_data),
                "mississippi_river_relevance": self._assess_river_relevance(vessel_data),
                "navigation_priority": self._assess_navigation_priority(vessel_data),
                
                # Data provenance
                "extraction_timestamp": datetime.now().isoformat(),
                "data_source_api": "mock_ais_data",
                "collection_method": "simulated_real_time_ais"
            }
            
            raw_records.append(raw_record)
        
        logger.info(f"Generated {len(raw_records)} mock vessel records with semantic context")
        return raw_records
    
    def structure_data(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure AIS data with transportation domain knowledge
        Applies vessel and cargo semantic transformations during structuring
        """
        
        try:
            # Parse and validate vessel identifiers
            mmsi = str(raw_record.get("mmsi", "")).strip()
            vessel_name = self._canonicalize_vessel_name(raw_record.get("vessel_name", ""))
            
            # Parse vessel dimensions with validation
            length = self._validate_vessel_dimension(raw_record.get("length", 0))
            width = self._validate_vessel_dimension(raw_record.get("width", 0))
            draught = self._validate_vessel_dimension(raw_record.get("draught", 0), max_val=50)
            
            # Parse position with geospatial validation
            latitude = self._validate_coordinate(raw_record.get("latitude", 0), "latitude")
            longitude = self._validate_coordinate(raw_record.get("longitude", 0), "longitude")
            
            # Parse movement data with validation
            speed = self._validate_speed(raw_record.get("speed_over_ground", 0))
            heading = self._validate_heading(raw_record.get("heading", 0))
            course = self._validate_heading(raw_record.get("course_over_ground", 0))
            
            # Parse timestamps
            try:
                # Convert pandas Timestamp to Python datetime for JSON serialization
                measurement_timestamp = pd.to_datetime(raw_record.get("timestamp")).to_pydatetime()
            except ValueError:
                measurement_timestamp = datetime.now()
            
            # Apply transportation semantic structure
            structured_record = {
                # Standardized vessel identity
                "vessel_mmsi": mmsi,
                "vessel_imo": str(raw_record.get("imo", "")).strip() or None,
                "vessel_name_canonical": vessel_name,
                "call_sign": str(raw_record.get("call_sign", "")).strip() or None,
                
                # Vessel characteristics with semantic typing
                "vessel_type_code": int(raw_record.get("vessel_type", 0)),
                "vessel_category": self._get_vessel_category(raw_record.get("vessel_type", 0)),
                "vessel_subcategory": self._get_vessel_subcategory(raw_record.get("vessel_type", 0)),
                "vessel_length_meters": length,
                "vessel_width_meters": width,
                "vessel_draught_meters": draught,
                
                # Position information with spatial semantics
                "position_latitude": latitude,
                "position_longitude": longitude,
                "position_timestamp": measurement_timestamp,
                "coordinate_reference_system": "EPSG:4326",
                
                # Movement characteristics with validation
                "speed_over_ground_knots": speed,
                "course_over_ground_degrees": course,
                "heading_degrees": heading,
                "navigation_status_code": int(raw_record.get("navigation_status", 15)),
                "navigation_status_semantic": self._get_navigation_status_semantic(raw_record.get("navigation_status", 15)),
                
                # Voyage information
                "destination_reported": str(raw_record.get("destination", "")).strip() or None,
                "destination_canonical": self._canonicalize_destination(raw_record.get("destination", "")),
                "eta_reported": raw_record.get("eta") or None,
                
                # Semantic enrichment applied during structuring
                "river_mile_estimated": self._estimate_river_mile_from_coordinates(latitude, longitude),
                "waterway_segment": self._identify_waterway_segment(latitude, longitude),
                "navigation_district": self._determine_navigation_district(latitude, longitude),
                
                # Transportation-specific semantic classifications
                "cargo_category_estimated": raw_record.get("estimated_cargo_category", "unknown"),
                "vessel_operational_role": self._determine_operational_role(raw_record),
                "commercial_significance": self._assess_commercial_significance(raw_record),
                "navigation_priority_level": raw_record.get("navigation_priority", "normal"),
                
                # Quality and reliability metrics
                "position_accuracy_assessment": self._assess_position_accuracy(raw_record),
                "data_freshness_minutes": self._calculate_data_freshness(measurement_timestamp),
                "vessel_identification_confidence": self._assess_identification_confidence(raw_record),
                
                # Interoperability and cross-referencing
                "geonames_nearest_feature": self._find_nearest_geographic_feature(latitude, longitude),
                "usace_navigation_context": self._get_usace_context(latitude, longitude),
                
                # Provenance and lineage
                "source_system": "AIS_Global_Network",
                "collection_timestamp": raw_record["extraction_timestamp"],
                "processing_stage": "structured_with_transportation_semantics"
            }
            
            return structured_record
            
        except Exception as e:
            logger.error(f"Failed to structure AIS record: {e}")
            return raw_record  # Fallback to raw data
    
    def _get_vessel_semantic_context(self, vessel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get transportation semantic context for vessel during extraction"""
        
        vessel_type = int(vessel_data.get("shiptype", 0))
        vessel_name = str(vessel_data.get("shipname", "")).lower()
        
        context = {
            "vessel_uri": f"http://transportation.dot.gov/vessel/{vessel_data.get('mmsi', '')}",
            "vessel_ontology_class": "CommercialVessel",
            "maritime_identification": "AIS_Tracked",
            "regulatory_framework": "US_Coast_Guard",
        }
        
        # Add vessel type semantics
        if vessel_type in self.vessel_type_semantics:
            type_info = self.vessel_type_semantics[vessel_type]
            context.update({
                "vessel_category": type_info["category"],
                "vessel_subcategory": type_info["subcategory"],
                "navigation_relevance": type_info["navigation_relevance"],
                "commercial_vessel": True
            })
        else:
            context.update({
                "vessel_category": "unknown",
                "commercial_vessel": False
            })
        
        # Add cargo estimation context
        for cargo_type, patterns in self.river_commodity_patterns.items():
            if any(keyword in vessel_name for keyword in patterns["keywords"]):
                context.update({
                    "estimated_cargo_type": cargo_type,
                    "commodity_category": patterns["commodity_type"],
                    "cargo_estimation_confidence": "medium"
                })
                break
        
        return context
    
    def _get_navigation_semantic_context(self, vessel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get navigation semantic context during extraction"""
        
        nav_status = int(vessel_data.get("navstat", 15))
        
        context = {
            "navigation_domain": "inland_waterway",
            "waterway_system": "mississippi_river_system",
            "navigation_rules": "inland_navigation_rules"
        }
        
        # Add navigation status semantics
        if nav_status in self.navigation_status_semantics:
            status_info = self.navigation_status_semantics[nav_status]
            context.update({
                "movement_status": status_info["status"],
                "mobility_classification": status_info["mobility"],
                "traffic_priority": status_info["priority"],
                "navigation_restrictions": self._determine_navigation_restrictions(status_info)
            })
        
        return context
    
    def _get_spatial_semantic_context(self, vessel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get geospatial semantic context during extraction"""
        
        lat = float(vessel_data.get("lat", 0))
        lon = float(vessel_data.get("lon", 0))
        
        context = {
            "spatial_reference": "WGS84",
            "coordinate_precision": "high",
            "geographic_context": "north_american_inland_waterways"
        }
        
        # Determine if vessel is on Mississippi River system
        if self._is_on_mississippi_system(lat, lon):
            context.update({
                "waterway_system": "mississippi_river",
                "navigation_context": "inland_commercial_navigation",
                "regulatory_jurisdiction": "us_army_corps_of_engineers",
                "estimated_river_mile": self._estimate_river_mile_from_coordinates(lat, lon)
            })
            
            # Add specific reach information
            reach_info = self._identify_river_reach(lat, lon)
            if reach_info:
                context.update(reach_info)
        
        return context
    
    def _estimate_cargo_category(self, vessel_data: Dict[str, Any]) -> str:
        """Estimate cargo category based on vessel characteristics"""
        
        vessel_type = int(vessel_data.get("shiptype", 0))
        vessel_name = str(vessel_data.get("shipname", "")).lower()
        
        # Check vessel type first
        if vessel_type in self.vessel_type_semantics:
            category = self.vessel_type_semantics[vessel_type]["category"]
            if category != "cargo":
                return category
        
        # Estimate based on vessel name patterns
        for cargo_type, patterns in self.river_commodity_patterns.items():
            if any(keyword in vessel_name for keyword in patterns["keywords"]):
                return patterns["commodity_type"]
        
        return "unknown"
    
    def _assess_river_relevance(self, vessel_data: Dict[str, Any]) -> str:
        """Assess relevance to Mississippi River navigation"""
        
        lat = float(vessel_data.get("lat", 0))
        lon = float(vessel_data.get("lon", 0))
        
        if self._is_on_mississippi_system(lat, lon):
            vessel_type = int(vessel_data.get("shiptype", 0))
            
            # Towing vessels and cargo vessels are highly relevant
            if vessel_type in [31, 32] or vessel_type in range(70, 90):
                return "high"
            else:
                return "medium"
        else:
            return "low"
    
    def _assess_navigation_priority(self, vessel_data: Dict[str, Any]) -> str:
        """Assess navigation priority level"""
        
        nav_status = int(vessel_data.get("navstat", 15))
        vessel_type = int(vessel_data.get("shiptype", 0))
        
        # Emergency situations get critical priority
        if nav_status in [2, 6]:  # Not under command, aground
            return "critical"
        
        # Restricted maneuverability gets high priority
        elif nav_status in [3, 4]:  # Restricted maneuverability, constrained by draught
            return "high"
        
        # Hazardous cargo gets high priority
        elif vessel_type in [71, 81]:  # Hazardous cargo, hazardous liquid tanker
            return "high"
        
        # Commercial vessels get normal priority
        elif vessel_type in range(70, 90):
            return "normal"
        
        else:
            return "low"
    
    # Additional helper methods for vessel-specific processing
    def _canonicalize_vessel_name(self, vessel_name: str) -> str:
        """Canonicalize vessel name for consistent referencing"""
        if not vessel_name:
            return ""
        
        # Clean and standardize vessel names
        name = vessel_name.strip().upper()
        
        # Remove common prefixes/suffixes
        prefixes = ["M/V", "MV", "T/V", "TV", "S/V", "SV"]
        for prefix in prefixes:
            if name.startswith(prefix + " "):
                name = name[len(prefix):].strip()
        
        return name
    
    def _validate_vessel_dimension(self, dimension: Any, max_val: float = 500) -> Optional[float]:
        """Validate vessel dimension values"""
        try:
            dim = float(dimension)
            return dim if 0 <= dim <= max_val else None
        except (ValueError, TypeError):
            return None
    
    def _validate_coordinate(self, coord: Any, coord_type: str) -> Optional[float]:
        """Validate coordinate values"""
        try:
            coord_val = float(coord)
            if coord_type == "latitude" and -90 <= coord_val <= 90:
                return coord_val
            elif coord_type == "longitude" and -180 <= coord_val <= 180:
                return coord_val
            else:
                return None
        except (ValueError, TypeError):
            return None
    
    def _validate_speed(self, speed: Any) -> Optional[float]:
        """Validate speed values"""
        try:
            speed_val = float(speed)
            return speed_val if 0 <= speed_val <= 50 else None  # Max 50 knots reasonable for inland
        except (ValueError, TypeError):
            return None
    
    def _validate_heading(self, heading: Any) -> Optional[float]:
        """Validate heading values"""
        try:
            heading_val = float(heading)
            return heading_val if 0 <= heading_val <= 360 else None
        except (ValueError, TypeError):
            return None
    
    def _get_vessel_category(self, vessel_type: int) -> str:
        """Get vessel category from type code"""
        return self.vessel_type_semantics.get(vessel_type, {}).get("category", "unknown")
    
    def _get_vessel_subcategory(self, vessel_type: int) -> str:
        """Get vessel subcategory from type code"""
        return self.vessel_type_semantics.get(vessel_type, {}).get("subcategory", "unknown")
    
    def _get_navigation_status_semantic(self, nav_status: int) -> str:
        """Get semantic meaning of navigation status"""
        return self.navigation_status_semantics.get(nav_status, {}).get("status", "not_defined")
    
    def _canonicalize_destination(self, destination: str) -> Optional[str]:
        """Canonicalize destination name"""
        if not destination or destination.strip() == "":
            return None
        
        dest = destination.strip().upper()
        
        # Map common abbreviations to full names
        destination_mappings = {
            "STL": "St. Louis",
            "NOLA": "New Orleans", 
            "MSP": "Minneapolis-St. Paul",
            "CHI": "Chicago",
            "MEM": "Memphis"
        }
        
        return destination_mappings.get(dest, dest.title())
    
    def _estimate_river_mile_from_coordinates(self, lat: Optional[float], lon: Optional[float]) -> Optional[float]:
        """Estimate river mile from coordinates using simplified calculation"""
        if lat is None or lon is None:
            return None
        
        # Simplified river mile estimation (production would use actual river geometry)
        head_lat = 44.98  # Minneapolis
        mouth_lat = 29.95  # New Orleans
        
        if not (mouth_lat <= lat <= head_lat):
            return None
            
        lat_progress = (head_lat - lat) / (head_lat - mouth_lat)
        return max(0, min(2320, lat_progress * 2320))
    
    def _identify_waterway_segment(self, lat: Optional[float], lon: Optional[float]) -> Optional[str]:
        """Identify specific waterway segment"""
        if lat is None or lon is None:
            return None
        
        # Simplified segment identification
        if lat >= 44:
            return "Upper Mississippi River - Twin Cities"
        elif lat >= 40:
            return "Upper Mississippi River - Iowa/Illinois"
        elif lat >= 35:
            return "Middle Mississippi River - Missouri/Arkansas"
        elif lat >= 32:
            return "Lower Mississippi River - Louisiana"
        else:
            return "Mississippi River Delta"
    
    def _determine_navigation_district(self, lat: Optional[float], lon: Optional[float]) -> Optional[str]:
        """Determine USACE navigation district"""
        if lat is None:
            return None
        
        if lat >= 44:
            return "St. Paul District"
        elif lat >= 40:
            return "Rock Island District" 
        elif lat >= 36:
            return "St. Louis District"
        elif lat >= 32:
            return "Memphis District"
        else:
            return "New Orleans District"
    
    def _determine_operational_role(self, raw_record: Dict[str, Any]) -> str:
        """Determine vessel's operational role"""
        vessel_type = int(raw_record.get("vessel_type", 0))
        
        if vessel_type in [31, 32]:
            return "towing_operations"
        elif vessel_type in range(70, 80):
            return "cargo_transport"
        elif vessel_type in range(80, 90):
            return "bulk_liquid_transport"
        elif vessel_type in [50, 51, 52]:
            return "support_services"
        else:
            return "other_operations"
    
    def _assess_commercial_significance(self, raw_record: Dict[str, Any]) -> str:
        """Assess commercial significance of vessel"""
        vessel_type = int(raw_record.get("vessel_type", 0))
        length = float(raw_record.get("length", 0)) if raw_record.get("length") else 0
        
        # Large commercial vessels
        if vessel_type in range(70, 90) and length > 100:
            return "high"
        elif vessel_type in [31, 32]:  # Towing vessels
            return "high"
        elif vessel_type in range(70, 90):
            return "medium"
        else:
            return "low"
    
    def _assess_position_accuracy(self, raw_record: Dict[str, Any]) -> str:
        """Assess position accuracy based on AIS data quality"""
        # Simplified accuracy assessment
        if raw_record.get("latitude") and raw_record.get("longitude"):
            if raw_record.get("speed_over_ground") is not None:
                return "high"
            else:
                return "medium"
        else:
            return "low"
    
    def _calculate_data_freshness(self, timestamp: datetime) -> float:
        """Calculate data freshness in minutes"""
        return (datetime.now() - timestamp).total_seconds() / 60
    
    def _assess_identification_confidence(self, raw_record: Dict[str, Any]) -> str:
        """Assess confidence in vessel identification"""
        mmsi = raw_record.get("mmsi", "")
        vessel_name = raw_record.get("vessel_name", "")
        imo = raw_record.get("imo", "")
        
        if mmsi and vessel_name and imo:
            return "high"
        elif mmsi and vessel_name:
            return "medium"
        elif mmsi:
            return "low"
        else:
            return "very_low"
    
    def _find_nearest_geographic_feature(self, lat: Optional[float], lon: Optional[float]) -> Optional[str]:
        """Find nearest named geographic feature"""
        # Simplified - production would use geocoding services
        if lat is None or lon is None:
            return None
        
        # Major cities along Mississippi River
        cities = [
            ("Minneapolis", 44.98, -93.27),
            ("St. Louis", 38.63, -90.20),
            ("Memphis", 35.15, -90.05),
            ("New Orleans", 29.95, -90.07)
        ]
        
        min_distance = float('inf')
        nearest_city = None
        
        for city, city_lat, city_lon in cities:
            distance = math.sqrt((lat - city_lat)**2 + (lon - city_lon)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_city = city
        
        return nearest_city if min_distance < 1.0 else None  # Within ~60 miles
    
    def _get_usace_context(self, lat: Optional[float], lon: Optional[float]) -> Optional[Dict[str, Any]]:
        """Get US Army Corps of Engineers operational context"""
        if lat is None or lon is None:
            return None
        
        district = self._determine_navigation_district(lat, lon)
        if district:
            return {
                "usace_district": district,
                "regulatory_authority": "US Army Corps of Engineers",
                "navigation_jurisdiction": "federal_waterway"
            }
        
        return None
    
    def _determine_navigation_restrictions(self, status_info: Dict[str, Any]) -> List[str]:
        """Determine navigation restrictions based on status"""
        restrictions = []
        
        mobility = status_info.get("mobility", "unknown")
        
        if mobility == "restricted":
            restrictions.append("limited_maneuverability")
        elif mobility == "emergency":
            restrictions.append("navigation_hazard")
        elif mobility == "anchored":
            restrictions.append("temporary_obstruction")
        
        return restrictions
    
    def _identify_river_reach(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Identify specific river reach characteristics"""
        # Simplified reach identification
        if 44 <= lat <= 47:
            return {
                "reach_name": "Upper Mississippi River",
                "navigation_season": "april_to_december",
                "ice_risk": "high",
                "lock_dam_system": "active"
            }
        elif 35 <= lat < 44:
            return {
                "reach_name": "Middle Mississippi River", 
                "navigation_season": "year_round",
                "ice_risk": "moderate",
                "lock_dam_system": "limited"
            }
        elif lat < 35:
            return {
                "reach_name": "Lower Mississippi River",
                "navigation_season": "year_round", 
                "ice_risk": "low",
                "lock_dam_system": "none"
            }
        
        return None
    
    def _is_on_mississippi_system(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within Mississippi River system"""
        # Simplified bounding box check
        return 29.0 <= lat <= 47.9 and -95.2 <= lon <= -89.0


# Usage example showing transportation domain ET(K)L
if __name__ == "__main__":
    async def main():
        # Initialize AIS collector with transportation semantic processing
        collector = AISSemanticCollector(
            kuzu_temp_db="./temp_transportation_semantic.kuzu",
            api_key="your_vesselfinder_api_key"  # Replace with actual API key
        )
        
        # Run ET(K)L collection for vessels
        print("Starting AIS vessel semantic data collection...")
        try:
            enriched_records = await collector.collect_semantically_enriched_data()
            
            print(f"\nCollected {len(enriched_records)} semantically enriched vessel records")
            
            # Show sample record demonstrating transportation semantic enrichment
            if enriched_records:
                sample_record = enriched_records[0]
                print("\n=== Sample Transportation Semantically Enriched Record ===")
                print(f"Source: {sample_record.source_id}")
                print(f"Vessel MMSI: {sample_record.structured_data.get('vessel_mmsi')}")
                print(f"Vessel Category: {sample_record.structured_data.get('vessel_category')}")
                print(f"Navigation Priority: {sample_record.structured_data.get('navigation_priority_level')}")
                print(f"Estimated River Mile: {sample_record.structured_data.get('river_mile_estimated')}")
                
                print("\nTransportation Semantic Annotations:")
                entities = sample_record.semantic_annotations.get('entities', [])
                for entity in entities[:3]:  # Show first 3 entities
                    print(f"  Entity: {entity.get('entity_type')} - {entity.get('canonical_form')}")
                    print(f"    URI: {entity.get('semantic_uri')}")
                    print(f"    Confidence: {entity.get('confidence_score'):.2f}")
            
            # Store in KuzuDB ready for transportation graph analytics
            collector.store_in_kuzu_tables(enriched_records, "VesselPosition")
            
            print("\nVessel data successfully collected with transportation semantic enrichment!")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Note: This example requires a valid VesselFinder API key")
    
    # Run the transportation example
    import asyncio
    asyncio.run(main())