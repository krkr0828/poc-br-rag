"""
Cache Response Handler

Step Functions task Lambda - caches successful query response in DynamoDB.
"""

import time
from typing import Dict, Any

from src.services.cache_service import CacheService
from src.models.response import Source
from src.utils.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Cache response Lambda handler for Step Functions

    Args:
        event: Step Functions input with 'query', 'answer', 'kb_results', etc.
        context: Lambda context

    Returns:
        Event with added 'sources' and 'cached' fields
    """
    query = event["query"]
    answer = event["answer"]
    kb_results = event.get("kb_results", [])
    request_id = event["request_id"]
    start_time = event.get("start_time", time.time())

    logger.info(
        "Caching response",
        extra={"request_id": request_id, "cache_enabled": settings.CACHE_ENABLED},
    )

    try:
        # Format sources from KB results
        sources = []
        for result in kb_results:
            metadata = result.get("metadata", {})
            source = Source(
                uri=metadata.get("x-amz-bedrock-kb-source-uri", ""),
                title=metadata.get("x-amz-bedrock-kb-source-title", ""),
                score=result.get("score", 0.0),
            )
            sources.append(source.model_dump())

        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Prepare response data
        response_data = {
            "answer": answer,
            "sources": sources,
            "execution_time_ms": execution_time_ms,
        }

        # Cache if enabled
        if settings.CACHE_ENABLED:
            cache_service = CacheService(settings.CACHE_TABLE_NAME)
            cache_success = cache_service.put(
                query, response_data, ttl_seconds=settings.CACHE_TTL_SECONDS
            )

            if cache_success:
                logger.info("Response cached successfully", extra={"request_id": request_id})
            else:
                logger.warning(
                    "Failed to cache response (non-critical)",
                    extra={"request_id": request_id},
                )

        # Add final fields to event
        event["sources"] = sources
        event["cached"] = False
        event["execution_time_ms"] = execution_time_ms

        return event

    except Exception as e:
        # Don't fail the execution if caching fails - it's not critical
        logger.error(
            f"Cache error (non-critical): {e}",
            extra={"request_id": request_id},
            exc_info=True,
        )

        # Return event with empty sources if something goes wrong
        event["sources"] = []
        event["cached"] = False
        event["execution_time_ms"] = int((time.time() - start_time) * 1000)

        return event
