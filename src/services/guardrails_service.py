"""
Bedrock Guardrails Service

Handles all Guardrails API calls for content safety checks.
"""

from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

from src.utils.logger import get_logger
from src.utils.error_handler import GuardrailsError

logger = get_logger(__name__)


class GuardrailsService:
    """Service for Bedrock Guardrails content safety checks"""

    def __init__(self, guardrails_id: str, guardrails_version: str = "DRAFT"):
        """
        Initialize GuardrailsService

        Args:
            guardrails_id: Bedrock Guardrails ID
            guardrails_version: Guardrails version (default: DRAFT)
        """
        self.guardrails_id = guardrails_id
        self.guardrails_version = guardrails_version
        self.client = boto3.client("bedrock-runtime")
        logger.info(
            f"GuardrailsService initialized",
            extra={"guardrails_id": guardrails_id, "version": guardrails_version},
        )

    def check_content(self, text: str, check_type: str) -> Dict[str, Any]:
        """
        Check content with Guardrails

        Args:
            text: Content to check
            check_type: "input" or "output"

        Returns:
            Dict with keys:
                - passed: bool (True if content is safe)
                - action: str ("PASSED" or "BLOCKED")
                - reason: str (optional, why content was blocked)

        Raises:
            GuardrailsError: If API call fails
        """
        if check_type not in ["input", "output"]:
            raise ValueError(f"Invalid check_type: {check_type}. Must be 'input' or 'output'")

        try:
            response = self.client.apply_guardrail(
                guardrailIdentifier=self.guardrails_id,
                guardrailVersion=self.guardrails_version,
                source=check_type.upper(),
                content=[{"text": {"text": text}}],
            )

            result = self._parse_guardrails_response(response)

            logger.info(
                f"Guardrails check completed",
                extra={
                    "check_type": check_type,
                    "action": result["action"],
                    "text_length": len(text),
                },
            )

            return result

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            logger.error(
                f"Guardrails API error: {error_code} - {error_message}",
                extra={"check_type": check_type},
            )
            raise GuardrailsError(f"Guardrails check failed: {error_message}")

    def _parse_guardrails_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Guardrails API response

        Args:
            response: Raw API response

        Returns:
            Dict with passed, action, and optional reason
        """
        action = response.get("action", "NONE")
        # NONE means no intervention (content is safe)
        # GUARDRAIL_INTERVENED means content was blocked
        passed = action == "NONE"

        # If blocked, try to extract reason
        reason = None
        if not passed:
            assessments = response.get("assessments", [])
            if assessments:
                # Collect all blocked reasons
                reasons = []
                for assessment in assessments:
                    if assessment.get("topicPolicy"):
                        reasons.append("Topic policy violation")
                    if assessment.get("contentPolicy"):
                        reasons.append("Content policy violation")
                    if assessment.get("wordPolicy"):
                        reasons.append("Word policy violation")
                    if assessment.get("sensitiveInformationPolicy"):
                        reasons.append("PII detected")

                reason = "; ".join(reasons) if reasons else "Content blocked by guardrails"

        return {"passed": passed, "action": action, "reason": reason}
