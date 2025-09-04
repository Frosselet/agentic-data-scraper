"""
Data parsing modules for the Agentic Data Scraper.

This module provides parsing capabilities for various data formats including HTML, JSON, XML,
CSV, and structured documents. It includes both rule-based and AI-powered parsing approaches.

Classes:
    HtmlParser: Parse and extract data from HTML documents
    JsonParser: Parse and validate JSON data structures
    XmlParser: Parse XML documents and extract structured data
    CsvParser: Parse CSV files with schema validation
    DocumentParser: Parse various document formats (PDF, Word, etc.)
    AiParser: AI-powered parsing using BAML agents

Functions:
    parse_content: Auto-detect format and parse content
    validate_parsed_data: Validate parsed data against schemas

Example:
    ```python
    from agentic_data_scraper.parsers import HtmlParser, parse_content
    
    # Parse HTML content
    parser = HtmlParser()
    data = parser.parse(html_content, selectors={
        'title': 'h1',
        'description': '.description',
        'links': 'a[href]'
    })
    
    # Auto-detect and parse
    parsed_data = parse_content(raw_content)
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .html_parser import HtmlParser
    from .json_parser import JsonParser
    from .xml_parser import XmlParser
    from .csv_parser import CsvParser
    from .document_parser import DocumentParser
    from .ai_parser import AiParser

__all__ = [
    "HtmlParser",
    "JsonParser",
    "XmlParser", 
    "CsvParser",
    "DocumentParser",
    "AiParser",
    "parse_content",
    "validate_parsed_data",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "HtmlParser":
        from .html_parser import HtmlParser
        return HtmlParser
    elif name == "JsonParser":
        from .json_parser import JsonParser
        return JsonParser
    elif name == "XmlParser":
        from .xml_parser import XmlParser
        return XmlParser
    elif name == "CsvParser":
        from .csv_parser import CsvParser
        return CsvParser
    elif name == "DocumentParser":
        from .document_parser import DocumentParser
        return DocumentParser
    elif name == "AiParser":
        from .ai_parser import AiParser
        return AiParser
    elif name == "parse_content":
        from .utils import parse_content
        return parse_content
    elif name == "validate_parsed_data":
        from .validation import validate_parsed_data
        return validate_parsed_data
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")