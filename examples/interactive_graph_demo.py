#!/usr/bin/env python3
"""
Interactive Graph Visualization Demo
Showcases the KuzuDB-powered semantic SOW graph with real-time discovery
"""

import asyncio
import json
from pathlib import Path
import webbrowser
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Dict, Any

# Import our semantic SOW system
from agentic_data_scraper.semantic.kuzu_sow_schema import KuzuSOWEngine
from agentic_data_scraper.semantic.sow_analytics_engine import SOWAnalyticsEngine
from agentic_data_scraper.semantic.graph_visualization import GraphVisualizer

class InteractiveGraphDemo:
    """Demo showcasing the interactive graph visualization capabilities"""
    
    def __init__(self):
        self.app = FastAPI(title="SOW Graph Visualization Demo")
        self.kuzu_engine = None
        self.analytics_engine = None
        self.visualizer = None
        self.setup_routes()
        
    async def initialize_demo_data(self):
        """Initialize demo data for showcase"""
        # Create demo database
        self.kuzu_engine = KuzuSOWEngine("demo_sow.db")
        await self.kuzu_engine.initialize()
        
        self.analytics_engine = SOWAnalyticsEngine(self.kuzu_engine)
        self.visualizer = GraphVisualizer(self.kuzu_engine)
        
        # Create sample SOW project
        project = await self.kuzu_engine.create_sow_project(
            name="Global Supply Chain Optimization",
            company="ACME Manufacturing Corp",
            industry="automotive",
            project_type="digital_transformation"
        )
        
        # Add sample requirements that will trigger intelligent discovery
        requirements = [
            {
                "description": "Track supplier performance across global locations",
                "priority": 1,
                "domain": "supply_chain",
                "complexity": "high"
            },
            {
                "description": "Monitor inventory levels in real-time",
                "priority": 1,
                "domain": "operations",
                "complexity": "medium"
            },
            {
                "description": "Ensure compliance with regulatory requirements",
                "priority": 2,
                "domain": "governance",
                "complexity": "high"
            },
            {
                "description": "Optimize logistics costs and delivery times",
                "priority": 1,
                "domain": "logistics",
                "complexity": "medium"
            }
        ]
        
        # Add each requirement and let the system discover opportunities
        for req_data in requirements:
            await self.kuzu_engine.add_business_requirement(
                project_id=project.project_id,
                **req_data
            )
        
        # Run analytics to discover opportunities
        await self.analytics_engine.discover_all_opportunities(project.project_id)
        
        return project
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            return HTMLResponse(self.get_demo_html())
            
        @self.app.get("/api/graph-data")
        async def get_graph_data():
            """Get the complete graph data for visualization"""
            if not self.kuzu_engine:
                await self.initialize_demo_data()
                
            # Get graph data from KuzuDB
            graph_data = await self.visualizer.get_interactive_graph_data()
            return graph_data
            
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time graph updates"""
            await websocket.accept()
            
            try:
                while True:
                    # Listen for client requests
                    data = await websocket.receive_json()
                    
                    if data["action"] == "discover_opportunities":
                        # Simulate adding a new requirement
                        new_req = data["requirement"]
                        
                        # Add to KuzuDB and discover opportunities
                        result = await self.analytics_engine.add_requirement_with_discovery(
                            project_id=data["project_id"],
                            requirement=new_req
                        )
                        
                        # Send back the updated graph data
                        graph_data = await self.visualizer.get_interactive_graph_data()
                        await websocket.send_json({
                            "type": "graph_update",
                            "data": graph_data,
                            "discovered_opportunities": len(result.discovered_opportunities)
                        })
                        
            except Exception as e:
                print(f"WebSocket error: {e}")
                await websocket.close()
    
    def get_demo_html(self) -> str:
        """Generate the interactive demo HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOW Graph Visualization Demo</title>
    
    <!-- Cytoscape.js for graph visualization -->
    <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
    <script src="https://unpkg.com/cytoscape-cose-bilkent@4.1.0/cytoscape-cose-bilkent.js"></script>
    
    <!-- Bootstrap for styling -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
        }
        
        .demo-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .demo-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .demo-header h1 {
            margin: 0;
            font-size: 2.2rem;
            font-weight: 300;
        }
        
        .demo-header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        #graph-container {
            width: 100%;
            height: 600px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .controls-panel {
            padding: 20px;
            background: #f8f9fa;
        }
        
        .stats-panel {
            background: #e8f4f8;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        
        .opportunity-item {
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .btn-demo {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            color: white;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn-demo:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .legend {
            display: flex;
            gap: 15px;
            margin: 15px 0;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="demo-container">
            <div class="demo-header">
                <h1>🚀 Interactive SOW Graph Visualization</h1>
                <p>KuzuDB-Powered Semantic Analytics with Real-Time Opportunity Discovery</p>
            </div>
            
            <div id="graph-container"></div>
            
            <div class="controls-panel">
                <div class="row">
                    <div class="col-md-4">
                        <div class="stats-panel">
                            <h5>📊 Graph Statistics</h5>
                            <div id="stats-content">
                                <p><strong>Requirements:</strong> <span id="req-count">Loading...</span></p>
                                <p><strong>Opportunities:</strong> <span id="opp-count">Loading...</span></p>
                                <p><strong>Connections:</strong> <span id="edge-count">Loading...</span></p>
                            </div>
                        </div>
                        
                        <div class="legend">
                            <div class="legend-item">
                                <div class="legend-dot" style="background: #007bff;"></div>
                                <span>Requirements</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-dot" style="background: #28a745;"></div>
                                <span>Opportunities</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-dot" style="background: #ffc107;"></div>
                                <span>Entities</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-8">
                        <h5>🎯 Interactive Demo Actions</h5>
                        <div class="mb-3">
                            <button class="btn-demo" onclick="addNewRequirement()">
                                Add New Requirement
                            </button>
                            <button class="btn-demo" onclick="discoverOpportunities()">
                                Discover Opportunities
                            </button>
                            <button class="btn-demo" onclick="resetLayout()">
                                Reset Layout
                            </button>
                        </div>
                        
                        <div id="opportunities-panel">
                            <h6>💡 Recently Discovered Opportunities</h6>
                            <div id="opportunities-list"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let cy;
        let ws;
        let currentProjectId;
        
        // Initialize the demo
        async function initializeDemo() {
            console.log('Initializing SOW Graph Visualization Demo...');
            
            // Setup WebSocket connection
            setupWebSocket();
            
            // Load initial graph data
            await loadGraphData();
        }
        
        function setupWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                
                if (message.type === 'graph_update') {
                    updateGraph(message.data);
                    showNotification(`Discovered ${message.discovered_opportunities} new opportunities!`);
                }
            };
        }
        
        async function loadGraphData() {
            try {
                const response = await fetch('/api/graph-data');
                const graphData = await response.json();
                
                currentProjectId = graphData.project_id;
                initializeGraph(graphData);
                updateStats(graphData);
                
            } catch (error) {
                console.error('Error loading graph data:', error);
                showNotification('Error loading graph data', 'error');
            }
        }
        
        function initializeGraph(graphData) {
            cy = cytoscape({
                container: document.getElementById('graph-container'),
                
                elements: graphData.elements,
                
                style: [
                    {
                        selector: 'node[type="requirement"]',
                        style: {
                            'background-color': '#007bff',
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': 'white',
                            'text-outline-width': 2,
                            'text-outline-color': '#007bff',
                            'font-size': '10px',
                            'width': '60px',
                            'height': '60px'
                        }
                    },
                    {
                        selector: 'node[type="opportunity"]',
                        style: {
                            'background-color': '#28a745',
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': 'white',
                            'text-outline-width': 2,
                            'text-outline-color': '#28a745',
                            'font-size': '9px',
                            'width': '50px',
                            'height': '50px'
                        }
                    },
                    {
                        selector: 'node[type="entity"]',
                        style: {
                            'background-color': '#ffc107',
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': '#333',
                            'text-outline-width': 1,
                            'text-outline-color': '#ffc107',
                            'font-size': '8px',
                            'width': '40px',
                            'height': '40px'
                        }
                    },
                    {
                        selector: 'edge',
                        style: {
                            'width': 2,
                            'line-color': '#666',
                            'target-arrow-color': '#666',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'label': 'data(relationship)',
                            'font-size': '8px',
                            'text-rotation': 'autorotate'
                        }
                    },
                    {
                        selector: 'edge[relationship="IMPLIES"]',
                        style: {
                            'line-color': '#28a745',
                            'target-arrow-color': '#28a745',
                            'line-style': 'dashed'
                        }
                    }
                ],
                
                layout: {
                    name: 'cose-bilkent',
                    quality: 'default',
                    nodeDimensionsIncludeLabels: true,
                    refresh: 20,
                    fit: true,
                    padding: 30,
                    randomize: false,
                    nodeRepulsion: 4500,
                    idealEdgeLength: 50,
                    edgeElasticity: 0.45,
                    nestingFactor: 0.1,
                    gravity: 0.25,
                    numIter: 2500
                }
            });
            
            // Add click handlers
            cy.on('tap', 'node', function(evt) {
                const node = evt.target;
                showNodeDetails(node.data());
            });
            
            cy.on('tap', 'edge', function(evt) {
                const edge = evt.target;
                highlightPath(edge);
            });
        }
        
        function updateGraph(graphData) {
            if (cy) {
                cy.elements().remove();
                cy.add(graphData.elements);
                cy.layout({name: 'cose-bilkent', fit: true}).run();
                updateStats(graphData);
            }
        }
        
        function updateStats(graphData) {
            const requirements = graphData.elements.filter(e => e.data.type === 'requirement').length;
            const opportunities = graphData.elements.filter(e => e.data.type === 'opportunity').length;
            const edges = graphData.elements.filter(e => e.group === 'edges').length;
            
            document.getElementById('req-count').textContent = requirements;
            document.getElementById('opp-count').textContent = opportunities;
            document.getElementById('edge-count').textContent = edges;
        }
        
        function showNodeDetails(nodeData) {
            const modal = `
                <div class="alert alert-info alert-dismissible fade show" role="alert">
                    <strong>${nodeData.type.charAt(0).toUpperCase() + nodeData.type.slice(1)}:</strong> ${nodeData.label}<br>
                    ${nodeData.description || 'No additional details available.'}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            document.getElementById('opportunities-list').innerHTML = modal + document.getElementById('opportunities-list').innerHTML;
        }
        
        function addNewRequirement() {
            const requirements = [
                "Implement predictive maintenance for manufacturing equipment",
                "Monitor environmental compliance across facilities",
                "Track customer satisfaction and feedback",
                "Optimize energy consumption and sustainability",
                "Enhance cybersecurity monitoring"
            ];
            
            const newReq = {
                description: requirements[Math.floor(Math.random() * requirements.length)],
                priority: Math.floor(Math.random() * 3) + 1,
                domain: "operations",
                complexity: ["low", "medium", "high"][Math.floor(Math.random() * 3)]
            };
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    action: "discover_opportunities",
                    project_id: currentProjectId,
                    requirement: newReq
                }));
                
                showNotification("Adding new requirement and discovering opportunities...");
            }
        }
        
        function discoverOpportunities() {
            showNotification("Running advanced analytics to discover cross-domain opportunities...");
            
            // Simulate discovery animation
            if (cy) {
                cy.nodes('[type="opportunity"]').animate({
                    style: { 'background-color': '#ff6b6b' }
                }, {
                    duration: 500,
                    complete: function() {
                        cy.nodes('[type="opportunity"]').animate({
                            style: { 'background-color': '#28a745' }
                        }, { duration: 500 });
                    }
                });
            }
        }
        
        function resetLayout() {
            if (cy) {
                cy.layout({name: 'cose-bilkent', fit: true}).run();
                showNotification("Layout reset complete!");
            }
        }
        
        function showNotification(message, type = 'success') {
            const alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
            const notification = `
                <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                     style="top: 20px; right: 20px; z-index: 9999;" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            document.body.insertAdjacentHTML('afterbegin', notification);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {
                const alerts = document.querySelectorAll('.alert');
                if (alerts.length > 0) {
                    alerts[0].remove();
                }
            }, 3000);
        }
        
        function highlightPath(edge) {
            cy.elements().removeClass('highlighted');
            edge.addClass('highlighted');
            edge.source().addClass('highlighted');
            edge.target().addClass('highlighted');
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', initializeDemo);
    </script>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """

    async def run_demo(self, port: int = 8000):
        """Run the interactive demo server"""
        print(f"""
🚀 SOW Graph Visualization Demo Starting...

📊 Features:
• KuzuDB-powered graph database
• Real-time opportunity discovery
• Interactive graph exploration
• Cross-domain analytics
• 4D visualization layers

🌐 Opening demo at: http://localhost:{port}
        """)
        
        # Open browser automatically
        webbrowser.open(f"http://localhost:{port}")
        
        # Run the server
        config = uvicorn.Config(
            app=self.app,
            host="127.0.0.1",
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


# Main execution
async def main():
    """Run the interactive demo"""
    demo = InteractiveGraphDemo()
    await demo.run_demo(port=8000)


if __name__ == "__main__":
    asyncio.run(main())