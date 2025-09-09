# ADR-009: Temporal-Spatial Canvas Architecture for Navigation Intelligence

## Status
**PROPOSED** - Foundation for advanced analytics and dashboard visualization

## Context

Our semantic ET(K)L system successfully captures rich data, but we need a unified architecture for temporal-spatial analytics and visualization. Current challenges:

```
❌ Current Limitations:
- Data points exist in isolation without temporal-spatial relationships
- No unified canvas for viewing historical trends with geographic context  
- Dashboard concepts exist but lack architectural foundation
- Temporal analysis disconnected from spatial context
- No framework for "playing back" historical data changes

🎯 Vision: Unified Temporal-Spatial Analytics
- Every data point positioned in space AND time
- Interactive canvas with time cursor for historical analysis
- Real-time updates with historical delta visualization
- Context-aware analytics with geographic drill-down
```

The goal is to create an **intelligent temporal-spatial canvas** that makes patterns, relationships, and insights immediately visible.

## Decision

We will implement a **Temporal-Spatial Canvas Architecture** with these core components:

1. **Unified Data Model** - Every entity has temporal + spatial + semantic dimensions
2. **Time-Series Spatial Index** - Efficient queries across time and space
3. **Interactive Canvas Framework** - Map-based visualization with time controls
4. **Real-time Delta Engine** - Show changes over time with spatial context
5. **Context-Aware Analytics** - Insights that consider temporal-spatial relationships

## Architecture Overview

```mermaid
graph TB
    subgraph "Data Layer"
        A[Semantic ET(K)L Collectors] --> B[Temporal-Spatial Indexer]
        B --> C[(Time-Series Spatial DB)]
    end
    
    subgraph "Analytics Layer"  
        C --> D[Delta Computation Engine]
        C --> E[Spatial Relationship Engine]
        C --> F[Temporal Pattern Engine]
    end
    
    subgraph "Canvas Layer"
        D --> G[Interactive Map Canvas]
        E --> G
        F --> G
        G --> H[Time Cursor Controls]
        G --> I[Spatial Context Panel]
        G --> J[Analytics Dashboard]
    end
    
    subgraph "User Experience"
        H --> K[Historical Playback]
        I --> L[Geographic Drill-down]
        J --> M[Real-time Insights]
    end
```

## Core Components

### 1. Unified Temporal-Spatial Data Model
```python
@dataclass
class TemporalSpatialEntity:
    """Every entity in our system has temporal + spatial + semantic dimensions"""
    
    # Identity
    entity_id: str
    entity_type: str  # vessel, gauge_station, port, commodity_flow
    
    # Temporal dimension
    timestamp: datetime
    valid_from: datetime
    valid_until: Optional[datetime]
    temporal_precision: str  # second, minute, hour, day
    
    # Spatial dimension  
    geometry: Dict  # Point, LineString, Polygon (GeoJSON)
    spatial_hierarchy: Dict  # country → state → county → city
    spatial_relationships: List[Dict]  # nearby entities with distances
    
    # Semantic dimension
    domain_context: Dict  # hydrology, transportation, economics
    quality_metrics: Dict
    semantic_annotations: Dict
    
    # Temporal-spatial metrics
    movement_vector: Optional[Dict]  # speed, heading, acceleration
    spatial_footprint: Optional[Dict]  # area of influence/effect
    temporal_pattern: Optional[Dict]  # seasonal, cyclical, trending
```

### 2. Time-Series Spatial Indexer
```python
class TemporalSpatialIndexer:
    """Efficient indexing for time-series spatial queries"""
    
    def __init__(self, kuzu_db: str, spatial_index: str):
        self.kuzu_conn = kuzu.Connection(kuzu.Database(kuzu_db))
        self.spatial_index = spatial_index  # PostGIS or similar
        
    async def index_entity(self, entity: TemporalSpatialEntity):
        """Index entity across temporal, spatial, and semantic dimensions"""
        
        # Temporal index - efficient time range queries
        await self.create_temporal_index(entity)
        
        # Spatial index - geographic proximity queries  
        await self.create_spatial_index(entity)
        
        # Combined index - spatio-temporal queries
        await self.create_spatiotemporal_index(entity)
        
    async def query_spatiotemporal(self, 
                                 bbox: Dict,
                                 time_range: Tuple[datetime, datetime],
                                 entity_types: List[str] = None) -> List[TemporalSpatialEntity]:
        """Query entities within spatial bounds and time range"""
        pass
```

### 3. Interactive Canvas Framework
```python
class TemporalSpatialCanvas:
    """Interactive map-based canvas with temporal controls"""
    
    def __init__(self):
        self.base_layers = self._initialize_base_layers()
        self.dynamic_layers = {}
        self.time_cursor = datetime.now()
        self.time_window = timedelta(hours=24)
        
    def _initialize_base_layers(self) -> Dict:
        """Static geographic context"""
        return {
            'administrative': {  # Countries, states, counties, cities
                'source': 'natural_earth',
                'style': {'fill': '#f0f0f0', 'stroke': '#999'}
            },
            'waterways': {  # Rivers, lakes as polylines/polygons
                'source': 'openstreetmap',
                'style': {'stroke': '#4a90e2', 'stroke-width': 2}
            },
            'infrastructure': {  # Ports, locks, bridges as points
                'source': 'our_database',
                'style': {'marker': 'circle', 'color': '#333'}
            }
        }
        
    async def add_dynamic_layer(self, layer_name: str, entity_type: str, style: Dict):
        """Add time-varying data layer (vessels, water levels, flows)"""
        self.dynamic_layers[layer_name] = {
            'entity_type': entity_type,
            'style': style,
            'data': await self.load_temporal_data(entity_type)
        }
        
    async def update_time_cursor(self, new_time: datetime):
        """Move time cursor and update all dynamic layers"""
        self.time_cursor = new_time
        
        for layer_name, layer in self.dynamic_layers.items():
            # Get data valid at this time point
            layer['current_data'] = await self.query_at_time(
                layer['entity_type'], 
                new_time
            )
            
            # Calculate deltas from previous time
            layer['deltas'] = await self.calculate_temporal_deltas(
                layer['entity_type'],
                new_time - timedelta(hours=1),
                new_time
            )
```

### 4. Real-time Delta Engine
```python
class TemporalDeltaEngine:
    """Calculate and visualize changes over time with spatial context"""
    
    async def calculate_spatial_deltas(self, 
                                     entity_type: str,
                                     time1: datetime, 
                                     time2: datetime) -> Dict:
        """Calculate what changed spatially between two time points"""
        
        entities_t1 = await self.query_entities_at_time(entity_type, time1)
        entities_t2 = await self.query_entities_at_time(entity_type, time2)
        
        return {
            'moved': self._find_moved_entities(entities_t1, entities_t2),
            'appeared': self._find_new_entities(entities_t1, entities_t2),
            'disappeared': self._find_removed_entities(entities_t1, entities_t2),
            'value_changes': self._find_value_changes(entities_t1, entities_t2)
        }
        
    async def visualize_deltas(self, deltas: Dict) -> Dict:
        """Create visualization layers for temporal changes"""
        return {
            'movement_arrows': self._create_movement_vectors(deltas['moved']),
            'appear_animation': self._create_appear_effects(deltas['appeared']),
            'disappear_animation': self._create_fade_effects(deltas['disappeared']),
            'value_color_coding': self._create_value_change_styling(deltas['value_changes'])
        }
```

## Dashboard User Experience

### Main Interface Layout
```
┌─────────────────────────────────────────────────┬───────────────────────────┐
│ 🗺️ Interactive Temporal-Spatial Canvas          │ 📊 Context Analytics      │
│                                                 │                           │
│ Base Layers (Static):                          │ 📈 Time Series Charts:    │
│ • Countries, states, counties (polygons)       │ • Water levels            │
│ • Rivers, waterways (polylines)                │ • Vessel counts           │
│ • Cities, ports, infrastructure (points)       │ • Commodity flows         │
│                                                 │                           │
│ Dynamic Layers (Time-varying):                 │ 🎯 Current KPIs:          │
│ • 🚢 Vessel positions (animated tracks)         │ • Active vessels: 1,247   │
│ • 🌊 Water levels (color-coded points)          │ • Avg water level: 4.2ft  │
│ • 📦 Commodity flows (animated arrows)          │ • Navigation risk: LOW    │
│ • ⚠️ Navigation alerts (pulsing markers)        │                           │
│                                                 │ 🔍 Spatial Filters:       │
│ 📍 Hover Context Example:                       │ □ Upper Mississippi       │
│    Mississippi River at St. Paul, MN           │ □ Illinois Waterway       │
│    Site: 05331000 | Mile: 847.9               │ □ Ohio River              │
│    Current: 4.77ft | 24h Δ: +0.23ft           │ □ Arkansas River          │
│    Risk: NORMAL | Pool: 1                     │                           │
├─────────────────────────────────────────────────┤ 🚨 Active Alerts:         │
│ 🕒 Time Controls:                              │ • Lock 15 delay: 2hrs     │
│    ◀ ⏸ ▶ [████████████████████████████] ⏩    │ • Low water at Mile 203   │
│    2025-01-15 ←─────── NOW ──────→ 2025-01-31  │                           │
│                                                 │                           │
│ 📊 Playback Speed: [1x] [2x] [5x] [10x]       │ 📋 Selected Entity:       │
│ 🎯 Auto-follow: □ Vessels □ Alerts □ Changes   │    MV GRAIN TRADER        │
│                                                 │    15 barges, 22.5k tons  │
└─────────────────────────────────────────────────┴───────────────────────────┘
```

### Key User Interactions

1. **Time Cursor Movement**:
   - Drag time cursor to see historical data
   - Play/pause for automatic temporal progression
   - Speed controls for rapid historical analysis

2. **Spatial Navigation**:
   - Zoom from continental view to individual locks
   - Click any entity for detailed context panel
   - Hover for instant spatial-temporal context

3. **Layer Management**:
   - Toggle base layers (infrastructure, waterways)
   - Enable/disable dynamic layers (vessels, alerts)
   - Adjust styling and opacity for visual clarity

4. **Delta Visualization**:
   - Movement arrows show vessel track changes
   - Color gradients show water level changes
   - Pulsing indicators show new alerts/events

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3)
- Implement TemporalSpatialEntity data model
- Create time-series spatial indexing in KuzuDB
- Basic temporal queries and data retrieval

### Phase 2: Canvas Framework (Weeks 4-6)  
- Interactive map canvas with base layers
- Time cursor controls and temporal navigation
- Basic dynamic layer rendering

### Phase 3: Delta Engine (Weeks 7-9)
- Temporal delta calculations
- Movement and change visualization  
- Animation framework for temporal transitions

### Phase 4: Advanced Analytics (Weeks 10-12)
- Spatial relationship analysis
- Pattern recognition across time/space
- Predictive analytics integration

### Phase 5: Dashboard Integration (Weeks 13-15)
- Complete user interface implementation
- Real-time data streaming
- Performance optimization and testing

## Benefits

### 1. Unified Analytics Perspective
- Every analysis considers temporal, spatial, and semantic dimensions
- Patterns emerge that would be invisible in siloed data views
- Context-aware insights with geographic and historical perspective

### 2. Intuitive User Experience
- Map-based interface familiar to navigation professionals  
- Time controls enable historical analysis and trend identification
- Hover context provides instant detailed information

### 3. Real-time Decision Support
- Current conditions overlaid on historical patterns
- Spatial relationships inform routing and timing decisions
- Alert systems with geographic and temporal context

### 4. Scalable Visualization Architecture
- Canvas framework supports arbitrary temporal-spatial datasets
- Extensible layer system for new data types and visualizations
- Performance optimized for large-scale real-time data

## Success Criteria

1. **Unified Canvas** displays static and dynamic layers seamlessly
2. **Time Controls** enable smooth navigation through historical data
3. **Delta Visualization** clearly shows changes over time with spatial context  
4. **Context Panels** provide rich information on hover/click
5. **Real-time Updates** reflect live data changes in appropriate layers
6. **Performance** maintains smooth interaction with 10,000+ entities
7. **Extensibility** supports easy addition of new data types and visualizations

## Related ADRs

- ADR-007: Resolvable Semantic URIs (provides linked data for canvas entities)
- ADR-008: Rich Spatial Context Integration (provides spatial hierarchy and relationships)
- ADR-006: ET(K)L Semantic-First Pattern (provides semantically enriched data for canvas)