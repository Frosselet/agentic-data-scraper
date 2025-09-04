"""
Data Parser Specialist Agent - Multi-format parsing with quality assessment and anomaly detection.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from .base import BaseAgent
import asyncio
import logging

class ParsedData(BaseModel):
    """Structured representation of parsed data with quality metrics."""
    
    format: str = Field(description="Original data format (html, csv, excel, pdf, json, xml, image)")
    schema: Dict[str, str] = Field(
        description="Inferred data schema with field names and types"
    )
    quality_score: float = Field(
        description="Overall data quality score (0.0 to 1.0)"
    )
    anomalies: List[str] = Field(
        default_factory=list,
        description="Detected anomalies and data quality issues"
    )
    encoding: Optional[str] = Field(
        default=None,
        description="Character encoding of the source data"
    )
    size_mb: float = Field(
        description="Size of the parsed data in megabytes"
    )
    row_count: int = Field(
        default=0,
        description="Number of data rows/records parsed"
    )
    column_count: int = Field(
        default=0,
        description="Number of columns/fields identified"
    )
    completeness_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Completeness percentage for each field"
    )
    data_types: Dict[str, str] = Field(
        default_factory=dict,
        description="Detected data types for each field"
    )
    sample_data: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Sample records for validation"
    )
    parsing_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata from parsing process"
    )

class DataQualityReport(BaseModel):
    """Comprehensive data quality assessment report."""
    
    overall_score: float = Field(description="Overall quality score (0.0 to 1.0)")
    completeness_score: float = Field(description="Data completeness score")
    consistency_score: float = Field(description="Data consistency score")
    accuracy_indicators: Dict[str, float] = Field(
        default_factory=dict,
        description="Accuracy indicators for different aspects"
    )
    anomalies_detected: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detailed anomaly information"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Data quality improvement recommendations"
    )

class DataParserAgent(BaseAgent):
    """
    Agent specialized in parsing diverse data formats with comprehensive quality assessment.
    
    Handles HTML, CSV, Excel, PDF, JSON, XML, and image formats with OCR capabilities.
    Provides intelligent schema inference and anomaly detection.
    """
    
    def __init__(
        self,
        agent_id: str = "data_parser",
        logger: Optional[logging.Logger] = None,
        timeout_seconds: int = 900
    ):
        super().__init__(agent_id, logger, timeout_seconds)
        self.supported_formats = [
            "html", "csv", "excel", "xlsx", "pdf", "json", "xml", 
            "txt", "tsv", "parquet", "avro", "image", "png", "jpg", "jpeg"
        ]
        self.parsers = self._initialize_parsers()
    
    def _initialize_parsers(self) -> Dict[str, Any]:
        """Initialize format-specific parsers and configurations."""
        return {
            "html": {
                "libraries": ["beautifulsoup4", "lxml", "html5lib"],
                "selectors": ["css", "xpath"],
                "table_detection": True
            },
            "csv": {
                "libraries": ["pandas", "polars", "csv"],
                "delimiter_detection": True,
                "encoding_detection": True,
                "header_inference": True
            },
            "excel": {
                "libraries": ["openpyxl", "xlrd", "pandas"],
                "sheet_detection": True,
                "formula_evaluation": False,
                "merged_cell_handling": True
            },
            "pdf": {
                "libraries": ["pdfplumber", "pymupdf", "camelot"],
                "ocr_fallback": True,
                "table_extraction": True,
                "image_extraction": True
            },
            "json": {
                "libraries": ["json", "ijson"],
                "streaming": True,
                "schema_inference": True,
                "nested_flattening": True
            },
            "xml": {
                "libraries": ["lxml", "xml.etree"],
                "namespace_handling": True,
                "schema_validation": True,
                "xpath_support": True
            },
            "image": {
                "libraries": ["tesseract", "easyocr", "paddleocr"],
                "preprocessing": True,
                "table_detection": True,
                "language_detection": True
            }
        }
    
    async def _process(
        self,
        raw_data: Union[str, bytes],
        data_format: str,
        schema_hints: Optional[List[str]] = None,
        quality_thresholds: Optional[Dict[str, float]] = None,
        **kwargs
    ) -> ParsedData:
        """
        Parse raw data and perform comprehensive quality assessment.
        
        Args:
            raw_data: Raw data content to parse
            data_format: Format of the data (html, csv, excel, etc.)
            schema_hints: Optional hints about expected schema
            quality_thresholds: Quality thresholds for assessment
            
        Returns:
            ParsedData: Parsed data with quality metrics and schema information
        """
        self.logger.info(f"Parsing data format: {data_format}")
        
        if data_format not in self.supported_formats:
            raise ValueError(f"Unsupported data format: {data_format}")
        
        schema_hints = schema_hints or []
        quality_thresholds = quality_thresholds or self._get_default_quality_thresholds()
        
        # Detect encoding if dealing with text data
        encoding = await self._detect_encoding(raw_data) if isinstance(raw_data, bytes) else "utf-8"
        
        # Parse data based on format
        parsed_result = await self._parse_by_format(raw_data, data_format, encoding)
        
        # Infer schema
        schema = await self._infer_schema(parsed_result, schema_hints)
        
        # Assess data quality
        quality_report = await self._assess_data_quality(parsed_result, quality_thresholds)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(parsed_result, schema)
        
        # Calculate size metrics
        size_mb = await self._calculate_size(raw_data)
        
        return ParsedData(
            format=data_format,
            schema=schema,
            quality_score=quality_report.overall_score,
            anomalies=[str(a) for a in anomalies],
            encoding=encoding,
            size_mb=size_mb,
            row_count=len(parsed_result) if isinstance(parsed_result, list) else 1,
            column_count=len(schema),
            completeness_metrics=await self._calculate_completeness(parsed_result),
            data_types=await self._detect_data_types(parsed_result),
            sample_data=await self._extract_sample_data(parsed_result),
            parsing_metadata=await self._generate_parsing_metadata(data_format, parsed_result)
        )
    
    async def _detect_encoding(self, data: bytes) -> str:
        """Detect character encoding of byte data."""
        try:
            import chardet
            result = chardet.detect(data)
            return result['encoding'] or 'utf-8'
        except ImportError:
            # Fallback to common encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    data.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue
            return 'utf-8'
    
    async def _parse_by_format(
        self,
        raw_data: Union[str, bytes],
        data_format: str,
        encoding: str
    ) -> Any:
        """Parse data based on its format."""
        
        if data_format == "html":
            return await self._parse_html(raw_data, encoding)
        elif data_format in ["csv", "tsv"]:
            return await self._parse_csv(raw_data, encoding, data_format)
        elif data_format in ["excel", "xlsx", "xls"]:
            return await self._parse_excel(raw_data)
        elif data_format == "pdf":
            return await self._parse_pdf(raw_data)
        elif data_format == "json":
            return await self._parse_json(raw_data, encoding)
        elif data_format == "xml":
            return await self._parse_xml(raw_data, encoding)
        elif data_format in ["image", "png", "jpg", "jpeg"]:
            return await self._parse_image(raw_data)
        else:
            return await self._parse_text(raw_data, encoding)
    
    async def _parse_html(self, data: Union[str, bytes], encoding: str) -> List[Dict[str, Any]]:
        """Parse HTML content and extract structured data."""
        from bs4 import BeautifulSoup
        
        if isinstance(data, bytes):
            data = data.decode(encoding)
        
        soup = BeautifulSoup(data, 'html.parser')
        
        # Extract tables first (most structured data)
        tables = soup.find_all('table')
        structured_data = []
        
        for table in tables:
            table_data = await self._extract_table_data(table)
            if table_data:
                structured_data.extend(table_data)
        
        # If no tables, try to extract other structured elements
        if not structured_data:
            structured_data = await self._extract_html_elements(soup)
        
        return structured_data
    
    async def _parse_csv(
        self,
        data: Union[str, bytes],
        encoding: str,
        format_type: str
    ) -> List[Dict[str, Any]]:
        """Parse CSV/TSV data with intelligent delimiter detection."""
        import csv
        import io
        
        if isinstance(data, bytes):
            data = data.decode(encoding)
        
        # Detect delimiter
        delimiter = '\t' if format_type == 'tsv' else await self._detect_delimiter(data)
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(data), delimiter=delimiter)
        
        parsed_data = []
        for row in reader:
            # Clean up field names and values
            clean_row = {}
            for key, value in row.items():
                clean_key = str(key).strip() if key else f"field_{len(clean_row)}"
                clean_value = str(value).strip() if value else None
                clean_row[clean_key] = clean_value
            parsed_data.append(clean_row)
        
        return parsed_data
    
    async def _parse_excel(self, data: Union[str, bytes]) -> List[Dict[str, Any]]:
        """Parse Excel files with sheet detection."""
        import pandas as pd
        import io
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Read Excel file
        excel_file = pd.ExcelFile(io.BytesIO(data))
        
        all_data = []
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Convert to list of dictionaries
            sheet_data = df.fillna('').to_dict('records')
            
            # Add sheet information
            for row in sheet_data:
                row['_sheet_name'] = sheet_name
            
            all_data.extend(sheet_data)
        
        return all_data
    
    async def _parse_pdf(self, data: Union[str, bytes]) -> List[Dict[str, Any]]:
        """Parse PDF with table extraction and OCR fallback."""
        import pdfplumber
        import io
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        extracted_data = []
        
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Try to extract tables first
                tables = page.extract_tables()
                
                if tables:
                    for table_num, table in enumerate(tables):
                        if table and len(table) > 1:  # Has header and data rows
                            headers = table[0]
                            for row_data in table[1:]:
                                row_dict = {}
                                for i, cell in enumerate(row_data):
                                    header = headers[i] if i < len(headers) else f"col_{i}"
                                    row_dict[str(header)] = str(cell) if cell else ""
                                row_dict['_page'] = page_num + 1
                                row_dict['_table'] = table_num + 1
                                extracted_data.append(row_dict)
                
                # If no tables, extract text
                if not tables:
                    text = page.extract_text()
                    if text:
                        extracted_data.append({
                            '_page': page_num + 1,
                            '_content_type': 'text',
                            'text': text
                        })
        
        return extracted_data
    
    async def _parse_json(self, data: Union[str, bytes], encoding: str) -> Any:
        """Parse JSON with nested structure flattening option."""
        import json
        
        if isinstance(data, bytes):
            data = data.decode(encoding)
        
        parsed_json = json.loads(data)
        
        # If it's a list of objects, return as is
        if isinstance(parsed_json, list):
            return parsed_json
        
        # If it's a single object, wrap in a list
        if isinstance(parsed_json, dict):
            return [parsed_json]
        
        # For primitive types, create a simple structure
        return [{'value': parsed_json, 'type': type(parsed_json).__name__}]
    
    async def _parse_xml(self, data: Union[str, bytes], encoding: str) -> List[Dict[str, Any]]:
        """Parse XML with intelligent structure extraction."""
        import xml.etree.ElementTree as ET
        
        if isinstance(data, bytes):
            data = data.decode(encoding)
        
        root = ET.fromstring(data)
        
        # Extract data based on XML structure
        extracted_data = []
        
        # If root has multiple children of the same tag, treat as records
        child_tags = [child.tag for child in root]
        if len(set(child_tags)) == 1 and len(child_tags) > 1:
            # Multiple records of the same type
            for child in root:
                record = await self._xml_element_to_dict(child)
                extracted_data.append(record)
        else:
            # Single record or mixed structure
            record = await self._xml_element_to_dict(root)
            extracted_data.append(record)
        
        return extracted_data
    
    async def _parse_image(self, data: bytes) -> List[Dict[str, Any]]:
        """Parse image using OCR to extract text and table data."""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # Open image
            image = Image.open(io.BytesIO(data))
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)
            
            # Try to detect and extract tables
            table_data = await self._extract_table_from_text(extracted_text)
            
            if table_data:
                return table_data
            else:
                return [{
                    '_content_type': 'ocr_text',
                    'text': extracted_text,
                    'confidence': 'medium'  # Could be improved with actual confidence scores
                }]
                
        except ImportError:
            self.logger.warning("OCR libraries not available, returning metadata only")
            return [{
                '_content_type': 'image',
                'size_bytes': len(data),
                'parsing_status': 'ocr_unavailable'
            }]
    
    async def _parse_text(self, data: Union[str, bytes], encoding: str) -> List[Dict[str, Any]]:
        """Parse plain text data."""
        if isinstance(data, bytes):
            data = data.decode(encoding)
        
        # Try to detect structure in text
        lines = data.split('\n')
        
        # Check if it looks like delimited data
        if len(lines) > 1:
            first_line = lines[0]
            potential_delimiters = [',', '\t', '|', ';']
            
            for delimiter in potential_delimiters:
                if delimiter in first_line and len(first_line.split(delimiter)) > 1:
                    # Looks like delimited data, reparse as CSV
                    return await self._parse_csv(data, encoding, 'csv')
        
        # Treat as unstructured text
        return [{
            '_content_type': 'unstructured_text',
            'text': data,
            'line_count': len(lines),
            'character_count': len(data)
        }]
    
    # Quality assessment methods
    
    async def _assess_data_quality(
        self,
        data: List[Dict[str, Any]],
        thresholds: Dict[str, float]
    ) -> DataQualityReport:
        """Perform comprehensive data quality assessment."""
        
        if not data:
            return DataQualityReport(
                overall_score=0.0,
                completeness_score=0.0,
                consistency_score=0.0,
                recommendations=["No data to assess"]
            )
        
        # Calculate completeness
        completeness = await self._assess_completeness(data)
        
        # Calculate consistency
        consistency = await self._assess_consistency(data)
        
        # Calculate accuracy indicators
        accuracy_indicators = await self._assess_accuracy_indicators(data)
        
        # Overall score weighted average
        overall_score = (
            completeness * 0.4 +
            consistency * 0.3 +
            sum(accuracy_indicators.values()) / len(accuracy_indicators) * 0.3
        ) if accuracy_indicators else (completeness * 0.6 + consistency * 0.4)
        
        # Generate recommendations
        recommendations = await self._generate_quality_recommendations(
            completeness, consistency, accuracy_indicators, thresholds
        )
        
        return DataQualityReport(
            overall_score=min(overall_score, 1.0),
            completeness_score=completeness,
            consistency_score=consistency,
            accuracy_indicators=accuracy_indicators,
            recommendations=recommendations
        )
    
    async def _assess_completeness(self, data: List[Dict[str, Any]]) -> float:
        """Assess data completeness."""
        if not data:
            return 0.0
        
        total_cells = 0
        filled_cells = 0
        
        for record in data:
            for value in record.values():
                total_cells += 1
                if value is not None and str(value).strip():
                    filled_cells += 1
        
        return filled_cells / total_cells if total_cells > 0 else 0.0
    
    async def _assess_consistency(self, data: List[Dict[str, Any]]) -> float:
        """Assess data consistency across records."""
        if len(data) < 2:
            return 1.0  # Single record is always consistent
        
        # Check field consistency across records
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        field_presence_scores = []
        for field in all_fields:
            present_count = sum(1 for record in data if field in record)
            field_presence_scores.append(present_count / len(data))
        
        return sum(field_presence_scores) / len(field_presence_scores)
    
    async def _assess_accuracy_indicators(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Assess various accuracy indicators."""
        indicators = {}
        
        if not data:
            return indicators
        
        # Format consistency for each field
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        for field in all_fields:
            values = [record.get(field) for record in data if field in record]
            non_null_values = [v for v in values if v is not None and str(v).strip()]
            
            if non_null_values:
                # Check data type consistency
                types = [type(v) for v in non_null_values]
                type_consistency = len(set(types)) == 1
                indicators[f"{field}_type_consistency"] = 1.0 if type_consistency else 0.5
        
        return indicators
    
    async def _detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        schema: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies and data quality issues."""
        anomalies = []
        
        if not data:
            return anomalies
        
        # Detect missing values
        for field, field_type in schema.items():
            missing_count = sum(1 for record in data 
                             if field not in record or not record[field])
            if missing_count > len(data) * 0.1:  # More than 10% missing
                anomalies.append({
                    'type': 'high_missing_values',
                    'field': field,
                    'missing_count': missing_count,
                    'total_count': len(data),
                    'percentage': missing_count / len(data) * 100
                })
        
        # Detect outliers for numeric fields
        numeric_fields = [field for field, ftype in schema.items() 
                         if ftype in ['int', 'float', 'number']]
        
        for field in numeric_fields:
            values = []
            for record in data:
                if field in record and record[field] is not None:
                    try:
                        values.append(float(record[field]))
                    except (ValueError, TypeError):
                        continue
            
            if len(values) > 3:
                outliers = await self._detect_numeric_outliers(values)
                if outliers:
                    anomalies.append({
                        'type': 'numeric_outliers',
                        'field': field,
                        'outlier_count': len(outliers),
                        'outlier_values': outliers[:5]  # First 5 outliers
                    })
        
        return anomalies
    
    async def _detect_numeric_outliers(self, values: List[float]) -> List[float]:
        """Detect numeric outliers using IQR method."""
        if len(values) < 4:
            return []
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Calculate quartiles
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [v for v in values if v < lower_bound or v > upper_bound]
        return outliers
    
    # Schema inference methods
    
    async def _infer_schema(
        self,
        data: List[Dict[str, Any]],
        hints: List[str]
    ) -> Dict[str, str]:
        """Infer data schema from parsed data."""
        if not data:
            return {}
        
        # Collect all field names
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        schema = {}
        
        for field in all_fields:
            # Collect sample values for this field
            sample_values = []
            for record in data:
                if field in record and record[field] is not None:
                    value = record[field]
                    if str(value).strip():  # Non-empty string
                        sample_values.append(value)
            
            # Infer type from sample values
            inferred_type = await self._infer_field_type(sample_values, field, hints)
            schema[field] = inferred_type
        
        return schema
    
    async def _infer_field_type(
        self,
        values: List[Any],
        field_name: str,
        hints: List[str]
    ) -> str:
        """Infer the data type of a field based on sample values."""
        if not values:
            return "unknown"
        
        # Check hints first
        for hint in hints:
            if field_name.lower() in hint.lower():
                if "date" in hint.lower() or "time" in hint.lower():
                    return "datetime"
                elif "number" in hint.lower() or "int" in hint.lower():
                    return "integer"
                elif "float" in hint.lower() or "decimal" in hint.lower():
                    return "float"
                elif "bool" in hint.lower():
                    return "boolean"
        
        # Analyze actual values
        sample_size = min(len(values), 100)  # Check up to 100 samples
        sample_values = values[:sample_size]
        
        # Test for boolean
        bool_values = {"true", "false", "yes", "no", "1", "0", "y", "n"}
        if all(str(v).lower().strip() in bool_values for v in sample_values):
            return "boolean"
        
        # Test for integer
        integer_count = 0
        for value in sample_values:
            try:
                int(str(value))
                integer_count += 1
            except ValueError:
                pass
        
        if integer_count == len(sample_values):
            return "integer"
        
        # Test for float
        float_count = 0
        for value in sample_values:
            try:
                float(str(value))
                float_count += 1
            except ValueError:
                pass
        
        if float_count == len(sample_values):
            return "float"
        
        # Test for datetime
        if await self._looks_like_datetime(sample_values):
            return "datetime"
        
        # Default to string
        return "string"
    
    async def _looks_like_datetime(self, values: List[Any]) -> bool:
        """Check if values look like datetime strings."""
        import re
        
        # Common datetime patterns
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        ]
        
        match_count = 0
        for value in values[:10]:  # Check first 10 values
            value_str = str(value).strip()
            if any(re.search(pattern, value_str) for pattern in datetime_patterns):
                match_count += 1
        
        return match_count > len(values[:10]) * 0.7  # 70% threshold
    
    # Helper methods
    
    async def _detect_delimiter(self, data: str) -> str:
        """Detect CSV delimiter."""
        import csv
        
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(data[:1024]).delimiter
            return delimiter
        except csv.Error:
            return ','  # Default to comma
    
    async def _extract_table_data(self, table_element) -> List[Dict[str, Any]]:
        """Extract data from HTML table element."""
        rows = table_element.find_all('tr')
        if len(rows) < 2:
            return []
        
        # Extract headers
        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Extract data rows
        data_rows = []
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            row_data = {}
            
            for i, cell in enumerate(cells):
                header = headers[i] if i < len(headers) else f'col_{i}'
                row_data[header] = cell.get_text(strip=True)
            
            if any(v for v in row_data.values()):  # Skip empty rows
                data_rows.append(row_data)
        
        return data_rows
    
    async def _extract_html_elements(self, soup) -> List[Dict[str, Any]]:
        """Extract structured data from HTML elements."""
        # Look for lists, divs with classes, etc.
        elements = []
        
        # Extract list items
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            for i, item in enumerate(items):
                elements.append({
                    'type': 'list_item',
                    'index': i,
                    'text': item.get_text(strip=True)
                })
        
        # Extract divs with data attributes or classes
        divs = soup.find_all('div', attrs={'class': True})
        for div in divs:
            if div.get_text(strip=True):
                elements.append({
                    'type': 'div',
                    'class': ' '.join(div.get('class', [])),
                    'text': div.get_text(strip=True)
                })
        
        return elements if elements else [{'text': soup.get_text(strip=True)}]
    
    async def _xml_element_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            for key, value in element.attrib.items():
                result[f'@{key}'] = value
        
        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = await self._xml_element_to_dict(child)
            
            if child.tag in result:
                # Multiple elements with same tag - convert to list
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    async def _extract_table_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Attempt to extract table data from OCR text."""
        lines = text.split('\n')
        
        # Look for lines that might be table headers or rows
        # This is a simplified approach - could be enhanced with ML
        potential_table_lines = []
        
        for line in lines:
            line = line.strip()
            if line and ('\t' in line or '  ' in line):  # Multiple spaces or tabs
                potential_table_lines.append(line)
        
        if len(potential_table_lines) < 2:
            return []
        
        # Try to parse as delimited data
        delimiter = '\t' if '\t' in potential_table_lines[0] else '  '
        
        headers = [h.strip() for h in potential_table_lines[0].split(delimiter)]
        data_rows = []
        
        for line in potential_table_lines[1:]:
            values = [v.strip() for v in line.split(delimiter)]
            row_data = {}
            
            for i, value in enumerate(values):
                header = headers[i] if i < len(headers) else f'col_{i}'
                row_data[header] = value
            
            data_rows.append(row_data)
        
        return data_rows
    
    async def _calculate_size(self, data: Union[str, bytes]) -> float:
        """Calculate data size in megabytes."""
        if isinstance(data, str):
            size_bytes = len(data.encode('utf-8'))
        else:
            size_bytes = len(data)
        
        return size_bytes / (1024 * 1024)  # Convert to MB
    
    async def _calculate_completeness(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate completeness metrics for each field."""
        if not data:
            return {}
        
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        completeness = {}
        for field in all_fields:
            present_count = sum(
                1 for record in data 
                if field in record and record[field] is not None and str(record[field]).strip()
            )
            completeness[field] = present_count / len(data)
        
        return completeness
    
    async def _detect_data_types(self, data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Detect data types for each field."""
        if not data:
            return {}
        
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        data_types = {}
        for field in all_fields:
            sample_values = [record.get(field) for record in data if field in record]
            data_types[field] = await self._infer_field_type(sample_values, field, [])
        
        return data_types
    
    async def _extract_sample_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract sample data for validation."""
        if not data:
            return []
        
        # Return first 5 records as sample
        return data[:5]
    
    async def _generate_parsing_metadata(
        self,
        format_type: str,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate metadata about the parsing process."""
        return {
            "format": format_type,
            "parser_used": self.parsers.get(format_type, {}).get("libraries", ["unknown"])[0],
            "records_parsed": len(data),
            "parsing_timestamp": "datetime.now().isoformat()",
            "parsing_agent": self.agent_id
        }
    
    def _get_default_quality_thresholds(self) -> Dict[str, float]:
        """Get default quality assessment thresholds."""
        return {
            "completeness": 0.9,
            "consistency": 0.85,
            "accuracy": 0.95
        }
    
    async def _generate_quality_recommendations(
        self,
        completeness: float,
        consistency: float,
        accuracy_indicators: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> List[str]:
        """Generate data quality improvement recommendations."""
        recommendations = []
        
        if completeness < thresholds.get("completeness", 0.9):
            recommendations.append(
                f"Completeness is {completeness:.1%}, consider data imputation or source improvement"
            )
        
        if consistency < thresholds.get("consistency", 0.85):
            recommendations.append(
                f"Consistency is {consistency:.1%}, review field standardization and validation"
            )
        
        low_accuracy_fields = [
            field for field, score in accuracy_indicators.items()
            if score < thresholds.get("accuracy", 0.95)
        ]
        
        if low_accuracy_fields:
            recommendations.append(
                f"Low accuracy detected in fields: {', '.join(low_accuracy_fields)}"
            )
        
        return recommendations
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        base_capabilities = super().get_capabilities()
        base_capabilities.update({
            "supported_formats": self.supported_formats,
            "parsing_capabilities": [
                "multi_format_parsing",
                "schema_inference", 
                "quality_assessment",
                "anomaly_detection",
                "encoding_detection",
                "table_extraction",
                "ocr_processing",
                "data_type_detection"
            ],
            "quality_metrics": [
                "completeness",
                "consistency", 
                "accuracy_indicators",
                "anomaly_detection",
                "outlier_detection"
            ],
            "output_format": "ParsedData"
        })
        return base_capabilities