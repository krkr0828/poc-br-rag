"""
DynamoDB Cache Service

Handles all cache operations for query responses.
"""

import hashlib
import time
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Service for managing DynamoDB cache operations"""

    def __init__(self, table_name: str):
        """
        Initialize CacheService

        Args:
            table_name: DynamoDB table name
        """
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        logger.info(f"CacheService initialized with table: {table_name}")

    def _generate_cache_key(self, query: str) -> str:
        """
        Generate SHA-256 hash for query

        Args:
            query: Query string

        Returns:
            str: SHA-256 hash hex string
        """
        return hashlib.sha256(query.encode("utf-8")).hexdigest()

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response for query

        Args:
            query: Query string

        Returns:
            Optional[Dict]: Cached data if exists and not expired, None otherwise
        """
        cache_key = self._generate_cache_key(query)

        try:
            response = self.table.get_item(Key={"query_hash": cache_key})

            if "Item" in response:
                item = response["Item"]

                # Check if TTL has expired (DynamoDB TTL is eventually consistent)
                current_time = int(time.time())
                if item.get("ttl", 0) > current_time:
                    logger.info(
                        "Cache hit",
                        extra={"query_hash": cache_key, "query": query[:50]},
                    )
                    return item
                else:
                    logger.info(
                        "Cache expired",
                        extra={"query_hash": cache_key, "ttl": item.get("ttl")},
                    )
                    return None
            else:
                logger.info("Cache miss", extra={"query_hash": cache_key})
                return None

        except ClientError as e:
            logger.error(
                f"DynamoDB get_item failed: {e}", extra={"query_hash": cache_key}
            )
            # Return None on error - cache is best-effort
            return None

    def put(
        self, query: str, data: Dict[str, Any], ttl_seconds: int = 86400
    ) -> bool:
        """
        Cache response data

        Args:
            query: Query string
            data: Response data to cache (answer, sources, execution_time_ms)
            ttl_seconds: Time-to-live in seconds (default: 24 hours)

        Returns:
            bool: True if successful, False otherwise
        """
        cache_key = self._generate_cache_key(query)
        current_time = int(time.time())
        ttl = current_time + ttl_seconds

        cache_item = {
            "query_hash": cache_key,
            "query_text": query,
            "answer": data.get("answer", ""),
            "sources": data.get("sources", []),
            "cached_at": current_time,
            "ttl": ttl,
            "execution_time_ms": data.get("execution_time_ms", 0),
        }

        try:
            self.table.put_item(Item=cache_item)
            logger.info(
                "Cached response",
                extra={"query_hash": cache_key, "ttl": ttl, "query": query[:50]},
            )
            return True

        except ClientError as e:
            logger.error(
                f"DynamoDB put_item failed: {e}", extra={"query_hash": cache_key}
            )
            # Don't fail the request if caching fails
            return False
