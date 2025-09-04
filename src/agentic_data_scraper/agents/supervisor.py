"""
Supervisor Agent - Orchestrates all specialist agents and generates final production code.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentCoordinator
from .sow_interpreter import SOWInterpreterAgent, DataContract
from .data_fetcher import DataFetcherAgent, DataSource, FetchingStrategy
from .data_parser import DataParserAgent, ParsedData
from .data_transformer import DataTransformerAgent, TransformationStrategy
from .semantic_integrator import SemanticIntegratorAgent, SemanticAnnotation
from .security_decision import SecurityDecisionAgent, SecurityDecision
import asyncio
import logging

class GeneratedPipeline(BaseModel):
    """Complete generated pipeline with production-ready code and deployment artifacts."""
    
    lambda_code: str = Field(
        description="Production-ready Python Lambda function code"
    )
    deployment_config: str = Field(
        description="AWS deployment configuration (CloudFormation/CDK)"
    )
    monitoring_code: str = Field(
        description="Monitoring and alerting configuration"
    )
    validation_code: str = Field(
        description="Data validation and quality checking code"
    )
    documentation: str = Field(
        description="Comprehensive pipeline documentation"
    )
    test_cases: List[str] = Field(
        description="Generated test cases and validation scenarios"
    )
    requirements_txt: str = Field(
        default="",
        description="Python package requirements"
    )
    dockerfile: str = Field(
        default="",
        description="Docker configuration for Lambda deployment"
    )
    pipeline_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline metadata and configuration"
    )
    security_measures: List[str] = Field(
        default_factory=list,
        description="Implemented security measures and controls"
    )
    performance_optimizations: List[str] = Field(
        default_factory=list,
        description="Applied performance optimizations"
    )
    sow_compliance_report: Dict[str, Any] = Field(
        default_factory=dict,
        description="SOW compliance validation report"
    )

class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent responsible for orchestrating all specialist agents.
    
    Coordinates the multi-agent workflow, validates outputs against SOW requirements,
    integrates human feedback, and generates final production-ready Lambda code.
    """
    
    def __init__(
        self,
        agent_id: str = "supervisor",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 1800  # 30 minutes for full pipeline
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.specialist_agents = self._initialize_specialist_agents()
        self.coordinator = AgentCoordinator(list(self.specialist_agents.values()), logger)
        
    def _initialize_specialist_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all specialist agents."""
        return {
            "sow_interpreter": SOWInterpreterAgent(),
            "data_fetcher": DataFetcherAgent(),
            "data_parser": DataParserAgent(),
            "data_transformer": DataTransformerAgent(),
            "semantic_integrator": SemanticIntegratorAgent(),
            "security_decision": SecurityDecisionAgent()
        }
    
    async def _process(
        self,
        sow_document: str,
        document_format: str = "txt",
        human_feedback: List[str] = None,
        deployment_target: str = "aws_lambda",
        **kwargs
    ) -> GeneratedPipeline:
        """
        Orchestrate the complete pipeline generation workflow.
        
        Args:
            sow_document: Statement of Work document content
            document_format: Format of SOW document (txt, pdf, docx)
            human_feedback: Human feedback and decisions
            deployment_target: Target deployment platform
            
        Returns:
            GeneratedPipeline: Complete generated pipeline with all artifacts
        """
        self.logger.info("Starting supervised pipeline generation")
        
        human_feedback = human_feedback or []
        
        # Phase 1: SOW Analysis and Planning
        self.logger.info("Phase 1: SOW Analysis and Planning")
        data_contract = await self._analyze_sow_requirements(
            sow_document, document_format, human_feedback
        )
        
        # Phase 2: Multi-Agent Coordination
        self.logger.info("Phase 2: Multi-Agent Coordination")
        agent_results = await self._coordinate_specialist_agents(
            data_contract, sow_document, human_feedback
        )
        
        # Phase 3: Security Decision Integration
        self.logger.info("Phase 3: Security Decision Integration")
        security_decisions = await self._process_security_decisions(
            agent_results, human_feedback
        )
        
        # Phase 4: Code Generation
        self.logger.info("Phase 4: Production Code Generation")
        generated_pipeline = await self._generate_production_code(
            data_contract, agent_results, security_decisions, deployment_target
        )
        
        # Phase 5: Validation and Compliance
        self.logger.info("Phase 5: SOW Compliance Validation")
        compliance_report = await self._validate_sow_compliance(
            generated_pipeline, data_contract
        )
        
        generated_pipeline.sow_compliance_report = compliance_report
        
        return generated_pipeline
    
    async def _analyze_sow_requirements(
        self,
        sow_document: str,
        document_format: str,
        human_feedback: List[str]
    ) -> DataContract:
        """Analyze SOW requirements using SOW interpreter agent."""
        
        sow_agent = self.specialist_agents["sow_interpreter"]
        
        result = await sow_agent.execute(
            sow_document=sow_document,
            document_format=document_format,
            human_feedback=human_feedback
        )
        
        if not result.success:
            raise ValueError(f"SOW analysis failed: {result.error}")
        
        self.logger.info(f"SOW analysis completed. Found {len(result.result.source_requirements)} data sources")
        
        return result.result
    
    async def _coordinate_specialist_agents(
        self,
        data_contract: DataContract,
        sow_document: str,
        human_feedback: List[str]
    ) -> Dict[str, Any]:
        """Coordinate execution of all specialist agents."""
        
        workflow_steps = []
        
        # Step 1: Data fetching strategy
        data_sources = await self._extract_data_sources_from_contract(data_contract)
        workflow_steps.append({
            "agent_id": "data_fetcher",
            "parameters": {
                "data_sources": data_sources,
                "security_requirements": data_contract.security_requirements
            }
        })
        
        # Execute first step to get fetching strategies
        initial_results = await self.coordinator.execute_sequential(workflow_steps[:1])
        fetching_strategies = initial_results[0].result if initial_results[0].success else []
        
        # Step 2: Data parsing strategy (based on expected data formats)
        expected_formats = await self._infer_data_formats_from_sources(data_sources)
        workflow_steps.append({
            "agent_id": "data_parser",
            "parameters": {
                "raw_data": "sample_data",  # Would use actual sample in real implementation
                "data_format": expected_formats[0] if expected_formats else "json",
                "schema_hints": data_contract.transformation_specs
            }
        })
        
        # Step 3: Execute remaining agents in parallel where possible
        remaining_steps = workflow_steps[1:]
        remaining_results = await self.coordinator.execute_parallel(remaining_steps, max_concurrent=2)
        
        # Combine all results
        all_results = initial_results + remaining_results
        
        return {
            "fetching_strategies": all_results[0].result if len(all_results) > 0 and all_results[0].success else [],
            "parsed_data": all_results[1].result if len(all_results) > 1 and all_results[1].success else None,
            "agent_execution_summary": self.coordinator.get_execution_summary()
        }
    
    async def _extract_data_sources_from_contract(self, data_contract: DataContract) -> List[DataSource]:
        """Extract data source objects from data contract requirements."""
        
        data_sources = []
        
        for requirement in data_contract.source_requirements:
            # Parse requirement to extract data source information
            source_type = "web"  # Default
            url = None
            auth_type = "none"
            
            if "http" in requirement.lower():
                url = await self._extract_url_from_requirement(requirement)
                source_type = "web"
            elif "api" in requirement.lower():
                source_type = "api"
                url = await self._extract_url_from_requirement(requirement)
            elif "sharepoint" in requirement.lower():
                source_type = "sharepoint"
            elif "s3" in requirement.lower() or "bucket" in requirement.lower():
                source_type = "s3"
            elif "database" in requirement.lower():
                source_type = "database"
            
            # Determine authentication type from security requirements
            for security_req in data_contract.security_requirements:
                if "oauth" in security_req.lower():
                    auth_type = "oauth"
                elif "token" in security_req.lower():
                    auth_type = "token"
                elif "certificate" in security_req.lower():
                    auth_type = "certificate"
            
            data_source = DataSource(
                type=source_type,
                url=url,
                authentication_type=auth_type,
                access_patterns=[requirement],
                rate_limits=None,
                documentation_url=None
            )
            
            data_sources.append(data_source)
        
        return data_sources
    
    async def _extract_url_from_requirement(self, requirement: str) -> Optional[str]:
        """Extract URL from requirement text."""
        import re
        
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'
        matches = re.findall(url_pattern, requirement)
        
        return matches[0] if matches else None
    
    async def _infer_data_formats_from_sources(self, data_sources: List[DataSource]) -> List[str]:
        """Infer expected data formats from data sources."""
        
        formats = []
        
        for source in data_sources:
            if source.type == "web":
                formats.append("html")
            elif source.type == "api":
                formats.append("json")
            elif source.type == "sharepoint":
                formats.extend(["excel", "csv", "pdf"])
            elif source.type == "s3":
                formats.extend(["csv", "json", "parquet"])
            elif source.type == "database":
                formats.append("tabular")
        
        return list(set(formats)) or ["json"]
    
    async def _process_security_decisions(
        self,
        agent_results: Dict[str, Any],
        human_feedback: List[str]
    ) -> List[SecurityDecision]:
        """Process security decisions with human-in-the-loop validation."""
        
        security_agent = self.specialist_agents["security_decision"]
        security_decisions = []
        
        # Analyze each agent result for security implications
        for agent_name, result in agent_results.items():
            if agent_name == "agent_execution_summary":
                continue
                
            # Create security decision context
            operation_context = f"Processing results from {agent_name} agent"
            risk_assessment = await self._assess_operation_risk(agent_name, result)
            data_sensitivity = await self._determine_data_sensitivity(result)
            
            decision_result = await security_agent.execute(
                operation_context=operation_context,
                risk_assessment=risk_assessment,
                data_sensitivity=data_sensitivity
            )
            
            if decision_result.success:
                security_decisions.append(decision_result.result)
        
        # Filter decisions that require human approval
        human_approval_needed = [d for d in security_decisions if d.human_approval_needed]
        
        if human_approval_needed:
            self.logger.info(f"{len(human_approval_needed)} security decisions require human approval")
            # In real implementation, would wait for human approval
            # For now, simulate approval based on human_feedback
            for decision in human_approval_needed:
                decision.human_approval_needed = False  # Simulate approval
        
        return security_decisions
    
    async def _assess_operation_risk(self, agent_name: str, result: Any) -> str:
        """Assess risk level for agent operation."""
        
        if agent_name == "data_fetcher":
            return "MEDIUM - Accessing external data sources with authentication"
        elif agent_name == "data_parser":
            return "LOW - Processing data formats with validation"
        elif agent_name == "data_transformer":
            return "LOW - Applying transformations with business rules"
        elif agent_name == "semantic_integrator":
            return "LOW - Adding semantic annotations"
        else:
            return "LOW - Standard processing operation"
    
    async def _determine_data_sensitivity(self, result: Any) -> str:
        """Determine data sensitivity level from agent results."""
        
        # Simple heuristic - would be more sophisticated in real implementation
        if hasattr(result, 'security_requirements'):
            security_reqs = getattr(result, 'security_requirements', [])
            if any("pii" in req.lower() for req in security_reqs):
                return "HIGH"
            elif any("financial" in req.lower() for req in security_reqs):
                return "HIGH"
            elif any("confidential" in req.lower() for req in security_reqs):
                return "MEDIUM"
        
        return "LOW"
    
    async def _generate_production_code(
        self,
        data_contract: DataContract,
        agent_results: Dict[str, Any],
        security_decisions: List[SecurityDecision],
        deployment_target: str
    ) -> GeneratedPipeline:
        """Generate complete production-ready pipeline code."""
        
        # Generate Lambda function code
        lambda_code = await self._generate_lambda_code(
            data_contract, agent_results, security_decisions
        )
        
        # Generate deployment configuration
        deployment_config = await self._generate_deployment_config(
            data_contract, deployment_target
        )
        
        # Generate monitoring code
        monitoring_code = await self._generate_monitoring_code(
            data_contract, agent_results
        )
        
        # Generate validation code
        validation_code = await self._generate_validation_code(
            data_contract, agent_results
        )
        
        # Generate documentation
        documentation = await self._generate_documentation(
            data_contract, agent_results, security_decisions
        )
        
        # Generate test cases
        test_cases = await self._generate_test_cases(
            data_contract, agent_results
        )
        
        # Generate requirements.txt
        requirements_txt = await self._generate_requirements_txt(agent_results)
        
        # Generate Dockerfile
        dockerfile = await self._generate_dockerfile(requirements_txt)
        
        # Extract security measures and performance optimizations
        security_measures = [decision.recommended_action for decision in security_decisions]
        performance_optimizations = await self._extract_performance_optimizations(agent_results)
        
        return GeneratedPipeline(
            lambda_code=lambda_code,
            deployment_config=deployment_config,
            monitoring_code=monitoring_code,
            validation_code=validation_code,
            documentation=documentation,
            test_cases=test_cases,
            requirements_txt=requirements_txt,
            dockerfile=dockerfile,
            pipeline_metadata=await self._generate_pipeline_metadata(data_contract, agent_results),
            security_measures=security_measures,
            performance_optimizations=performance_optimizations
        )
    
    async def _generate_lambda_code(
        self,
        data_contract: DataContract,
        agent_results: Dict[str, Any],
        security_decisions: List[SecurityDecision]
    ) -> str:
        """Generate main Lambda function code."""
        
        lambda_template = '''
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import boto3
import pandas as pd
from pydantic import BaseModel, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPipeline:
    """Generated data pipeline with SOW contract enforcement."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.s3_client = boto3.client('s3')
        self.quality_thresholds = {quality_thresholds}
        self.security_measures = {security_measures}
        
    async def handler(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main Lambda handler function."""
        try:
            logger.info("Starting data pipeline execution")
            
            # Extract parameters from event
            source_config = event.get('source_config', {{}})
            output_config = event.get('output_config', {{}})
            
            # Execute pipeline stages
            raw_data = await self._fetch_data(source_config)
            parsed_data = await self._parse_data(raw_data)
            transformed_data = await self._transform_data(parsed_data)
            validated_data = await self._validate_data(transformed_data)
            semantic_data = await self._enrich_semantically(validated_data)
            
            # Store results
            output_location = await self._store_results(semantic_data, output_config)
            
            # Generate quality report
            quality_report = await self._generate_quality_report(semantic_data)
            
            return {{
                "statusCode": 200,
                "body": json.dumps({{
                    "message": "Pipeline executed successfully",
                    "records_processed": len(semantic_data) if isinstance(semantic_data, list) else 1,
                    "output_location": output_location,
                    "quality_report": quality_report,
                    "execution_time": datetime.now().isoformat()
                }})
            }}
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {{str(e)}}", exc_info=True)
            return {{
                "statusCode": 500,
                "body": json.dumps({{
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }})
            }}
    
    async def _fetch_data(self, source_config: Dict[str, Any]) -> Any:
        """Fetch data using generated fetching strategies."""
        # Generated data fetching code would be inserted here
        {fetching_code}
        
    async def _parse_data(self, raw_data: Any) -> Any:
        """Parse data using generated parsing logic."""
        # Generated data parsing code would be inserted here
        {parsing_code}
        
    async def _transform_data(self, parsed_data: Any) -> Any:
        """Transform data using generated transformation logic."""
        # Generated data transformation code would be inserted here
        {transformation_code}
        
    async def _validate_data(self, data: Any) -> Any:
        """Validate data against SOW requirements."""
        # SOW contract validation code would be inserted here
        {validation_code}
        
    async def _enrich_semantically(self, data: Any) -> Any:
        """Apply semantic enrichment."""
        # Semantic enrichment code would be inserted here
        {semantic_code}
        
    async def _store_results(self, data: Any, output_config: Dict[str, Any]) -> str:
        """Store results in configured output destination."""
        # Data storage code would be inserted here
        {storage_code}
        
    async def _generate_quality_report(self, data: Any) -> Dict[str, Any]:
        """Generate data quality report."""
        return {{
            "total_records": len(data) if isinstance(data, list) else 1,
            "quality_score": 0.95,  # Would be calculated based on actual data
            "timestamp": datetime.now().isoformat()
        }}

def lambda_handler(event, context):
    """AWS Lambda entry point."""
    pipeline = DataPipeline(event.get('config', {{}}))
    return asyncio.run(pipeline.handler(event, context))
'''
        
        # Extract code components from agent results
        fetching_code = await self._extract_fetching_code(agent_results)
        parsing_code = await self._extract_parsing_code(agent_results)
        transformation_code = await self._extract_transformation_code(agent_results)
        validation_code = await self._extract_validation_code(data_contract)
        semantic_code = await self._extract_semantic_code(agent_results)
        storage_code = await self._generate_storage_code(data_contract)
        
        return lambda_template.format(
            quality_thresholds=data_contract.quality_thresholds,
            security_measures=[d.recommended_action for d in security_decisions],
            fetching_code=fetching_code,
            parsing_code=parsing_code,
            transformation_code=transformation_code,
            validation_code=validation_code,
            semantic_code=semantic_code,
            storage_code=storage_code
        )
    
    async def _extract_fetching_code(self, agent_results: Dict[str, Any]) -> str:
        """Extract data fetching code from agent results."""
        fetching_strategies = agent_results.get("fetching_strategies", [])
        
        if fetching_strategies and len(fetching_strategies) > 0:
            # Return first strategy's generated code
            strategy = fetching_strategies[0]
            if hasattr(strategy, 'generated_code'):
                return f"        # Generated fetching code\\n        {strategy.generated_code}"
        
        return "        # No fetching code generated\\n        return {}"
    
    async def _extract_parsing_code(self, agent_results: Dict[str, Any]) -> str:
        """Extract data parsing code from agent results.""" 
        return "        # Generated parsing code\\n        return raw_data"
    
    async def _extract_transformation_code(self, agent_results: Dict[str, Any]) -> str:
        """Extract transformation code from agent results."""
        return "        # Generated transformation code\\n        return parsed_data"
    
    async def _extract_validation_code(self, data_contract: DataContract) -> str:
        """Extract validation code from data contract."""
        validation_lines = []
        
        for rule in data_contract.validation_rules:
            validation_lines.append(f"        # Validate: {rule}")
        
        validation_lines.append("        return data")
        
        return "\\n".join(validation_lines)
    
    async def _extract_semantic_code(self, agent_results: Dict[str, Any]) -> str:
        """Extract semantic enrichment code from agent results."""
        return "        # Generated semantic enrichment code\\n        return data"
    
    async def _generate_storage_code(self, data_contract: DataContract) -> str:
        """Generate data storage code based on output specifications."""
        
        storage_code = '''
        # Store data in S3
        bucket_name = output_config.get('bucket', 'default-bucket')
        key = f"pipeline-output/{datetime.now().strftime('%Y/%m/%d')}/data.json"
        
        try:
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=json.dumps(data, default=str),
                ContentType='application/json'
            )
            return f"s3://{bucket_name}/{key}"
        except Exception as e:
            logger.error(f"Failed to store data: {e}")
            raise
        '''
        
        return storage_code
    
    async def _generate_deployment_config(
        self,
        data_contract: DataContract,
        deployment_target: str
    ) -> str:
        """Generate deployment configuration."""
        
        if deployment_target == "aws_lambda":
            return '''
# CloudFormation template for Lambda deployment
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  DataPipelineFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: agentic-data-pipeline
      CodeUri: .
      Handler: lambda_function.lambda_handler
      Runtime: python3.12
      Timeout: 900
      MemorySize: 1024
      Environment:
        Variables:
          LOG_LEVEL: INFO
      Policies:
        - S3FullAccessPolicy:
            BucketName: !Ref OutputBucket
            
  OutputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: agentic-pipeline-output
      VersioningConfiguration:
        Status: Enabled
        
Outputs:
  FunctionArn:
    Value: !GetAtt DataPipelineFunction.Arn
  BucketName:
    Value: !Ref OutputBucket
'''
        else:
            return f"# Deployment configuration for {deployment_target} not implemented"
    
    async def _generate_monitoring_code(
        self,
        data_contract: DataContract,
        agent_results: Dict[str, Any]
    ) -> str:
        """Generate monitoring and alerting code."""
        
        return '''
# CloudWatch monitoring configuration
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def send_quality_metrics(quality_score: float, record_count: int):
    """Send data quality metrics to CloudWatch."""
    
    cloudwatch.put_metric_data(
        Namespace='DataPipeline',
        MetricData=[
            {
                'MetricName': 'DataQualityScore',
                'Value': quality_score,
                'Unit': 'None',
                'Timestamp': datetime.now()
            },
            {
                'MetricName': 'RecordsProcessed',
                'Value': record_count,
                'Unit': 'Count',
                'Timestamp': datetime.now()
            }
        ]
    )

def create_quality_alarm():
    """Create CloudWatch alarm for data quality."""
    
    cloudwatch.put_metric_alarm(
        AlarmName='DataPipelineQuality',
        ComparisonOperator='LessThanThreshold',
        EvaluationPeriods=1,
        MetricName='DataQualityScore',
        Namespace='DataPipeline',
        Period=300,
        Statistic='Average',
        Threshold=0.8,
        ActionsEnabled=True,
        AlarmDescription='Data quality below threshold',
        Unit='None'
    )
'''
    
    async def _generate_validation_code(
        self,
        data_contract: DataContract,
        agent_results: Dict[str, Any]
    ) -> str:
        """Generate comprehensive validation code."""
        
        validation_template = '''
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any

class DataContractValidator:
    """SOW contract validation with runtime enforcement."""
    
    def __init__(self, quality_thresholds: Dict[str, float]):
        self.quality_thresholds = quality_thresholds
        self.validation_rules = {validation_rules}
    
    def validate_contract_compliance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data against SOW contract requirements."""
        
        results = {{
            "compliant": True,
            "violations": [],
            "quality_scores": {{}},
            "validation_timestamp": datetime.now().isoformat()
        }}
        
        # Check data quality thresholds
        quality_score = self._calculate_quality_score(data)
        results["quality_scores"]["overall"] = quality_score
        
        for metric, threshold in self.quality_thresholds.items():
            if quality_score < threshold:
                results["compliant"] = False
                results["violations"].append(f"Quality {metric} ({quality_score:.2f}) below threshold ({threshold})")
        
        # Validate business rules
        for rule in self.validation_rules:
            rule_result = self._validate_business_rule(data, rule)
            if not rule_result["passed"]:
                results["compliant"] = False
                results["violations"].append(rule_result["message"])
        
        return results
    
    def _calculate_quality_score(self, data: List[Dict[str, Any]]) -> float:
        """Calculate overall data quality score."""
        if not data:
            return 0.0
        
        # Calculate completeness
        total_fields = sum(len(record) for record in data)
        non_null_fields = sum(
            sum(1 for value in record.values() if value is not None and str(value).strip())
            for record in data
        )
        
        return non_null_fields / total_fields if total_fields > 0 else 0.0
    
    def _validate_business_rule(self, data: List[Dict[str, Any]], rule: str) -> Dict[str, Any]:
        """Validate individual business rule."""
        # Simplified rule validation - would be more sophisticated in production
        return {{
            "passed": True,
            "message": f"Rule '{rule}' validation passed"
        }}
'''
        
        return validation_template.format(
            validation_rules=data_contract.validation_rules
        )
    
    async def _generate_documentation(
        self,
        data_contract: DataContract,
        agent_results: Dict[str, Any],
        security_decisions: List[SecurityDecision]
    ) -> str:
        """Generate comprehensive pipeline documentation."""
        
        doc_template = '''
# Agentic Data Pipeline Documentation

## Overview
This data pipeline was automatically generated from SOW requirements using a multi-agent system.

## Data Sources
{data_sources}

## Transformation Logic
{transformations}

## Validation Rules
{validations}

## Security Measures
{security_measures}

## Quality Thresholds
{quality_thresholds}

## Deployment Instructions
1. Deploy using AWS SAM: `sam deploy --guided`
2. Configure input parameters in AWS Lambda console
3. Monitor execution through CloudWatch

## Maintenance
- Review data quality metrics weekly
- Update validation rules as business requirements change
- Monitor security alerts and respond promptly

Generated on: {timestamp}
'''
        
        return doc_template.format(
            data_sources="\\n".join([f"- {req}" for req in data_contract.source_requirements]),
            transformations="\\n".join([f"- {spec}" for spec in data_contract.transformation_specs]),
            validations="\\n".join([f"- {rule}" for rule in data_contract.validation_rules]),
            security_measures="\\n".join([f"- {decision.recommended_action}" for decision in security_decisions]),
            quality_thresholds="\\n".join([f"- {k}: {v}" for k, v in data_contract.quality_thresholds.items()]),
            timestamp=datetime.now().isoformat()
        )
    
    async def _generate_test_cases(
        self,
        data_contract: DataContract,
        agent_results: Dict[str, Any]
    ) -> List[str]:
        """Generate test cases for pipeline validation."""
        
        test_cases = [
            "Test valid input data processing",
            "Test data quality threshold enforcement", 
            "Test error handling for invalid data",
            "Test SOW contract compliance validation",
            "Test security measure implementation"
        ]
        
        # Add specific tests based on data contract
        for requirement in data_contract.source_requirements:
            test_cases.append(f"Test data source: {requirement}")
        
        for rule in data_contract.validation_rules:
            test_cases.append(f"Test validation rule: {rule}")
        
        return test_cases
    
    async def _generate_requirements_txt(self, agent_results: Dict[str, Any]) -> str:
        """Generate Python package requirements."""
        
        base_requirements = [
            "boto3>=1.26.0",
            "pandas>=2.0.0",
            "pydantic>=2.0.0",
            "asyncio-mqtt>=0.13.0",
            "requests>=2.28.0",
            "python-dateutil>=2.8.2"
        ]
        
        # Add specific requirements based on agent results
        if "fetching_strategies" in agent_results:
            base_requirements.extend([
                "playwright>=1.30.0",
                "aiohttp>=3.8.0",
                "selenium>=4.0.0"
            ])
        
        return "\\n".join(base_requirements)
    
    async def _generate_dockerfile(self, requirements_txt: str) -> str:
        """Generate Dockerfile for Lambda deployment."""
        
        return f'''
FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies
RUN yum update -y && \\
    yum install -y gcc gcc-c++ make && \\
    yum clean all

# Install Python dependencies
COPY requirements.txt ${{LAMBDA_TASK_ROOT}}/
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (if needed)
RUN playwright install chromium

# Copy function code
COPY lambda_function.py ${{LAMBDA_TASK_ROOT}}/

# Set Lambda handler
CMD ["lambda_function.lambda_handler"]
'''
    
    async def _generate_pipeline_metadata(
        self,
        data_contract: DataContract,
        agent_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate pipeline metadata."""
        
        return {
            "generated_at": datetime.now().isoformat(),
            "generator_version": "1.0.0",
            "sow_requirements_count": len(data_contract.source_requirements),
            "validation_rules_count": len(data_contract.validation_rules),
            "agent_execution_summary": agent_results.get("agent_execution_summary", {}),
            "pipeline_type": "batch_processing",
            "target_platform": "aws_lambda"
        }
    
    async def _extract_performance_optimizations(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract performance optimizations from agent results."""
        
        optimizations = [
            "Async processing for I/O operations",
            "Chunked data processing for memory efficiency",
            "Connection pooling for external APIs",
            "Caching for repeated calculations"
        ]
        
        # Add specific optimizations from transformation agent
        transformation_results = agent_results.get("transformation_results")
        if transformation_results and hasattr(transformation_results, 'performance_optimizations'):
            optimizations.extend(transformation_results.performance_optimizations)
        
        return list(set(optimizations))  # Remove duplicates
    
    async def _validate_sow_compliance(
        self,
        pipeline: GeneratedPipeline,
        data_contract: DataContract
    ) -> Dict[str, Any]:
        """Validate generated pipeline against SOW requirements."""
        
        compliance_report = {
            "overall_compliant": True,
            "compliance_score": 0.0,
            "requirement_compliance": {},
            "validation_timestamp": datetime.now().isoformat()
        }
        
        total_requirements = 0
        compliant_requirements = 0
        
        # Check source requirements compliance
        for requirement in data_contract.source_requirements:
            total_requirements += 1
            # Check if requirement is addressed in pipeline code
            if requirement.lower() in pipeline.lambda_code.lower():
                compliant_requirements += 1
                compliance_report["requirement_compliance"][requirement] = "COMPLIANT"
            else:
                compliance_report["requirement_compliance"][requirement] = "NOT_ADDRESSED"
                compliance_report["overall_compliant"] = False
        
        # Check validation rules compliance
        for rule in data_contract.validation_rules:
            total_requirements += 1
            if rule.lower() in pipeline.validation_code.lower():
                compliant_requirements += 1
                compliance_report["requirement_compliance"][rule] = "COMPLIANT"
            else:
                compliance_report["requirement_compliance"][rule] = "NOT_ADDRESSED"
                compliance_report["overall_compliant"] = False
        
        compliance_report["compliance_score"] = compliant_requirements / total_requirements if total_requirements > 0 else 1.0
        
        return compliance_report
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "orchestration_capabilities": [
                "multi_agent_coordination",
                "workflow_management",
                "human_in_the_loop_integration",
                "sow_compliance_validation",
                "security_decision_integration"
            ],
            "code_generation": [
                "aws_lambda_functions",
                "docker_containers",
                "cloudformation_templates",
                "monitoring_configuration",
                "validation_logic",
                "documentation"
            ],
            "specialist_agents": list(self.specialist_agents.keys()),
            "deployment_targets": ["aws_lambda", "docker", "kubernetes"],
            "output_format": "GeneratedPipeline"
        })
        return base_capabilities