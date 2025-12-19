"""
API Response models
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    """
    Source document information

    Attributes:
        title: Document title or filename
        page: Page number (if available)
        uri: Document URI (if available)
    """

    title: str = Field(..., description="Document title")
    page: Optional[int] = Field(None, description="Page number")
    uri: Optional[str] = Field(None, description="Document URI")
    score: Optional[float] = Field(None, description="Relevance score from KB")


class QueryResponse(BaseModel):
    """
    Successful API response model

    Attributes:
        query: Original user query
        answer: Generated answer from Bedrock
        sources: List of source documents used
        cached: Whether response was served from cache
        execution_time_ms: Total execution time in milliseconds
    """

    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source documents")
    cached: bool = Field(False, description="Whether response was cached")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What is Amazon Bedrock?",
                    "answer": "Amazon Bedrock is a fully managed service...",
                    "sources": [
                        {
                            "title": "bedrock-guide.pdf",
                            "page": 5,
                            "uri": "s3://...",
                            "score": 0.92,
                        }
                    ],
                    "cached": False,
                    "execution_time_ms": 3456,
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """
    Error API response model

    Attributes:
        error: Error code identifier
        message: Human-readable error message
        request_id: Request ID for tracking
    """

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "validation_error",
                    "message": "Query cannot be empty",
                    "request_id": "req-abc123",
                }
            ]
        }
    }
