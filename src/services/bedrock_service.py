"""
Bedrock Runtime Service

Handles all Bedrock model invocation for answer generation.
"""

import json
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

from src.utils.logger import get_logger
from src.utils.error_handler import BedrockError

logger = get_logger(__name__)


class BedrockService:
    """Service for Bedrock model invocation"""

    def __init__(self, model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"):
        """
        Initialize BedrockService

        Args:
            model_id: Bedrock model ID (default: Claude 3 Haiku)
        """
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime")
        logger.info(f"BedrockService initialized", extra={"model_id": model_id})

    def invoke_model(self, prompt: str, max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Invoke Bedrock model to generate response

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (default: 1024)

        Returns:
            Dict with keys:
                - answer: Generated text
                - tokens_used: Number of tokens used
                - stop_reason: Why generation stopped

        Raises:
            BedrockError: If API call fails
        """
        request_body = self._build_request_body(prompt, max_tokens)

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=request_body,
                contentType="application/json",
                accept="application/json",
            )

            result = self._parse_response(response)

            logger.info(
                f"Bedrock invocation completed",
                extra={
                    "model_id": self.model_id,
                    "tokens_used": result.get("tokens_used", 0),
                    "stop_reason": result.get("stop_reason", ""),
                },
            )

            return result

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            logger.error(
                f"Bedrock API error: {error_code} - {error_message}",
                extra={"model_id": self.model_id},
            )
            raise BedrockError(f"Bedrock invocation failed: {error_message}")

    def _build_request_body(self, prompt: str, max_tokens: int) -> str:
        """
        Build request body for Claude 3 model

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens

        Returns:
            str: JSON request body
        """
        request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ],
                }
            ],
        }

        return json.dumps(request)

    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Bedrock API response

        Args:
            response: Raw API response

        Returns:
            Dict with answer, tokens_used, stop_reason
        """
        # Read response body
        response_body = json.loads(response["body"].read())

        # Extract answer text from content blocks
        content = response_body.get("content", [])
        answer = ""
        if content:
            # Claude 3 returns content as list of blocks
            for block in content:
                if block.get("type") == "text":
                    answer += block.get("text", "")

        # Extract usage information
        usage = response_body.get("usage", {})
        tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)

        stop_reason = response_body.get("stop_reason", "end_turn")

        return {
            "answer": answer.strip(),
            "tokens_used": tokens_used,
            "stop_reason": stop_reason,
        }
