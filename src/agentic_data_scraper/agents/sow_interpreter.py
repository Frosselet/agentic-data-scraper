"""
SOW/Contract Interpreter Agent - Parses Statement of Work documents and extracts structured requirements.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .base import BaseAgent
import asyncio
import logging

class DataContract(BaseModel):
    """Structured representation of data contract requirements from SOW."""
    
    source_requirements: List[str] = Field(
        description="Data source specifications and access requirements"
    )
    validation_rules: List[str] = Field(
        description="Data validation and quality rules"
    )
    transformation_specs: List[str] = Field(
        description="Required data transformations and mappings"
    )
    quality_thresholds: Dict[str, float] = Field(
        description="Minimum acceptable quality levels for different metrics"
    )
    security_requirements: List[str] = Field(
        description="Security, encryption, and access control requirements"
    )
    compliance_rules: List[str] = Field(
        description="Regulatory compliance and governance requirements"
    )
    output_specifications: Dict[str, str] = Field(
        default_factory=dict,
        description="Output format and schema requirements"
    )
    performance_requirements: Dict[str, str] = Field(
        default_factory=dict,
        description="Performance, throughput, and latency requirements"
    )
    business_context: str = Field(
        default="",
        description="Business domain and context information"
    )
    stakeholder_requirements: List[str] = Field(
        default_factory=list,
        description="Stakeholder-specific requirements and constraints"
    )

class SOWInterpreterAgent(BaseAgent):
    """
    Agent specialized in parsing and interpreting Statement of Work documents.
    
    Extracts structured data contracts, requirements, and validation rules from
    various document formats including PDF, Word, and text files.
    """
    
    def __init__(
        self,
        agent_id: str = "sow_interpreter",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 300
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.supported_formats = ["pdf", "docx", "txt", "md", "html"]
        self.extraction_patterns = self._initialize_extraction_patterns()
    
    def _initialize_extraction_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for requirement extraction."""
        return {
            "data_sources": [
                r"(?i)data\s+source[s]?[:\s]+([^.]+)",
                r"(?i)extract[s]?\s+from[:\s]+([^.]+)",
                r"(?i)fetch[s]?\s+data\s+from[:\s]+([^.]+)"
            ],
            "validation_rules": [
                r"(?i)validat[e|ion][s]?[:\s]+([^.]+)",
                r"(?i)must\s+(?:be|have|contain)[:\s]+([^.]+)",
                r"(?i)require[d|s]?\s+to[:\s]+([^.]+)"
            ],
            "quality_metrics": [
                r"(?i)accuracy[:\s]+(\d+(?:\.\d+)?%?)",
                r"(?i)completeness[:\s]+(\d+(?:\.\d+)?%?)",
                r"(?i)quality[:\s]+(?:threshold|minimum)[:\s]+(\d+(?:\.\d+)?%?)"
            ],
            "security": [
                r"(?i)encrypt[ed|ion][s]?[:\s]+([^.]+)",
                r"(?i)security[:\s]+([^.]+)",
                r"(?i)access\s+control[:\s]+([^.]+)"
            ],
            "compliance": [
                r"(?i)(?:gdpr|hipaa|sox|pci)[:\s]+([^.]+)",
                r"(?i)compliance[:\s]+([^.]+)",
                r"(?i)regulation[s]?[:\s]+([^.]+)"
            ]
        }
    
    async def _process(
        self,
        sow_document: str,
        document_format: str = "txt",
        business_domain: str = "",
        **kwargs
    ) -> DataContract:
        """
        Process SOW document and extract structured data contract.
        
        Args:
            sow_document: Content of the SOW document
            document_format: Format of the document (pdf, docx, txt, etc.)
            business_domain: Business domain context for better interpretation
            
        Returns:
            DataContract: Structured data contract with extracted requirements
        """
        self.logger.info(f"Processing SOW document (format: {document_format})")
        
        # Validate input format
        if document_format not in self.supported_formats:
            raise ValueError(f"Unsupported document format: {document_format}")
        
        # Extract different requirement categories
        source_requirements = await self._extract_data_sources(sow_document)
        validation_rules = await self._extract_validation_rules(sow_document)
        transformation_specs = await self._extract_transformation_specs(sow_document)
        quality_thresholds = await self._extract_quality_thresholds(sow_document)
        security_requirements = await self._extract_security_requirements(sow_document)
        compliance_rules = await self._extract_compliance_rules(sow_document)
        output_specs = await self._extract_output_specifications(sow_document)
        performance_reqs = await self._extract_performance_requirements(sow_document)
        stakeholder_reqs = await self._extract_stakeholder_requirements(sow_document)
        
        return DataContract(
            source_requirements=source_requirements,
            validation_rules=validation_rules,
            transformation_specs=transformation_specs,
            quality_thresholds=quality_thresholds,
            security_requirements=security_requirements,
            compliance_rules=compliance_rules,
            output_specifications=output_specs,
            performance_requirements=performance_reqs,
            business_context=business_domain or self._infer_business_context(sow_document),
            stakeholder_requirements=stakeholder_reqs
        )
    
    async def _extract_data_sources(self, document: str) -> List[str]:
        """Extract data source specifications from SOW document."""
        import re
        
        sources = []
        for pattern in self.extraction_patterns["data_sources"]:
            matches = re.findall(pattern, document)
            sources.extend([match.strip() for match in matches])
        
        # Enhanced extraction for common data source types
        web_sources = re.findall(r"https?://[^\s]+", document)
        api_sources = re.findall(r"(?i)api[s]?\s+(?:endpoint|url)[:\s]+([^\s]+)", document)
        database_sources = re.findall(r"(?i)database[:\s]+([^.]+)", document)
        
        sources.extend(web_sources)
        sources.extend(api_sources)
        sources.extend(database_sources)
        
        # Remove duplicates and empty strings
        return list(set([s for s in sources if s.strip()]))
    
    async def _extract_validation_rules(self, document: str) -> List[str]:
        """Extract validation rules and constraints."""
        import re
        
        rules = []
        for pattern in self.extraction_patterns["validation_rules"]:
            matches = re.findall(pattern, document)
            rules.extend([match.strip() for match in matches])
        
        # Look for specific validation patterns
        format_rules = re.findall(r"(?i)format[:\s]+([^.]+)", document)
        range_rules = re.findall(r"(?i)(?:between|range)[:\s]+([^.]+)", document)
        required_fields = re.findall(r"(?i)required[:\s]+(?:field[s]?|column[s]?)[:\s]+([^.]+)", document)
        
        rules.extend(format_rules)
        rules.extend(range_rules)
        rules.extend(required_fields)
        
        return list(set([r for r in rules if r.strip()]))
    
    async def _extract_transformation_specs(self, document: str) -> List[str]:
        """Extract data transformation specifications."""
        import re
        
        transformations = []
        
        # Common transformation patterns
        mapping_rules = re.findall(r"(?i)map[s]?\s+([^.]+)\s+to\s+([^.]+)", document)
        conversion_rules = re.findall(r"(?i)convert[s]?\s+([^.]+)", document)
        aggregation_rules = re.findall(r"(?i)(?:aggregate|sum|count|average)[s]?\s+([^.]+)", document)
        filter_rules = re.findall(r"(?i)filter[s]?\s+([^.]+)", document)
        
        transformations.extend([f"Map {m[0].strip()} to {m[1].strip()}" for m in mapping_rules])
        transformations.extend([f"Convert {c.strip()}" for c in conversion_rules])
        transformations.extend([f"Aggregate {a.strip()}" for a in aggregation_rules])
        transformations.extend([f"Filter {f.strip()}" for f in filter_rules])
        
        return list(set([t for t in transformations if t.strip()]))
    
    async def _extract_quality_thresholds(self, document: str) -> Dict[str, float]:
        """Extract quality threshold specifications."""
        import re
        
        thresholds = {}
        
        # Standard quality metrics with percentage values
        accuracy_matches = re.findall(r"(?i)accuracy[:\s]+(\d+(?:\.\d+)?)%?", document)
        completeness_matches = re.findall(r"(?i)completeness[:\s]+(\d+(?:\.\d+)?)%?", document)
        consistency_matches = re.findall(r"(?i)consistency[:\s]+(\d+(?:\.\d+)?)%?", document)
        timeliness_matches = re.findall(r"(?i)timeliness[:\s]+(\d+(?:\.\d+)?)%?", document)
        
        if accuracy_matches:
            thresholds["accuracy"] = float(accuracy_matches[0]) / 100.0
        if completeness_matches:
            thresholds["completeness"] = float(completeness_matches[0]) / 100.0
        if consistency_matches:
            thresholds["consistency"] = float(consistency_matches[0]) / 100.0
        if timeliness_matches:
            thresholds["timeliness"] = float(timeliness_matches[0]) / 100.0
        
        # Default thresholds if none specified
        if not thresholds:
            thresholds = {
                "accuracy": 0.95,
                "completeness": 0.90,
                "consistency": 0.85,
                "timeliness": 0.80
            }
        
        return thresholds
    
    async def _extract_security_requirements(self, document: str) -> List[str]:
        """Extract security and access control requirements."""
        import re
        
        security_reqs = []
        
        for pattern in self.extraction_patterns["security"]:
            matches = re.findall(pattern, document)
            security_reqs.extend([match.strip() for match in matches])
        
        # Look for specific security keywords
        encryption_reqs = re.findall(r"(?i)encrypt[ed|ion][:\s]+([^.]+)", document)
        auth_reqs = re.findall(r"(?i)authentication[:\s]+([^.]+)", document)
        audit_reqs = re.findall(r"(?i)audit[ing]?[:\s]+([^.]+)", document)
        
        security_reqs.extend(encryption_reqs)
        security_reqs.extend(auth_reqs)
        security_reqs.extend(audit_reqs)
        
        return list(set([s for s in security_reqs if s.strip()]))
    
    async def _extract_compliance_rules(self, document: str) -> List[str]:
        """Extract regulatory compliance requirements."""
        import re
        
        compliance = []
        
        for pattern in self.extraction_patterns["compliance"]:
            matches = re.findall(pattern, document)
            compliance.extend([match.strip() for match in matches])
        
        # Check for specific regulations
        gdpr_mentions = re.findall(r"(?i)gdpr[:\s]*([^.]*)", document)
        hipaa_mentions = re.findall(r"(?i)hipaa[:\s]*([^.]*)", document)
        sox_mentions = re.findall(r"(?i)sox[:\s]*([^.]*)", document)
        
        if gdpr_mentions:
            compliance.append("GDPR compliance required")
        if hipaa_mentions:
            compliance.append("HIPAA compliance required")
        if sox_mentions:
            compliance.append("SOX compliance required")
        
        return list(set([c for c in compliance if c.strip()]))
    
    async def _extract_output_specifications(self, document: str) -> Dict[str, str]:
        """Extract output format and schema specifications."""
        import re
        
        output_specs = {}
        
        # Look for output format specifications
        format_matches = re.findall(r"(?i)output[s]?\s+format[:\s]+([^\s.]+)", document)
        schema_matches = re.findall(r"(?i)(?:output\s+)?schema[:\s]+([^.]+)", document)
        destination_matches = re.findall(r"(?i)(?:save|store|output)\s+(?:to|in)[:\s]+([^.]+)", document)
        
        if format_matches:
            output_specs["format"] = format_matches[0].strip()
        if schema_matches:
            output_specs["schema"] = schema_matches[0].strip()
        if destination_matches:
            output_specs["destination"] = destination_matches[0].strip()
        
        return output_specs
    
    async def _extract_performance_requirements(self, document: str) -> Dict[str, str]:
        """Extract performance and SLA requirements."""
        import re
        
        performance = {}
        
        # Look for performance metrics
        throughput_matches = re.findall(r"(?i)throughput[:\s]+([^.]+)", document)
        latency_matches = re.findall(r"(?i)latency[:\s]+([^.]+)", document)
        sla_matches = re.findall(r"(?i)sla[:\s]+([^.]+)", document)
        availability_matches = re.findall(r"(?i)availability[:\s]+([^.]+)", document)
        
        if throughput_matches:
            performance["throughput"] = throughput_matches[0].strip()
        if latency_matches:
            performance["latency"] = latency_matches[0].strip()
        if sla_matches:
            performance["sla"] = sla_matches[0].strip()
        if availability_matches:
            performance["availability"] = availability_matches[0].strip()
        
        return performance
    
    async def _extract_stakeholder_requirements(self, document: str) -> List[str]:
        """Extract stakeholder-specific requirements."""
        import re
        
        stakeholders = []
        
        # Look for stakeholder mentions and their requirements
        stakeholder_patterns = [
            r"(?i)(?:business|product|data)\s+owner[s]?[:\s]+([^.]+)",
            r"(?i)stakeholder[s]?\s+require[s]?[:\s]+([^.]+)",
            r"(?i)user[s]?\s+need[s]?[:\s]+([^.]+)"
        ]
        
        for pattern in stakeholder_patterns:
            matches = re.findall(pattern, document)
            stakeholders.extend([match.strip() for match in matches])
        
        return list(set([s for s in stakeholders if s.strip()]))
    
    def _infer_business_context(self, document: str) -> str:
        """Infer business domain context from document content."""
        import re
        
        # Domain-specific keywords
        domain_keywords = {
            "agriculture": ["farm", "crop", "harvest", "commodity", "weather", "yield"],
            "trading": ["market", "price", "trade", "financial", "instrument", "exchange"],
            "supply_chain": ["logistics", "inventory", "supplier", "warehouse", "shipment"],
            "healthcare": ["patient", "medical", "clinical", "health", "diagnosis"],
            "finance": ["account", "transaction", "payment", "banking", "credit"]
        }
        
        document_lower = document.lower()
        domain_scores = {}
        
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in document_lower)
            domain_scores[domain] = score
        
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain
        
        return "general"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "supported_formats": self.supported_formats,
            "extraction_capabilities": [
                "data_source_identification",
                "validation_rule_extraction",
                "transformation_specification",
                "quality_threshold_detection",
                "security_requirement_analysis",
                "compliance_rule_identification",
                "business_context_inference"
            ],
            "output_format": "DataContract"
        })
        return base_capabilities