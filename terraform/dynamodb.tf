/**
 * DynamoDB Cache Table
 *
 * On-demand pricing for cost efficiency
 * TTL enabled for automatic expiration
 */

resource "aws_dynamodb_table" "cache" {
  name         = "${var.project_name}-${var.environment}-cache"
  billing_mode = "PAY_PER_REQUEST" # On-demand pricing
  hash_key     = "query_hash"

  attribute {
    name = "query_hash"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = false # Disabled for learning/cost optimization
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cache"
  }
}

output "cache_table_name" {
  description = "DynamoDB cache table name"
  value       = aws_dynamodb_table.cache.name
}

output "cache_table_arn" {
  description = "DynamoDB cache table ARN"
  value       = aws_dynamodb_table.cache.arn
}
