"""
API Handler

API Gateway Lambda handler - entry point for the RAG system.
Validates input, checks cache, and initiates Step Functions execution.
"""

import json
import time
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

from src.models.request import QueryRequest
from src.models.response import QueryResponse, ErrorResponse
from src.utils.logger import get_logger
from src.utils.error_handler import ValidationError, error_response, success_response
from src.utils.validators import validate_query
from src.services.cache_service import CacheService
from src.config.settings import settings

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gateway Lambda handler

    Args:
        event: API Gateway event with 'body' containing QueryRequest JSON
        context: Lambda context

    Returns:
        API Gateway response with status code and body
    """
    start_time = time.time()
    request_id = getattr(context, "aws_request_id", "unknown-request")

    try:
        # Parse and validate request
        logger.info("Processing API request", extra={"request_id": request_id})

        body = json.loads(event.get("body", "{}"))
        request = QueryRequest(**body)

        # Validate query
        sanitized_query = validate_query(request.query)

        # Check cache if enabled
        if settings.CACHE_ENABLED:
            cache_service = CacheService(settings.CACHE_TABLE_NAME)
            cached_result = cache_service.get(sanitized_query)

            if cached_result:
                execution_time_ms = int((time.time() - start_time) * 1000)
                logger.info(
                    "Returning cached response",
                    extra={
                        "request_id": request_id,
                        "execution_time_ms": execution_time_ms,
                    },
                )

                response = QueryResponse(
                    query=sanitized_query,
                    answer=cached_result.get("answer", ""),
                    sources=cached_result.get("sources", []),
                    cached=True,
                    execution_time_ms=execution_time_ms,
                )

                return success_response(response.model_dump())

        # Start Step Functions execution
        sfn_client = boto3.client("stepfunctions")
        state_machine_arn = settings.STATE_MACHINE_ARN

        execution_input = {
            "query": sanitized_query,
            "request_id": request_id,
            "start_time": start_time,
        }

        try:
            sfn_response = sfn_client.start_execution(
                stateMachineArn=state_machine_arn,
                input=json.dumps(execution_input),
            )

            execution_arn = sfn_response["executionArn"]

            logger.info(
                "Started Step Functions execution",
                extra={"request_id": request_id, "execution_arn": execution_arn},
            )

            # Wait for execution to complete (with timeout)
            execution_result = _wait_for_execution(
                sfn_client, execution_arn, timeout_seconds=30
            )

            if execution_result["status"] == "SUCCEEDED":
                output = json.loads(execution_result["output"])

                execution_time_ms = int((time.time() - start_time) * 1000)

                response = QueryResponse(
                    query=sanitized_query,
                    answer=output.get("answer", ""),
                    sources=output.get("sources", []),
                    cached=False,
                    execution_time_ms=execution_time_ms,
                )

                return success_response(response.model_dump())

            else:
                exec_error = execution_result.get("error")
                exec_cause = execution_result.get("cause")
                logger.error(
                    "Step Functions execution failed",
                    extra={
                        "request_id": request_id,
                        "status": execution_result["status"],
                        "error": exec_error,
                    },
                )
                if exec_error == "GuardrailsBlocked":
                    return error_response(
                        error_code="guardrails_blocked",
                        message="Content blocked by safety guidelines",
                        request_id=request_id,
                        status_code=400,
                    )
                return error_response(
                    error_code="workflow_failed",
                    message="Query processing failed",
                    request_id=request_id,
                    status_code=500,
                )

        except ClientError as e:
            logger.error(
                f"Step Functions error: {e}",
                extra={"request_id": request_id},
            )
            return error_response(
                error_code="workflow_start_failed",
                message="Failed to start query processing",
                request_id=request_id,
                status_code=500,
            )

    except ValidationError as e:
        logger.warning(f"Validation error: {e}", extra={"request_id": request_id})
        return error_response(
            error_code="validation_error",
            message=str(e),
            request_id=request_id,
            status_code=400,
        )

    except json.JSONDecodeError:
        logger.warning("Invalid JSON in request body", extra={"request_id": request_id})
        return error_response(
            error_code="invalid_json",
            message="Invalid JSON in request body",
            request_id=request_id,
            status_code=400,
        )

    except Exception as e:
        logger.error(
            f"Unexpected error: {e}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        return error_response(
            error_code="internal_error",
            message="Internal server error",
            request_id=request_id,
            status_code=500,
        )


def _wait_for_execution(
    sfn_client, execution_arn: str, timeout_seconds: int = 30
) -> Dict[str, Any]:
    """
    Wait for Step Functions execution to complete

    Args:
        sfn_client: Step Functions client
        execution_arn: Execution ARN
        timeout_seconds: Maximum time to wait

    Returns:
        Dict with status and output
    """
    start = time.time()

    while time.time() - start < timeout_seconds:
        response = sfn_client.describe_execution(executionArn=execution_arn)
        status = response["status"]

        if status in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
            return {
                "status": status,
                "output": response.get("output", "{}"),
                "error": response.get("error"),
                "cause": response.get("cause"),
            }

        time.sleep(0.5)

    return {"status": "TIMEOUT", "output": "{}", "error": "Timeout", "cause": None}
