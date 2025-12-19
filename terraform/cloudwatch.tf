/**
 * CloudWatch Log Groups
 *
 * Pre-create log groups with retention policies
 */

# Lambda function log groups
resource "aws_cloudwatch_log_group" "lambda_api_handler" {
  name              = "/aws/lambda/${var.project_name}-api-handler-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-api-handler-logs"
  }
}

resource "aws_cloudwatch_log_group" "lambda_guardrails_check" {
  name              = "/aws/lambda/${var.project_name}-guardrails-check-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-guardrails-check-logs"
  }
}

resource "aws_cloudwatch_log_group" "lambda_kb_query" {
  name              = "/aws/lambda/${var.project_name}-kb-query-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-kb-query-logs"
  }
}

resource "aws_cloudwatch_log_group" "lambda_bedrock_invoke" {
  name              = "/aws/lambda/${var.project_name}-bedrock-invoke-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-bedrock-invoke-logs"
  }
}

resource "aws_cloudwatch_log_group" "lambda_cache_response" {
  name              = "/aws/lambda/${var.project_name}-cache-response-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-cache-response-logs"
  }
}

# Step Functions log group
resource "aws_cloudwatch_log_group" "step_functions" {
  name              = "/aws/vendedlogs/states/${var.project_name}-rag-workflow-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-step-functions-logs"
  }
}

# CloudWatch Logs Resource Policy for Step Functions
resource "aws_cloudwatch_log_resource_policy" "step_functions_logging" {
  policy_name = "${var.project_name}-step-functions-logging-${var.environment}"

  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "delivery.logs.amazonaws.com"
        }
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.step_functions.arn}:*"
      }
    ]
  })
}

# ==============================================================================
# Outputs
# ==============================================================================

output "log_group_names" {
  description = "CloudWatch log group names"
  value = {
    api_handler       = aws_cloudwatch_log_group.lambda_api_handler.name
    guardrails_check  = aws_cloudwatch_log_group.lambda_guardrails_check.name
    kb_query          = aws_cloudwatch_log_group.lambda_kb_query.name
    bedrock_invoke    = aws_cloudwatch_log_group.lambda_bedrock_invoke.name
    cache_response    = aws_cloudwatch_log_group.lambda_cache_response.name
    step_functions    = aws_cloudwatch_log_group.step_functions.name
  }
}
