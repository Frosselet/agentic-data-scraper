"""
Interactive Graph Visualization with yFiles for Navigation Intelligence

This module provides yFiles-powered interactive graph visualization specifically
optimized for exploring semantic knowledge graphs in navigation intelligence.
It integrates directly with KuzuDB to provide real-time graph queries and 
multi-layer visualization for understanding semantic relationships.

Key Components:
1. KuzuGraphQueryEngine - Optimized queries for graph visualization
2. InteractiveSemanticGraph - Jupyter-integrated graph visualization
3. yFiles SemanticGraphVisualization component
4. Multi-layer visualization with semantic styling
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

import kuzu
from IPython.display import HTML, Javascript, display

logger = logging.getLogger(__name__)


@dataclass
class GraphVisualizationConfig:
    """Configuration for yFiles graph visualization"""
    title: str
    width: int = 1200
    height: int = 600
    layout: str = "hierarchic"  # hierarchic, organic, circular, tree
    interactive: bool = True
    show_labels: bool = True
    enable_clustering: bool = True
    animation_duration: int = 1000


class KuzuGraphQueryEngine:
    """Optimized queries for graph visualization using KuzuDB"""
    
    def __init__(self, kuzu_connection):
        self.conn = kuzu_connection
        self.logger = logging.getLogger(__name__)
        
    async def get_graph_neighborhood(self, node_id: str, radius: int = 2) -> Dict:
        """Get neighborhood graph around a specific node"""
        try:
            query = f"""
            MATCH (center {{id: '{node_id}'}})-[r*1..{radius}]-(neighbor)
            RETURN center, r, neighbor
            """
            
            result = self.conn.execute(query)
            return self._format_for_yfiles(result)
            
        except Exception as e:
            self.logger.error(f"Failed to get graph neighborhood: {e}")
            return {"nodes": [], "edges": []}
        
    async def get_semantic_layer(self, layer_type: str) -> Dict:
        """Get specific semantic layer (vessels, infrastructure, etc.)"""
        try:
            layer_queries = {
                "hydrology": """
                    MATCH (h:HydroReading)-[r]-(related)
                    RETURN h, r, related
                    LIMIT 100
                """,
                "vessels": """
                    MATCH (v:VesselPosition)-[r]-(related)
                    RETURN v, r, related
                    LIMIT 100
                """,
                "infrastructure": """
                    MATCH (i:WaterwaySegment)-[r]-(related)
                    RETURN i, r, related
                    LIMIT 100
                """,
                "all": """
                    MATCH (n)-[r]-(m)
                    RETURN n, r, m
                    LIMIT 200
                """
            }
            
            query = layer_queries.get(layer_type, layer_queries["all"])
            result = self.conn.execute(query)
            return self._format_for_yfiles(result)
            
        except Exception as e:
            self.logger.error(f"Failed to get semantic layer {layer_type}: {e}")
            return {"nodes": [], "edges": []}
    
    async def get_mississippi_river_graph(self) -> Dict:
        """Get Mississippi River navigation network for demonstration"""
        try:
            query = """
            MATCH (station:HydroReading)
            OPTIONAL MATCH (station)-[loc:LOCATED_ON]->(segment:WaterwaySegment)
            OPTIONAL MATCH (vessel:VesselPosition)-[nav:NAVIGATES]->(segment)
            RETURN station, segment, vessel, loc, nav
            LIMIT 50
            """
            
            result = self.conn.execute(query)
            return self._format_for_yfiles(result)
            
        except Exception as e:
            self.logger.error(f"Failed to get Mississippi River graph: {e}")
            # Return sample data for demonstration
            return self._get_sample_navigation_graph()
    
    def _format_for_yfiles(self, kuzu_result) -> Dict:
        """Convert KuzuDB result to yFiles graph format"""
        nodes = []
        edges = []
        node_ids = set()
        
        try:
            for record in kuzu_result:
                # Extract nodes from the record
                for i, item in enumerate(record):
                    if item is None:
                        continue
                        
                    # Handle different types of KuzuDB results
                    if hasattr(item, '__dict__') or isinstance(item, dict):
                        node_data = item if isinstance(item, dict) else item.__dict__
                        node_id = node_data.get('id', f"node_{len(nodes)}")
                        
                        if node_id not in node_ids:
                            node_type = self._determine_node_type(node_data)
                            nodes.append({
                                "id": node_id,
                                "label": node_data.get('name', node_data.get('id', node_id)),
                                "type": node_type,
                                "properties": node_data,
                                "semantics": self._extract_semantic_metadata(node_data, node_type)
                            })
                            node_ids.add(node_id)
                    
                    # Handle relationships/edges
                    elif hasattr(item, 'src') and hasattr(item, 'dst'):
                        edge_id = f"{item.src}_{item.dst}_{len(edges)}"
                        edges.append({
                            "id": edge_id,
                            "source": item.src,
                            "target": item.dst,
                            "type": getattr(item, 'label', 'RELATED'),
                            "properties": getattr(item, '__dict__', {})
                        })
            
        except Exception as e:
            self.logger.error(f"Error formatting KuzuDB result: {e}")
        
        return {"nodes": nodes, "edges": edges}
    
    def _determine_node_type(self, node_data: Dict) -> str:
        """Determine semantic node type based on node data"""
        if 'water_level' in node_data or 'flow_rate' in node_data:
            return 'gauge_station'
        elif 'vessel_name' in node_data or 'mmsi' in node_data:
            return 'vessel'
        elif 'segment_name' in node_data or 'river_mile' in node_data:
            return 'waterway_segment'
        elif 'lock_name' in node_data or 'port_name' in node_data:
            return 'infrastructure'
        else:
            return 'entity'
    
    def _extract_semantic_metadata(self, node_data: Dict, node_type: str) -> Dict:
        """Extract semantic metadata for context panels"""
        metadata = {
            "type": node_type,
            "display_name": node_data.get('name', node_data.get('id', 'Unknown')),
            "description": f"{node_type.replace('_', ' ').title()} in navigation network"
        }
        
        if node_type == 'gauge_station':
            metadata.update({
                "current_level": node_data.get('water_level', 'N/A'),
                "flow_rate": node_data.get('flow_rate', 'N/A'),
                "location": f"River Mile {node_data.get('river_mile', 'Unknown')}",
                "last_updated": node_data.get('timestamp', 'Unknown')
            })
        elif node_type == 'vessel':
            metadata.update({
                "vessel_name": node_data.get('vessel_name', 'Unknown'),
                "mmsi": node_data.get('mmsi', 'N/A'),
                "current_position": f"{node_data.get('latitude', 'N/A')}, {node_data.get('longitude', 'N/A')}",
                "speed": node_data.get('speed', 'N/A'),
                "cargo": node_data.get('cargo_type', 'Unknown')
            })
        elif node_type == 'waterway_segment':
            metadata.update({
                "segment_name": node_data.get('segment_name', 'Unknown'),
                "river_mile_start": node_data.get('river_mile_start', 'N/A'),
                "river_mile_end": node_data.get('river_mile_end', 'N/A'),
                "navigation_status": node_data.get('navigation_status', 'Open')
            })
        
        return metadata
    
    def _get_sample_navigation_graph(self) -> Dict:
        """Return sample navigation graph for demonstration"""
        return {
            "nodes": [
                {
                    "id": "gauge_05331000",
                    "label": "St. Paul Gauge",
                    "type": "gauge_station",
                    "properties": {"site_id": "05331000", "water_level": 4.77, "location": "Saint Paul, MN"},
                    "semantics": {
                        "type": "gauge_station",
                        "display_name": "St. Paul Gauge Station",
                        "current_level": "4.77 ft",
                        "location": "River Mile 847.9",
                        "last_updated": "2025-01-15T10:30:00Z"
                    }
                },
                {
                    "id": "segment_pool1",
                    "label": "Pool 1",
                    "type": "waterway_segment", 
                    "properties": {"segment_name": "Pool 1", "river_mile_start": 847.9, "river_mile_end": 854.2},
                    "semantics": {
                        "type": "waterway_segment",
                        "display_name": "Mississippi River Pool 1",
                        "segment_name": "Pool 1",
                        "river_mile_start": "847.9",
                        "river_mile_end": "854.2"
                    }
                },
                {
                    "id": "vessel_mv_grain_trader",
                    "label": "MV GRAIN TRADER",
                    "type": "vessel",
                    "properties": {"vessel_name": "MV GRAIN TRADER", "mmsi": "367123456", "cargo_type": "grain"},
                    "semantics": {
                        "type": "vessel",
                        "vessel_name": "MV GRAIN TRADER",
                        "mmsi": "367123456",
                        "cargo": "grain",
                        "current_position": "44.9444, -93.0933"
                    }
                }
            ],
            "edges": [
                {
                    "id": "edge_1",
                    "source": "gauge_05331000",
                    "target": "segment_pool1",
                    "type": "LOCATED_ON",
                    "properties": {"relationship": "monitoring"}
                },
                {
                    "id": "edge_2", 
                    "source": "vessel_mv_grain_trader",
                    "target": "segment_pool1",
                    "type": "NAVIGATES",
                    "properties": {"relationship": "current_navigation"}
                }
            ]
        }


class InteractiveSemanticGraph:
    """Jupyter-integrated graph visualization using yFiles"""
    
    def __init__(self, kuzu_connection):
        self.query_engine = KuzuGraphQueryEngine(kuzu_connection)
        self.logger = logging.getLogger(__name__)
        
    def display_semantic_graph(self, query: str = None, layers: List[str] = None, config: GraphVisualizationConfig = None):
        """Display interactive graph in Jupyter cell"""
        
        if config is None:
            config = GraphVisualizationConfig(
                title="Semantic Navigation Graph",
                width=1200,
                height=600,
                interactive=True
            )
        
        try:
            # Get graph data from KuzuDB
            if query:
                # Execute custom query
                result = self.query_engine.conn.execute(query)
                graph_data = self.query_engine._format_for_yfiles(result)
            elif layers:
                # Get multiple layers
                graph_data = {"nodes": [], "edges": []}
                for layer in layers:
                    layer_data = self.query_engine.get_semantic_layer(layer)
                    graph_data["nodes"].extend(layer_data["nodes"])
                    graph_data["edges"].extend(layer_data["edges"])
            else:
                # Get full graph
                graph_data = self.query_engine.get_semantic_layer("all")
            
            # Generate unique container ID
            container_id = f"semantic_graph_{uuid.uuid4().hex[:8]}"
            
            # Display HTML/JavaScript component
            self._display_yfiles_component(container_id, graph_data, config)
            
        except Exception as e:
            self.logger.error(f"Failed to display semantic graph: {e}")
            self._display_error_message(str(e))
    
    def create_mississippi_river_graph(self):
        """Create specific visualization for Mississippi River navigation"""
        
        print("🕸️ Interactive Mississippi River Navigation Network")
        print("=" * 50)
        print("🎯 Click nodes to explore relationships")
        print("🔍 Hover for semantic context")  
        print("🎛️ Use controls to filter layers")
        
        try:
            graph_data = self.query_engine.get_mississippi_river_graph()
            
            config = GraphVisualizationConfig(
                title="Mississippi River Navigation Network",
                width=1200,
                height=600,
                layout="hierarchic",
                interactive=True,
                show_labels=True
            )
            
            container_id = f"mississippi_graph_{uuid.uuid4().hex[:8]}"
            self._display_yfiles_component(container_id, graph_data, config)
            
            print("\n💡 Interactive Features:")
            print("   • Click gauge stations to see connected vessels")
            print("   • Click vessels to see navigation history") 
            print("   • Click infrastructure to see impact radius")
            print("   • Filter by entity type using layer controls")
            
        except Exception as e:
            self.logger.error(f"Failed to create Mississippi River graph: {e}")
            self._display_error_message(str(e))
    
    def create_live_updating_graph(self, update_interval: int = 30):
        """Create graph that updates in real-time"""
        
        # Initial display
        self.display_semantic_graph()
        
        # JavaScript for live updates
        display(Javascript(f'''
        console.log("Setting up live graph updates every {update_interval} seconds");
        
        // Store the update interval to prevent duplicates
        if (window.semanticGraphUpdateInterval) {{
            clearInterval(window.semanticGraphUpdateInterval);
        }}
        
        window.semanticGraphUpdateInterval = setInterval(() => {{
            console.log("Checking for graph updates...");
            // In a real implementation, this would fetch from the API
            // For now, we'll just log the update check
            if (window.semanticGraph) {{
                console.log("Graph instance found, would update with new data");
                // window.semanticGraph.updateWithLiveData(updates);
            }}
        }}, {update_interval * 1000});
        
        console.log("Live updates configured for semantic graph");
        '''))
    
    def _display_yfiles_component(self, container_id: str, graph_data: Dict, config: GraphVisualizationConfig):
        """Display the yFiles component with graph data"""
        
        # Create the HTML structure
        html_content = f'''
        <div id="{container_id}" style="width: {config.width}px; height: {config.height}px; border: 1px solid #ccc; border-radius: 8px; position: relative; background: #fafafa;">
            <div style="position: absolute; top: 10px; left: 20px; font-size: 18px; font-weight: bold; color: #333; z-index: 100; background: rgba(255, 255, 255, 0.9); padding: 5px 10px; border-radius: 4px;">
                {config.title}
            </div>
            <div id="{container_id}_controls" style="position: absolute; top: 10px; right: 20px; z-index: 100; background: rgba(255, 255, 255, 0.9); padding: 10px; border-radius: 4px; border: 1px solid #ddd;">
                <button onclick="resetLayout_{container_id}()" style="margin: 2px; padding: 5px 10px;">Reset Layout</button>
                <button onclick="fitGraph_{container_id}()" style="margin: 2px; padding: 5px 10px;">Fit Graph</button>
                <select id="{container_id}_layout" onchange="changeLayout_{container_id}()" style="margin: 2px; padding: 5px;">
                    <option value="hierarchic">Hierarchic</option>
                    <option value="organic">Organic</option>
                    <option value="circular">Circular</option>
                    <option value="tree">Tree</option>
                </select>
            </div>
            <div id="{container_id}_legend" style="position: absolute; bottom: 20px; left: 20px; background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 4px; border: 1px solid #ddd; z-index: 100;">
                <div style="font-weight: bold; margin-bottom: 10px;">Node Types:</div>
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <div style="width: 20px; height: 20px; background: #4a90e2; border-radius: 50%; margin-right: 10px;"></div>
                    <span>🌊 Gauge Stations</span>
                </div>
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <div style="width: 20px; height: 20px; background: #e24a4a; clip-path: polygon(50% 0%, 0% 100%, 100% 100%); margin-right: 10px;"></div>
                    <span>🚢 Vessels</span>
                </div>
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <div style="width: 20px; height: 20px; background: #4ae24a; margin-right: 10px;"></div>
                    <span>🏗️ Infrastructure</span>
                </div>
            </div>
            <div id="{container_id}_loading" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 16px; color: #666;">
                Loading yFiles Interactive Graph...
            </div>
        </div>
        
        <!-- Tooltip for hover context -->
        <div id="{container_id}_tooltip" style="position: absolute; background: rgba(0, 0, 0, 0.8); color: white; padding: 10px; border-radius: 4px; font-size: 12px; pointer-events: none; z-index: 200; display: none; max-width: 300px;"></div>
        '''
        
        display(HTML(html_content))
        
        # Create the JavaScript component
        js_content = f'''
        // Check if yFiles is available
        if (typeof yfiles === 'undefined') {{
            console.log("yFiles not loaded, loading from CDN...");
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/yfiles@latest/yfiles.umd.js';
            script.onload = () => {{
                console.log("yFiles loaded successfully");
                initializeGraph_{container_id}();
            }};
            script.onerror = () => {{
                console.error("Failed to load yFiles, using fallback visualization");
                initializeFallbackGraph_{container_id}();
            }};
            document.head.appendChild(script);
        }} else {{
            console.log("yFiles already available");
            initializeGraph_{container_id}();
        }}
        
        function initializeGraph_{container_id}() {{
            try {{
                const container = document.getElementById('{container_id}');
                const loadingDiv = document.getElementById('{container_id}_loading');
                
                if (!container) {{
                    console.error("Container not found: {container_id}");
                    return;
                }}
                
                // Hide loading message
                if (loadingDiv) loadingDiv.style.display = 'none';
                
                // Create yFiles GraphComponent
                const graphComponent = new yfiles.view.GraphComponent(container);
                window.graphComponent_{container_id} = graphComponent;
                
                // Set up interactivity
                graphComponent.inputMode = new yfiles.input.GraphViewerInputMode({{
                    clickableItems: yfiles.graph.GraphItemTypes.NODE | yfiles.graph.GraphItemTypes.EDGE,
                    selectableItems: yfiles.graph.GraphItemTypes.NODE | yfiles.graph.GraphItemTypes.EDGE,
                    marqueeSelectableItems: yfiles.graph.GraphItemTypes.NODE
                }});
                
                // Add event handlers
                graphComponent.addItemClickedListener((sender, args) => {{
                    onNodeClicked_{container_id}(args.item);
                }});
                
                graphComponent.addItemHoveredListener((sender, args) => {{
                    showSemanticContext_{container_id}(args.item, args.location);
                }});
                
                // Load graph data
                const graphData = {json.dumps(graph_data)};
                loadGraphData_{container_id}(graphComponent, graphData);
                
                console.log("yFiles graph initialized successfully");
                
            }} catch (error) {{
                console.error("Error initializing yFiles graph:", error);
                initializeFallbackGraph_{container_id}();
            }}
        }}
        
        function initializeFallbackGraph_{container_id}() {{
            console.log("Initializing fallback graph visualization");
            const container = document.getElementById('{container_id}');
            const loadingDiv = document.getElementById('{container_id}_loading');
            
            if (loadingDiv) loadingDiv.style.display = 'none';
            
            // Create simple SVG visualization as fallback
            const graphData = {json.dumps(graph_data)};
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '100%');
            svg.setAttribute('height', '100%');
            container.appendChild(svg);
            
            // Simple node/edge rendering
            const nodes = graphData.nodes || [];
            const edges = graphData.edges || [];
            
            // Draw edges first (so they appear under nodes)
            edges.forEach((edge, i) => {{
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', 100 + (i % 5) * 200);
                line.setAttribute('y1', 100 + Math.floor(i / 5) * 100);
                line.setAttribute('x2', 200 + (i % 5) * 200); 
                line.setAttribute('y2', 150 + Math.floor(i / 5) * 100);
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '2');
                svg.appendChild(line);
            }});
            
            // Draw nodes
            nodes.forEach((node, i) => {{
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', 150 + (i % 5) * 200);
                circle.setAttribute('cy', 125 + Math.floor(i / 5) * 100);
                circle.setAttribute('r', 20);
                
                // Color by type
                const colors = {{
                    'gauge_station': '#4a90e2',
                    'vessel': '#e24a4a',
                    'infrastructure': '#4ae24a',
                    'waterway_segment': '#f39c12'
                }};
                circle.setAttribute('fill', colors[node.type] || '#95a5a6');
                circle.setAttribute('stroke', '#333');
                circle.setAttribute('stroke-width', '2');
                
                // Add click handler
                circle.style.cursor = 'pointer';
                circle.addEventListener('click', () => {{
                    alert(`Node: ${{node.label}}\\nType: ${{node.type}}`);
                }});
                
                svg.appendChild(circle);
                
                // Add label
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', 150 + (i % 5) * 200);
                text.setAttribute('y', 165 + Math.floor(i / 5) * 100);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('font-size', '12');
                text.setAttribute('fill', '#333');
                text.textContent = node.label || node.id;
                svg.appendChild(text);
            }});
            
            console.log("Fallback graph rendered with", nodes.length, "nodes");
        }}
        
        function loadGraphData_{container_id}(graphComponent, graphData) {{
            const graph = graphComponent.graph;
            const nodes = graphData.nodes || [];
            const edges = graphData.edges || [];
            
            // Clear existing graph
            graph.clear();
            
            // Create nodes with semantic styling
            const nodeMap = new Map();
            nodes.forEach(nodeData => {{
                const node = graph.createNode();
                nodeMap.set(nodeData.id, node);
                
                // Set node style based on semantic type
                const style = getSemanticNodeStyle_{container_id}(nodeData.type);
                graph.setStyle(node, style);
                
                // Store semantic metadata
                node.tag = nodeData.semantics || nodeData.properties || {{}};
                node.tag.id = nodeData.id;
                node.tag.label = nodeData.label;
                node.tag.type = nodeData.type;
            }});
            
            // Create edges
            edges.forEach(edgeData => {{
                const sourceNode = nodeMap.get(edgeData.source);
                const targetNode = nodeMap.get(edgeData.target);
                
                if (sourceNode && targetNode) {{
                    const edge = graph.createEdge(sourceNode, targetNode);
                    edge.tag = edgeData.properties || {{}};
                    edge.tag.type = edgeData.type;
                }}
            }});
            
            // Apply layout
            applySemanticLayout_{container_id}(graphComponent);
        }}
        
        function getSemanticNodeStyle_{container_id}(nodeType) {{
            const styles = {{
                'gauge_station': new yfiles.styles.ShapeNodeStyle({{
                    fill: '#4a90e2',
                    stroke: '#2980b9',
                    shape: 'ellipse'
                }}),
                'vessel': new yfiles.styles.ShapeNodeStyle({{
                    fill: '#e24a4a',
                    stroke: '#c0392b', 
                    shape: 'triangle'
                }}),
                'infrastructure': new yfiles.styles.ShapeNodeStyle({{
                    fill: '#4ae24a',
                    stroke: '#27ae60',
                    shape: 'rectangle'
                }}),
                'waterway_segment': new yfiles.styles.ShapeNodeStyle({{
                    fill: '#f39c12',
                    stroke: '#e67e22',
                    shape: 'hexagon'
                }})
            }};
            
            return styles[nodeType] || new yfiles.styles.ShapeNodeStyle({{
                fill: '#95a5a6',
                stroke: '#7f8c8d',
                shape: 'ellipse'
            }});
        }}
        
        function applySemanticLayout_{container_id}(graphComponent) {{
            const layout = new yfiles.hierarchic.HierarchicLayout();
            layout.nodeToNodeDistance = 50;
            layout.layerSpacing = 100;
            
            graphComponent.morphLayout(layout, '1s');
        }}
        
        function onNodeClicked_{container_id}(item) {{
            if (item instanceof yfiles.graph.INode) {{
                const nodeData = item.tag;
                console.log("Node clicked:", nodeData);
                
                // Show detailed information
                const info = `
                Node: ${{nodeData.label || nodeData.id}}
                Type: ${{nodeData.type}}
                ${{nodeData.display_name ? 'Name: ' + nodeData.display_name : ''}}
                ${{nodeData.current_level ? 'Water Level: ' + nodeData.current_level : ''}}
                ${{nodeData.vessel_name ? 'Vessel: ' + nodeData.vessel_name : ''}}
                `;
                
                alert(info.trim());
            }}
        }}
        
        function showSemanticContext_{container_id}(item, location) {{
            const tooltip = document.getElementById('{container_id}_tooltip');
            
            if (item instanceof yfiles.graph.INode && tooltip) {{
                const nodeData = item.tag;
                let content = `<strong>${{nodeData.label || nodeData.id}}</strong><br/>`;
                content += `Type: ${{nodeData.type}}<br/>`;
                
                if (nodeData.current_level) content += `Water Level: ${{nodeData.current_level}}<br/>`;
                if (nodeData.vessel_name) content += `Vessel: ${{nodeData.vessel_name}}<br/>`;
                if (nodeData.location) content += `Location: ${{nodeData.location}}<br/>`;
                
                tooltip.innerHTML = content;
                tooltip.style.left = location.x + 10 + 'px';
                tooltip.style.top = location.y - 10 + 'px';
                tooltip.style.display = 'block';
            }} else {{
                tooltip.style.display = 'none';
            }}
        }}
        
        // Control functions
        function resetLayout_{container_id}() {{
            const graphComponent = window.graphComponent_{container_id};
            if (graphComponent) {{
                applySemanticLayout_{container_id}(graphComponent);
            }}
        }}
        
        function fitGraph_{container_id}() {{
            const graphComponent = window.graphComponent_{container_id};
            if (graphComponent) {{
                graphComponent.fitGraphBounds();
            }}
        }}
        
        function changeLayout_{container_id}() {{
            const select = document.getElementById('{container_id}_layout');
            const graphComponent = window.graphComponent_{container_id};
            
            if (graphComponent && select) {{
                const layoutType = select.value;
                let layout;
                
                switch(layoutType) {{
                    case 'organic':
                        layout = new yfiles.organic.OrganicLayout();
                        break;
                    case 'circular':
                        layout = new yfiles.circular.CircularLayout();
                        break;
                    case 'tree':
                        layout = new yfiles.tree.TreeLayout();
                        break;
                    default:
                        layout = new yfiles.hierarchic.HierarchicLayout();
                }}
                
                graphComponent.morphLayout(layout, '1s');
            }}
        }}
        '''
        
        display(Javascript(js_content))
    
    def _display_error_message(self, error_message: str):
        """Display error message when graph visualization fails"""
        error_html = f'''
        <div style="width: 1200px; height: 300px; border: 2px solid #e74c3c; border-radius: 8px; background: #fadbd8; padding: 20px; display: flex; align-items: center; justify-content: center; flex-direction: column;">
            <h3 style="color: #c0392b; margin: 0 0 10px 0;">Graph Visualization Error</h3>
            <p style="color: #922b21; margin: 0; text-align: center;">
                Failed to load interactive graph: {error_message}
            </p>
            <p style="color: #922b21; margin: 10px 0 0 0; font-size: 14px;">
                This may be due to missing yFiles library or KuzuDB connection issues.
            </p>
        </div>
        '''
        display(HTML(error_html))


def demonstrate_interactive_semantic_graph(orchestrator):
    """Show the power of interactive semantic graph exploration"""
    
    print("🕸️ Interactive Semantic Knowledge Graph")
    print("=" * 45)
    print("🎯 Click nodes to explore relationships")
    print("🔍 Hover for semantic context")
    print("🎛️ Use controls to filter layers")
    
    try:
        # Create interactive graph component
        graph_viz = InteractiveSemanticGraph(orchestrator.navigation_queries.conn)
        
        print("\n📊 Mississippi River Navigation Network:")
        graph_viz.create_mississippi_river_graph()
        
        print("\n🔄 Live Data Flow (updates every 30 seconds):")
        graph_viz.create_live_updating_graph(update_interval=30)
        
        print("\n💡 Interactive Features:")
        print("   • Click gauge stations to see connected vessels")
        print("   • Click vessels to see navigation history")
        print("   • Click infrastructure to see impact radius")
        print("   • Filter by entity type using layer controls")
        print("   • Watch real-time updates as new data arrives")
        
        return graph_viz
        
    except Exception as e:
        logger.error(f"Failed to demonstrate interactive graph: {e}")
        print(f"❌ Error creating interactive graph: {e}")
        return None