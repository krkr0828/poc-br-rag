"""
Application Settings

Loads all configuration from environment variables.
"""

import os
from typing import Optional


class Settings:
    """Application configuration loaded from environment variables"""

    # AWS Region
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-1")

    # Bedrock Configuration
    MODEL_ID: str = os.getenv(
        "MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"
    )
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))

    # Knowledge Base Configuration
    KB_ID: str = os.getenv("KB_ID", "")
    KB_MAX_RESULTS: int = int(os.getenv("KB_MAX_RESULTS", "5"))

    # Guardrails Configuration
    GUARDRAILS_ID: str = os.getenv("GUARDRAILS_ID", "")
    GUARDRAILS_VERSION: str = os.getenv("GUARDRAILS_VERSION", "DRAFT")

    # Cache Configuration
    CACHE_TABLE_NAME: str = os.getenv("CACHE_TABLE_NAME", "")
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 24 hours
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    # Step Functions Configuration
    STATE_MACHINE_ARN: str = os.getenv("STATE_MACHINE_ARN", "")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """
        Validate that all required environment variables are set

        Raises:
            ValueError: If required environment variables are missing
        """
        missing = []

        if not cls.KB_ID:
            missing.append("KB_ID")
        if not cls.GUARDRAILS_ID:
            missing.append("GUARDRAILS_ID")
        if not cls.CACHE_TABLE_NAME:
            missing.append("CACHE_TABLE_NAME")
        if not cls.STATE_MACHINE_ARN:
            missing.append("STATE_MACHINE_ARN")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

    @classmethod
    def get_summary(cls) -> dict:
        """
        Get configuration summary (for logging on startup)

        Returns:
            dict: Configuration summary with sensitive values masked
        """
        return {
            "aws_region": cls.AWS_REGION,
            "model_id": cls.MODEL_ID,
            "max_tokens": cls.MAX_TOKENS,
            "kb_id": cls.KB_ID[:8] + "..." if cls.KB_ID else "NOT_SET",
            "kb_max_results": cls.KB_MAX_RESULTS,
            "guardrails_id": cls.GUARDRAILS_ID[:8] + "..."
            if cls.GUARDRAILS_ID
            else "NOT_SET",
            "guardrails_version": cls.GUARDRAILS_VERSION,
            "cache_table_name": cls.CACHE_TABLE_NAME,
            "cache_ttl_seconds": cls.CACHE_TTL_SECONDS,
            "cache_enabled": cls.CACHE_ENABLED,
            "state_machine_arn": cls.STATE_MACHINE_ARN[:20] + "..."
            if cls.STATE_MACHINE_ARN
            else "NOT_SET",
            "log_level": cls.LOG_LEVEL,
        }


# Create singleton instance
settings = Settings()
