"""
Input validation utility

Provides validation functions for user inputs.
"""

from src.utils.error_handler import ValidationError


def validate_query(query: str) -> str:
    """
    Validate and sanitize query input

    Args:
        query: User query string

    Returns:
        str: Sanitized query string (whitespace trimmed)

    Raises:
        ValidationError: If query is empty, whitespace-only, or too long

    Validation rules:
    - Must not be empty or whitespace-only
    - Must not exceed 1000 characters

    Example:
        >>> validate_query("  What is AWS Bedrock?  ")
        "What is AWS Bedrock?"
        >>> validate_query("")
        ValidationError: Query cannot be empty
    """
    if not query or not isinstance(query, str):
        raise ValidationError("Query must be a non-empty string")

    # Strip whitespace
    sanitized_query = query.strip()

    # Check if empty after stripping
    if not sanitized_query:
        raise ValidationError("Query cannot be empty or whitespace only")

    # Check length
    if len(sanitized_query) > 1000:
        raise ValidationError(
            f"Query is too long ({len(sanitized_query)} characters). Maximum is 1000 characters"
        )

    return sanitized_query
