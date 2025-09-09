"""
Business-Friendly SOW Elicitation System

This package provides a magical business experience for SOW elicitation that captures
explicit requirements while intelligently inferring implicit analytical opportunities.
"""

from .sow_wizard import SOWElicitationWizard
from .inference_engine import SemanticInferenceEngine
from .graph_discovery import GraphDiscoveryEngine

__all__ = [
    "SOWElicitationWizard",
    "SemanticInferenceEngine", 
    "GraphDiscoveryEngine"
]