"""
Engaging SOW Graph Builder Interface with Real-time Opportunity Discovery

This module creates an intuitive, business-friendly interface for building SOW
graphs with real-time opportunity discovery. Users can visually construct
requirements and immediately see discovered analytical opportunities.

Key Features:
1. Interactive SOW requirement builder
2. Real-time opportunity discovery as requirements are added
3. Visual graph construction with drag-and-drop
4. Business value calculator and ROI projector
5. Implementation timeline planning
6. Cross-domain opportunity detection
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn

from .kuzu_sow_schema import KuzuSOWGraphEngine, BusinessRequirement, DomainEntity, AnalyticalOpportunity
from .sow_analytics_engine import AdvancedSOWAnalytics, OpportunityCluster, BusinessImpactAnalysis
from .graph_visualization import SOWGraphVisualizer

logger = logging.getLogger(__name__)


@dataclass
class SOWRequirementInput:
    """Input structure for SOW requirement creation"""
    description: str
    priority: int
    domain: str
    complexity: str
    estimated_hours: Optional[int] = None
    business_value: Optional[float] = None
    stakeholder: Optional[str] = None
    deadline: Optional[str] = None
    context: Optional[str] = None


@dataclass
class OpportunityDiscoveryResult:
    """Result structure for opportunity discovery"""
    requirement_id: str
    discovered_opportunities: List[AnalyticalOpportunity]
    discovery_summary: Dict[str, Any]
    business_impact: List[BusinessImpactAnalysis]
    implementation_roadmap: Dict[str, Any]
    total_value: float
    confidence_score: float


@dataclass
class SOWProject:
    """Complete SOW project structure"""
    project_id: str
    project_name: str
    client_name: str
    industry: str
    project_type: str
    requirements: List[BusinessRequirement]
    opportunities: List[AnalyticalOpportunity]
    clusters: List[OpportunityCluster]
    total_estimated_hours: int
    total_business_value: float
    confidence_weighted_value: float
    created_at: datetime
    updated_at: datetime


class SOWBuilderEngine:
    """
    Core engine for SOW graph building with intelligent opportunity discovery.
    
    This class orchestrates the creation of SOW projects, real-time opportunity
    discovery, and business value optimization.
    """
    
    def __init__(self, kuzu_engine: KuzuSOWGraphEngine, analytics_engine: AdvancedSOWAnalytics):
        self.kuzu_engine = kuzu_engine
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
        
        # Active projects cache
        self.active_projects: Dict[str, SOWProject] = {}
        
        # Discovery settings
        self.discovery_settings = {
            'auto_discovery_enabled': True,
            'cross_domain_enabled': True,
            'pattern_matching_enabled': True,
            'min_confidence_threshold': 0.6,
            'max_opportunities_per_requirement': 5
        }
    
    async def create_sow_project(self, project_name: str, client_name: str, 
                               industry: str, project_type: str) -> SOWProject:
        """Create a new SOW project with initial setup"""
        try:
            project_id = f"SOW_{uuid.uuid4().hex[:8].upper()}"
            
            # Create domain entity for the client
            client_entity = DomainEntity(
                id=f"ENT_{project_id}",
                name=client_name,
                entity_type="client",
                industry=industry,
                maturity_level="mature",  # Default assumption
                technology_stack=[],
                data_maturity="defined"   # Default assumption
            )
            
            self.kuzu_engine.add_domain_entity(client_entity)
            
            # Initialize project
            project = SOWProject(
                project_id=project_id,
                project_name=project_name,
                client_name=client_name,
                industry=industry,
                project_type=project_type,
                requirements=[],
                opportunities=[],
                clusters=[],
                total_estimated_hours=0,
                total_business_value=0,
                confidence_weighted_value=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.active_projects[project_id] = project
            self.logger.info(f"Created SOW project: {project_id}")
            
            return project
            
        except Exception as e:
            self.logger.error(f"Failed to create SOW project: {e}")
            raise HTTPException(status_code=500, detail=f"Project creation failed: {e}")
    
    async def add_requirement_with_discovery(self, project_id: str, 
                                           req_input: SOWRequirementInput) -> OpportunityDiscoveryResult:
        """
        Add requirement and perform real-time opportunity discovery.
        
        This is the core interactive feature - as soon as a requirement is added,
        the system discovers related opportunities and presents them to the user.
        """
        try:
            if project_id not in self.active_projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.active_projects[project_id]
            
            # Generate requirement ID
            req_id = f"REQ_{project_id}_{len(project.requirements) + 1:03d}"
            
            # Create business requirement
            requirement = BusinessRequirement(
                id=req_id,
                description=req_input.description,
                priority=req_input.priority,
                domain=req_input.domain,
                complexity=req_input.complexity,
                estimated_hours=req_input.estimated_hours,
                business_value=req_input.business_value
            )
            
            # Add to graph database
            self.kuzu_engine.add_business_requirement(requirement)
            
            # Link to client entity
            await self._link_requirement_to_client(req_id, project_id)
            
            # Perform real-time opportunity discovery
            discovery_result = await self._discover_opportunities_realtime(req_id, project)
            
            # Update project
            project.requirements.append(requirement)
            project.opportunities.extend(discovery_result.discovered_opportunities)
            project.total_estimated_hours += requirement.estimated_hours or 0
            project.total_business_value += sum(opp.business_value for opp in discovery_result.discovered_opportunities)
            project.confidence_weighted_value += discovery_result.confidence_score * discovery_result.total_value
            project.updated_at = datetime.now()
            
            self.logger.info(f"Added requirement {req_id} with {len(discovery_result.discovered_opportunities)} opportunities")
            return discovery_result
            
        except Exception as e:
            self.logger.error(f"Failed to add requirement: {e}")
            raise HTTPException(status_code=500, detail=f"Requirement addition failed: {e}")
    
    async def _discover_opportunities_realtime(self, req_id: str, project: SOWProject) -> OpportunityDiscoveryResult:
        """Perform real-time opportunity discovery for a requirement"""
        
        # Use multiple discovery strategies
        opportunities = []
        
        if self.discovery_settings['pattern_matching_enabled']:
            # Pattern-based discovery
            pattern_opportunities = self.analytics_engine.discover_pattern_based_opportunities(req_id)
            opportunities.extend(pattern_opportunities)
        
        if self.discovery_settings['auto_discovery_enabled']:
            # Traditional rule-based discovery
            rule_opportunities = self.kuzu_engine.discover_implicit_opportunities(req_id)
            opportunities.extend(rule_opportunities)
        
        if self.discovery_settings['cross_domain_enabled'] and len(project.requirements) > 0:
            # Cross-domain discovery based on existing requirements
            cross_opportunities = await self._discover_cross_project_opportunities(req_id, project)
            opportunities.extend(cross_opportunities)
        
        # Filter by confidence threshold and limit
        filtered_opportunities = [
            opp for opp in opportunities 
            if opp.confidence_score >= self.discovery_settings['min_confidence_threshold']
        ][:self.discovery_settings['max_opportunities_per_requirement']]
        
        # Calculate business impact for top opportunities
        business_impacts = []
        for opp in filtered_opportunities:
            impact = self.analytics_engine.analyze_business_impact(opp.id)
            business_impacts.append(impact)
        
        # Create implementation roadmap
        roadmap = self._create_implementation_roadmap(filtered_opportunities, business_impacts)
        
        # Generate discovery summary
        summary = self._create_discovery_summary(filtered_opportunities, business_impacts)
        
        total_value = sum(opp.business_value for opp in filtered_opportunities)
        avg_confidence = sum(opp.confidence_score for opp in filtered_opportunities) / len(filtered_opportunities) if filtered_opportunities else 0
        
        return OpportunityDiscoveryResult(
            requirement_id=req_id,
            discovered_opportunities=filtered_opportunities,
            discovery_summary=summary,
            business_impact=business_impacts,
            implementation_roadmap=roadmap,
            total_value=total_value,
            confidence_score=avg_confidence
        )
    
    async def _discover_cross_project_opportunities(self, req_id: str, project: SOWProject) -> List[AnalyticalOpportunity]:
        """Discover opportunities by analyzing patterns within the project"""
        cross_opportunities = []
        
        try:
            # Analyze requirement patterns within the project
            existing_domains = set(req.domain for req in project.requirements)
            existing_complexities = [req.complexity for req in project.requirements]
            
            # Look for synergistic opportunities
            if len(existing_domains) > 1:
                # Multi-domain project - look for integration opportunities
                integration_opp = AnalyticalOpportunity(
                    id=f"{req_id}_CROSS_INTEGRATION",
                    description=f"Cross-domain integration platform spanning {', '.join(existing_domains)} domains",
                    complexity="high",
                    business_value=5000 + len(existing_domains) * 2000,
                    confidence_score=0.75,
                    discovery_method="cross_project",
                    related_requirements=[req.id for req in project.requirements],
                    implementation_approach="Build unified platform with domain-specific modules and shared services",
                    estimated_hours=400 + len(existing_domains) * 100
                )
                cross_opportunities.append(integration_opp)
            
            # Look for data consolidation opportunities
            data_requirements = [req for req in project.requirements if 'data' in req.description.lower()]
            if len(data_requirements) > 1:
                consolidation_opp = AnalyticalOpportunity(
                    id=f"{req_id}_CROSS_DATA_HUB",
                    description="Centralized data hub serving all project data requirements",
                    complexity="medium",
                    business_value=3000 + len(data_requirements) * 1000,
                    confidence_score=0.8,
                    discovery_method="cross_project", 
                    related_requirements=[req.id for req in data_requirements],
                    implementation_approach="Implement data lake with domain-specific data marts and unified API",
                    estimated_hours=250 + len(data_requirements) * 75
                )
                cross_opportunities.append(consolidation_opp)
            
            # Look for automation opportunities
            process_requirements = [req for req in project.requirements if any(
                keyword in req.description.lower() for keyword in ['process', 'workflow', 'manual', 'report']
            )]
            if len(process_requirements) > 1:
                automation_opp = AnalyticalOpportunity(
                    id=f"{req_id}_CROSS_AUTOMATION",
                    description="Comprehensive process automation platform addressing multiple workflows",
                    complexity="high",
                    business_value=4000 + len(process_requirements) * 1500,
                    confidence_score=0.7,
                    discovery_method="cross_project",
                    related_requirements=[req.id for req in process_requirements],
                    implementation_approach="Build workflow engine with configurable process templates and automation rules",
                    estimated_hours=350 + len(process_requirements) * 80
                )
                cross_opportunities.append(automation_opp)
            
            # Add discovered opportunities to graph
            for opp in cross_opportunities:
                self.kuzu_engine._add_discovered_opportunity(opp, req_id, "CROSS_PROJECT")
            
            return cross_opportunities
            
        except Exception as e:
            self.logger.error(f"Cross-project discovery failed: {e}")
            return cross_opportunities
    
    def _create_implementation_roadmap(self, opportunities: List[AnalyticalOpportunity], 
                                     impacts: List[BusinessImpactAnalysis]) -> Dict[str, Any]:
        """Create implementation roadmap for discovered opportunities"""
        
        # Sort opportunities by ROI and strategic value
        opportunity_scores = []
        for i, opp in enumerate(opportunities):
            impact = impacts[i] if i < len(impacts) else None
            score = (
                opp.confidence_score * 0.3 +
                (opp.business_value / 10000) * 0.3 +  # Normalize business value
                (impact.strategic_alignment if impact else 0.5) * 0.2 +
                (1 - (impact.implementation_complexity if impact else 0.5)) * 0.2  # Lower complexity = higher score
            )
            opportunity_scores.append((opp, impact, score))
        
        # Sort by score descending
        opportunity_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Create phases
        phases = []
        current_phase = 1
        phase_capacity = 500  # hours per phase
        current_phase_hours = 0
        current_phase_opps = []
        
        for opp, impact, score in opportunity_scores:
            opp_hours = opp.estimated_hours or 200
            
            if current_phase_hours + opp_hours > phase_capacity and current_phase_opps:
                # Start new phase
                phases.append({
                    'phase': current_phase,
                    'opportunities': current_phase_opps.copy(),
                    'total_hours': current_phase_hours,
                    'total_value': sum(o.business_value for o in current_phase_opps),
                    'duration_weeks': max(4, current_phase_hours // 40),  # Assuming 40 hours per week
                    'dependencies': self._analyze_phase_dependencies(current_phase_opps)
                })
                
                current_phase += 1
                current_phase_opps = []
                current_phase_hours = 0
            
            current_phase_opps.append(opp)
            current_phase_hours += opp_hours
        
        # Add final phase
        if current_phase_opps:
            phases.append({
                'phase': current_phase,
                'opportunities': current_phase_opps,
                'total_hours': current_phase_hours,
                'total_value': sum(opp.business_value for opp in current_phase_opps),
                'duration_weeks': max(4, current_phase_hours // 40),
                'dependencies': self._analyze_phase_dependencies(current_phase_opps)
            })
        
        return {
            'phases': phases,
            'total_phases': len(phases),
            'total_duration_weeks': sum(phase['duration_weeks'] for phase in phases),
            'total_investment': sum(phase['total_hours'] for phase in phases) * 150,  # $150/hour
            'total_expected_value': sum(phase['total_value'] for phase in phases),
            'overall_roi': self._calculate_overall_roi(phases)
        }
    
    def _analyze_phase_dependencies(self, opportunities: List[AnalyticalOpportunity]) -> List[str]:
        """Analyze dependencies within a phase"""
        dependencies = []
        
        # Simple heuristic-based dependency analysis
        governance_opps = [opp for opp in opportunities if 'governance' in opp.description.lower()]
        data_opps = [opp for opp in opportunities if 'data' in opp.description.lower() and 'governance' not in opp.description.lower()]
        
        if governance_opps and data_opps:
            dependencies.append("Data governance must be established before data analytics implementations")
        
        platform_opps = [opp for opp in opportunities if 'platform' in opp.description.lower()]
        specific_opps = [opp for opp in opportunities if 'platform' not in opp.description.lower()]
        
        if platform_opps and specific_opps:
            dependencies.append("Platform infrastructure should be implemented before specific analytics solutions")
        
        return dependencies
    
    def _calculate_overall_roi(self, phases: List[Dict]) -> float:
        """Calculate overall ROI for the implementation roadmap"""
        total_investment = sum(phase['total_hours'] for phase in phases) * 150
        total_value = sum(phase['total_value'] for phase in phases)
        
        if total_investment == 0:
            return 0
        
        return ((total_value - total_investment) / total_investment) * 100
    
    def _create_discovery_summary(self, opportunities: List[AnalyticalOpportunity],
                                impacts: List[BusinessImpactAnalysis]) -> Dict[str, Any]:
        """Create comprehensive discovery summary"""
        
        if not opportunities:
            return {
                'total_opportunities': 0,
                'discovery_methods': {},
                'complexity_distribution': {},
                'value_ranges': {},
                'confidence_stats': {},
                'key_insights': []
            }
        
        # Discovery methods breakdown
        discovery_methods = {}
        for opp in opportunities:
            method = opp.discovery_method
            discovery_methods[method] = discovery_methods.get(method, 0) + 1
        
        # Complexity distribution
        complexity_dist = {}
        for opp in opportunities:
            complexity = opp.complexity
            complexity_dist[complexity] = complexity_dist.get(complexity, 0) + 1
        
        # Value ranges
        values = [opp.business_value for opp in opportunities]
        value_ranges = {
            'min': min(values),
            'max': max(values),
            'average': sum(values) / len(values),
            'total': sum(values)
        }
        
        # Confidence statistics
        confidences = [opp.confidence_score for opp in opportunities]
        confidence_stats = {
            'min': min(confidences),
            'max': max(confidences),
            'average': sum(confidences) / len(confidences)
        }
        
        # Generate key insights
        insights = []
        
        # High-value opportunities
        high_value_opps = [opp for opp in opportunities if opp.business_value > 5000]
        if high_value_opps:
            insights.append(f"{len(high_value_opps)} high-value opportunities (>${5000}) identified")
        
        # High-confidence discoveries
        high_conf_opps = [opp for opp in opportunities if opp.confidence_score > 0.8]
        if high_conf_opps:
            insights.append(f"{len(high_conf_opps)} opportunities have high confidence (>80%)")
        
        # Cross-domain opportunities
        cross_domain_opps = [opp for opp in opportunities if opp.discovery_method == 'cross_project']
        if cross_domain_opps:
            insights.append(f"{len(cross_domain_opps)} cross-domain synergy opportunities discovered")
        
        # Pattern-based discoveries
        pattern_opps = [opp for opp in opportunities if opp.discovery_method == 'pattern_matching']
        if pattern_opps:
            insights.append(f"{len(pattern_opps)} opportunities discovered through advanced pattern matching")
        
        return {
            'total_opportunities': len(opportunities),
            'discovery_methods': discovery_methods,
            'complexity_distribution': complexity_dist,
            'value_ranges': value_ranges,
            'confidence_stats': confidence_stats,
            'key_insights': insights
        }
    
    async def _link_requirement_to_client(self, req_id: str, project_id: str):
        """Link requirement to client entity in the graph"""
        try:
            entity_id = f"ENT_{project_id}"
            
            link_query = """
            MATCH (req:BusinessRequirement {id: $req_id})
            MATCH (entity:DomainEntity {id: $entity_id})
            CREATE (req)-[:BELONGS_TO {
                ownership_level: 'primary',
                stakeholder_priority: 1.0
            }]->(entity)
            """
            
            self.kuzu_engine.conn.execute(link_query, {
                "req_id": req_id,
                "entity_id": entity_id
            })
            
        except Exception as e:
            self.logger.error(f"Failed to link requirement to client: {e}")
    
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project summary"""
        if project_id not in self.active_projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.active_projects[project_id]
        
        # Calculate project metrics
        total_opportunities = len(project.opportunities)
        avg_confidence = sum(opp.confidence_score for opp in project.opportunities) / total_opportunities if total_opportunities > 0 else 0
        
        # Cluster opportunities for better organization
        clusters = self.analytics_engine.cluster_related_opportunities(project.industry)
        
        return {
            'project': asdict(project),
            'metrics': {
                'requirements_count': len(project.requirements),
                'opportunities_count': total_opportunities,
                'total_estimated_hours': project.total_estimated_hours,
                'total_business_value': project.total_business_value,
                'average_confidence': avg_confidence,
                'clusters_count': len(clusters)
            },
            'opportunity_clusters': [asdict(cluster) for cluster in clusters],
            'recent_discoveries': [
                asdict(opp) for opp in sorted(project.opportunities, key=lambda x: x.created_at, reverse=True)[:5]
            ]
        }
    
    def update_discovery_settings(self, settings: Dict[str, Any]):
        """Update discovery engine settings"""
        self.discovery_settings.update(settings)
        self.logger.info(f"Updated discovery settings: {settings}")


class SOWBuilderAPI:
    """FastAPI application for SOW Graph Builder interface"""
    
    def __init__(self, kuzu_engine: KuzuSOWGraphEngine, analytics_engine: AdvancedSOWAnalytics):
        self.app = FastAPI(title="SOW Graph Builder API")
        self.kuzu_engine = kuzu_engine
        self.analytics_engine = analytics_engine
        self.builder_engine = SOWBuilderEngine(kuzu_engine, analytics_engine)
        self.visualizer = SOWGraphVisualizer(kuzu_engine, analytics_engine)
        
        self.templates = Jinja2Templates(directory=str(self.visualizer.static_path.parent / "templates"))
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def builder_interface(request: Request):
            return self.templates.TemplateResponse("sow_builder.html", {"request": request})
        
        @self.app.post("/api/projects")
        async def create_project(project_data: Dict[str, str]):
            project = await self.builder_engine.create_sow_project(
                project_name=project_data["name"],
                client_name=project_data["client"],
                industry=project_data["industry"],
                project_type=project_data["type"]
            )
            return {"project_id": project.project_id, "project": asdict(project)}
        
        @self.app.post("/api/projects/{project_id}/requirements")
        async def add_requirement(project_id: str, req_data: Dict[str, Any], background_tasks: BackgroundTasks):
            req_input = SOWRequirementInput(**req_data)
            result = await self.builder_engine.add_requirement_with_discovery(project_id, req_input)
            
            # Schedule background analysis for enhanced discovery
            background_tasks.add_task(self._enhanced_discovery_analysis, project_id, result.requirement_id)
            
            return {
                "requirement_id": result.requirement_id,
                "opportunities": [asdict(opp) for opp in result.discovered_opportunities],
                "summary": result.discovery_summary,
                "business_impact": [asdict(impact) for impact in result.business_impact],
                "roadmap": result.implementation_roadmap,
                "total_value": result.total_value,
                "confidence_score": result.confidence_score
            }
        
        @self.app.get("/api/projects/{project_id}")
        async def get_project(project_id: str):
            summary = self.builder_engine.get_project_summary(project_id)
            return summary
        
        @self.app.get("/api/projects/{project_id}/graph")
        async def get_project_graph(project_id: str):
            # Get all requirements for the project
            if project_id in self.builder_engine.active_projects:
                project = self.builder_engine.active_projects[project_id]
                if project.requirements:
                    # Return graph for first requirement (can be enhanced to show all)
                    return self.visualizer.create_cytoscape_visualization(project.requirements[0].id)
            
            return {"elements": {"nodes": [], "edges": []}, "layout": {}, "style": [], "config": {}}
        
        @self.app.put("/api/discovery-settings")
        async def update_settings(settings: Dict[str, Any]):
            self.builder_engine.update_discovery_settings(settings)
            return {"status": "updated", "settings": self.builder_engine.discovery_settings}
        
        @self.app.get("/api/discovery-settings")
        async def get_settings():
            return self.builder_engine.discovery_settings
    
    async def _enhanced_discovery_analysis(self, project_id: str, requirement_id: str):
        """Enhanced discovery analysis in the background"""
        try:
            # Run additional analysis that takes more time
            self.logger.info(f"Running enhanced discovery for {requirement_id}")
            
            # Perform clustering analysis
            clusters = self.analytics_engine.cluster_related_opportunities()
            
            # Update project with clusters
            if project_id in self.builder_engine.active_projects:
                project = self.builder_engine.active_projects[project_id]
                project.clusters = clusters
                project.updated_at = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Enhanced discovery analysis failed: {e}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8001):
        """Run the SOW Builder API server"""
        uvicorn.run(self.app, host=host, port=port)


# Example usage and demonstration
if __name__ == "__main__":
    from .kuzu_sow_schema import KuzuSOWGraphEngine
    from .sow_analytics_engine import AdvancedSOWAnalytics
    
    # Initialize engines
    kuzu_engine = KuzuSOWGraphEngine("sow_builder.db")
    analytics_engine = AdvancedSOWAnalytics(kuzu_engine)
    
    # Create and run SOW Builder API
    builder_api = SOWBuilderAPI(kuzu_engine, analytics_engine)
    
    print("Starting SOW Graph Builder on http://localhost:8001")
    print("Features:")
    print("- Interactive requirement input")
    print("- Real-time opportunity discovery")
    print("- Visual graph construction") 
    print("- Business value calculation")
    print("- Implementation roadmap planning")
    
    builder_api.run()
    
    kuzu_engine.close()