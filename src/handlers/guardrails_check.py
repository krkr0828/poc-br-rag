"""
Guardrails Check Handler

Step Functions task Lambda - checks input query with Bedrock Guardrails.
"""

from typing import Dict, Any

from src.services.guardrails_service import GuardrailsService
from src.utils.logger import get_logger
from src.utils.error_handler import GuardrailsError
from src.config.settings import settings

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Guardrails check Lambda handler for Step Functions

    Args:
        event: Step Functions input with 'query', 'request_id'
        context: Lambda context

    Returns:
        Event with added 'guardrails_passed' and 'guardrails_reason' fields

    Raises:
        GuardrailsError: If guardrails check fails or content is blocked
    """
    query = event["query"]
    request_id = event["request_id"]

    logger.info(
        "Checking query with guardrails",
        extra={"request_id": request_id, "query_length": len(query)},
    )

    try:
        guardrails_service = GuardrailsService(
            settings.GUARDRAILS_ID, settings.GUARDRAILS_VERSION
        )

        result = guardrails_service.check_content(query, check_type="input")

        if not result["passed"]:
            logger.warning(
                "Query blocked by guardrails",
                extra={
                    "request_id": request_id,
                    "reason": result.get("reason", "Unknown"),
                },
            )
            raise GuardrailsError(
                f"Query blocked by content policy: {result.get('reason', 'Content blocked')}"
            )

        logger.info(
            "Query passed guardrails check",
            extra={"request_id": request_id},
        )

        # Add guardrails result to event
        event["guardrails_passed"] = True
        event["guardrails_action"] = result["action"]

        return event

    except GuardrailsError:
        # Re-raise to fail the Step Functions execution
        raise

    except Exception as e:
        logger.error(
            f"Guardrails check error: {e}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        raise GuardrailsError(f"Guardrails check failed: {str(e)}")
