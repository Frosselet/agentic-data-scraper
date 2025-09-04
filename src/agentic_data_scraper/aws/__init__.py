"""
AWS integration modules for the Agentic Data Scraper.

This module provides comprehensive AWS integration including Lambda deployment,
S3 data storage, Iceberg table management, and other AWS services. It handles
authentication, resource management, and deployment automation.

Classes:
    LambdaManager: Deploy and manage AWS Lambda functions  
    S3Manager: Manage S3 buckets and objects
    IcebergManager: Manage Iceberg tables on AWS
    CloudFormationManager: Infrastructure as code management
    IAMManager: Identity and access management
    MonitoringManager: CloudWatch monitoring and alerting

Functions:
    deploy_lambda: Deploy pipeline as Lambda function
    upload_to_s3: Upload data to S3 buckets
    create_iceberg_table: Create Iceberg tables
    get_aws_credentials: Retrieve AWS credentials

Example:
    ```python
    from agentic_data_scraper.aws import (
        LambdaManager, S3Manager, deploy_lambda
    )
    
    # Deploy pipeline as Lambda
    lambda_manager = LambdaManager()
    deployment = deploy_lambda(
        pipeline_name="web_scraping_pipeline",
        environment="production"
    )
    
    # Upload results to S3
    s3_manager = S3Manager()
    s3_manager.upload_file("data.json", "my-bucket", "results/data.json")
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lambda_manager import LambdaManager
    from .s3_manager import S3Manager
    from .iceberg_manager import IcebergManager
    from .cloudformation_manager import CloudFormationManager
    from .iam_manager import IAMManager
    from .monitoring_manager import MonitoringManager

__all__ = [
    "LambdaManager",
    "S3Manager", 
    "IcebergManager",
    "CloudFormationManager",
    "IAMManager",
    "MonitoringManager",
    "deploy_lambda",
    "upload_to_s3",
    "create_iceberg_table",
    "get_aws_credentials",
]

def __getattr__(name: str) -> object:
    """Lazy import for performance."""
    if name == "LambdaManager":
        from .lambda_manager import LambdaManager
        return LambdaManager
    elif name == "S3Manager":
        from .s3_manager import S3Manager
        return S3Manager
    elif name == "IcebergManager":
        from .iceberg_manager import IcebergManager
        return IcebergManager
    elif name == "CloudFormationManager":
        from .cloudformation_manager import CloudFormationManager
        return CloudFormationManager
    elif name == "IAMManager":
        from .iam_manager import IAMManager
        return IAMManager
    elif name == "MonitoringManager":
        from .monitoring_manager import MonitoringManager
        return MonitoringManager
    elif name == "deploy_lambda":
        from .deployment import deploy_lambda
        return deploy_lambda
    elif name == "upload_to_s3":
        from .s3_manager import upload_to_s3
        return upload_to_s3
    elif name == "create_iceberg_table":
        from .iceberg_manager import create_iceberg_table
        return create_iceberg_table
    elif name == "get_aws_credentials":
        from .auth import get_aws_credentials
        return get_aws_credentials
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")