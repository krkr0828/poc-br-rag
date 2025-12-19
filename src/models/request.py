"""
API Request models
"""

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    """
    API request model for query endpoint

    Attributes:
        query: User query string (1-1000 characters)
    """

    query: str = Field(..., min_length=1, max_length=1000, description="User query")

    @field_validator("query")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        """Validate query is not empty or whitespace only"""
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"query": "What is Amazon Bedrock?"},
                {"query": "How do I use Knowledge Bases with RAG?"},
            ]
        }
    }
