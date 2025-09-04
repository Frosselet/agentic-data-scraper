"""
Data transformation modules for the Agentic Data Scraper.

This module provides data transformation capabilities including cleaning, normalization,
enrichment, and format conversion. It supports both batch and streaming transformations.

Classes:
    DataCleaner: Clean and standardize raw data
    DataNormalizer: Normalize data formats and structures
    DataEnricher: Enrich data with additional information
    FormatConverter: Convert between different data formats
    TransformationPipeline: Chain multiple transformations
    StreamingTransformer: Process data streams efficiently

Functions:
    transform_data: Apply transformations to data
    validate_transformation: Validate transformation results
    create_pipeline: Create transformation pipeline from config

Example:
    ```python
    from agentic_data_scraper.transformers import (
        DataCleaner, DataNormalizer, TransformationPipeline
    )
    
    # Create transformation pipeline
    pipeline = TransformationPipeline([
        DataCleaner(remove_nulls=True, trim_whitespace=True),
        DataNormalizer(date_format="%Y-%m-%d", case="lower")
    ])
    
    # Transform data
    cleaned_data = pipeline.transform(raw_data)
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_cleaner import DataCleaner
    from .data_normalizer import DataNormalizer
    from .data_enricher import DataEnricher
    from .format_converter import FormatConverter
    from .pipeline import TransformationPipeline
    from .streaming import StreamingTransformer

__all__ = [
    "DataCleaner",
    "DataNormalizer",
    "DataEnricher",
    "FormatConverter", 
    "TransformationPipeline",
    "StreamingTransformer",
    "transform_data",
    "validate_transformation",
    "create_pipeline",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "DataCleaner":
        from .data_cleaner import DataCleaner
        return DataCleaner
    elif name == "DataNormalizer":
        from .data_normalizer import DataNormalizer
        return DataNormalizer
    elif name == "DataEnricher":
        from .data_enricher import DataEnricher
        return DataEnricher
    elif name == "FormatConverter":
        from .format_converter import FormatConverter
        return FormatConverter
    elif name == "TransformationPipeline":
        from .pipeline import TransformationPipeline
        return TransformationPipeline
    elif name == "StreamingTransformer":
        from .streaming import StreamingTransformer
        return StreamingTransformer
    elif name == "transform_data":
        from .utils import transform_data
        return transform_data
    elif name == "validate_transformation":
        from .validation import validate_transformation
        return validate_transformation
    elif name == "create_pipeline":
        from .factory import create_pipeline
        return create_pipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")