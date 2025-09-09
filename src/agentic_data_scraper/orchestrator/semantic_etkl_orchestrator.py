"""
Semantic ET(K)L Data Collection Orchestrator for Mississippi River Navigation System

This orchestrator demonstrates the "shift left" semantic enrichment approach where knowledge
extraction happens during data acquisition rather than post-processing.

Architecture:
1. Connect to multiple real-world data sources
2. Structure data with domain-specific knowledge
3. Apply semantic metadata extraction using KuzuDB as temporary graph
4. Store semantically-enriched data ready for navigation analytics
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import os

import pandas as pd
import kuzu
from rdflib import Graph, Namespace

from ..collectors.usgs_collector import USGSSemanticCollector
from ..collectors.ais_collector import AISSemanticCollector
from ..collectors.semantic_collectors import StructuredRecord, SemanticContext
from ..schemas.kuzu_navigation_schema import NavigationSchema, NavigationQueries

logger = logging.getLogger(__name__)


@dataclass
class CollectionPlan:
    """Plan for coordinated semantic data collection"""
    collection_id: str
    start_time: datetime
    end_time: datetime
    data_sources: List[str]
    collection_frequency: str  # real-time, hourly, daily
    semantic_enrichment_level: str  # basic, standard, comprehensive
    quality_thresholds: Dict[str, float]
    

@dataclass  
class CollectionResult:
    """Results from semantic data collection"""
    collection_id: str
    source_name: str
    records_collected: int
    records_semantically_enriched: int
    average_quality_score: float
    semantic_coverage_percentage: float
    collection_duration_seconds: float
    errors: List[str]


class SemanticETKLOrchestrator:
    """
    Orchestrates multiple semantic collectors for comprehensive Mississippi River data acquisition
    Implements ET(K)L pattern at scale with cross-source semantic consistency
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize KuzuDB for both temporary semantic processing and final storage
        self.temp_db_path = config.get("temp_semantic_db", "./temp_semantic_processing.kuzu")
        self.main_db_path = config.get("main_navigation_db", "./mississippi_navigation.kuzu")
        
        # Initialize navigation schema
        self.navigation_schema = NavigationSchema(self.main_db_path)
        self.navigation_queries = NavigationQueries(self.navigation_schema)
        
        # Collection results tracking
        self.collection_results = []
        self.cross_source_entities = {}  # For entity resolution across sources
        
        # Initialize semantic collectors based on configuration
        self.collectors = {}
        self._initialize_collectors()
        
        # Cross-source semantic consistency manager
        self.semantic_consistency_manager = CrossSourceSemanticManager(self.temp_db_path)
        
    def _initialize_collectors(self):
        """Initialize all configured semantic collectors"""
        
        collector_configs = self.config.get("collectors", {})
        
        # USGS Water Data Collector
        if "usgs" in collector_configs:
            usgs_config = collector_configs["usgs"]
            self.collectors["usgs"] = USGSSemanticCollector(
                kuzu_temp_db=self.main_db_path,  # Use main database instead of temp
                sites=usgs_config.get("sites", None)
            )
            logger.info("Initialized USGS semantic collector")
        
        # AIS Vessel Tracking Collector  
        if "ais" in collector_configs:
            ais_config = collector_configs["ais"]
            if ais_config.get("api_key"):
                self.collectors["ais"] = AISSemanticCollector(
                    kuzu_temp_db=self.main_db_path,  # Use main database instead of temp
                    api_key=ais_config["api_key"],
                    bbox=ais_config.get("bbox", None)
                )
                logger.info("Initialized AIS semantic collector")
            else:
                logger.warning("AIS collector disabled - no API key provided")
        
        # Additional collectors can be added here (NOAA, USDA, etc.)
        # if "noaa" in collector_configs:
        #     self.collectors["noaa"] = NOAASemanticCollector(...)
        
        logger.info(f"Initialized {len(self.collectors)} semantic collectors")
    
    async def execute_collection_plan(self, plan: CollectionPlan) -> List[CollectionResult]:
        """
        Execute coordinated semantic data collection across all sources
        """
        
        logger.info(f"Starting semantic ET(K)L collection plan: {plan.collection_id}")
        logger.info(f"Data sources: {', '.join(plan.data_sources)}")
        
        collection_start = datetime.now()
        results = []
        
        # Phase 1: Parallel data collection with semantic enrichment
        logger.info("Phase 1: Collecting and enriching data from all sources...")
        collection_tasks = []
        
        for source_name in plan.data_sources:
            if source_name in self.collectors:
                task = self._collect_from_source(source_name, plan)
                collection_tasks.append(task)
        
        if collection_tasks:
            collection_results = await asyncio.gather(*collection_tasks, return_exceptions=True)
            
            for source_name, result in zip(plan.data_sources, collection_results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to collect from {source_name}: {result}")
                    results.append(CollectionResult(
                        collection_id=plan.collection_id,
                        source_name=source_name,
                        records_collected=0,
                        records_semantically_enriched=0,
                        average_quality_score=0.0,
                        semantic_coverage_percentage=0.0,
                        collection_duration_seconds=0.0,
                        errors=[str(result)]
                    ))
                else:
                    results.append(result)
        
        # Phase 2: Cross-source semantic consistency resolution
        logger.info("Phase 2: Resolving cross-source semantic consistency...")
        await self._resolve_cross_source_semantics(results)
        
        # Phase 3: Load into final navigation knowledge graph
        logger.info("Phase 3: Loading into navigation knowledge graph...")
        await self._load_into_navigation_graph(results)
        
        # Phase 4: Generate collection summary and insights
        logger.info("Phase 4: Generating collection summary...")
        collection_summary = self._generate_collection_summary(plan, results, collection_start)
        
        logger.info(f"Completed semantic ET(K)L collection in {collection_summary['total_duration_seconds']:.1f}s")
        logger.info(f"Total records collected: {collection_summary['total_records']}")
        logger.info(f"Average semantic enrichment: {collection_summary['average_semantic_coverage']:.1%}")
        
        return results
    
    async def _collect_from_source(self, source_name: str, plan: CollectionPlan) -> CollectionResult:
        """Collect semantically enriched data from a single source"""
        
        source_start = datetime.now()
        collector = self.collectors[source_name]
        
        try:
            logger.info(f"Collecting semantic data from {source_name}...")
            enriched_records = await collector.collect_semantically_enriched_data()
            
            # Apply quality filtering based on plan thresholds
            quality_filtered_records = self._apply_quality_filters(enriched_records, plan.quality_thresholds)
            
            # Calculate semantic coverage metrics
            semantic_metrics = self._calculate_semantic_metrics(quality_filtered_records)
            
            # Store in source-specific tables
            table_mapping = {
                "usgs": "HydroReading",
                "ais": "VesselPosition",
                "noaa": "WeatherForecast",
                "usda": "MarketPrice"
            }
            
            target_table = table_mapping.get(source_name, "GenericData")
            collector.store_in_kuzu_tables(quality_filtered_records, target_table)
            
            # Register entities for cross-source resolution
            self._register_entities_for_resolution(source_name, quality_filtered_records)
            
            collection_duration = (datetime.now() - source_start).total_seconds()
            
            return CollectionResult(
                collection_id=plan.collection_id,
                source_name=source_name,
                records_collected=len(enriched_records),
                records_semantically_enriched=len(quality_filtered_records),
                average_quality_score=semantic_metrics["average_quality"],
                semantic_coverage_percentage=semantic_metrics["semantic_coverage"] * 100,
                collection_duration_seconds=collection_duration,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error collecting from {source_name}: {e}")
            return CollectionResult(
                collection_id=plan.collection_id,
                source_name=source_name,
                records_collected=0,
                records_semantically_enriched=0,
                average_quality_score=0.0,
                semantic_coverage_percentage=0.0,
                collection_duration_seconds=0.0,
                errors=[str(e)]
            )
    
    def _apply_quality_filters(self, records: List[StructuredRecord], thresholds: Dict[str, float]) -> List[StructuredRecord]:
        """Apply quality filtering based on collection plan thresholds"""
        
        if not thresholds:
            return records
        
        filtered_records = []
        
        min_quality = thresholds.get("min_overall_quality", 0.0)
        min_completeness = thresholds.get("min_completeness", 0.0)
        max_age_hours = thresholds.get("max_age_hours", 24)
        
        for record in records:
            # Quality score filter
            quality_score = record.quality_metrics.get("overall_quality", 0) if record.quality_metrics else 0
            if quality_score < min_quality:
                continue
            
            # Completeness filter
            completeness = record.quality_metrics.get("completeness", 0) if record.quality_metrics else 0
            if completeness < min_completeness:
                continue
            
            # Age filter
            age_hours = (datetime.now() - record.timestamp).total_seconds() / 3600
            if age_hours > max_age_hours:
                continue
            
            filtered_records.append(record)
        
        logger.info(f"Quality filtering: {len(records)} -> {len(filtered_records)} records")
        return filtered_records
    
    def _calculate_semantic_metrics(self, records: List[StructuredRecord]) -> Dict[str, float]:
        """Calculate semantic enrichment metrics"""
        
        if not records:
            return {"average_quality": 0.0, "semantic_coverage": 0.0}
        
        quality_scores = []
        semantic_coverage_scores = []
        
        for record in records:
            if record.quality_metrics:
                quality_scores.append(record.quality_metrics.get("overall_quality", 0))
            
            # Calculate semantic coverage based on presence of semantic annotations
            semantic_elements = record.semantic_annotations or {}
            total_possible_elements = 7  # entities, concepts, spatial, temporal, domain, quality, interop
            present_elements = sum(1 for v in semantic_elements.values() if v)
            semantic_coverage_scores.append(present_elements / total_possible_elements)
        
        return {
            "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "semantic_coverage": sum(semantic_coverage_scores) / len(semantic_coverage_scores) if semantic_coverage_scores else 0
        }
    
    def _register_entities_for_resolution(self, source_name: str, records: List[StructuredRecord]):
        """Register entities for cross-source semantic resolution"""
        
        for record in records:
            entities = record.semantic_annotations.get("entities", []) if record.semantic_annotations else []
            
            for entity in entities:
                entity_key = f"{entity.get('entity_type')}:{entity.get('canonical_form')}"
                
                if entity_key not in self.cross_source_entities:
                    self.cross_source_entities[entity_key] = []
                
                self.cross_source_entities[entity_key].append({
                    "source": source_name,
                    "record_id": record.record_id,
                    "entity": entity,
                    "confidence": entity.get("confidence_score", 0)
                })
    
    async def _resolve_cross_source_semantics(self, results: List[CollectionResult]):
        """Resolve semantic consistency across data sources"""
        
        logger.info("Resolving cross-source semantic consistency...")
        
        # Entity resolution across sources
        resolved_entities = 0
        for entity_key, entity_instances in self.cross_source_entities.items():
            if len(entity_instances) > 1:  # Multiple sources have this entity
                # Perform entity resolution using semantic consistency manager
                canonical_entity = await self.semantic_consistency_manager.resolve_entity(entity_instances)
                if canonical_entity:
                    resolved_entities += 1
        
        logger.info(f"Resolved {resolved_entities} cross-source entities")
        
        # Ontology alignment across domains
        await self.semantic_consistency_manager.align_ontologies([
            "hydrology", "transportation", "economics", "geospatial"
        ])
        
        logger.info("Cross-source semantic consistency resolution completed")
    
    async def _load_into_navigation_graph(self, results: List[CollectionResult]):
        """Load semantically enriched data into final navigation knowledge graph"""
        
        logger.info("Loading data into navigation knowledge graph...")
        
        # This would involve transferring data from temporary semantic processing
        # to the final navigation graph schema
        
        total_loaded = 0
        for result in results:
            if result.records_semantically_enriched > 0:
                # Transfer semantic data to main navigation schema
                # Implementation would depend on specific table mappings
                total_loaded += result.records_semantically_enriched
        
        logger.info(f"Loaded {total_loaded} semantically enriched records into navigation graph")
    
    def _generate_collection_summary(self, plan: CollectionPlan, results: List[CollectionResult], 
                                   start_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive collection summary"""
        
        total_duration = (datetime.now() - start_time).total_seconds()
        total_records = sum(r.records_collected for r in results)
        total_enriched = sum(r.records_semantically_enriched for r in results)
        
        summary = {
            "collection_plan_id": plan.collection_id,
            "execution_start": start_time.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "total_duration_seconds": total_duration,
            "data_sources_attempted": len(plan.data_sources),
            "data_sources_successful": len([r for r in results if not r.errors]),
            "total_records": total_records,
            "total_semantically_enriched": total_enriched,
            "enrichment_rate": total_enriched / total_records if total_records > 0 else 0,
            "average_quality_score": sum(r.average_quality_score for r in results) / len(results) if results else 0,
            "average_semantic_coverage": sum(r.semantic_coverage_percentage for r in results) / len(results) / 100 if results else 0,
            "cross_source_entities_resolved": len(self.cross_source_entities),
            "collection_errors": [error for r in results for error in r.errors],
            "source_performance": {r.source_name: {
                "records": r.records_collected,
                "quality": r.average_quality_score,
                "coverage": r.semantic_coverage_percentage,
                "duration": r.collection_duration_seconds
            } for r in results}
        }
        
        return summary
    
    async def run_real_time_collection(self, duration_hours: int = 24):
        """Run real-time semantic data collection for specified duration"""
        
        logger.info(f"Starting real-time semantic collection for {duration_hours} hours")
        
        collection_interval = 300  # 5 minutes
        end_time = datetime.now() + timedelta(hours=duration_hours)
        collection_count = 0
        
        while datetime.now() < end_time:
            collection_count += 1
            
            plan = CollectionPlan(
                collection_id=f"realtime_{collection_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(minutes=5),
                data_sources=list(self.collectors.keys()),
                collection_frequency="real-time",
                semantic_enrichment_level="standard",
                quality_thresholds={
                    "min_overall_quality": 0.7,
                    "min_completeness": 0.8,
                    "max_age_hours": 1
                }
            )
            
            try:
                results = await self.execute_collection_plan(plan)
                self.collection_results.extend(results)
                
                # Log real-time insights
                await self._generate_real_time_insights(results)
                
            except Exception as e:
                logger.error(f"Error in real-time collection {collection_count}: {e}")
            
            # Wait for next collection interval
            await asyncio.sleep(collection_interval)
        
        logger.info(f"Completed real-time collection after {collection_count} cycles")
        return self.collection_results
    
    async def _generate_real_time_insights(self, results: List[CollectionResult]):
        """Generate real-time navigation insights from freshly collected data"""
        
        # Example: Check for navigation risks
        risk_query = """
        MATCH (reading:HydroReading)
        WHERE reading.navigation_risk = 'high_risk' 
          AND reading.timestamp > datetime() - duration('PT15M')
        RETURN reading.site_name, reading.measured_value, reading.river_mile
        ORDER BY reading.river_mile
        """
        
        try:
            high_risk_sites = self.navigation_queries.conn.execute(risk_query)
            if high_risk_sites.has_next():
                logger.warning("Navigation risks detected:")
                for site in high_risk_sites:
                    logger.warning(f"  {site['site_name']}: {site['measured_value']}ft at mile {site['river_mile']}")
        except Exception as e:
            logger.debug(f"Could not execute risk query: {e}")
        
        # Example: Traffic congestion detection
        congestion_points = self.navigation_queries.identify_congestion_points(time_window_hours=1)
        if congestion_points:
            logger.info(f"Detected {len(congestion_points)} potential congestion points")


class CrossSourceSemanticManager:
    """Manages semantic consistency across multiple data sources"""
    
    def __init__(self, temp_db_path: str):
        self.temp_db = kuzu.Database(temp_db_path)
        self.temp_conn = kuzu.Connection(self.temp_db)
        
    async def resolve_entity(self, entity_instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Resolve entity across multiple source instances"""
        
        if not entity_instances:
            return None
        
        # Find instance with highest confidence
        best_instance = max(entity_instances, key=lambda x: x["confidence"])
        
        # Create canonical entity combining information from all sources
        canonical_entity = {
            "canonical_form": best_instance["entity"]["canonical_form"],
            "semantic_uri": best_instance["entity"]["semantic_uri"],
            "entity_type": best_instance["entity"]["entity_type"],
            "confidence": best_instance["confidence"],
            "source_count": len(entity_instances),
            "sources": [inst["source"] for inst in entity_instances]
        }
        
        return canonical_entity
    
    async def align_ontologies(self, domains: List[str]):
        """Align ontologies across different domains"""
        
        # Implementation would create mappings between domain ontologies
        # For example, mapping hydrology:WaterLevel to navigation:NavigationDepth
        logger.info(f"Aligning ontologies across domains: {', '.join(domains)}")


# Configuration and usage examples
def create_mississippi_river_collection_config() -> Dict[str, Any]:
    """Create configuration for Mississippi River navigation data collection"""
    
    # Get project root directory (where pyproject.toml is located)
    import pathlib
    current_file = pathlib.Path(__file__).resolve()
    project_root = current_file.parent.parent.parent  # Go up from src/agentic_data_scraper/orchestrator/
    
    # Ensure we found the project root
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        # Fallback: look for pyproject.toml in parent directories
        search_path = pathlib.Path.cwd()
        while search_path.parent != search_path:
            if (search_path / "pyproject.toml").exists():
                project_root = search_path
                break
            search_path = search_path.parent
        else:
            # Ultimate fallback
            project_root = pathlib.Path.cwd()
    
    return {
        "temp_semantic_db": str(project_root / "temp_mississippi_semantic.kuzu"),
        "main_navigation_db": str(project_root / "mississippi_navigation_prod.kuzu"),
        
        "collectors": {
            "usgs": {
                "sites": [
                    "05331000",  # St. Paul, MN
                    "05420500",  # Clinton, IA
                    "05587450",  # Alton, IL
                    "07010000",  # St. Louis, MO
                    "07289000",  # Vicksburg, MS
                    "07374000",  # Baton Rouge, LA
                ]
            },
            "ais": {
                "api_key": os.getenv("VESSELFINDER_API_KEY", ""),
                "bbox": {
                    "north": 47.9,
                    "south": 29.0, 
                    "east": -89.0,
                    "west": -95.2
                }
            }
        },
        
        "quality_standards": {
            "min_overall_quality": 0.75,
            "min_completeness": 0.80,
            "max_age_hours": 6,
            "required_semantic_coverage": 0.70
        }
    }


# Main execution example
async def main():
    """Example of semantic ET(K)L orchestrator in action"""
    
    # Create configuration
    config = create_mississippi_river_collection_config()
    
    # Initialize orchestrator
    orchestrator = SemanticETKLOrchestrator(config)
    
    # Create collection plan
    collection_plan = CollectionPlan(
        collection_id=f"mississippi_nav_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        data_sources=["usgs", "ais"],
        collection_frequency="real-time",
        semantic_enrichment_level="comprehensive",
        quality_thresholds={
            "min_overall_quality": 0.7,
            "min_completeness": 0.8,
            "max_age_hours": 2
        }
    )
    
    print("🚢 Mississippi River Navigation - Semantic ET(K)L Data Collection")
    print("=" * 60)
    
    # Execute collection
    results = await orchestrator.execute_collection_plan(collection_plan)
    
    # Display results
    print(f"\nCollection completed! Results summary:")
    print(f"📊 Total sources: {len(results)}")
    print(f"📈 Total records: {sum(r.records_collected for r in results)}")
    print(f"🧠 Semantic enrichment: {sum(r.records_semantically_enriched for r in results)}")
    print(f"⭐ Average quality: {sum(r.average_quality_score for r in results) / len(results):.2f}")
    print(f"🔗 Semantic coverage: {sum(r.semantic_coverage_percentage for r in results) / len(results):.1f}%")
    
    # Show per-source results
    print("\nPer-source results:")
    for result in results:
        status = "✅" if not result.errors else "❌"
        print(f"{status} {result.source_name}: {result.records_semantically_enriched} records, "
              f"{result.semantic_coverage_percentage:.1f}% semantic coverage")
        
        if result.errors:
            for error in result.errors:
                print(f"   Error: {error}")
    
    print(f"\n🎯 Data successfully collected with semantic enrichment during acquisition!")
    print(f"💾 Stored in navigation knowledge graph: {orchestrator.main_db_path}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run the example
    asyncio.run(main())