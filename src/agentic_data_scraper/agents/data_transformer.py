"""
Data Transformer Specialist Agent - Generates sophisticated data transformation and cleaning logic.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from .base import BaseAgent
from .data_parser import ParsedData
import asyncio
import logging

class TransformationStrategy(BaseModel):
    """Comprehensive data transformation strategy with code generation."""
    
    source_schema: Dict[str, str] = Field(
        description="Source data schema with field names and types"
    )
    target_schema: Dict[str, str] = Field(
        description="Target data schema with field names and types"
    )
    transformation_rules: List[str] = Field(
        description="High-level transformation rules and mappings"
    )
    validation_logic: List[str] = Field(
        description="Data validation and quality rules"
    )
    performance_optimizations: List[str] = Field(
        description="Performance optimization strategies"
    )
    error_handling: List[str] = Field(
        description="Error handling and recovery strategies"
    )
    generated_code: str = Field(
        default="",
        description="Generated Python transformation code"
    )
    field_mappings: Dict[str, str] = Field(
        default_factory=dict,
        description="Direct field-to-field mappings"
    )
    calculated_fields: Dict[str, str] = Field(
        default_factory=dict,
        description="Calculated field definitions with formulas"
    )
    data_cleaning_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Data cleaning and standardization rules"
    )
    quality_metrics: Dict[str, str] = Field(
        default_factory=dict,
        description="Quality metrics to track during transformation"
    )

class DataTransformerAgent(BaseAgent):
    """
    Agent specialized in generating data transformation and cleaning strategies.
    
    Creates schema alignment logic, data cleaning strategies, validation rules,
    and performance-optimized transformation code.
    """
    
    def __init__(
        self,
        agent_id: str = "data_transformer",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 600
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.transformation_patterns = self._initialize_transformation_patterns()
        self.data_types_mapping = self._initialize_data_type_mappings()
        
    def _initialize_transformation_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common transformation patterns."""
        return {
            "name_normalization": {
                "pattern": r"[^\w\s]",
                "replacement": "",
                "case": "title"
            },
            "phone_standardization": {
                "pattern": r"[^\d]",
                "replacement": "",
                "format": "xxx-xxx-xxxx"
            },
            "email_validation": {
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "validation": True
            },
            "date_standardization": {
                "input_formats": ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"],
                "output_format": "%Y-%m-%d"
            },
            "currency_normalization": {
                "pattern": r"[^\d.-]",
                "replacement": "",
                "type": "decimal"
            }
        }
    
    def _initialize_data_type_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize data type conversion mappings."""
        return {
            "string_to_number": {
                "method": "pd.to_numeric",
                "error_handling": "coerce",
                "fillna": "0"
            },
            "string_to_datetime": {
                "method": "pd.to_datetime",
                "error_handling": "coerce",
                "infer_datetime_format": "True"
            },
            "number_to_string": {
                "method": "astype",
                "dtype": "str",
                "fillna": "0"
            },
            "boolean_conversion": {
                "true_values": ["true", "yes", "1", "y", "on"],
                "false_values": ["false", "no", "0", "n", "off"]
            }
        }
    
    async def _process(
        self,
        source_data: ParsedData,
        target_schema: Dict[str, str],
        business_rules: List[str] = None,
        performance_targets: Dict[str, Any] = None,
        **kwargs
    ) -> TransformationStrategy:
        """
        Generate comprehensive transformation strategy for data alignment.
        
        Args:
            source_data: Parsed source data with schema information
            target_schema: Target schema specification
            business_rules: Business validation and transformation rules
            performance_targets: Performance optimization targets
            
        Returns:
            TransformationStrategy: Complete transformation strategy with generated code
        """
        self.logger.info("Generating data transformation strategy")
        
        business_rules = business_rules or []
        performance_targets = performance_targets or {}
        
        # Analyze source and target schemas
        schema_analysis = await self._analyze_schema_alignment(
            source_data.schema, target_schema
        )
        
        # Generate field mappings
        field_mappings = await self._generate_field_mappings(
            source_data.schema, target_schema, business_rules
        )
        
        # Generate transformation rules
        transformation_rules = await self._generate_transformation_rules(
            schema_analysis, business_rules
        )
        
        # Generate validation logic
        validation_logic = await self._generate_validation_logic(
            target_schema, business_rules, source_data.quality_score
        )
        
        # Generate data cleaning rules
        cleaning_rules = await self._generate_cleaning_rules(
            source_data, business_rules
        )
        
        # Generate calculated fields
        calculated_fields = await self._generate_calculated_fields(
            business_rules, target_schema
        )
        
        # Generate performance optimizations
        performance_optimizations = await self._generate_performance_optimizations(
            source_data, performance_targets
        )
        
        # Generate error handling strategies
        error_handling = await self._generate_error_handling_strategies(
            source_data, business_rules
        )
        
        # Generate quality metrics
        quality_metrics = await self._generate_quality_metrics(
            target_schema, business_rules
        )
        
        # Generate transformation code
        generated_code = await self._generate_transformation_code(
            source_data,
            target_schema,
            field_mappings,
            transformation_rules,
            validation_logic,
            cleaning_rules,
            calculated_fields,
            performance_optimizations
        )
        
        return TransformationStrategy(
            source_schema=source_data.schema,
            target_schema=target_schema,
            transformation_rules=transformation_rules,
            validation_logic=validation_logic,
            performance_optimizations=performance_optimizations,
            error_handling=error_handling,
            generated_code=generated_code,
            field_mappings=field_mappings,
            calculated_fields=calculated_fields,
            data_cleaning_rules=cleaning_rules,
            quality_metrics=quality_metrics
        )
    
    async def _analyze_schema_alignment(
        self,
        source_schema: Dict[str, str],
        target_schema: Dict[str, str]
    ) -> Dict[str, Any]:
        """Analyze alignment between source and target schemas."""
        analysis = {
            "direct_matches": {},
            "type_conversions": {},
            "missing_in_source": [],
            "missing_in_target": [],
            "fuzzy_matches": {},
            "complex_mappings": {}
        }
        
        # Find direct field name matches
        for target_field, target_type in target_schema.items():
            if target_field in source_schema:
                source_type = source_schema[target_field]
                if source_type == target_type:
                    analysis["direct_matches"][target_field] = target_field
                else:
                    analysis["type_conversions"][target_field] = {
                        "source_type": source_type,
                        "target_type": target_type
                    }
        
        # Find missing fields
        analysis["missing_in_source"] = [
            field for field in target_schema.keys() 
            if field not in source_schema
        ]
        analysis["missing_in_target"] = [
            field for field in source_schema.keys() 
            if field not in target_schema
        ]
        
        # Find fuzzy matches (similar field names)
        for target_field in analysis["missing_in_source"]:
            fuzzy_match = await self._find_fuzzy_field_match(
                target_field, source_schema.keys()
            )
            if fuzzy_match:
                analysis["fuzzy_matches"][target_field] = fuzzy_match
        
        return analysis
    
    async def _find_fuzzy_field_match(
        self,
        target_field: str,
        source_fields: List[str]
    ) -> Optional[str]:
        """Find fuzzy matches for field names using string similarity."""
        import difflib
        
        # Normalize field names for comparison
        target_normalized = target_field.lower().replace("_", "").replace(" ", "")
        
        best_match = None
        best_score = 0.0
        
        for source_field in source_fields:
            source_normalized = source_field.lower().replace("_", "").replace(" ", "")
            
            # Calculate similarity score
            score = difflib.SequenceMatcher(
                None, target_normalized, source_normalized
            ).ratio()
            
            if score > 0.8 and score > best_score:  # 80% similarity threshold
                best_score = score
                best_match = source_field
        
        return best_match
    
    async def _generate_field_mappings(
        self,
        source_schema: Dict[str, str],
        target_schema: Dict[str, str],
        business_rules: List[str]
    ) -> Dict[str, str]:
        """Generate direct field-to-field mappings."""
        mappings = {}
        
        # Direct matches
        for target_field in target_schema:
            if target_field in source_schema:
                mappings[target_field] = target_field
        
        # Fuzzy matches
        for target_field in target_schema:
            if target_field not in mappings:
                fuzzy_match = await self._find_fuzzy_field_match(
                    target_field, source_schema.keys()
                )
                if fuzzy_match:
                    mappings[target_field] = fuzzy_match
        
        # Business rule based mappings
        for rule in business_rules:
            mapping = await self._extract_mapping_from_rule(rule)
            if mapping:
                mappings.update(mapping)
        
        return mappings
    
    async def _extract_mapping_from_rule(self, rule: str) -> Optional[Dict[str, str]]:
        """Extract field mappings from business rules."""
        import re
        
        # Look for mapping patterns in business rules
        mapping_patterns = [
            r"map\s+(\w+)\s+to\s+(\w+)",
            r"(\w+)\s+(?:becomes|->|maps to)\s+(\w+)",
            r"rename\s+(\w+)\s+(?:as|to)\s+(\w+)"
        ]
        
        for pattern in mapping_patterns:
            match = re.search(pattern, rule.lower())
            if match:
                source_field, target_field = match.groups()
                return {target_field: source_field}
        
        return None
    
    async def _generate_transformation_rules(
        self,
        schema_analysis: Dict[str, Any],
        business_rules: List[str]
    ) -> List[str]:
        """Generate high-level transformation rules."""
        rules = []
        
        # Type conversion rules
        for field, conversion in schema_analysis["type_conversions"].items():
            source_type = conversion["source_type"]
            target_type = conversion["target_type"]
            rules.append(f"Convert {field} from {source_type} to {target_type}")
        
        # Missing field handling
        for field in schema_analysis["missing_in_source"]:
            rules.append(f"Generate default value for missing field: {field}")
        
        # Fuzzy match mappings
        for target_field, source_field in schema_analysis["fuzzy_matches"].items():
            rules.append(f"Map {source_field} to {target_field} with validation")
        
        # Business rule derived transformations
        for rule in business_rules:
            transformation = await self._extract_transformation_from_rule(rule)
            if transformation:
                rules.append(transformation)
        
        return rules
    
    async def _extract_transformation_from_rule(self, rule: str) -> Optional[str]:
        """Extract transformation logic from business rules."""
        import re
        
        # Common transformation patterns
        if re.search(r"normalize|standardize", rule.lower()):
            return f"Normalize data according to rule: {rule}"
        elif re.search(r"validate|check", rule.lower()):
            return f"Validate data according to rule: {rule}"
        elif re.search(r"calculate|compute|derive", rule.lower()):
            return f"Calculate derived field according to rule: {rule}"
        elif re.search(r"clean|remove|filter", rule.lower()):
            return f"Clean data according to rule: {rule}"
        
        return None
    
    async def _generate_validation_logic(
        self,
        target_schema: Dict[str, str],
        business_rules: List[str],
        source_quality_score: float
    ) -> List[str]:
        """Generate data validation logic."""
        validation_rules = []
        
        # Schema-based validation
        for field, field_type in target_schema.items():
            if field_type == "integer":
                validation_rules.append(f"Validate {field} is a valid integer")
            elif field_type == "float":
                validation_rules.append(f"Validate {field} is a valid float")
            elif field_type == "datetime":
                validation_rules.append(f"Validate {field} is a valid datetime")
            elif field_type == "string":
                validation_rules.append(f"Validate {field} is not null or empty")
        
        # Business rule validation
        for rule in business_rules:
            if "must" in rule.lower() or "required" in rule.lower():
                validation_rules.append(f"Business rule validation: {rule}")
        
        # Quality-based validation
        if source_quality_score < 0.8:
            validation_rules.append("Apply strict validation due to low source data quality")
            validation_rules.append("Implement additional data quality checks")
        
        return validation_rules
    
    async def _generate_cleaning_rules(
        self,
        source_data: ParsedData,
        business_rules: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate data cleaning and standardization rules."""
        cleaning_rules = []
        
        # Based on detected anomalies
        for anomaly in source_data.anomalies:
            if "missing_values" in anomaly:
                cleaning_rules.append({
                    "type": "handle_missing_values",
                    "strategy": "imputation",
                    "method": "median_for_numeric_mean_for_categorical"
                })
            elif "outliers" in anomaly:
                cleaning_rules.append({
                    "type": "handle_outliers",
                    "strategy": "cap_at_percentile",
                    "percentiles": [5, 95]
                })
        
        # Format-specific cleaning
        if source_data.format in ["html", "text"]:
            cleaning_rules.append({
                "type": "text_cleaning",
                "operations": ["strip_whitespace", "remove_html_tags", "normalize_unicode"]
            })
        
        # Business rule based cleaning
        for rule in business_rules:
            if "clean" in rule.lower() or "standardize" in rule.lower():
                cleaning_rules.append({
                    "type": "business_rule_cleaning",
                    "rule": rule,
                    "implementation": "custom"
                })
        
        return cleaning_rules
    
    async def _generate_calculated_fields(
        self,
        business_rules: List[str],
        target_schema: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate calculated field definitions."""
        calculated_fields = {}
        
        # Extract calculation rules from business requirements
        for rule in business_rules:
            field_calc = await self._extract_calculation_from_rule(rule)
            if field_calc:
                calculated_fields.update(field_calc)
        
        # Common derived fields based on schema
        if "full_name" in target_schema and "first_name" in target_schema and "last_name" in target_schema:
            calculated_fields["full_name"] = "first_name + ' ' + last_name"
        
        if "total_amount" in target_schema and "quantity" in target_schema and "unit_price" in target_schema:
            calculated_fields["total_amount"] = "quantity * unit_price"
        
        return calculated_fields
    
    async def _extract_calculation_from_rule(self, rule: str) -> Optional[Dict[str, str]]:
        """Extract field calculation logic from business rules."""
        import re
        
        # Look for calculation patterns
        calc_patterns = [
            r"calculate\s+(\w+)\s+(?:as|=)\s+(.+)",
            r"(\w+)\s+(?:equals|=)\s+(.+)",
            r"derive\s+(\w+)\s+from\s+(.+)"
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, rule.lower())
            if match:
                field_name, calculation = match.groups()
                return {field_name: calculation.strip()}
        
        return None
    
    async def _generate_performance_optimizations(
        self,
        source_data: ParsedData,
        performance_targets: Dict[str, Any]
    ) -> List[str]:
        """Generate performance optimization strategies."""
        optimizations = []
        
        # Based on data size
        if source_data.size_mb > 100:  # Large dataset
            optimizations.extend([
                "Use chunked processing for memory efficiency",
                "Implement parallel processing with multiprocessing",
                "Consider using Polars instead of Pandas for better performance",
                "Use vectorized operations where possible"
            ])
        
        if source_data.row_count > 1000000:  # Many rows
            optimizations.extend([
                "Use streaming processing to avoid memory issues",
                "Implement incremental processing with progress tracking",
                "Consider database-based transformations for very large datasets"
            ])
        
        # Performance target based optimizations
        if "max_processing_time" in performance_targets:
            optimizations.append("Optimize for processing time with parallel execution")
        
        if "memory_limit" in performance_targets:
            optimizations.append("Optimize for memory usage with streaming and chunking")
        
        return optimizations
    
    async def _generate_error_handling_strategies(
        self,
        source_data: ParsedData,
        business_rules: List[str]
    ) -> List[str]:
        """Generate error handling and recovery strategies."""
        error_strategies = []
        
        # Based on data quality
        if source_data.quality_score < 0.8:
            error_strategies.extend([
                "Implement robust error handling for data quality issues",
                "Create detailed error logs with row-level information",
                "Provide data quality reports for manual review"
            ])
        
        # Common error handling patterns
        error_strategies.extend([
            "Handle type conversion errors gracefully",
            "Implement retry logic for transient failures",
            "Create error quarantine for problematic records",
            "Generate comprehensive error reports",
            "Implement circuit breaker pattern for cascading failures"
        ])
        
        # Business rule specific error handling
        critical_rules = [rule for rule in business_rules if "critical" in rule.lower()]
        if critical_rules:
            error_strategies.append("Implement strict error handling for critical business rules")
        
        return error_strategies
    
    async def _generate_quality_metrics(
        self,
        target_schema: Dict[str, str],
        business_rules: List[str]
    ) -> Dict[str, str]:
        """Generate quality metrics to track during transformation."""
        metrics = {
            "overall_success_rate": "percentage of successfully transformed records",
            "data_completeness": "percentage of non-null values",
            "validation_pass_rate": "percentage of records passing validation",
            "error_rate": "percentage of records with errors"
        }
        
        # Field-specific metrics
        for field in target_schema.keys():
            metrics[f"{field}_completeness"] = f"completeness rate for {field}"
        
        # Business rule metrics
        for rule in business_rules:
            if "must" in rule.lower():
                rule_key = rule.lower().replace(" ", "_")[:30]
                metrics[f"{rule_key}_compliance"] = f"compliance rate for rule: {rule}"
        
        return metrics
    
    async def _generate_transformation_code(
        self,
        source_data: ParsedData,
        target_schema: Dict[str, str],
        field_mappings: Dict[str, str],
        transformation_rules: List[str],
        validation_logic: List[str],
        cleaning_rules: List[Dict[str, Any]],
        calculated_fields: Dict[str, str],
        performance_optimizations: List[str]
    ) -> str:
        """Generate comprehensive Python transformation code."""
        
        code_template = '''
import pandas as pd
import polars as pl
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import re

class DataTransformer:
    """Generated data transformer with comprehensive transformation logic."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        self.logger = logging.getLogger(__name__)
        self.quality_metrics = {{}}
        self.error_records = []
        
        # Field mappings
        self.field_mappings = {field_mappings}
        
        # Target schema
        self.target_schema = {target_schema}
        
        # Calculated fields
        self.calculated_fields = {calculated_fields}
    
    async def transform_data(self, source_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Main transformation method."""
        try:
            self.logger.info(f"Starting transformation of {{len(source_data)}} records")
            
            # Convert to DataFrame for processing
            {df_creation_code}
            
            # Apply data cleaning
            df_cleaned = await self._apply_cleaning_rules(df)
            
            # Apply field mappings and transformations
            df_mapped = await self._apply_field_mappings(df_cleaned)
            
            # Apply type conversions
            df_typed = await self._apply_type_conversions(df_mapped)
            
            # Generate calculated fields
            df_calculated = await self._generate_calculated_fields(df_typed)
            
            # Apply validation
            df_validated, validation_results = await self._apply_validation(df_calculated)
            
            # Generate quality metrics
            quality_metrics = await self._calculate_quality_metrics(df_validated)
            
            # Convert back to records
            result_records = df_validated.to_dict('records')
            
            return {{
                "success": True,
                "data": result_records,
                "quality_metrics": quality_metrics,
                "validation_results": validation_results,
                "records_processed": len(result_records),
                "error_count": len(self.error_records)
            }}
            
        except Exception as e:
            self.logger.error(f"Transformation failed: {{e}}")
            return {{
                "success": False,
                "error": str(e),
                "error_records": self.error_records
            }}
    
    async def _apply_cleaning_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply data cleaning and standardization rules."""
        df_clean = df.copy()
        
        {cleaning_code}
        
        return df_clean
    
    async def _apply_field_mappings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply field mappings and basic transformations."""
        df_mapped = pd.DataFrame()
        
        for target_field, source_field in self.field_mappings.items():
            if source_field in df.columns:
                df_mapped[target_field] = df[source_field]
            else:
                self.logger.warning(f"Source field {{source_field}} not found, setting default")
                df_mapped[target_field] = None
        
        return df_mapped
    
    async def _apply_type_conversions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply data type conversions based on target schema."""
        df_typed = df.copy()
        
        {type_conversion_code}
        
        return df_typed
    
    async def _generate_calculated_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate calculated fields based on business rules."""
        df_calc = df.copy()
        
        {calculated_fields_code}
        
        return df_calc
    
    async def _apply_validation(self, df: pd.DataFrame) -> tuple:
        """Apply validation rules and return results."""
        validation_results = {{}}
        df_valid = df.copy()
        
        {validation_code}
        
        return df_valid, validation_results
    
    async def _calculate_quality_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate data quality metrics."""
        metrics = {{}}
        
        # Overall completeness
        total_cells = df.size
        non_null_cells = df.count().sum()
        metrics['overall_completeness'] = non_null_cells / total_cells if total_cells > 0 else 0
        
        # Field-specific completeness
        for column in df.columns:
            metrics[f'{{column}}_completeness'] = df[column].count() / len(df)
        
        # Success rate
        metrics['success_rate'] = (len(df) - len(self.error_records)) / len(df) if len(df) > 0 else 0
        
        return metrics
    
    def _handle_transformation_error(self, error: Exception, record_index: int, context: str):
        """Handle transformation errors gracefully."""
        error_info = {{
            'index': record_index,
            'error': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }}
        self.error_records.append(error_info)
        self.logger.error(f"Transformation error at record {{record_index}}: {{error}}")

# Usage example
async def main():
    transformer = DataTransformer()
    
    # Sample data for testing
    sample_data = [
        {sample_data_example}
    ]
    
    result = await transformer.transform_data(sample_data)
    return result

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(main())
    print(result)
'''
        
        # Generate specific code sections
        df_creation_code = await self._generate_df_creation_code(source_data, performance_optimizations)
        cleaning_code = await self._generate_cleaning_code(cleaning_rules)
        type_conversion_code = await self._generate_type_conversion_code(target_schema)
        calculated_fields_code = await self._generate_calculated_fields_code(calculated_fields)
        validation_code = await self._generate_validation_code(validation_logic)
        sample_data_example = await self._generate_sample_data(source_data.sample_data)
        
        return code_template.format(
            field_mappings=field_mappings,
            target_schema=target_schema,
            calculated_fields=calculated_fields,
            df_creation_code=df_creation_code,
            cleaning_code=cleaning_code,
            type_conversion_code=type_conversion_code,
            calculated_fields_code=calculated_fields_code,
            validation_code=validation_code,
            sample_data_example=sample_data_example
        )
    
    async def _generate_df_creation_code(
        self,
        source_data: ParsedData,
        performance_optimizations: List[str]
    ) -> str:
        """Generate DataFrame creation code with performance considerations."""
        
        if "Use Polars" in " ".join(performance_optimizations):
            return '''
            # Use Polars for better performance
            df = pl.from_dicts(source_data)
            '''
        elif source_data.size_mb > 100:
            return '''
            # Use chunked processing for large datasets
            if len(source_data) > 100000:
                df = pd.DataFrame(source_data, dtype='object')  # Prevent automatic type inference
            else:
                df = pd.DataFrame(source_data)
            '''
        else:
            return '''
            # Standard DataFrame creation
            df = pd.DataFrame(source_data)
            '''
    
    async def _generate_cleaning_code(self, cleaning_rules: List[Dict[str, Any]]) -> str:
        """Generate data cleaning code."""
        cleaning_code_parts = []
        
        for rule in cleaning_rules:
            if rule["type"] == "handle_missing_values":
                cleaning_code_parts.append('''
        # Handle missing values
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
        categorical_columns = df_clean.select_dtypes(include=['object']).columns
        
        for col in numeric_columns:
            df_clean[col].fillna(df_clean[col].median(), inplace=True)
        
        for col in categorical_columns:
            df_clean[col].fillna('Unknown', inplace=True)
                ''')
            
            elif rule["type"] == "handle_outliers":
                cleaning_code_parts.append('''
        # Handle outliers by capping at percentiles
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            q5 = df_clean[col].quantile(0.05)
            q95 = df_clean[col].quantile(0.95)
            df_clean[col] = df_clean[col].clip(lower=q5, upper=q95)
                ''')
            
            elif rule["type"] == "text_cleaning":
                cleaning_code_parts.append('''
        # Text cleaning operations
        text_columns = df_clean.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].str.replace(r'<[^>]+>', '', regex=True)  # Remove HTML tags
            df_clean[col] = df_clean[col].str.normalize('NFKD')  # Unicode normalization
                ''')
        
        return "\n".join(cleaning_code_parts) if cleaning_code_parts else "        # No specific cleaning rules defined"
    
    async def _generate_type_conversion_code(self, target_schema: Dict[str, str]) -> str:
        """Generate type conversion code."""
        conversion_code_parts = []
        
        for field, field_type in target_schema.items():
            if field_type == "integer":
                conversion_code_parts.append(f'''
        # Convert {field} to integer
        if '{field}' in df_typed.columns:
            try:
                df_typed['{field}'] = pd.to_numeric(df_typed['{field}'], errors='coerce').astype('Int64')
            except Exception as e:
                self.logger.warning(f"Failed to convert {field} to integer: {{e}}")
                ''')
            
            elif field_type == "float":
                conversion_code_parts.append(f'''
        # Convert {field} to float
        if '{field}' in df_typed.columns:
            try:
                df_typed['{field}'] = pd.to_numeric(df_typed['{field}'], errors='coerce')
            except Exception as e:
                self.logger.warning(f"Failed to convert {field} to float: {{e}}")
                ''')
            
            elif field_type == "datetime":
                conversion_code_parts.append(f'''
        # Convert {field} to datetime
        if '{field}' in df_typed.columns:
            try:
                df_typed['{field}'] = pd.to_datetime(df_typed['{field}'], errors='coerce')
            except Exception as e:
                self.logger.warning(f"Failed to convert {field} to datetime: {{e}}")
                ''')
        
        return "\n".join(conversion_code_parts) if conversion_code_parts else "        # No type conversions needed"
    
    async def _generate_calculated_fields_code(self, calculated_fields: Dict[str, str]) -> str:
        """Generate calculated fields code."""
        calc_code_parts = []
        
        for field, calculation in calculated_fields.items():
            calc_code_parts.append(f'''
        # Calculate {field}
        try:
            df_calc['{field}'] = {calculation}
        except Exception as e:
            self.logger.error(f"Failed to calculate {field}: {{e}}")
            df_calc['{field}'] = None
            ''')
        
        return "\n".join(calc_code_parts) if calc_code_parts else "        # No calculated fields defined"
    
    async def _generate_validation_code(self, validation_logic: List[str]) -> str:
        """Generate validation code."""
        validation_code_parts = []
        
        # Generate validation based on rules
        validation_code_parts.append('''
        # Validate required fields are not null
        for column in df_valid.columns:
            null_count = df_valid[column].isnull().sum()
            validation_results[f'{column}_null_count'] = null_count
            validation_results[f'{column}_completeness'] = (len(df_valid) - null_count) / len(df_valid)
        ''')
        
        # Add specific validation rules
        for rule in validation_logic:
            if "integer" in rule.lower():
                field = rule.split()[1]  # Extract field name
                validation_code_parts.append(f'''
        # Validate {field} is integer
        if '{field}' in df_valid.columns:
            invalid_integers = df_valid['{field}'].apply(lambda x: not isinstance(x, (int, np.integer)) and pd.notna(x))
            validation_results['{field}_invalid_integers'] = invalid_integers.sum()
                ''')
        
        return "\n".join(validation_code_parts) if validation_code_parts else "        # Basic validation only"
    
    async def _generate_sample_data(self, sample_data: List[Dict[str, Any]]) -> str:
        """Generate sample data for testing."""
        if sample_data:
            return str(sample_data[0])
        else:
            return '{"field1": "sample_value", "field2": 123}'
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "transformation_types": [
                "schema_alignment",
                "data_type_conversion",
                "field_mapping",
                "calculated_fields",
                "data_cleaning",
                "validation_rules",
                "performance_optimization"
            ],
            "supported_patterns": list(self.transformation_patterns.keys()),
            "data_type_mappings": list(self.data_types_mapping.keys()),
            "code_generation": [
                "pandas_transformations",
                "polars_transformations",
                "vectorized_operations",
                "chunked_processing",
                "error_handling",
                "quality_metrics"
            ],
            "output_format": "TransformationStrategy"
        })
        return base_capabilities