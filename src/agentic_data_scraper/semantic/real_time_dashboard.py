"""
Real-time Graph Analytics Dashboard with Performance Metrics and Pattern Discovery

This module creates a comprehensive real-time dashboard for SOW analytics,
providing live insights into graph performance, pattern discovery effectiveness,
and business impact metrics. It uses KuzuDB's analytical capabilities with
engaging real-time visualizations.

Key Features:
1. Real-time graph performance monitoring
2. Pattern discovery effectiveness tracking
3. Business value analytics with ROI projections
4. Cross-domain correlation insights
5. Interactive trend analysis and forecasting
6. Automated anomaly detection and alerting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import time
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from .kuzu_sow_schema import KuzuSOWGraphEngine
from .sow_analytics_engine import AdvancedSOWAnalytics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Real-time performance metric"""
    timestamp: datetime
    metric_name: str
    metric_value: float
    metric_unit: str
    category: str  # 'graph', 'discovery', 'business', 'system'
    context: Optional[Dict[str, Any]] = None


@dataclass
class DiscoveryEvent:
    """Pattern discovery event for real-time tracking"""
    timestamp: datetime
    event_type: str  # 'opportunity_discovered', 'pattern_matched', 'correlation_found'
    requirement_id: str
    opportunity_id: str
    pattern_name: str
    confidence_score: float
    business_value: float
    discovery_method: str
    processing_time_ms: float


@dataclass
class BusinessInsight:
    """Business insight generated from analytics"""
    timestamp: datetime
    insight_type: str  # 'trend', 'anomaly', 'correlation', 'optimization'
    title: str
    description: str
    impact_level: str  # 'low', 'medium', 'high', 'critical'
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]


@dataclass
class AlertEvent:
    """System alert for important events"""
    timestamp: datetime
    alert_type: str  # 'performance', 'discovery', 'business', 'system'
    severity: str  # 'info', 'warning', 'error', 'critical'
    title: str
    message: str
    source_component: str
    auto_resolve: bool = False


class RealTimeAnalytics:
    """
    Real-time analytics engine for SOW graph performance monitoring.
    
    This class tracks and analyzes graph operations, discovery effectiveness,
    and business metrics in real-time, providing actionable insights.
    """
    
    def __init__(self, kuzu_engine: KuzuSOWGraphEngine, analytics_engine: AdvancedSOWAnalytics):
        self.kuzu_engine = kuzu_engine
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
        
        # Real-time data stores (using deque for efficient FIFO operations)
        self.performance_metrics = deque(maxlen=10000)
        self.discovery_events = deque(maxlen=5000)
        self.business_insights = deque(maxlen=1000)
        self.alert_events = deque(maxlen=500)
        
        # Active monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_analysis_time = datetime.now()
        
        # Performance baselines
        self.performance_baselines = {
            'query_response_time_ms': 100,
            'discovery_confidence_threshold': 0.7,
            'business_value_threshold': 1000,
            'graph_density_optimal': 0.15
        }
        
        # WebSocket connections for real-time updates
        self.active_connections: List[WebSocket] = []
    
    def start_monitoring(self):
        """Start real-time monitoring of graph analytics"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Started real-time analytics monitoring")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Stopped real-time analytics monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop - runs in separate thread"""
        while self.is_monitoring:
            try:
                self._collect_performance_metrics()
                self._analyze_discovery_patterns()
                self._generate_business_insights()
                self._check_for_anomalies()
                
                # Update last analysis time
                self.last_analysis_time = datetime.now()
                
                # Sleep for monitoring interval
                time.sleep(10)  # Collect metrics every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _collect_performance_metrics(self):
        """Collect real-time performance metrics from KuzuDB"""
        current_time = datetime.now()
        
        try:
            # Graph structure metrics
            graph_stats = self._get_graph_statistics()
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="graph_node_count",
                metric_value=graph_stats.get('total_nodes', 0),
                metric_unit="count",
                category="graph"
            ))
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="graph_edge_count",
                metric_value=graph_stats.get('total_edges', 0),
                metric_unit="count",
                category="graph"
            ))
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="graph_density",
                metric_value=graph_stats.get('density', 0),
                metric_unit="ratio",
                category="graph"
            ))
            
            # Query performance metrics
            query_perf = self._measure_query_performance()
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="avg_query_response_time",
                metric_value=query_perf.get('avg_response_time', 0),
                metric_unit="ms",
                category="system"
            ))
            
            # Discovery effectiveness metrics
            discovery_stats = self._get_discovery_statistics()
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="discovery_success_rate",
                metric_value=discovery_stats.get('success_rate', 0),
                metric_unit="percentage",
                category="discovery"
            ))
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="avg_confidence_score",
                metric_value=discovery_stats.get('avg_confidence', 0),
                metric_unit="score",
                category="discovery"
            ))
            
            # Business value metrics
            business_stats = self._get_business_value_statistics()
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="total_business_value",
                metric_value=business_stats.get('total_value', 0),
                metric_unit="dollars",
                category="business"
            ))
            
            self._add_metric(PerformanceMetric(
                timestamp=current_time,
                metric_name="avg_opportunity_value",
                metric_value=business_stats.get('avg_value', 0),
                metric_unit="dollars",
                category="business"
            ))
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance metrics: {e}")
    
    def _get_graph_statistics(self) -> Dict[str, float]:
        """Get current graph statistics"""
        try:
            stats_query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->()
            RETURN count(DISTINCT n) as node_count, count(r) as edge_count
            """
            
            result = self.kuzu_engine.conn.execute(stats_query)
            record = result.get_next()
            
            if record:
                node_count = record[0] or 0
                edge_count = record[1] or 0
                
                # Calculate density
                max_edges = node_count * (node_count - 1) if node_count > 1 else 1
                density = edge_count / max_edges if max_edges > 0 else 0
                
                return {
                    'total_nodes': float(node_count),
                    'total_edges': float(edge_count),
                    'density': density
                }
            
            return {'total_nodes': 0, 'total_edges': 0, 'density': 0}
            
        except Exception as e:
            self.logger.error(f"Failed to get graph statistics: {e}")
            return {'total_nodes': 0, 'total_edges': 0, 'density': 0}
    
    def _measure_query_performance(self) -> Dict[str, float]:
        """Measure query performance metrics"""
        try:
            response_times = []
            
            # Test different query types
            test_queries = [
                "MATCH (req:BusinessRequirement) RETURN count(req)",
                "MATCH (opp:AnalyticalOpportunity) RETURN count(opp)",
                "MATCH (req:BusinessRequirement)-[:IMPLIES]->(opp:AnalyticalOpportunity) RETURN count(*)"
            ]
            
            for query in test_queries:
                start_time = time.time()
                try:
                    self.kuzu_engine.conn.execute(query)
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    response_times.append(response_time)
                except:
                    response_times.append(1000)  # Default high response time on error
            
            return {
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0,
                'min_response_time': min(response_times) if response_times else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to measure query performance: {e}")
            return {'avg_response_time': 0, 'max_response_time': 0, 'min_response_time': 0}
    
    def _get_discovery_statistics(self) -> Dict[str, float]:
        """Get discovery effectiveness statistics"""
        try:
            discovery_query = """
            MATCH (opp:AnalyticalOpportunity)
            WHERE opp.created_at >= $recent_time
            RETURN 
                count(opp) as total_opportunities,
                avg(opp.confidence_score) as avg_confidence,
                sum(CASE WHEN opp.confidence_score > 0.7 THEN 1 ELSE 0 END) as high_confidence_count
            """
            
            recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
            result = self.kuzu_engine.conn.execute(discovery_query, {"recent_time": recent_time})
            record = result.get_next()
            
            if record:
                total = record[0] or 0
                avg_confidence = record[1] or 0
                high_confidence = record[2] or 0
                
                success_rate = (high_confidence / total * 100) if total > 0 else 0
                
                return {
                    'total_opportunities': float(total),
                    'avg_confidence': float(avg_confidence),
                    'success_rate': success_rate
                }
            
            return {'total_opportunities': 0, 'avg_confidence': 0, 'success_rate': 0}
            
        except Exception as e:
            self.logger.error(f"Failed to get discovery statistics: {e}")
            return {'total_opportunities': 0, 'avg_confidence': 0, 'success_rate': 0}
    
    def _get_business_value_statistics(self) -> Dict[str, float]:
        """Get business value statistics"""
        try:
            value_query = """
            MATCH (opp:AnalyticalOpportunity)
            WHERE opp.created_at >= $recent_time
            RETURN 
                sum(opp.business_value) as total_value,
                avg(opp.business_value) as avg_value,
                count(opp) as opportunity_count
            """
            
            recent_time = (datetime.now() - timedelta(hours=24)).isoformat()
            result = self.kuzu_engine.conn.execute(value_query, {"recent_time": recent_time})
            record = result.get_next()
            
            if record:
                return {
                    'total_value': float(record[0] or 0),
                    'avg_value': float(record[1] or 0),
                    'opportunity_count': float(record[2] or 0)
                }
            
            return {'total_value': 0, 'avg_value': 0, 'opportunity_count': 0}
            
        except Exception as e:
            self.logger.error(f"Failed to get business value statistics: {e}")
            return {'total_value': 0, 'avg_value': 0, 'opportunity_count': 0}
    
    def _analyze_discovery_patterns(self):
        """Analyze pattern discovery effectiveness over time"""
        try:
            # Look at recent discovery events
            recent_events = [
                event for event in self.discovery_events 
                if event.timestamp >= datetime.now() - timedelta(hours=1)
            ]
            
            if len(recent_events) < 5:
                return  # Not enough data
            
            # Analyze confidence trends
            confidences = [event.confidence_score for event in recent_events]
            avg_confidence = statistics.mean(confidences)
            
            # Check for declining confidence trend
            if len(confidences) >= 10:
                recent_avg = statistics.mean(confidences[-5:])
                older_avg = statistics.mean(confidences[-10:-5])
                
                if recent_avg < older_avg - 0.1:  # 10% decline
                    self._add_alert(AlertEvent(
                        timestamp=datetime.now(),
                        alert_type="discovery",
                        severity="warning",
                        title="Discovery Confidence Declining",
                        message=f"Average confidence declined from {older_avg:.2f} to {recent_avg:.2f}",
                        source_component="pattern_discovery"
                    ))
            
            # Analyze processing time trends
            processing_times = [event.processing_time_ms for event in recent_events]
            avg_processing_time = statistics.mean(processing_times)
            
            if avg_processing_time > 5000:  # 5 seconds
                self._add_alert(AlertEvent(
                    timestamp=datetime.now(),
                    alert_type="performance",
                    severity="warning",
                    title="Slow Discovery Performance",
                    message=f"Average discovery time: {avg_processing_time:.0f}ms",
                    source_component="discovery_engine"
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to analyze discovery patterns: {e}")
    
    def _generate_business_insights(self):
        """Generate automated business insights from collected data"""
        try:
            current_time = datetime.now()
            
            # Trend analysis
            self._analyze_value_trends(current_time)
            self._analyze_domain_patterns(current_time)
            self._analyze_opportunity_clustering(current_time)
            
        except Exception as e:
            self.logger.error(f"Failed to generate business insights: {e}")
    
    def _analyze_value_trends(self, current_time: datetime):
        """Analyze business value trends"""
        try:
            # Get recent business value metrics
            recent_metrics = [
                metric for metric in self.performance_metrics
                if (metric.category == "business" and 
                    metric.metric_name == "total_business_value" and
                    metric.timestamp >= current_time - timedelta(hours=4))
            ]
            
            if len(recent_metrics) >= 10:
                values = [metric.metric_value for metric in recent_metrics]
                
                # Calculate trend
                if len(values) >= 2:
                    trend_slope = (values[-1] - values[0]) / len(values)
                    
                    if trend_slope > 1000:  # Positive trend
                        self._add_insight(BusinessInsight(
                            timestamp=current_time,
                            insight_type="trend",
                            title="Positive Business Value Trend",
                            description=f"Business value increased by ${trend_slope:.0f} per measurement",
                            impact_level="medium",
                            recommended_actions=[
                                "Continue current discovery strategies",
                                "Scale successful pattern matching approaches",
                                "Document effective techniques for replication"
                            ],
                            supporting_data={"trend_slope": trend_slope, "sample_size": len(values)}
                        ))
                    elif trend_slope < -500:  # Negative trend
                        self._add_insight(BusinessInsight(
                            timestamp=current_time,
                            insight_type="trend",
                            title="Declining Business Value Trend",
                            description=f"Business value decreased by ${abs(trend_slope):.0f} per measurement",
                            impact_level="high",
                            recommended_actions=[
                                "Review discovery algorithms for effectiveness",
                                "Analyze low-value opportunity patterns",
                                "Adjust confidence thresholds",
                                "Focus on high-value domains"
                            ],
                            supporting_data={"trend_slope": trend_slope, "sample_size": len(values)}
                        ))
                        
        except Exception as e:
            self.logger.error(f"Failed to analyze value trends: {e}")
    
    def _analyze_domain_patterns(self, current_time: datetime):
        """Analyze cross-domain discovery patterns"""
        try:
            # Get recent discovery events grouped by domain
            recent_events = [
                event for event in self.discovery_events
                if event.timestamp >= current_time - timedelta(hours=2)
            ]
            
            if len(recent_events) < 10:
                return
            
            # Group by discovery method
            method_stats = defaultdict(list)
            for event in recent_events:
                method_stats[event.discovery_method].append(event.business_value)
            
            # Find most effective methods
            method_effectiveness = {}
            for method, values in method_stats.items():
                if len(values) >= 3:
                    method_effectiveness[method] = statistics.mean(values)
            
            if method_effectiveness:
                best_method = max(method_effectiveness.items(), key=lambda x: x[1])
                
                if best_method[1] > 3000:  # High-value method
                    self._add_insight(BusinessInsight(
                        timestamp=current_time,
                        insight_type="optimization",
                        title=f"High-Performance Discovery Method: {best_method[0]}",
                        description=f"Method '{best_method[0]}' generates avg value of ${best_method[1]:.0f}",
                        impact_level="high",
                        recommended_actions=[
                            f"Prioritize {best_method[0]} discovery method",
                            "Allocate more resources to this approach",
                            "Train team on effective patterns",
                            "Consider automating this method further"
                        ],
                        supporting_data={"method_stats": method_effectiveness}
                    ))
                    
        except Exception as e:
            self.logger.error(f"Failed to analyze domain patterns: {e}")
    
    def _analyze_opportunity_clustering(self, current_time: datetime):
        """Analyze opportunity clustering effectiveness"""
        try:
            # Get opportunity clusters from analytics engine
            clusters = self.analytics_engine.cluster_related_opportunities()
            
            if not clusters:
                return
            
            # Analyze cluster synergy scores
            high_synergy_clusters = [cluster for cluster in clusters if cluster.synergy_score > 0.8]
            
            if len(high_synergy_clusters) > 0:
                total_synergy_value = sum(cluster.combined_value for cluster in high_synergy_clusters)
                
                self._add_insight(BusinessInsight(
                    timestamp=current_time,
                    insight_type="correlation",
                    title="High-Synergy Opportunity Clusters Identified",
                    description=f"Found {len(high_synergy_clusters)} high-synergy clusters worth ${total_synergy_value:.0f}",
                    impact_level="high",
                    recommended_actions=[
                        "Prioritize clustered opportunities for implementation",
                        "Consider package deals for related opportunities",
                        "Leverage synergies in implementation planning",
                        "Use cluster insights for future discovery"
                    ],
                    supporting_data={
                        "cluster_count": len(high_synergy_clusters),
                        "total_value": total_synergy_value,
                        "avg_synergy_score": statistics.mean([c.synergy_score for c in high_synergy_clusters])
                    }
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to analyze opportunity clustering: {e}")
    
    def _check_for_anomalies(self):
        """Check for anomalies in system performance and discovery"""
        try:
            current_time = datetime.now()
            
            # Check query performance anomalies
            recent_perf_metrics = [
                metric for metric in self.performance_metrics
                if (metric.category == "system" and 
                    metric.metric_name == "avg_query_response_time" and
                    metric.timestamp >= current_time - timedelta(minutes=30))
            ]
            
            if len(recent_perf_metrics) >= 5:
                response_times = [metric.metric_value for metric in recent_perf_metrics]
                avg_response_time = statistics.mean(response_times)
                
                if avg_response_time > self.performance_baselines['query_response_time_ms'] * 3:
                    self._add_alert(AlertEvent(
                        timestamp=current_time,
                        alert_type="performance",
                        severity="error",
                        title="Query Performance Degradation",
                        message=f"Query response time ({avg_response_time:.0f}ms) exceeds baseline by 300%",
                        source_component="kuzu_engine"
                    ))
            
            # Check discovery anomalies
            recent_discovery_metrics = [
                metric for metric in self.performance_metrics
                if (metric.category == "discovery" and
                    metric.metric_name == "avg_confidence_score" and
                    metric.timestamp >= current_time - timedelta(hours=1))
            ]
            
            if len(recent_discovery_metrics) >= 5:
                confidence_scores = [metric.metric_value for metric in recent_discovery_metrics]
                avg_confidence = statistics.mean(confidence_scores)
                
                if avg_confidence < self.performance_baselines['discovery_confidence_threshold']:
                    self._add_alert(AlertEvent(
                        timestamp=current_time,
                        alert_type="discovery",
                        severity="warning",
                        title="Low Discovery Confidence",
                        message=f"Average confidence ({avg_confidence:.2f}) below threshold ({self.performance_baselines['discovery_confidence_threshold']})",
                        source_component="discovery_engine"
                    ))
                    
        except Exception as e:
            self.logger.error(f"Failed to check for anomalies: {e}")
    
    def _add_metric(self, metric: PerformanceMetric):
        """Add a performance metric to the real-time store"""
        self.performance_metrics.append(metric)
        
        # Broadcast to connected WebSocket clients
        asyncio.create_task(self._broadcast_metric_update(metric))
    
    def _add_insight(self, insight: BusinessInsight):
        """Add a business insight to the store"""
        self.business_insights.append(insight)
        
        # Broadcast to connected WebSocket clients
        asyncio.create_task(self._broadcast_insight_update(insight))
    
    def _add_alert(self, alert: AlertEvent):
        """Add an alert event to the store"""
        self.alert_events.append(alert)
        self.logger.warning(f"Alert: {alert.title} - {alert.message}")
        
        # Broadcast to connected WebSocket clients
        asyncio.create_task(self._broadcast_alert_update(alert))
    
    async def _broadcast_metric_update(self, metric: PerformanceMetric):
        """Broadcast metric update to WebSocket clients"""
        message = {
            "type": "metric_update",
            "data": asdict(metric)
        }
        await self._broadcast_to_websockets(message)
    
    async def _broadcast_insight_update(self, insight: BusinessInsight):
        """Broadcast insight update to WebSocket clients"""
        message = {
            "type": "insight_update", 
            "data": asdict(insight)
        }
        await self._broadcast_to_websockets(message)
    
    async def _broadcast_alert_update(self, alert: AlertEvent):
        """Broadcast alert update to WebSocket clients"""
        message = {
            "type": "alert_update",
            "data": asdict(alert)
        }
        await self._broadcast_to_websockets(message)
    
    async def _broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message, default=str)
        
        # Remove disconnected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.active_connections.remove(connection)
    
    def add_discovery_event(self, requirement_id: str, opportunity_id: str, 
                           pattern_name: str, confidence_score: float,
                           business_value: float, discovery_method: str, processing_time_ms: float):
        """Add a discovery event for tracking"""
        event = DiscoveryEvent(
            timestamp=datetime.now(),
            event_type="opportunity_discovered",
            requirement_id=requirement_id,
            opportunity_id=opportunity_id,
            pattern_name=pattern_name,
            confidence_score=confidence_score,
            business_value=business_value,
            discovery_method=discovery_method,
            processing_time_ms=processing_time_ms
        )
        
        self.discovery_events.append(event)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        current_time = datetime.now()
        
        # Get recent metrics by category
        recent_metrics = [
            metric for metric in self.performance_metrics
            if metric.timestamp >= current_time - timedelta(hours=4)
        ]
        
        # Group metrics by category
        metrics_by_category = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_category[metric.category].append(metric)
        
        # Get recent insights and alerts
        recent_insights = [
            insight for insight in self.business_insights
            if insight.timestamp >= current_time - timedelta(hours=24)
        ]
        
        recent_alerts = [
            alert for alert in self.alert_events
            if alert.timestamp >= current_time - timedelta(hours=24)
        ]
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(recent_metrics)
        
        return {
            "timestamp": current_time.isoformat(),
            "metrics_by_category": {
                category: [asdict(metric) for metric in metrics]
                for category, metrics in metrics_by_category.items()
            },
            "recent_insights": [asdict(insight) for insight in recent_insights],
            "recent_alerts": [asdict(alert) for alert in recent_alerts],
            "summary_statistics": summary_stats,
            "system_status": self._get_system_status(),
            "monitoring_active": self.is_monitoring
        }
    
    def _calculate_summary_statistics(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate summary statistics from metrics"""
        stats = {}
        
        # Group by metric name
        metrics_by_name = defaultdict(list)
        for metric in metrics:
            metrics_by_name[metric.metric_name].append(metric.metric_value)
        
        # Calculate stats for each metric
        for metric_name, values in metrics_by_name.items():
            if values:
                stats[metric_name] = {
                    "current": values[-1],
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                    "trend": "up" if len(values) > 1 and values[-1] > values[0] else "down" if len(values) > 1 else "stable"
                }
        
        return stats
    
    def _get_system_status(self) -> Dict[str, str]:
        """Get overall system status"""
        try:
            # Check recent alerts
            recent_critical_alerts = [
                alert for alert in self.alert_events
                if (alert.timestamp >= datetime.now() - timedelta(minutes=30) and
                    alert.severity in ['error', 'critical'])
            ]
            
            if recent_critical_alerts:
                return {"status": "error", "message": "Critical alerts present"}
            
            recent_warning_alerts = [
                alert for alert in self.alert_events
                if (alert.timestamp >= datetime.now() - timedelta(minutes=30) and
                    alert.severity == 'warning')
            ]
            
            if recent_warning_alerts:
                return {"status": "warning", "message": f"{len(recent_warning_alerts)} warnings"}
            
            return {"status": "healthy", "message": "All systems operational"}
            
        except Exception as e:
            return {"status": "error", "message": f"Status check failed: {e}"}
    
    async def add_websocket_connection(self, websocket: WebSocket):
        """Add WebSocket connection for real-time updates"""
        self.active_connections.append(websocket)
        
    async def remove_websocket_connection(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)


class RealTimeDashboardAPI:
    """FastAPI application for real-time analytics dashboard"""
    
    def __init__(self, kuzu_engine: KuzuSOWGraphEngine, analytics_engine: AdvancedSOWAnalytics):
        self.app = FastAPI(title="SOW Real-time Analytics Dashboard")
        self.kuzu_engine = kuzu_engine
        self.analytics_engine = analytics_engine
        self.real_time_analytics = RealTimeAnalytics(kuzu_engine, analytics_engine)
        
        # Start monitoring
        self.real_time_analytics.start_monitoring()
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes for real-time dashboard"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_interface():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SOW Real-time Analytics Dashboard</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container-fluid">
                    <h1 class="mt-4">SOW Real-time Analytics Dashboard</h1>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">Performance Metrics</div>
                                <div class="card-body">
                                    <canvas id="metricsChart"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">Discovery Insights</div>
                                <div class="card-body" id="insightsPanel">
                                    <p>Loading insights...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">System Alerts</div>
                                <div class="card-body" id="alertsPanel">
                                    <p>Loading alerts...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <script>
                    // WebSocket connection for real-time updates
                    const ws = new WebSocket('ws://localhost:8002/ws/dashboard');
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'metric_update') {
                            updateMetricsChart(data.data);
                        } else if (data.type === 'insight_update') {
                            updateInsightsPanel(data.data);
                        } else if (data.type === 'alert_update') {
                            updateAlertsPanel(data.data);
                        }
                    };
                    
                    // Initialize dashboard
                    fetch('/api/dashboard-data')
                        .then(response => response.json())
                        .then(data => initializeDashboard(data));
                    
                    function initializeDashboard(data) {
                        // Initialize charts and panels with data
                        console.log('Dashboard initialized:', data);
                    }
                    
                    function updateMetricsChart(metric) {
                        console.log('Metric update:', metric);
                        // Update metrics visualization
                    }
                    
                    function updateInsightsPanel(insight) {
                        const panel = document.getElementById('insightsPanel');
                        const insightDiv = document.createElement('div');
                        insightDiv.className = 'alert alert-info';
                        insightDiv.innerHTML = `<strong>${insight.title}</strong><br>${insight.description}`;
                        panel.insertBefore(insightDiv, panel.firstChild);
                    }
                    
                    function updateAlertsPanel(alert) {
                        const panel = document.getElementById('alertsPanel');
                        const alertDiv = document.createElement('div');
                        alertDiv.className = `alert alert-${alert.severity === 'error' ? 'danger' : 'warning'}`;
                        alertDiv.innerHTML = `<strong>${alert.title}</strong><br>${alert.message}`;
                        panel.insertBefore(alertDiv, panel.firstChild);
                    }
                </script>
            </body>
            </html>
            """
        
        @self.app.get("/api/dashboard-data")
        async def get_dashboard_data():
            return self.real_time_analytics.get_dashboard_data()
        
        @self.app.websocket("/ws/dashboard")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            await self.real_time_analytics.add_websocket_connection(websocket)
            
            try:
                while True:
                    # Keep connection alive
                    await websocket.receive_text()
            except WebSocketDisconnect:
                await self.real_time_analytics.remove_websocket_connection(websocket)
        
        @self.app.post("/api/discovery-event")
        async def record_discovery_event(event_data: Dict[str, Any]):
            self.real_time_analytics.add_discovery_event(
                requirement_id=event_data["requirement_id"],
                opportunity_id=event_data["opportunity_id"],
                pattern_name=event_data["pattern_name"],
                confidence_score=event_data["confidence_score"],
                business_value=event_data["business_value"],
                discovery_method=event_data["discovery_method"],
                processing_time_ms=event_data["processing_time_ms"]
            )
            return {"status": "recorded"}
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            self.real_time_analytics.stop_monitoring()
    
    def run(self, host: str = "0.0.0.0", port: int = 8002):
        """Run the real-time dashboard"""
        uvicorn.run(self.app, host=host, port=port)


# Example usage
if __name__ == "__main__":
    from .kuzu_sow_schema import KuzuSOWGraphEngine
    from .sow_analytics_engine import AdvancedSOWAnalytics
    
    # Initialize engines
    kuzu_engine = KuzuSOWGraphEngine("dashboard_sow.db")
    analytics_engine = AdvancedSOWAnalytics(kuzu_engine)
    
    # Create and run dashboard
    dashboard_api = RealTimeDashboardAPI(kuzu_engine, analytics_engine)
    
    print("Starting Real-time SOW Analytics Dashboard on http://localhost:8002")
    print("Features:")
    print("- Real-time performance monitoring")
    print("- Pattern discovery effectiveness tracking") 
    print("- Business value analytics and ROI projections")
    print("- Automated anomaly detection and alerting")
    print("- Interactive trend analysis and forecasting")
    
    dashboard_api.run()
    
    kuzu_engine.close()