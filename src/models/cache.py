"""
Cache data models
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class CacheItem(BaseModel):
    """
    DynamoDB cache item model

    Attributes:
        query_hash: SHA-256 hash of query (partition key)
        query_text: Original query text
        answer: Generated answer
        sources: List of source documents
        cached_at: Unix timestamp when cached
        ttl: DynamoDB TTL attribute (Unix timestamp)
        execution_time_ms: Original execution time
    """

    query_hash: str = Field(..., description="SHA-256 hash of query")
    query_text: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="Source documents"
    )
    cached_at: int = Field(..., description="Cache timestamp (Unix)")
    ttl: int = Field(..., description="DynamoDB TTL (Unix)")
    execution_time_ms: int = Field(..., description="Execution time in ms")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query_hash": "a1b2c3d4e5...",
                    "query_text": "What is Amazon Bedrock?",
                    "answer": "Amazon Bedrock is...",
                    "sources": [{"title": "guide.pdf", "page": 5}],
                    "cached_at": 1734422400,
                    "ttl": 1734508800,
                    "execution_time_ms": 3456,
                }
            ]
        }
    }
