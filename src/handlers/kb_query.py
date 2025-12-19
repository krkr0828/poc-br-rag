"""
Knowledge Base Query Handler

Step Functions task Lambda - retrieves relevant documents from Knowledge Base.
"""

from typing import Dict, Any

from src.services.kb_service import KnowledgeBaseService
from src.utils.logger import get_logger
from src.utils.error_handler import KnowledgeBaseError
from src.config.settings import settings

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Knowledge Base query Lambda handler for Step Functions

    Args:
        event: Step Functions input with 'query', 'request_id'
        context: Lambda context

    Returns:
        Event with added 'kb_results' and 'context' fields

    Raises:
        KnowledgeBaseError: If Knowledge Base query fails
    """
    query = event["query"]
    request_id = event["request_id"]

    logger.info(
        "Querying Knowledge Base",
        extra={"request_id": request_id, "query_length": len(query)},
    )

    try:
        kb_service = KnowledgeBaseService(settings.KB_ID)

        results = kb_service.retrieve(query, max_results=settings.KB_MAX_RESULTS)

        logger.info(
            "Knowledge Base query completed",
            extra={"request_id": request_id, "results_count": len(results)},
        )

        # Format context from results
        context = _format_context(results)

        # Add results to event
        event["kb_results"] = results
        event["context"] = context
        event["kb_results_count"] = len(results)

        return event

    except KnowledgeBaseError:
        # Re-raise to fail the Step Functions execution
        raise

    except Exception as e:
        logger.error(
            f"Knowledge Base query error: {e}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        raise KnowledgeBaseError(f"Knowledge Base query failed: {str(e)}")


def _format_context(results: list[Dict[str, Any]]) -> str:
    """
    Format Knowledge Base results into context string

    Args:
        results: List of KB retrieval results

    Returns:
        str: Formatted context string for prompt
    """
    if not results:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for i, result in enumerate(results, 1):
        text = result.get("text", "").strip()
        if text:
            # Add source information if available
            metadata = result.get("metadata", {})
            source_uri = metadata.get("x-amz-bedrock-kb-source-uri", "Unknown source")

            context_parts.append(f"[Source {i}: {source_uri}]\n{text}")

    return "\n\n".join(context_parts)
