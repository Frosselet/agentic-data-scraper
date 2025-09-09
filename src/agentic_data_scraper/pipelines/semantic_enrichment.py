"""
Semantic Data Enrichment Pipeline for Mississippi River Navigation System
Implements ET(K)L pattern: Extract Transform Knowledge Load with semantic layer integration
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

import httpx
import pandas as pd
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, SKOS, GEO, TIME
import kuzu
from pydantic import BaseModel, Field
import numpy as np

# Custom namespaces for Mississippi River navigation domain
NAV = Namespace("http://mississippi.navigation.org/ontology/")
HYDRO = Namespace("http://hydrology.usgs.gov/ontology/")
TRANSPORT = Namespace("http://transportation.dot.gov/ontology/")
COMMODITY = Namespace("http://commodities.usda.gov/ontology/")
GEONAMES = Namespace("http://www.geonames.org/ontology#")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    """Configuration for external data sources"""
    name: str
    url: str
    api_key: Optional[str] = None
    update_frequency: str = "hourly"  # hourly, daily, real-time
    data_format: str = "json"  # json, xml, csv
    semantic_context: Dict[str, str] = None


class SemanticEnrichmentPipeline:
    """
    Comprehensive semantic enrichment pipeline for navigation data
    Implements ET(K)L pattern with knowledge graph integration
    """
    
    def __init__(self, kuzu_db_path: str, rdf_store_path: str = "navigation_kb.ttl"):
        self.kuzu_db_path = kuzu_db_path
        self.rdf_store_path = rdf_store_path
        
        # Initialize knowledge graph
        self.rdf_graph = Graph()
        self.rdf_graph.bind("nav", NAV)
        self.rdf_graph.bind("hydro", HYDRO)
        self.rdf_graph.bind("transport", TRANSPORT)
        self.rdf_graph.bind("commodity", COMMODITY)
        self.rdf_graph.bind("geonames", GEONAMES)
        
        # KuzuDB connection
        self.kuzu_db = kuzu.Database(kuzu_db_path)
        self.kuzu_conn = kuzu.Connection(self.kuzu_db)
        
        # Data source configurations
        self.data_sources = self._configure_data_sources()
        
        # Semantic mappings cache
        self.semantic_cache: Dict[str, Any] = {}
        
        # Initialize ontology mappings
        self._load_domain_ontologies()
    
    def _configure_data_sources(self) -> Dict[str, DataSource]:
        """Configure real-world data sources for Mississippi River navigation"""
        
        return {
            "usgs_gauges": DataSource(
                name="USGS Water Data",
                url="https://waterdata.usgs.gov/nwis/current",
                update_frequency="real-time",
                data_format="json",
                semantic_context={
                    "domain": "hydrology",
                    "ontology": "http://hydrology.usgs.gov/ontology/",
                    "concepts": "water_level,flow_rate,temperature"
                }
            ),
            
            "noaa_forecasts": DataSource(
                name="NOAA River Forecasts",
                url="https://water.weather.gov/ahps2/forecasts.php",
                update_frequency="hourly",
                data_format="xml",
                semantic_context={
                    "domain": "weather",
                    "ontology": "http://weather.noaa.gov/ontology/",
                    "concepts": "forecast,precipitation,flood_stage"
                }
            ),
            
            "usace_locks": DataSource(
                name="US Army Corps of Engineers Lock Status",
                url="https://corpslocks.usace.army.mil/lpwb/f",
                update_frequency="hourly",
                data_format="json",
                semantic_context={
                    "domain": "infrastructure",
                    "ontology": "http://transportation.dot.gov/ontology/",
                    "concepts": "lock,dam,operational_status,delay"
                }
            ),
            
            "ais_vessels": DataSource(
                name="AIS Vessel Tracking",
                url="https://api.vesselfinder.com/api/pro/realtime",
                api_key="VESSEL_FINDER_API_KEY",
                update_frequency="real-time",
                data_format="json",
                semantic_context={
                    "domain": "transportation",
                    "ontology": "http://transportation.dot.gov/ontology/",
                    "concepts": "vessel,position,speed,heading,cargo"
                }
            ),
            
            "commodity_prices": DataSource(
                name="USDA Agricultural Marketing Service",
                url="https://mymarketnews.ams.usda.gov/api/reports",
                update_frequency="daily",
                data_format="json",
                semantic_context={
                    "domain": "economics",
                    "ontology": "http://commodities.usda.gov/ontology/",
                    "concepts": "price,commodity,market,terminal"
                }
            ),
            
            "rail_rates": DataSource(
                name="STB Rail Rate Data",
                url="https://prod.stb.gov/reports-data/",
                update_frequency="weekly",
                data_format="csv",
                semantic_context={
                    "domain": "transportation",
                    "ontology": "http://transportation.dot.gov/ontology/",
                    "concepts": "rail,freight_rate,origin,destination"
                }
            )
        }
    
    def _load_domain_ontologies(self):
        """Load and integrate domain-specific ontologies"""
        
        # Hydrological ontology concepts
        self._create_hydrology_ontology()
        
        # Transportation infrastructure ontology
        self._create_transportation_ontology()
        
        # Economic/commodity ontology
        self._create_commodity_ontology()
        
        # Geospatial ontology integration
        self._create_geospatial_ontology()
    
    def _create_hydrology_ontology(self):
        """Create hydrological domain ontology"""
        
        # Core hydrological concepts
        self.rdf_graph.add((HYDRO.WaterLevel, RDF.type, OWL.Class))
        self.rdf_graph.add((HYDRO.WaterLevel, RDFS.label, Literal("Water Level")))
        self.rdf_graph.add((HYDRO.WaterLevel, RDFS.comment, 
                          Literal("Height of water surface above a reference datum")))
        
        self.rdf_graph.add((HYDRO.FlowRate, RDF.type, OWL.Class))
        self.rdf_graph.add((HYDRO.FlowRate, RDFS.label, Literal("Flow Rate")))
        self.rdf_graph.add((HYDRO.FlowRate, RDFS.comment,
                          Literal("Volume of water flowing past a point per unit time")))
        
        self.rdf_graph.add((HYDRO.GaugeStation, RDF.type, OWL.Class))
        self.rdf_graph.add((HYDRO.GaugeStation, RDFS.label, Literal("Gauge Station")))
        
        # Properties
        self.rdf_graph.add((HYDRO.hasWaterLevel, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((HYDRO.hasFlowRate, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((HYDRO.recordedAt, RDF.type, OWL.DatatypeProperty))
        
        # Units and measurements
        self.rdf_graph.add((HYDRO.Feet, RDF.type, OWL.Class))
        self.rdf_graph.add((HYDRO.CubicFeetPerSecond, RDF.type, OWL.Class))
    
    def _create_transportation_ontology(self):
        """Create transportation domain ontology"""
        
        # Vessel classification hierarchy
        self.rdf_graph.add((TRANSPORT.Vessel, RDF.type, OWL.Class))
        self.rdf_graph.add((TRANSPORT.Towboat, RDF.type, OWL.Class))
        self.rdf_graph.add((TRANSPORT.Towboat, RDFS.subClassOf, TRANSPORT.Vessel))
        
        self.rdf_graph.add((TRANSPORT.Barge, RDF.type, OWL.Class))
        self.rdf_graph.add((TRANSPORT.Barge, RDFS.subClassOf, TRANSPORT.Vessel))
        
        # Infrastructure
        self.rdf_graph.add((TRANSPORT.Lock, RDF.type, OWL.Class))
        self.rdf_graph.add((TRANSPORT.Dam, RDF.type, OWL.Class))
        self.rdf_graph.add((TRANSPORT.Port, RDF.type, OWL.Class))
        self.rdf_graph.add((TRANSPORT.Terminal, RDF.type, OWL.Class))
        
        # Properties
        self.rdf_graph.add((TRANSPORT.hasCapacity, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((TRANSPORT.operatesOn, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((TRANSPORT.connectsTo, RDF.type, OWL.ObjectProperty))
    
    def _create_commodity_ontology(self):
        """Create commodity and market ontology"""
        
        # Commodity hierarchy
        self.rdf_graph.add((COMMODITY.AgriculturalCommodity, RDF.type, OWL.Class))
        self.rdf_graph.add((COMMODITY.Grain, RDF.type, OWL.Class))
        self.rdf_graph.add((COMMODITY.Grain, RDFS.subClassOf, COMMODITY.AgriculturalCommodity))
        
        self.rdf_graph.add((COMMODITY.Corn, RDF.type, OWL.Class))
        self.rdf_graph.add((COMMODITY.Corn, RDFS.subClassOf, COMMODITY.Grain))
        
        self.rdf_graph.add((COMMODITY.Soybeans, RDF.type, OWL.Class))
        self.rdf_graph.add((COMMODITY.Soybeans, RDFS.subClassOf, COMMODITY.Grain))
        
        # Market concepts
        self.rdf_graph.add((COMMODITY.MarketPrice, RDF.type, OWL.Class))
        self.rdf_graph.add((COMMODITY.TransportationRate, RDF.type, OWL.Class))
        
        # Properties
        self.rdf_graph.add((COMMODITY.hasPrice, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((COMMODITY.pricePerUnit, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((COMMODITY.validFrom, RDF.type, OWL.DatatypeProperty))
        self.rdf_graph.add((COMMODITY.validTo, RDF.type, OWL.DatatypeProperty))
    
    def _create_geospatial_ontology(self):
        """Create geospatial reference ontology"""
        
        # River system hierarchy
        self.rdf_graph.add((NAV.RiverSystem, RDF.type, OWL.Class))
        self.rdf_graph.add((NAV.MississippiRiver, RDF.type, NAV.RiverSystem))
        self.rdf_graph.add((NAV.MississippiRiver, RDFS.label, Literal("Mississippi River")))
        
        self.rdf_graph.add((NAV.RiverMile, RDF.type, OWL.Class))
        self.rdf_graph.add((NAV.WaterwaySegment, RDF.type, OWL.Class))
        
        # Spatial relationships
        self.rdf_graph.add((NAV.upstreamOf, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((NAV.downstreamOf, RDF.type, OWL.ObjectProperty))
        self.rdf_graph.add((NAV.upstreamOf, OWL.inverseOf, NAV.downstreamOf))
        
        # GeoNames integration
        self.rdf_graph.add((GEONAMES.Feature, RDF.type, OWL.Class))
        self.rdf_graph.add((NAV.linkedToGeoNames, RDF.type, OWL.ObjectProperty))
    
    async def extract_data_sources(self) -> Dict[str, pd.DataFrame]:
        """
        Extract data from all configured sources
        Returns dictionary of dataframes by source name
        """
        extracted_data = {}
        
        async with httpx.AsyncClient() as client:
            tasks = []
            for source_name, source_config in self.data_sources.items():
                task = self._extract_single_source(client, source_name, source_config)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source_name, result in zip(self.data_sources.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to extract {source_name}: {result}")
                    extracted_data[source_name] = pd.DataFrame()  # Empty dataframe
                else:
                    extracted_data[source_name] = result
        
        return extracted_data
    
    async def _extract_single_source(self, client: httpx.AsyncClient, 
                                   source_name: str, source_config: DataSource) -> pd.DataFrame:
        """Extract data from a single source"""
        
        try:
            headers = {}
            if source_config.api_key:
                headers['Authorization'] = f'Bearer {source_config.api_key}'
            
            response = await client.get(source_config.url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            if source_config.data_format == "json":
                data = response.json()
                return self._normalize_json_data(source_name, data)
            
            elif source_config.data_format == "xml":
                # Parse XML and convert to DataFrame
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                return self._normalize_xml_data(source_name, root)
            
            elif source_config.data_format == "csv":
                return pd.read_csv(response.content)
            
            else:
                raise ValueError(f"Unsupported data format: {source_config.data_format}")
                
        except Exception as e:
            logger.error(f"Error extracting {source_name}: {e}")
            raise
    
    def _normalize_json_data(self, source_name: str, data: Dict) -> pd.DataFrame:
        """Normalize JSON data to consistent DataFrame format"""
        
        if source_name == "usgs_gauges":
            # USGS water data normalization
            if 'value' in data and 'timeSeries' in data['value']:
                records = []
                for series in data['value']['timeSeries']:
                    site_info = series.get('sourceInfo', {})
                    site_code = site_info.get('siteCode', [{}])[0].get('value', '')
                    
                    for value in series.get('values', [{}])[0].get('value', []):
                        records.append({
                            'site_code': site_code,
                            'site_name': site_info.get('siteName', ''),
                            'latitude': float(site_info.get('geoLocation', {}).get('geogLocation', {}).get('latitude', 0)),
                            'longitude': float(site_info.get('geoLocation', {}).get('geogLocation', {}).get('longitude', 0)),
                            'parameter_code': series.get('variable', {}).get('variableCode', [{}])[0].get('value', ''),
                            'parameter_name': series.get('variable', {}).get('variableName', ''),
                            'value': float(value.get('value', 0)) if value.get('value') not in [None, ''] else np.nan,
                            'timestamp': pd.to_datetime(value.get('dateTime', '')),
                            'quality_code': value.get('qualifiers', [{}])[0].get('qualifierCode', '')
                        })
                
                return pd.DataFrame(records)
        
        elif source_name == "ais_vessels":
            # AIS vessel data normalization
            if isinstance(data, list):
                records = []
                for vessel in data:
                    records.append({
                        'vessel_id': vessel.get('mmsi', ''),
                        'vessel_name': vessel.get('shipname', ''),
                        'vessel_type': vessel.get('shiptype', ''),
                        'latitude': float(vessel.get('lat', 0)),
                        'longitude': float(vessel.get('lon', 0)),
                        'speed': float(vessel.get('speed', 0)),
                        'heading': float(vessel.get('course', 0)),
                        'timestamp': pd.to_datetime(vessel.get('timestamp', '')),
                        'destination': vessel.get('destination', ''),
                        'eta': pd.to_datetime(vessel.get('eta', '')) if vessel.get('eta') else None
                    })
                
                return pd.DataFrame(records)
        
        elif source_name == "commodity_prices":
            # USDA commodity price normalization
            if 'results' in data:
                records = []
                for result in data['results']:
                    records.append({
                        'commodity': result.get('commodity_name', ''),
                        'location': result.get('location_desc', ''),
                        'price': float(result.get('avg_price', 0)) if result.get('avg_price') else np.nan,
                        'units': result.get('price_unit', ''),
                        'report_date': pd.to_datetime(result.get('report_date', '')),
                        'report_type': result.get('report_type', ''),
                        'quality_grade': result.get('grade', '')
                    })
                
                return pd.DataFrame(records)
        
        # Default: try to flatten JSON structure
        try:
            return pd.json_normalize(data)
        except Exception:
            return pd.DataFrame([data])
    
    def _normalize_xml_data(self, source_name: str, root) -> pd.DataFrame:
        """Normalize XML data to consistent DataFrame format"""
        
        records = []
        
        if source_name == "noaa_forecasts":
            # NOAA weather forecast XML parsing
            for forecast in root.findall('.//forecast'):
                record = {
                    'location': forecast.find('location').text if forecast.find('location') is not None else '',
                    'forecast_time': pd.to_datetime(forecast.find('forecast_time').text) if forecast.find('forecast_time') is not None else None,
                    'valid_time': pd.to_datetime(forecast.find('valid_time').text) if forecast.find('valid_time') is not None else None,
                    'stage': float(forecast.find('stage').text) if forecast.find('stage') is not None and forecast.find('stage').text else np.nan,
                    'flow': float(forecast.find('flow').text) if forecast.find('flow') is not None and forecast.find('flow').text else np.nan,
                    'precipitation': float(forecast.find('precipitation').text) if forecast.find('precipitation') is not None and forecast.find('precipitation').text else np.nan
                }
                records.append(record)
        
        else:
            # Generic XML parsing
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    record = {
                        'element': elem.tag,
                        'value': elem.text.strip(),
                        'attributes': dict(elem.attrib)
                    }
                    records.append(record)
        
        return pd.DataFrame(records)
    
    def transform_and_enrich(self, extracted_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Transform extracted data and add semantic enrichments
        """
        enriched_data = {}
        
        for source_name, df in extracted_data.items():
            if df.empty:
                enriched_data[source_name] = df
                continue
            
            # Apply source-specific transformations
            if source_name == "usgs_gauges":
                enriched_df = self._enrich_hydrological_data(df)
            elif source_name == "ais_vessels":
                enriched_df = self._enrich_vessel_data(df)
            elif source_name == "commodity_prices":
                enriched_df = self._enrich_commodity_data(df)
            else:
                enriched_df = self._apply_generic_enrichment(source_name, df)
            
            # Add universal semantic annotations
            enriched_df = self._add_semantic_annotations(source_name, enriched_df)
            
            enriched_data[source_name] = enriched_df
        
        return enriched_data
    
    def _enrich_hydrological_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich hydrological data with semantic context"""
        
        enriched_df = df.copy()
        
        # Add semantic URIs
        enriched_df['site_uri'] = enriched_df['site_code'].apply(
            lambda x: f"http://hydrology.usgs.gov/site/{x}"
        )
        
        # Classify parameters
        def classify_parameter(param_code):
            if param_code in ['00065', '62614']:  # Stage/Water Level
                return 'water_level'
            elif param_code in ['00060', '30208']:  # Discharge/Flow
                return 'flow_rate'
            elif param_code in ['00010']:  # Temperature
                return 'water_temperature'
            else:
                return 'other'
        
        enriched_df['parameter_category'] = enriched_df['parameter_code'].apply(classify_parameter)
        
        # Add navigation impact assessment
        def assess_navigation_impact(row):
            if row['parameter_category'] == 'water_level':
                if row['value'] < 9:  # feet - typical minimum navigation depth
                    return 'high_risk'
                elif row['value'] < 12:
                    return 'moderate_risk'
                else:
                    return 'low_risk'
            return 'unknown'
        
        enriched_df['navigation_risk'] = enriched_df.apply(assess_navigation_impact, axis=1)
        
        # Add river mile approximation based on coordinates
        enriched_df['river_mile'] = enriched_df.apply(self._estimate_river_mile, axis=1)
        
        # Add semantic triples to RDF graph
        for _, row in enriched_df.iterrows():
            self._add_hydrological_triples(row)
        
        return enriched_df
    
    def _enrich_vessel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich vessel data with semantic context"""
        
        enriched_df = df.copy()
        
        # Add semantic URIs
        enriched_df['vessel_uri'] = enriched_df['vessel_id'].apply(
            lambda x: f"http://transportation.dot.gov/vessel/{x}"
        )
        
        # Classify vessel types
        def classify_vessel_type(ship_type_code):
            if ship_type_code in [31, 32]:  # Towing vessel
                return 'towboat'
            elif ship_type_code in [36, 37]:  # Pleasure craft, sailing vessel
                return 'recreational'
            else:
                return 'commercial'
        
        enriched_df['vessel_category'] = enriched_df['vessel_type'].apply(
            lambda x: classify_vessel_type(int(x)) if str(x).isdigit() else 'unknown'
        )
        
        # Calculate vessel in Mississippi River system
        def is_on_mississippi_system(lat, lon):
            # Simplified bounding box for Mississippi River system
            # More sophisticated geospatial analysis would use actual river geometry
            if 29.0 <= lat <= 47.9 and -95.2 <= lon <= -89.0:
                return True
            return False
        
        enriched_df['on_mississippi_system'] = enriched_df.apply(
            lambda row: is_on_mississippi_system(row['latitude'], row['longitude']), axis=1
        )
        
        # Estimate cargo type based on vessel characteristics
        def estimate_cargo_type(vessel_name, vessel_type):
            name_lower = str(vessel_name).lower()
            if any(grain in name_lower for grain in ['grain', 'corn', 'soy', 'wheat']):
                return 'agricultural'
            elif any(energy in name_lower for energy in ['coal', 'petroleum', 'fuel', 'oil']):
                return 'energy'
            elif 'container' in name_lower:
                return 'container'
            else:
                return 'general'
        
        enriched_df['estimated_cargo_type'] = enriched_df.apply(
            lambda row: estimate_cargo_type(row['vessel_name'], row['vessel_type']), axis=1
        )
        
        # Add semantic triples
        for _, row in enriched_df.iterrows():
            if row['on_mississippi_system']:
                self._add_vessel_triples(row)
        
        return enriched_df
    
    def _enrich_commodity_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich commodity price data with semantic context"""
        
        enriched_df = df.copy()
        
        # Add semantic URIs
        enriched_df['commodity_uri'] = enriched_df['commodity'].apply(
            lambda x: f"http://commodities.usda.gov/commodity/{x.lower().replace(' ', '_')}"
        )
        
        enriched_df['location_uri'] = enriched_df['location'].apply(
            lambda x: f"http://geonames.org/search?q={x.replace(' ', '+')}"
        )
        
        # Classify commodities by transportation mode preference
        def transportation_preference(commodity):
            grain_commodities = ['corn', 'soybeans', 'wheat', 'grain']
            bulk_commodities = ['coal', 'iron ore', 'sand', 'gravel']
            
            commodity_lower = str(commodity).lower()
            
            if any(grain in commodity_lower for grain in grain_commodities):
                return 'barge_preferred'
            elif any(bulk in commodity_lower for bulk in bulk_commodities):
                return 'barge_required'
            else:
                return 'multimodal'
        
        enriched_df['transport_preference'] = enriched_df['commodity'].apply(transportation_preference)
        
        # Calculate price volatility and trends
        if 'report_date' in enriched_df.columns:
            enriched_df = enriched_df.sort_values('report_date')
            
            # Calculate 30-day rolling price volatility
            enriched_df['price_volatility'] = enriched_df.groupby('commodity')['price'].rolling(
                window=30, min_periods=5
            ).std().reset_index(0, drop=True)
            
            # Calculate price trend (30-day change)
            enriched_df['price_trend'] = enriched_df.groupby('commodity')['price'].pct_change(30)
        
        # Add market opportunity scoring
        def calculate_market_opportunity(row):
            # Simplified scoring based on price and volatility
            if pd.isna(row['price']) or pd.isna(row.get('price_volatility', 0)):
                return 0
            
            # Higher prices with lower volatility = better opportunity
            price_score = min(row['price'] / 100, 1.0)  # Normalize to 0-1
            volatility_penalty = min(row.get('price_volatility', 0) / 50, 1.0)
            
            return max(0, price_score - volatility_penalty)
        
        enriched_df['market_opportunity_score'] = enriched_df.apply(calculate_market_opportunity, axis=1)
        
        # Add semantic triples
        for _, row in enriched_df.iterrows():
            self._add_commodity_triples(row)
        
        return enriched_df
    
    def _apply_generic_enrichment(self, source_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Apply generic semantic enrichment to any data source"""
        
        enriched_df = df.copy()
        
        # Add data quality metrics
        enriched_df['data_completeness'] = enriched_df.notna().sum(axis=1) / len(df.columns)
        
        # Add temporal context if timestamp columns exist
        timestamp_columns = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        if timestamp_columns:
            enriched_df['data_freshness_hours'] = (
                datetime.now() - pd.to_datetime(enriched_df[timestamp_columns[0]])
            ).dt.total_seconds() / 3600
        
        return enriched_df
    
    def _add_semantic_annotations(self, source_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Add universal semantic annotations to any dataframe"""
        
        annotated_df = df.copy()
        
        # Add provenance information
        annotated_df['data_source'] = source_name
        annotated_df['extraction_timestamp'] = datetime.now()
        annotated_df['semantic_version'] = "1.0"
        
        # Add data quality assessment
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) > 0:
            annotated_df['outlier_score'] = 0
            for col in numeric_columns:
                if not df[col].empty and not df[col].isna().all():
                    q75, q25 = np.percentile(df[col].dropna(), [75, 25])
                    iqr = q75 - q25
                    if iqr > 0:
                        lower_bound = q25 - (1.5 * iqr)
                        upper_bound = q75 + (1.5 * iqr)
                        outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
                        annotated_df['outlier_score'] += outliers.astype(int)
        
        return annotated_df
    
    def _estimate_river_mile(self, row) -> float:
        """Estimate river mile based on latitude/longitude coordinates"""
        
        # Simplified river mile estimation using linear approximation
        # In production, this would use actual river geometry and spatial analysis
        
        lat = row['latitude']
        lon = row['longitude']
        
        if pd.isna(lat) or pd.isna(lon):
            return np.nan
        
        # Mississippi River approximate coordinates
        # Head of Navigation (Minneapolis): ~44.98°N, -93.27°W (Mile 0)
        # Mouth (New Orleans): ~29.95°N, -90.07°W (Mile 2320)
        
        head_lat, head_lon = 44.98, -93.27
        mouth_lat, mouth_lon = 29.95, -90.07
        
        # Calculate relative position along river (very simplified)
        lat_range = head_lat - mouth_lat
        lon_range = head_lon - mouth_lon
        
        if lat_range == 0 or lon_range == 0:
            return np.nan
        
        # Linear interpolation (simplified - real calculation would use river path)
        lat_progress = (head_lat - lat) / lat_range
        estimated_mile = lat_progress * 2320  # Total river miles
        
        return max(0, min(2320, estimated_mile))
    
    def _add_hydrological_triples(self, row):
        """Add RDF triples for hydrological data"""
        
        site_uri = URIRef(row['site_uri'])
        
        # Site information
        self.rdf_graph.add((site_uri, RDF.type, HYDRO.GaugeStation))
        self.rdf_graph.add((site_uri, RDFS.label, Literal(row['site_name'])))
        self.rdf_graph.add((site_uri, GEO.lat, Literal(row['latitude'])))
        self.rdf_graph.add((site_uri, GEO.long, Literal(row['longitude'])))
        
        if not pd.isna(row['river_mile']):
            self.rdf_graph.add((site_uri, NAV.riverMile, Literal(row['river_mile'])))
        
        # Measurement
        measurement_uri = URIRef(f"{row['site_uri']}/measurement/{row['timestamp'].isoformat()}")
        self.rdf_graph.add((measurement_uri, RDF.type, HYDRO.Measurement))
        self.rdf_graph.add((measurement_uri, HYDRO.measurementSite, site_uri))
        self.rdf_graph.add((measurement_uri, HYDRO.measurementTime, 
                          Literal(row['timestamp'], datatype=rdflib.XSD.dateTime)))
        
        if row['parameter_category'] == 'water_level':
            self.rdf_graph.add((measurement_uri, HYDRO.hasWaterLevel, Literal(row['value'])))
        elif row['parameter_category'] == 'flow_rate':
            self.rdf_graph.add((measurement_uri, HYDRO.hasFlowRate, Literal(row['value'])))
        
        # Navigation risk assessment
        if row['navigation_risk'] != 'unknown':
            self.rdf_graph.add((measurement_uri, NAV.navigationRisk, Literal(row['navigation_risk'])))
    
    def _add_vessel_triples(self, row):
        """Add RDF triples for vessel data"""
        
        vessel_uri = URIRef(row['vessel_uri'])
        
        # Vessel information
        self.rdf_graph.add((vessel_uri, RDF.type, TRANSPORT.Vessel))
        self.rdf_graph.add((vessel_uri, RDFS.label, Literal(row['vessel_name'])))
        self.rdf_graph.add((vessel_uri, TRANSPORT.vesselType, Literal(row['vessel_category'])))
        
        # Position
        position_uri = URIRef(f"{row['vessel_uri']}/position/{row['timestamp'].isoformat()}")
        self.rdf_graph.add((position_uri, RDF.type, TRANSPORT.VesselPosition))
        self.rdf_graph.add((position_uri, TRANSPORT.vessel, vessel_uri))
        self.rdf_graph.add((position_uri, GEO.lat, Literal(row['latitude'])))
        self.rdf_graph.add((position_uri, GEO.long, Literal(row['longitude'])))
        self.rdf_graph.add((position_uri, TRANSPORT.speed, Literal(row['speed'])))
        self.rdf_graph.add((position_uri, TRANSPORT.heading, Literal(row['heading'])))
        self.rdf_graph.add((position_uri, TIME.inXSDDateTime, 
                          Literal(row['timestamp'], datatype=rdflib.XSD.dateTime)))
        
        # Cargo estimation
        if row['estimated_cargo_type'] != 'general':
            self.rdf_graph.add((vessel_uri, TRANSPORT.estimatedCargoType, 
                              Literal(row['estimated_cargo_type'])))
    
    def _add_commodity_triples(self, row):
        """Add RDF triples for commodity data"""
        
        commodity_uri = URIRef(row['commodity_uri'])
        location_uri = URIRef(row['location_uri'])
        
        # Commodity information
        self.rdf_graph.add((commodity_uri, RDF.type, COMMODITY.AgriculturalCommodity))
        self.rdf_graph.add((commodity_uri, RDFS.label, Literal(row['commodity'])))
        self.rdf_graph.add((commodity_uri, COMMODITY.transportPreference, 
                          Literal(row['transport_preference'])))
        
        # Price information
        price_uri = URIRef(f"{row['commodity_uri']}/price/{row['report_date'].isoformat()}")
        self.rdf_graph.add((price_uri, RDF.type, COMMODITY.MarketPrice))
        self.rdf_graph.add((price_uri, COMMODITY.commodity, commodity_uri))
        self.rdf_graph.add((price_uri, COMMODITY.location, location_uri))
        self.rdf_graph.add((price_uri, COMMODITY.hasPrice, Literal(row['price'])))
        self.rdf_graph.add((price_uri, COMMODITY.priceUnit, Literal(row['units'])))
        self.rdf_graph.add((price_uri, TIME.inXSDDateTime, 
                          Literal(row['report_date'], datatype=rdflib.XSD.dateTime)))
        
        if not pd.isna(row['market_opportunity_score']):
            self.rdf_graph.add((price_uri, COMMODITY.marketOpportunityScore, 
                              Literal(row['market_opportunity_score'])))
    
    def load_to_knowledge_graph(self, enriched_data: Dict[str, pd.DataFrame]):
        """
        Load enriched data to both KuzuDB and RDF store
        """
        
        # Save RDF graph
        self.rdf_graph.serialize(destination=self.rdf_store_path, format='turtle')
        logger.info(f"Saved RDF knowledge graph to {self.rdf_store_path}")
        
        # Load to KuzuDB
        for source_name, df in enriched_data.items():
            if not df.empty:
                self._load_to_kuzu(source_name, df)
        
        logger.info("Successfully loaded all data to knowledge graph")
    
    def _load_to_kuzu(self, source_name: str, df: pd.DataFrame):
        """Load DataFrame to KuzuDB"""
        
        try:
            # Create temporary CSV file
            csv_path = f"/tmp/{source_name}_enriched.csv"
            df.to_csv(csv_path, index=False)
            
            # Map source names to KuzuDB table names
            table_mapping = {
                'usgs_gauges': 'HydroReading',
                'ais_vessels': 'VesselPosition',
                'commodity_prices': 'MarketPrice',
                'noaa_forecasts': 'WeatherForecast',
                'usace_locks': 'Lock',
                'rail_rates': 'TransportRate'
            }
            
            table_name = table_mapping.get(source_name, 'GenericData')
            
            # Load CSV to KuzuDB (simplified - production would handle schema mapping)
            self.kuzu_conn.execute(f"COPY {table_name} FROM '{csv_path}' (HEADER=true)")
            
            logger.info(f"Loaded {len(df)} records from {source_name} to {table_name}")
            
        except Exception as e:
            logger.error(f"Failed to load {source_name} to KuzuDB: {e}")
    
    async def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete ET(K)L pipeline
        Returns summary statistics and quality metrics
        """
        
        logger.info("Starting semantic enrichment pipeline")
        start_time = datetime.now()
        
        # Extract
        logger.info("Extracting data from sources...")
        extracted_data = await self.extract_data_sources()
        
        # Transform & Knowledge
        logger.info("Transforming and enriching data...")
        enriched_data = self.transform_and_enrich(extracted_data)
        
        # Load
        logger.info("Loading to knowledge graph...")
        self.load_to_knowledge_graph(enriched_data)
        
        # Generate pipeline summary
        end_time = datetime.now()
        pipeline_duration = (end_time - start_time).total_seconds()
        
        summary = {
            'pipeline_start': start_time,
            'pipeline_end': end_time,
            'duration_seconds': pipeline_duration,
            'sources_processed': len(extracted_data),
            'total_records': sum(len(df) for df in enriched_data.values()),
            'rdf_triples': len(self.rdf_graph),
            'data_quality_summary': self._generate_quality_summary(enriched_data),
            'semantic_coverage': self._calculate_semantic_coverage(enriched_data)
        }
        
        logger.info(f"Pipeline completed in {pipeline_duration:.1f} seconds")
        logger.info(f"Processed {summary['total_records']} records from {summary['sources_processed']} sources")
        logger.info(f"Generated {summary['rdf_triples']} RDF triples")
        
        return summary
    
    def _generate_quality_summary(self, enriched_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate data quality summary across all sources"""
        
        total_records = 0
        total_complete_records = 0
        quality_scores = []
        
        for source_name, df in enriched_data.items():
            if df.empty:
                continue
                
            total_records += len(df)
            
            # Calculate completeness
            if 'data_completeness' in df.columns:
                complete_records = (df['data_completeness'] >= 0.8).sum()
                total_complete_records += complete_records
                quality_scores.extend(df['data_completeness'].tolist())
        
        return {
            'total_records': total_records,
            'complete_records': total_complete_records,
            'completeness_rate': total_complete_records / total_records if total_records > 0 else 0,
            'average_quality_score': np.mean(quality_scores) if quality_scores else 0,
            'quality_distribution': {
                'high_quality': sum(1 for score in quality_scores if score >= 0.8),
                'medium_quality': sum(1 for score in quality_scores if 0.5 <= score < 0.8),
                'low_quality': sum(1 for score in quality_scores if score < 0.5)
            }
        }
    
    def _calculate_semantic_coverage(self, enriched_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate semantic enrichment coverage"""
        
        semantic_fields = ['semantic_version', 'data_source', 'extraction_timestamp']
        domain_specific_fields = {
            'usgs_gauges': ['site_uri', 'navigation_risk', 'river_mile'],
            'ais_vessels': ['vessel_uri', 'vessel_category', 'estimated_cargo_type'],
            'commodity_prices': ['commodity_uri', 'transport_preference', 'market_opportunity_score']
        }
        
        coverage_stats = {}
        
        for source_name, df in enriched_data.items():
            if df.empty:
                coverage_stats[source_name] = {'semantic_coverage': 0, 'domain_coverage': 0}
                continue
            
            # Basic semantic coverage
            semantic_present = sum(1 for field in semantic_fields if field in df.columns)
            semantic_coverage = semantic_present / len(semantic_fields)
            
            # Domain-specific coverage
            domain_fields = domain_specific_fields.get(source_name, [])
            if domain_fields:
                domain_present = sum(1 for field in domain_fields if field in df.columns)
                domain_coverage = domain_present / len(domain_fields)
            else:
                domain_coverage = 1.0  # No domain requirements
            
            coverage_stats[source_name] = {
                'semantic_coverage': semantic_coverage,
                'domain_coverage': domain_coverage,
                'total_fields': len(df.columns),
                'semantic_fields': semantic_present,
                'domain_fields': len(domain_fields)
            }
        
        return coverage_stats


# Usage example and testing
if __name__ == "__main__":
    async def main():
        # Initialize pipeline
        pipeline = SemanticEnrichmentPipeline(
            kuzu_db_path="./mississippi_navigation.kuzu",
            rdf_store_path="./navigation_knowledge_graph.ttl"
        )
        
        # Run full pipeline
        summary = await pipeline.run_full_pipeline()
        
        # Print results
        print(json.dumps(summary, indent=2, default=str))
        
        # Example semantic queries
        print("\n=== Sample Knowledge Graph Queries ===")
        
        # SPARQL query example
        query = """
        PREFIX nav: <http://mississippi.navigation.org/ontology/>
        PREFIX hydro: <http://hydrology.usgs.gov/ontology/>
        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        
        SELECT ?site ?name ?waterLevel ?risk WHERE {
            ?site a hydro:GaugeStation ;
                  rdfs:label ?name ;
                  geo:lat ?lat ;
                  geo:long ?lon .
            ?measurement hydro:measurementSite ?site ;
                        hydro:hasWaterLevel ?waterLevel ;
                        nav:navigationRisk ?risk .
            FILTER (?risk = "high_risk")
        }
        ORDER BY ?waterLevel
        """
        
        results = pipeline.rdf_graph.query(query)
        print("High-risk navigation sites:")
        for row in results:
            print(f"  {row.name}: {row.waterLevel}ft - {row.risk}")
    
    # Run the example
    import asyncio
    asyncio.run(main())