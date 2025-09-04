"""
Security and Human-in-the-Loop (HITL) modules for the Agentic Data Scraper.

This module provides security controls, access management, and human oversight capabilities
for data pipeline operations. It includes authentication, authorization, audit logging,
and interactive decision points.

Classes:
    SecurityManager: Central security management
    AccessControl: Role-based access control
    AuditLogger: Security audit logging
    HITLDecision: Human-in-the-loop decision point
    SecurityPolicy: Security policy enforcement
    ThreatDetector: Detect security threats and anomalies

Functions:
    authenticate_user: User authentication
    authorize_action: Action authorization
    require_human_approval: Request human approval for actions
    log_security_event: Log security-related events

Example:
    ```python
    from agentic_data_scraper.security import (
        SecurityManager, HITLDecision, require_human_approval
    )
    
    # Initialize security manager
    security = SecurityManager()
    
    # Require human approval for sensitive operations
    approval = require_human_approval(
        action="scrape_sensitive_data",
        justification="Required for compliance analysis",
        approver_role="data_steward"
    )
    
    if approval.approved:
        # Proceed with operation
        pass
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .security_manager import SecurityManager
    from .access_control import AccessControl
    from .audit_logger import AuditLogger
    from .hitl_decision import HITLDecision
    from .security_policy import SecurityPolicy
    from .threat_detector import ThreatDetector

__all__ = [
    "SecurityManager",
    "AccessControl",
    "AuditLogger",
    "HITLDecision",
    "SecurityPolicy",
    "ThreatDetector",
    "authenticate_user",
    "authorize_action", 
    "require_human_approval",
    "log_security_event",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "SecurityManager":
        from .security_manager import SecurityManager
        return SecurityManager
    elif name == "AccessControl":
        from .access_control import AccessControl
        return AccessControl
    elif name == "AuditLogger":
        from .audit_logger import AuditLogger
        return AuditLogger
    elif name == "HITLDecision":
        from .hitl_decision import HITLDecision
        return HITLDecision
    elif name == "SecurityPolicy":
        from .security_policy import SecurityPolicy
        return SecurityPolicy
    elif name == "ThreatDetector":
        from .threat_detector import ThreatDetector
        return ThreatDetector
    elif name == "authenticate_user":
        from .auth import authenticate_user
        return authenticate_user
    elif name == "authorize_action":
        from .auth import authorize_action
        return authorize_action
    elif name == "require_human_approval":
        from .hitl import require_human_approval
        return require_human_approval
    elif name == "log_security_event":
        from .audit_logger import log_security_event
        return log_security_event
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")