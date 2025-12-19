"""
Bedrock Invoke Handler

Step Functions task Lambda - invokes Bedrock model to generate answer.
"""

from typing import Dict, Any

from src.services.bedrock_service import BedrockService
from src.services.guardrails_service import GuardrailsService
from src.utils.logger import get_logger
from src.utils.error_handler import BedrockError, GuardrailsError
from src.config.settings import settings
from src.config.prompts import build_rag_prompt

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Bedrock model invocation Lambda handler for Step Functions

    Args:
        event: Step Functions input with 'query', 'context', 'request_id'
        context: Lambda context

    Returns:
        Event with added 'answer', 'tokens_used', 'stop_reason' fields

    Raises:
        BedrockError: If Bedrock invocation fails
        GuardrailsError: If output guardrails check fails
    """
    query = event["query"]
    context_text = event["context"]
    request_id = event["request_id"]

    logger.info(
        "Invoking Bedrock model",
        extra={
            "request_id": request_id,
            "query_length": len(query),
            "context_length": len(context_text),
        },
    )

    try:
        # Build prompt
        prompt = build_rag_prompt(query, context_text)

        # Invoke Bedrock
        bedrock_service = BedrockService(settings.MODEL_ID)
        result = bedrock_service.invoke_model(prompt, max_tokens=settings.MAX_TOKENS)

        answer = result["answer"]

        logger.info(
            "Bedrock invocation completed",
            extra={
                "request_id": request_id,
                "tokens_used": result["tokens_used"],
                "stop_reason": result["stop_reason"],
                "answer_length": len(answer),
            },
        )

        # Check output with guardrails
        guardrails_service = GuardrailsService(
            settings.GUARDRAILS_ID, settings.GUARDRAILS_VERSION
        )

        guardrails_result = guardrails_service.check_content(
            answer, check_type="output"
        )

        if not guardrails_result["passed"]:
            logger.warning(
                "Answer blocked by output guardrails",
                extra={
                    "request_id": request_id,
                    "reason": guardrails_result.get("reason", "Unknown"),
                },
            )
            raise GuardrailsError(
                f"Generated answer blocked by content policy: {guardrails_result.get('reason', 'Content blocked')}"
            )

        # Add result to event
        event["answer"] = answer
        event["tokens_used"] = result["tokens_used"]
        event["stop_reason"] = result["stop_reason"]
        event["output_guardrails_passed"] = True

        return event

    except (BedrockError, GuardrailsError):
        # Re-raise to fail the Step Functions execution
        raise

    except Exception as e:
        logger.error(
            f"Bedrock invocation error: {e}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        raise BedrockError(f"Bedrock invocation failed: {str(e)}")
