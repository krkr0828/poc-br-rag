"""
Bedrock Knowledge Base Service

Handles all Knowledge Base API calls for document retrieval (RAG).
"""

from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError

from src.utils.logger import get_logger
from src.utils.error_handler import KnowledgeBaseError

logger = get_logger(__name__)


class KnowledgeBaseService:
    """Service for Bedrock Knowledge Base document retrieval"""

    def __init__(self, kb_id: str):
        """
        Initialize KnowledgeBaseService

        Args:
            kb_id: Knowledge Base ID
        """
        self.kb_id = kb_id
        self.client = boto3.client("bedrock-agent-runtime")
        logger.info(f"KnowledgeBaseService initialized", extra={"kb_id": kb_id})

    def retrieve(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from Knowledge Base

        Args:
            query: Search query
            max_results: Maximum number of results to return (default: 5)

        Returns:
            List of result dictionaries with keys:
                - text: Retrieved text content
                - score: Relevance score
                - metadata: Document metadata (title, uri, etc.)

        Raises:
            KnowledgeBaseError: If API call fails
        """
        try:
            response = self.client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": max_results}
                },
            )

            results = response.get("retrievalResults", [])

            logger.info(
                f"Knowledge Base query completed",
                extra={
                    "kb_id": self.kb_id,
                    "query": query[:100],
                    "results_count": len(results),
                },
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "text": result.get("content", {}).get("text", ""),
                    "score": result.get("score", 0.0),
                    "metadata": result.get("metadata", {}),
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            logger.error(
                f"Knowledge Base API error: {error_code} - {error_message}",
                extra={"kb_id": self.kb_id, "query": query[:100]},
            )
            raise KnowledgeBaseError(f"Knowledge Base query failed: {error_message}")

    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieved results into context string

        Args:
            results: List of retrieval results

        Returns:
            str: Concatenated context string
        """
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            text = result.get("text", "").strip()
            if text:
                # Add source information if available
                metadata = result.get("metadata", {})
                source_info = metadata.get("x-amz-bedrock-kb-source-uri", "Unknown source")

                context_parts.append(f"[Source {i}: {source_info}]\n{text}")

        return "\n\n".join(context_parts)
