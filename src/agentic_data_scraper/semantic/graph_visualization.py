"""
Interactive Graph Visualization for SOW Analytics

This module creates engaging, interactive graph visualization components for
SOW exploration using modern web technologies. It provides multiple visualization
approaches optimized for different user types and use cases.

Key Components:
1. Cytoscape.js integration for network graphs
2. D3.js for custom interactive visualizations  
3. Plotly for 4D analytics dashboards
4. Real-time graph updates and exploration
5. Business-friendly interactive interfaces
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from starlette.requests import Request

from .kuzu_sow_schema import KuzuSOWGraphEngine
from .sow_analytics_engine import AdvancedSOWAnalytics

logger = logging.getLogger(__name__)


@dataclass
class GraphVisualizationConfig:
    """Configuration for graph visualization components"""
    title: str
    width: int = 1200
    height: int = 800
    layout: str = "cose"  # cose, circle, grid, breadthfirst, concentric
    node_size_attribute: str = "business_value"
    edge_weight_attribute: str = "confidence"
    color_scheme: str = "viridis"
    interactive: bool = True
    show_labels: bool = True
    cluster_view: bool = False


@dataclass
class VisualizationData:
    """Data structure for graph visualization"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    layout_config: Dict[str, Any]
    styling: Dict[str, Any]


class SOWGraphVisualizer:
    """
    Main graph visualization engine for SOW analytics.
    
    This class creates engaging, interactive visualizations that make
    graph exploration intuitive and business-friendly.
    """
    
    def __init__(self, kuzu_engine: KuzuSOWGraphEngine, analytics_engine: AdvancedSOWAnalytics):
        self.kuzu_engine = kuzu_engine
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
        
        # Initialize visualization templates and assets
        self.templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
        self.static_path = Path(__file__).parent / "static"
        self.static_path.mkdir(exist_ok=True)
        
        # Create required static files
        self._create_static_assets()
    
    def create_cytoscape_visualization(self, requirement_id: Optional[str] = None,
                                     config: Optional[GraphVisualizationConfig] = None) -> Dict[str, Any]:
        """
        Create Cytoscape.js visualization data for SOW graph exploration.
        
        This creates an interactive network visualization optimized for
        business users to explore requirements and opportunities.
        """
        if config is None:
            config = GraphVisualizationConfig(
                title=f"SOW Graph - {requirement_id or 'Overview'}",
                layout="cose",
                interactive=True
            )
        
        try:
            # Get graph data from KuzuDB
            graph_data = self.kuzu_engine.get_opportunity_graph_data(requirement_id)
            
            # Transform for Cytoscape.js format
            cyto_nodes = []
            cyto_edges = []
            
            # Process nodes with enhanced styling
            for node in graph_data['nodes']:
                node_data = node['data']
                node_type = node_data.get('type', 'unknown')
                
                cyto_node = {
                    'data': {
                        'id': node_data['id'],
                        'label': node_data.get('label', node_data['id']),
                        'type': node_type,
                        'weight': self._calculate_node_weight(node_data, config.node_size_attribute)
                    },
                    'classes': f"node-{node_type}",
                    'style': self._get_node_style(node_data, node_type)
                }
                
                # Add type-specific data
                if node_type == 'requirement':
                    cyto_node['data'].update({
                        'priority': node_data.get('priority', 3),
                        'domain': node_data.get('domain', ''),
                        'complexity': node_data.get('complexity', 'medium')
                    })
                elif node_type == 'opportunity':
                    cyto_node['data'].update({
                        'business_value': node_data.get('business_value', 0),
                        'confidence_score': node_data.get('confidence_score', 0),
                        'discovery_method': node_data.get('discovery_method', ''),
                        'status': node_data.get('status', 'discovered')
                    })
                elif node_type == 'entity':
                    cyto_node['data'].update({
                        'entity_type': node_data.get('entity_type', ''),
                        'industry': node_data.get('industry', ''),
                        'maturity_level': node_data.get('maturity_level', '')
                    })
                
                cyto_nodes.append(cyto_node)
            
            # Process edges with enhanced styling
            for edge in graph_data['edges']:
                edge_data = edge['data']
                edge_type = edge_data.get('type', 'unknown')
                
                cyto_edge = {
                    'data': {
                        'id': edge_data['id'],
                        'source': edge_data['source'],
                        'target': edge_data['target'],
                        'type': edge_type,
                        'weight': self._calculate_edge_weight(edge_data, config.edge_weight_attribute)
                    },
                    'classes': f"edge-{edge_type}",
                    'style': self._get_edge_style(edge_data, edge_type)
                }
                
                # Add type-specific data
                if edge_type == 'implies':
                    cyto_edge['data'].update({
                        'confidence': edge_data.get('confidence', 0),
                        'reasoning': edge_data.get('reasoning', '')
                    })
                elif edge_type == 'belongs_to':
                    cyto_edge['data'].update({
                        'ownership_level': edge_data.get('ownership_level', ''),
                        'stakeholder_priority': edge_data.get('stakeholder_priority', 0)
                    })
                
                cyto_edges.append(cyto_edge)
            
            # Create layout configuration
            layout_config = self._create_layout_config(config.layout)
            
            # Create styling configuration
            style_config = self._create_cytoscape_style(config)
            
            visualization_data = {
                'elements': {
                    'nodes': cyto_nodes,
                    'edges': cyto_edges
                },
                'layout': layout_config,
                'style': style_config,
                'config': {
                    'title': config.title,
                    'width': config.width,
                    'height': config.height,
                    'interactive': config.interactive,
                    'show_labels': config.show_labels
                },
                'stats': graph_data['stats']
            }
            
            self.logger.info(f"Created Cytoscape visualization with {len(cyto_nodes)} nodes and {len(cyto_edges)} edges")
            return visualization_data
            
        except Exception as e:
            self.logger.error(f"Failed to create Cytoscape visualization: {e}")
            return {'elements': {'nodes': [], 'edges': []}, 'layout': {}, 'style': [], 'config': {}, 'stats': {}}
    
    def create_d3_force_graph(self, requirement_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create D3.js force-directed graph visualization.
        
        This provides a highly interactive force simulation that's great
        for exploring graph structure and relationships.
        """
        try:
            graph_data = self.kuzu_engine.get_opportunity_graph_data(requirement_id)
            
            # Transform for D3.js format
            d3_nodes = []
            d3_links = []
            
            node_id_map = {}
            
            # Process nodes
            for i, node in enumerate(graph_data['nodes']):
                node_data = node['data']
                node_id = node_data['id']
                node_id_map[node_id] = i
                
                d3_node = {
                    'id': node_id,
                    'name': node_data.get('label', node_id),
                    'type': node_data.get('type', 'unknown'),
                    'group': self._get_node_group(node_data.get('type', 'unknown')),
                    'size': self._calculate_node_size(node_data),
                    'color': self._get_node_color(node_data.get('type', 'unknown')),
                    'data': node_data
                }
                
                d3_nodes.append(d3_node)
            
            # Process links/edges
            for edge in graph_data['edges']:
                edge_data = edge['data']
                source_id = edge_data['source']
                target_id = edge_data['target']
                
                if source_id in node_id_map and target_id in node_id_map:
                    d3_link = {
                        'source': source_id,
                        'target': target_id,
                        'type': edge_data.get('type', 'unknown'),
                        'weight': self._calculate_edge_weight(edge_data, 'confidence'),
                        'color': self._get_edge_color(edge_data.get('type', 'unknown')),
                        'data': edge_data
                    }
                    
                    d3_links.append(d3_link)
            
            visualization_data = {
                'nodes': d3_nodes,
                'links': d3_links,
                'config': {
                    'width': 1200,
                    'height': 800,
                    'charge_strength': -300,
                    'link_distance': 100,
                    'alpha': 0.3,
                    'alpha_decay': 0.02
                },
                'legend': self._create_d3_legend(),
                'stats': graph_data['stats']
            }
            
            self.logger.info(f"Created D3 force graph with {len(d3_nodes)} nodes and {len(d3_links)} links")
            return visualization_data
            
        except Exception as e:
            self.logger.error(f"Failed to create D3 force graph: {e}")
            return {'nodes': [], 'links': [], 'config': {}, 'legend': [], 'stats': {}}
    
    def create_4d_visualization_data(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Create 4D graph visualization data (Time-Space-Domain-Knowledge layers).
        
        This creates a sophisticated multi-dimensional view of the SOW graph
        that reveals temporal patterns, domain relationships, and knowledge evolution.
        """
        try:
            # Get comprehensive graph data with temporal information
            temporal_query = """
            MATCH (req:BusinessRequirement)
            """ + (f"WHERE req.domain = '{domain}'" if domain else "") + """
            OPTIONAL MATCH (req)-[impl:IMPLIES]->(opp:AnalyticalOpportunity)
            OPTIONAL MATCH (req)-[:BELONGS_TO]->(entity:DomainEntity)
            RETURN req.id, req.description, req.domain, req.created_at, req.priority,
                   opp.id, opp.description, opp.business_value, opp.confidence_score, opp.created_at,
                   entity.industry, entity.maturity_level,
                   impl.confidence, impl.created_at
            ORDER BY req.created_at DESC
            LIMIT 100
            """
            
            result = self.kuzu_engine.conn.execute(temporal_query)
            
            # Organize data by the four dimensions
            temporal_data = []  # Time dimension
            spatial_data = []   # Space dimension (domains/industries)
            domain_data = []    # Domain relationships
            knowledge_data = [] # Knowledge layer (patterns and inference)
            
            for record in result:
                req_id = record[0]
                req_desc = record[1]
                req_domain = record[2]
                req_created = record[3]
                req_priority = record[4]
                
                opp_id = record[5]
                opp_desc = record[6]
                opp_value = record[7]
                opp_confidence = record[8]
                opp_created = record[9]
                
                entity_industry = record[10]
                entity_maturity = record[11]
                
                impl_confidence = record[12]
                impl_created = record[13]
                
                # Temporal layer - evolution over time
                temporal_data.append({
                    'timestamp': req_created,
                    'type': 'requirement',
                    'id': req_id,
                    'value': req_priority * 1000,
                    'domain': req_domain,
                    'description': req_desc
                })
                
                if opp_id and opp_created:
                    temporal_data.append({
                        'timestamp': opp_created,
                        'type': 'opportunity',
                        'id': opp_id,
                        'value': opp_value or 0,
                        'domain': req_domain,
                        'description': opp_desc,
                        'confidence': opp_confidence
                    })
                
                # Spatial layer - domain/industry distribution
                spatial_data.append({
                    'domain': req_domain,
                    'industry': entity_industry or 'general',
                    'maturity': entity_maturity or 'mature',
                    'requirement_count': 1,
                    'total_value': req_priority * 500
                })
                
                if opp_value:
                    spatial_data.append({
                        'domain': req_domain,
                        'industry': entity_industry or 'general',
                        'maturity': entity_maturity or 'mature',
                        'opportunity_count': 1,
                        'total_value': opp_value
                    })
                
                # Domain layer - cross-domain relationships
                domain_data.append({
                    'source_domain': req_domain,
                    'target_domain': entity_industry or req_domain,
                    'relationship_type': 'belongs_to',
                    'strength': 1.0,
                    'req_id': req_id
                })
                
                # Knowledge layer - inference patterns
                if impl_confidence:
                    knowledge_data.append({
                        'pattern_type': 'implication',
                        'source_type': 'requirement',
                        'target_type': 'opportunity',
                        'confidence': impl_confidence,
                        'domain': req_domain,
                        'timestamp': impl_created,
                        'source_id': req_id,
                        'target_id': opp_id
                    })
            
            # Process and aggregate data for visualization
            viz_data = {
                'temporal': self._process_temporal_data(temporal_data),
                'spatial': self._process_spatial_data(spatial_data),
                'domain': self._process_domain_data(domain_data),
                'knowledge': self._process_knowledge_data(knowledge_data),
                'config': {
                    'time_range': self._get_time_range(temporal_data),
                    'domains': list(set(item['domain'] for item in temporal_data if item['domain'])),
                    'industries': list(set(item['industry'] for item in spatial_data if item['industry'])),
                    'visualization_type': '4d_analytics'
                }
            }
            
            self.logger.info("Created 4D visualization data")
            return viz_data
            
        except Exception as e:
            self.logger.error(f"Failed to create 4D visualization: {e}")
            return {'temporal': [], 'spatial': [], 'domain': [], 'knowledge': [], 'config': {}}
    
    def _calculate_node_weight(self, node_data: Dict[str, Any], attribute: str) -> float:
        """Calculate node weight for sizing based on specified attribute"""
        if attribute == "business_value":
            return float(node_data.get('business_value', 1000)) / 1000.0
        elif attribute == "priority":
            return float(node_data.get('priority', 3))
        elif attribute == "confidence_score":
            return float(node_data.get('confidence_score', 0.5))
        else:
            return 1.0
    
    def _calculate_edge_weight(self, edge_data: Dict[str, Any], attribute: str) -> float:
        """Calculate edge weight for thickness based on specified attribute"""
        if attribute == "confidence":
            return float(edge_data.get('confidence', 0.5))
        elif attribute == "stakeholder_priority":
            return float(edge_data.get('stakeholder_priority', 0.5))
        else:
            return 0.5
    
    def _get_node_style(self, node_data: Dict[str, Any], node_type: str) -> Dict[str, Any]:
        """Get Cytoscape node styling"""
        base_style = {
            'width': f"{20 + self._calculate_node_weight(node_data, 'business_value') * 30}px",
            'height': f"{20 + self._calculate_node_weight(node_data, 'business_value') * 30}px",
            'font-size': '12px',
            'text-valign': 'center',
            'text-halign': 'center'
        }
        
        type_styles = {
            'requirement': {
                'background-color': '#3498db',
                'border-color': '#2980b9',
                'border-width': '2px',
                'shape': 'roundrectangle'
            },
            'opportunity': {
                'background-color': '#e74c3c',
                'border-color': '#c0392b',
                'border-width': '2px',
                'shape': 'ellipse'
            },
            'entity': {
                'background-color': '#2ecc71',
                'border-color': '#27ae60',
                'border-width': '2px',
                'shape': 'triangle'
            }
        }
        
        base_style.update(type_styles.get(node_type, {}))
        return base_style
    
    def _get_edge_style(self, edge_data: Dict[str, Any], edge_type: str) -> Dict[str, Any]:
        """Get Cytoscape edge styling"""
        base_style = {
            'width': f"{1 + self._calculate_edge_weight(edge_data, 'confidence') * 5}px",
            'line-color': '#bdc3c7',
            'target-arrow-color': '#bdc3c7',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
        }
        
        type_styles = {
            'implies': {
                'line-color': '#e74c3c',
                'target-arrow-color': '#e74c3c',
                'line-style': 'solid'
            },
            'belongs_to': {
                'line-color': '#3498db',
                'target-arrow-color': '#3498db',
                'line-style': 'dashed'
            },
            'correlates_with': {
                'line-color': '#9b59b6',
                'target-arrow-color': '#9b59b6',
                'line-style': 'dotted'
            }
        }
        
        base_style.update(type_styles.get(edge_type, {}))
        return base_style
    
    def _create_layout_config(self, layout_type: str) -> Dict[str, Any]:
        """Create layout configuration for Cytoscape"""
        layouts = {
            'cose': {
                'name': 'cose',
                'animate': True,
                'animationDuration': 1000,
                'nodeOverlap': 20,
                'idealEdgeLength': 100,
                'edgeElasticity': 100,
                'nestingFactor': 5,
                'gravity': 80,
                'numIter': 1000,
                'coolingFactor': 0.99,
                'minTemp': 1.0
            },
            'circle': {
                'name': 'circle',
                'animate': True,
                'animationDuration': 1000,
                'radius': 200,
                'spacing': 40
            },
            'grid': {
                'name': 'grid',
                'animate': True,
                'animationDuration': 1000,
                'rows': None,
                'cols': None,
                'spacing': 50
            },
            'breadthfirst': {
                'name': 'breadthfirst',
                'animate': True,
                'animationDuration': 1000,
                'directed': True,
                'spacingFactor': 1.5
            }
        }
        
        return layouts.get(layout_type, layouts['cose'])
    
    def _create_cytoscape_style(self, config: GraphVisualizationConfig) -> List[Dict[str, Any]]:
        """Create comprehensive Cytoscape styling"""
        style = [
            # Node styles
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)' if config.show_labels else '',
                    'text-opacity': 1 if config.show_labels else 0,
                    'font-family': 'Arial, sans-serif',
                    'font-weight': 'bold',
                    'text-outline-width': 2,
                    'text-outline-color': '#ffffff',
                    'overlay-opacity': 0
                }
            },
            {
                'selector': '.node-requirement',
                'style': {
                    'background-color': '#3498db',
                    'border-color': '#2980b9',
                    'border-width': '3px',
                    'shape': 'roundrectangle'
                }
            },
            {
                'selector': '.node-opportunity',
                'style': {
                    'background-color': '#e74c3c',
                    'border-color': '#c0392b',
                    'border-width': '3px',
                    'shape': 'ellipse'
                }
            },
            {
                'selector': '.node-entity',
                'style': {
                    'background-color': '#2ecc71',
                    'border-color': '#27ae60',
                    'border-width': '3px',
                    'shape': 'triangle'
                }
            },
            # Edge styles
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'opacity': 0.8,
                    'overlay-opacity': 0
                }
            },
            {
                'selector': '.edge-implies',
                'style': {
                    'line-color': '#e74c3c',
                    'target-arrow-color': '#e74c3c',
                    'line-style': 'solid'
                }
            },
            {
                'selector': '.edge-belongs_to',
                'style': {
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db',
                    'line-style': 'dashed'
                }
            },
            # Hover effects
            {
                'selector': 'node:selected',
                'style': {
                    'border-width': '5px',
                    'overlay-color': '#f39c12',
                    'overlay-opacity': 0.3
                }
            },
            {
                'selector': 'edge:selected',
                'style': {
                    'line-color': '#f39c12',
                    'target-arrow-color': '#f39c12',
                    'width': '4px',
                    'opacity': 1
                }
            }
        ]
        
        return style
    
    def _get_node_group(self, node_type: str) -> int:
        """Get node group for D3 force simulation"""
        groups = {
            'requirement': 1,
            'opportunity': 2,
            'entity': 3,
            'pattern': 4
        }
        return groups.get(node_type, 0)
    
    def _calculate_node_size(self, node_data: Dict[str, Any]) -> int:
        """Calculate node size for D3 visualization"""
        if node_data.get('type') == 'opportunity':
            value = float(node_data.get('business_value', 1000))
            return max(5, min(50, int(value / 200)))
        elif node_data.get('type') == 'requirement':
            priority = int(node_data.get('priority', 3))
            return max(8, priority * 3)
        else:
            return 10
    
    def _get_node_color(self, node_type: str) -> str:
        """Get node color for D3 visualization"""
        colors = {
            'requirement': '#3498db',
            'opportunity': '#e74c3c', 
            'entity': '#2ecc71',
            'pattern': '#9b59b6'
        }
        return colors.get(node_type, '#95a5a6')
    
    def _get_edge_color(self, edge_type: str) -> str:
        """Get edge color for D3 visualization"""
        colors = {
            'implies': '#e74c3c',
            'belongs_to': '#3498db',
            'correlates_with': '#9b59b6',
            'enables': '#2ecc71'
        }
        return colors.get(edge_type, '#bdc3c7')
    
    def _create_d3_legend(self) -> List[Dict[str, Any]]:
        """Create legend for D3 visualization"""
        return [
            {'type': 'requirement', 'color': '#3498db', 'label': 'Business Requirements'},
            {'type': 'opportunity', 'color': '#e74c3c', 'label': 'Analytical Opportunities'}, 
            {'type': 'entity', 'color': '#2ecc71', 'label': 'Domain Entities'},
            {'type': 'pattern', 'color': '#9b59b6', 'label': 'Knowledge Patterns'}
        ]
    
    def _process_temporal_data(self, temporal_data: List[Dict]) -> Dict[str, Any]:
        """Process temporal data for 4D visualization"""
        # Group by time periods and calculate trends
        from collections import defaultdict
        import datetime as dt
        
        time_series = defaultdict(lambda: {'requirements': 0, 'opportunities': 0, 'total_value': 0})
        
        for item in temporal_data:
            if item['timestamp']:
                # Group by month
                period = item['timestamp'][:7] if isinstance(item['timestamp'], str) else item['timestamp'].strftime('%Y-%m')
                time_series[period]['total_value'] += item.get('value', 0)
                
                if item['type'] == 'requirement':
                    time_series[period]['requirements'] += 1
                elif item['type'] == 'opportunity':
                    time_series[period]['opportunities'] += 1
        
        return {
            'time_series': dict(time_series),
            'trends': self._calculate_trends(time_series),
            'total_items': len(temporal_data)
        }
    
    def _process_spatial_data(self, spatial_data: List[Dict]) -> Dict[str, Any]:
        """Process spatial data for domain/industry distribution"""
        from collections import defaultdict
        
        domain_stats = defaultdict(lambda: {'count': 0, 'value': 0})
        industry_stats = defaultdict(lambda: {'count': 0, 'value': 0})
        
        for item in spatial_data:
            domain = item.get('domain', 'unknown')
            industry = item.get('industry', 'unknown')
            value = item.get('total_value', 0)
            
            domain_stats[domain]['count'] += 1
            domain_stats[domain]['value'] += value
            
            industry_stats[industry]['count'] += 1
            industry_stats[industry]['value'] += value
        
        return {
            'domains': dict(domain_stats),
            'industries': dict(industry_stats),
            'distribution': self._calculate_distribution(domain_stats, industry_stats)
        }
    
    def _process_domain_data(self, domain_data: List[Dict]) -> Dict[str, Any]:
        """Process domain relationship data"""
        relationships = []
        domain_connections = defaultdict(int)
        
        for item in domain_data:
            source = item['source_domain']
            target = item['target_domain']
            strength = item['strength']
            
            relationships.append({
                'source': source,
                'target': target,
                'strength': strength,
                'type': item['relationship_type']
            })
            
            domain_connections[source] += 1
            domain_connections[target] += 1
        
        return {
            'relationships': relationships,
            'connections': dict(domain_connections),
            'network_density': self._calculate_network_density(relationships)
        }
    
    def _process_knowledge_data(self, knowledge_data: List[Dict]) -> Dict[str, Any]:
        """Process knowledge pattern data"""
        patterns = defaultdict(list)
        confidence_distribution = []
        
        for item in knowledge_data:
            pattern_type = item['pattern_type']
            confidence = item['confidence']
            
            patterns[pattern_type].append(item)
            confidence_distribution.append(confidence)
        
        return {
            'patterns': dict(patterns),
            'confidence_stats': {
                'mean': sum(confidence_distribution) / len(confidence_distribution) if confidence_distribution else 0,
                'min': min(confidence_distribution) if confidence_distribution else 0,
                'max': max(confidence_distribution) if confidence_distribution else 0,
                'distribution': confidence_distribution
            }
        }
    
    def _get_time_range(self, temporal_data: List[Dict]) -> Dict[str, str]:
        """Get time range from temporal data"""
        timestamps = [item['timestamp'] for item in temporal_data if item['timestamp']]
        if not timestamps:
            return {'start': '', 'end': ''}
        
        return {
            'start': min(timestamps),
            'end': max(timestamps)
        }
    
    def _calculate_trends(self, time_series: Dict) -> Dict[str, float]:
        """Calculate trends from time series data"""
        # Simple linear trend calculation
        periods = sorted(time_series.keys())
        if len(periods) < 2:
            return {'requirements': 0, 'opportunities': 0, 'value': 0}
        
        req_values = [time_series[p]['requirements'] for p in periods]
        opp_values = [time_series[p]['opportunities'] for p in periods]
        val_values = [time_series[p]['total_value'] for p in periods]
        
        return {
            'requirements': self._linear_trend(req_values),
            'opportunities': self._linear_trend(opp_values),
            'value': self._linear_trend(val_values)
        }
    
    def _linear_trend(self, values: List[float]) -> float:
        """Calculate linear trend (slope)"""
        n = len(values)
        if n < 2:
            return 0
        
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    def _calculate_distribution(self, domain_stats: Dict, industry_stats: Dict) -> Dict[str, Any]:
        """Calculate distribution metrics"""
        return {
            'domain_diversity': len(domain_stats),
            'industry_diversity': len(industry_stats),
            'concentration': self._calculate_concentration(domain_stats)
        }
    
    def _calculate_concentration(self, stats: Dict) -> float:
        """Calculate concentration index (higher = more concentrated)"""
        total = sum(item['count'] for item in stats.values())
        if total == 0:
            return 0
        
        # Herfindahl index
        shares = [(item['count'] / total) ** 2 for item in stats.values()]
        return sum(shares)
    
    def _calculate_network_density(self, relationships: List[Dict]) -> float:
        """Calculate network density"""
        nodes = set()
        for rel in relationships:
            nodes.add(rel['source'])
            nodes.add(rel['target'])
        
        n_nodes = len(nodes)
        n_edges = len(relationships)
        
        if n_nodes < 2:
            return 0
        
        max_edges = n_nodes * (n_nodes - 1)  # Directed graph
        return n_edges / max_edges if max_edges > 0 else 0
    
    def _create_static_assets(self):
        """Create static CSS and JavaScript files for visualizations"""
        # CSS for graph visualizations
        css_content = """
/* SOW Graph Visualization Styles */
.sow-graph-container {
    width: 100%;
    height: 800px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin: 20px 0;
    position: relative;
    background: #fafafa;
}

.sow-graph-title {
    position: absolute;
    top: 10px;
    left: 20px;
    font-size: 18px;
    font-weight: bold;
    color: #333;
    z-index: 100;
    background: rgba(255, 255, 255, 0.9);
    padding: 5px 10px;
    border-radius: 4px;
}

.sow-graph-controls {
    position: absolute;
    top: 10px;
    right: 20px;
    z-index: 100;
    background: rgba(255, 255, 255, 0.9);
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #ddd;
}

.sow-graph-legend {
    position: absolute;
    bottom: 20px;
    left: 20px;
    background: rgba(255, 255, 255, 0.9);
    padding: 15px;
    border-radius: 4px;
    border: 1px solid #ddd;
    z-index: 100;
}

.legend-item {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
}

.legend-color {
    width: 20px;
    height: 20px;
    border-radius: 10px;
    margin-right: 10px;
}

.sow-graph-stats {
    position: absolute;
    bottom: 20px;
    right: 20px;
    background: rgba(255, 255, 255, 0.9);
    padding: 15px;
    border-radius: 4px;
    border: 1px solid #ddd;
    z-index: 100;
    font-size: 12px;
}

/* Tooltip styles */
.graph-tooltip {
    position: absolute;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px;
    border-radius: 4px;
    font-size: 12px;
    pointer-events: none;
    z-index: 200;
    max-width: 300px;
}

/* 4D visualization styles */
.dimension-tabs {
    display: flex;
    margin-bottom: 20px;
}

.dimension-tab {
    padding: 10px 20px;
    background: #ecf0f1;
    border: 1px solid #bdc3c7;
    cursor: pointer;
    transition: background 0.3s;
}

.dimension-tab.active {
    background: #3498db;
    color: white;
}

.dimension-tab:hover {
    background: #d5dbdb;
}

.dimension-content {
    min-height: 600px;
}

/* Responsive design */
@media (max-width: 1200px) {
    .sow-graph-container {
        height: 600px;
    }
}

@media (max-width: 768px) {
    .sow-graph-container {
        height: 400px;
    }
    
    .sow-graph-controls,
    .sow-graph-legend,
    .sow-graph-stats {
        position: static;
        margin: 10px;
        display: inline-block;
    }
}
"""
        
        css_path = self.static_path / "sow_graph.css"
        css_path.write_text(css_content)
        
        # JavaScript utilities for visualizations
        js_content = """
// SOW Graph Visualization Utilities
class SOWGraphUtils {
    static createTooltip(data, type) {
        let content = `<strong>${data.label || data.id}</strong><br/>`;
        
        if (type === 'requirement') {
            content += `Priority: ${data.priority}<br/>`;
            content += `Domain: ${data.domain}<br/>`;
            content += `Complexity: ${data.complexity}`;
        } else if (type === 'opportunity') {
            content += `Value: $${data.business_value?.toLocaleString()}<br/>`;
            content += `Confidence: ${(data.confidence_score * 100).toFixed(1)}%<br/>`;
            content += `Method: ${data.discovery_method}`;
        } else if (type === 'entity') {
            content += `Type: ${data.entity_type}<br/>`;
            content += `Industry: ${data.industry}<br/>`;
            content += `Maturity: ${data.maturity_level}`;
        }
        
        return content;
    }
    
    static formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }
    
    static formatPercentage(value) {
        return `${(value * 100).toFixed(1)}%`;
    }
    
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    static showTooltip(event, content) {
        const tooltip = document.getElementById('graph-tooltip') || this.createTooltipElement();
        tooltip.innerHTML = content;
        tooltip.style.left = event.pageX + 10 + 'px';
        tooltip.style.top = event.pageY - 10 + 'px';
        tooltip.style.display = 'block';
    }
    
    static hideTooltip() {
        const tooltip = document.getElementById('graph-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }
    
    static createTooltipElement() {
        const tooltip = document.createElement('div');
        tooltip.id = 'graph-tooltip';
        tooltip.className = 'graph-tooltip';
        tooltip.style.display = 'none';
        document.body.appendChild(tooltip);
        return tooltip;
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SOWGraphUtils;
}
"""
        
        js_path = self.static_path / "sow_graph_utils.js"
        js_path.write_text(js_content)
        
        self.logger.info("Created static assets for graph visualization")


# FastAPI web server for serving visualizations
class SOWVisualizationServer:
    """Web server for serving interactive SOW graph visualizations"""
    
    def __init__(self, kuzu_engine: KuzuSOWGraphEngine, analytics_engine: AdvancedSOWAnalytics):
        self.app = FastAPI(title="SOW Graph Visualization Server")
        self.kuzu_engine = kuzu_engine
        self.analytics_engine = analytics_engine
        self.visualizer = SOWGraphVisualizer(kuzu_engine, analytics_engine)
        
        # Store active WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        self._setup_routes()
        self._setup_static_files()
    
    def _setup_routes(self):
        """Setup FastAPI routes for visualization endpoints"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return self.visualizer.templates.TemplateResponse(
                "index.html", {"request": request}
            )
        
        @self.app.get("/api/graph/cytoscape")
        async def get_cytoscape_data(requirement_id: Optional[str] = None):
            return self.visualizer.create_cytoscape_visualization(requirement_id)
        
        @self.app.get("/api/graph/d3")
        async def get_d3_data(requirement_id: Optional[str] = None):
            return self.visualizer.create_d3_force_graph(requirement_id)
        
        @self.app.get("/api/graph/4d")
        async def get_4d_data(domain: Optional[str] = None):
            return self.visualizer.create_4d_visualization_data(domain)
        
        @self.app.websocket("/ws/graph")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Handle different message types
                    if message.get('type') == 'get_graph_data':
                        graph_data = self.visualizer.create_cytoscape_visualization(
                            message.get('requirement_id')
                        )
                        await websocket.send_text(json.dumps({
                            'type': 'graph_data',
                            'data': graph_data
                        }))
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    def _setup_static_files(self):
        """Setup static file serving"""
        self.app.mount(
            "/static", 
            StaticFiles(directory=str(self.visualizer.static_path)), 
            name="static"
        )
    
    async def broadcast_graph_update(self, update_data: Dict[str, Any]):
        """Broadcast graph updates to all connected clients"""
        message = json.dumps({
            'type': 'graph_update',
            'data': update_data
        })
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the visualization server"""
        uvicorn.run(self.app, host=host, port=port)


# Example usage
if __name__ == "__main__":
    from .kuzu_sow_schema import KuzuSOWGraphEngine, BusinessRequirement, DomainEntity
    from .sow_analytics_engine import AdvancedSOWAnalytics
    
    # Initialize engines
    kuzu_engine = KuzuSOWGraphEngine("viz_sow.db")
    analytics_engine = AdvancedSOWAnalytics(kuzu_engine)
    
    # Add some test data
    req = BusinessRequirement(
        id="VIZ_REQ_001",
        description="Implement advanced customer analytics platform",
        priority=1,
        domain="retail",
        complexity="high",
        estimated_hours=400,
        business_value=15000.0
    )
    
    entity = DomainEntity(
        id="VIZ_ENT_001",
        name="RetailCorp Analytics Division",
        entity_type="department",
        industry="retail",
        maturity_level="enterprise",
        technology_stack=["AWS", "Snowflake", "Tableau"],
        data_maturity="managed"
    )
    
    kuzu_engine.add_business_requirement(req)
    kuzu_engine.add_domain_entity(entity)
    
    # Create visualizations
    visualizer = SOWGraphVisualizer(kuzu_engine, analytics_engine)
    
    # Test Cytoscape visualization
    cyto_viz = visualizer.create_cytoscape_visualization("VIZ_REQ_001")
    print(f"Cytoscape visualization created with {len(cyto_viz['elements']['nodes'])} nodes")
    
    # Test D3 visualization
    d3_viz = visualizer.create_d3_force_graph("VIZ_REQ_001")
    print(f"D3 visualization created with {len(d3_viz['nodes'])} nodes")
    
    # Test 4D visualization
    viz_4d = visualizer.create_4d_visualization_data("retail")
    print(f"4D visualization created with {len(viz_4d['temporal']['time_series'])} time periods")
    
    # Start visualization server
    print("Starting SOW visualization server on http://localhost:8000")
    server = SOWVisualizationServer(kuzu_engine, analytics_engine)
    server.run()
    
    kuzu_engine.close()