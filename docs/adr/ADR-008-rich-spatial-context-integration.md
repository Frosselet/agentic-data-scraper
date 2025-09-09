# ADR-008: Rich Spatial Context Integration with GeoNames and OSM

## Status
**PROPOSED** - Critical enhancement for comprehensive spatial intelligence

## Context

Current spatial annotations in our semantic enrichment are minimal and lack hierarchical context:

```
❌ Current Spatial Data (Insufficient):
• geospatial_data (confidence: 0.80)  ← Vague classification
• coordinate: 44.9444444 ← Raw latitude, no context

❌ Missing Critical Spatial Intelligence:
- Administrative hierarchy (country → state → county → city)
- River geometries as polylines for distance calculations
- Points of Interest (POIs) and infrastructure locations
- Real geometric distance calculations vs. Haversine approximations
- Resolvable GeoNames URIs for spatial entity linking
```

This limits our ability to provide rich spatial context for navigation intelligence and analytics.

## Decision

We will implement **comprehensive spatial intelligence** through integration with:

1. **GeoNames API** for administrative hierarchy and entity resolution
2. **OpenStreetMap Overpass API** for geometric features (rivers, roads, infrastructure)
3. **Spatial calculation engine** for real distance computations
4. **Hierarchical spatial context** for every data point

## Spatial Intelligence Architecture

### 1. Administrative Hierarchy Resolution
```python
class GeoNamesEnhancer:
    def __init__(self, geonames_username: str):
        self.username = geonames_username
        self.base_url = "http://api.geonames.org"
        
    async def resolve_spatial_hierarchy(self, lat: float, lon: float) -> Dict:
        """Extract complete administrative hierarchy from coordinates"""
        response = await self.reverse_geocode(lat, lon)
        
        return {
            'coordinates': {'latitude': lat, 'longitude': lon},
            'country': response.get('countryName'),
            'country_code': response.get('countryCode'),
            'state': response.get('adminName1'),  
            'county': response.get('adminName2'),
            'city': response.get('name'),
            'postal_code': response.get('postalCode'),
            'geonames_id': response.get('geonameId'),
            'geonames_uri': f"http://geonames.org/{response.get('geonameId')}",
            'population': response.get('population'),
            'timezone': response.get('timezone', {}).get('timeZoneId')
        }
```

### 2. Geometric Feature Extraction
```python
class OSMGeometryExtractor:
    def __init__(self):
        self.overpass_url = "http://overpass-api.de/api/interpreter"
        
    async def extract_river_geometry(self, river_name: str, bbox: Dict) -> Dict:
        """Extract river polyline geometry from OpenStreetMap"""
        query = f"""
        [out:json];
        (
          way["waterway"="river"]["name"~"{river_name}"]
          ({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        );
        out geom;
        """
        
        response = await self.execute_overpass_query(query)
        
        return {
            'geometry_type': 'LineString',
            'coordinates': self.extract_coordinates(response),
            'osm_id': response['elements'][0]['id'],
            'osm_uri': f"http://openstreetmap.org/way/{response['elements'][0]['id']}",
            'properties': {
                'waterway': 'river',
                'name': river_name
            }
        }
```

### 3. Enhanced Spatial Collector
```python
class EnhancedSpatialCollector(SemanticCollectorBase):
    def __init__(self, geonames_enhancer: GeoNamesEnhancer, osm_extractor: OSMGeometryExtractor):
        self.geonames = geonames_enhancer
        self.osm = osm_extractor
        
    async def apply_spatial_enrichment(self, structured_data: Dict) -> Dict:
        """Apply comprehensive spatial enrichment"""
        spatial_context = {}
        
        # Extract coordinates
        lat = structured_data.get('latitude')
        lon = structured_data.get('longitude')
        
        if lat and lon:
            # Administrative hierarchy
            hierarchy = await self.geonames.resolve_spatial_hierarchy(lat, lon)
            spatial_context['administrative'] = hierarchy
            
            # Nearby infrastructure
            infrastructure = await self.find_nearby_infrastructure(lat, lon)
            spatial_context['infrastructure'] = infrastructure
            
            # Waterway context if applicable
            if self.is_waterway_related(structured_data):
                waterway_info = await self.extract_waterway_context(lat, lon)
                spatial_context['waterway'] = waterway_info
                
        return spatial_context
```

### 4. Real Distance Calculations
```python
class SpatialAnalyticsEngine:
    def calculate_real_distance(self, point1: Dict, point2: Dict, geometry: Dict = None) -> float:
        """Calculate real distance using geometries when available"""
        
        if geometry and geometry.get('geometry_type') == 'LineString':
            # Use actual path geometry for accurate distance
            return self.calculate_path_distance(point1, point2, geometry['coordinates'])
        else:
            # Fallback to Haversine for straight-line distance
            return self.haversine_distance(point1, point2)
            
    def calculate_river_mile(self, lat: float, lon: float, river_geometry: Dict) -> float:
        """Calculate river mile position using actual river geometry"""
        point = {'latitude': lat, 'longitude': lon}
        closest_point_on_river = self.find_closest_point_on_line(point, river_geometry['coordinates'])
        
        # Calculate distance from river mouth to this point
        return self.calculate_distance_along_path(river_geometry['coordinates'], closest_point_on_river)
```

## Enhanced Semantic Annotations

### Before (Minimal):
```json
{
  "spatial_context": {
    "latitude": 44.9444444,
    "longitude": -93.0932654
  }
}
```

### After (Comprehensive):
```json
{
  "spatial_context": {
    "coordinates": {
      "latitude": 44.9444444,
      "longitude": -93.0932654,
      "coordinate_system": "WGS84"
    },
    "administrative": {
      "country": "United States",
      "country_code": "US", 
      "state": "Minnesota",
      "county": "Ramsey County",
      "city": "Saint Paul",
      "postal_code": "55101",
      "geonames_id": "5037649",
      "geonames_uri": "http://geonames.org/5037649",
      "population": 308096,
      "timezone": "America/Chicago"
    },
    "waterway": {
      "name": "Mississippi River",
      "river_mile": 847.9,
      "navigation_pool": "Pool 1",
      "osm_uri": "http://openstreetmap.org/way/8591149",
      "geometry_type": "LineString",
      "upstream_locks": ["Lock and Dam No. 1"],
      "downstream_locks": ["Lock and Dam No. 2"]
    },
    "infrastructure": {
      "nearest_port": {
        "name": "Port of Saint Paul",
        "distance_km": 2.3,
        "type": "inland_port"
      },
      "nearest_bridge": {
        "name": "Robert Street Bridge", 
        "distance_km": 0.8,
        "clearance_vertical_m": 22.9
      }
    }
  }
}
```

## Temporal-Spatial Canvas Architecture

### Dashboard Visualization Concept
```
┌─────────────────────────────────┬─────────────────────────┐
│ Interactive Spatial Canvas      │ Analytics Panel         │
│                                 │                         │
│ 🗺️  Base Layers:                │ 📊 Time Series          │
│   • Countries, States, Counties │ 📈 Quality Metrics      │
│   • Rivers (polylines)          │ 🎯 KPIs Dashboard       │
│   • Cities, Ports (points)      │                         │
│                                 │ 🕒 Time Controls:        │
│ 🚢 Dynamic Layers:              │   ◀ ⏸ ▶ [████████]      │
│   • Vessel positions/tracks     │   Jan ──────────── Dec  │
│   • Water levels/flow rates     │                         │
│   • Commodity flows             │ 🔍 Filters:             │
│   • Traffic congestion          │   □ Vessels             │
│                                 │   □ Water Levels        │
│ 📍 Context on Hover:            │   □ Infrastructure      │
│   Site: 05331000                │   □ Commodities         │
│   River Mile: 847.9             │                         │
│   Saint Paul, MN                │                         │
│   Pool 1, Mississippi River     │                         │
└─────────────────────────────────┴─────────────────────────┘
```

## Implementation Plan

### Phase 1: GeoNames Integration (Week 1-2)
- Set up GeoNames API integration
- Implement administrative hierarchy resolution
- Add resolvable GeoNames URIs to spatial annotations

### Phase 2: OSM Geometry Extraction (Week 3-4)  
- Implement Overpass API queries for river geometries
- Extract infrastructure locations (ports, bridges, locks)
- Calculate real distances using geometric paths

### Phase 3: Enhanced Spatial Collector (Week 5-6)
- Integrate GeoNames and OSM into semantic collectors
- Update all spatial annotations with rich context
- Test with live USGS and AIS data

### Phase 4: Spatial Analytics Engine (Week 7-8)
- Implement real distance calculations
- River mile calculations using actual geometry
- Spatial relationship analysis (nearest infrastructure)

## Benefits

### 1. Comprehensive Spatial Intelligence
- Every data point has complete geographic context
- Administrative hierarchy enables aggregation at any level
- Real geometries enable accurate distance/time calculations

### 2. Enhanced Decision Making
- Navigation decisions based on real spatial relationships
- Infrastructure analysis with actual positions and clearances
- Commodity flow analysis with accurate transport distances

### 3. Dashboard-Ready Visualization
- Rich spatial data ready for map-based dashboards
- Temporal-spatial canvas for historical analysis
- Context-aware analytics with geographic drill-down

### 4. Scalable Spatial Architecture
- Caching of GeoNames lookups for performance
- Geometric simplification for different zoom levels
- Integration with existing semantic enrichment pipeline

## Success Criteria

1. **Every data point** has complete administrative hierarchy (country → city)
2. **All waterway data** includes river mile calculations using real geometry
3. **Infrastructure relationships** calculated using actual positions
4. **Resolvable spatial URIs** link to GeoNames and OSM
5. **Real distance calculations** replace Haversine approximations
6. **Notebook demonstration** shows rich spatial context instead of minimal coordinates

## Related ADRs

- ADR-007: Resolvable Semantic URIs (spatial URIs will be resolvable)
- ADR-009: Temporal-Spatial Canvas Architecture (proposed)
- ADR-006: ET(K)L Semantic-First Pattern (enhanced with spatial intelligence)