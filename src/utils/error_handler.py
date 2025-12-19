"""
Error handling utility

Provides custom exception classes and error response formatting.
"""

from typing import Dict, Any


class BaseError(Exception):
    """Base exception class for all custom exceptions"""

    def __init__(self, message: str, error_code: str = "internal_error"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(BaseError):
    """Raised when input validation fails"""

    def __init__(self, message: str):
        super().__init__(message, error_code="validation_error")


class BedrockError(BaseError):
    """Raised when Bedrock API calls fail"""

    def __init__(self, message: str):
        super().__init__(message, error_code="bedrock_error")


class GuardrailsError(BaseError):
    """Raised when Guardrails API calls fail"""

    def __init__(self, message: str):
        super().__init__(message, error_code="guardrails_error")


class CacheError(BaseError):
    """Raised when cache operations fail"""

    def __init__(self, message: str):
        super().__init__(message, error_code="cache_error")


class KnowledgeBaseError(BaseError):
    """Raised when Knowledge Base API calls fail"""

    def __init__(self, message: str):
        super().__init__(message, error_code="knowledge_base_error")


def error_response(
    error_code: str, message: str, request_id: str, status_code: int = 500
) -> Dict[str, Any]:
    """
    Create standardized error response

    Args:
        error_code: Error code identifier
        message: Human-readable error message
        request_id: Request ID for tracking
        status_code: HTTP status code (default: 500)

    Returns:
        Dict containing API Gateway Proxy response format

    Example:
        >>> error_response("validation_error", "Query is empty", "req-123", 400)
        {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"error": "validation_error", "message": "Query is empty", ...}'
        }
    """
    import json

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {"error": error_code, "message": message, "request_id": request_id}
        ),
    }


def success_response(data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """
    Create standardized success response

    Args:
        data: Response data dictionary
        status_code: HTTP status code (default: 200)

    Returns:
        Dict containing API Gateway Proxy response format

    Example:
        >>> success_response({"answer": "Hello", "cached": False})
        {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"answer": "Hello", "cached": false}'
        }
    """
    import json

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data),
    }
