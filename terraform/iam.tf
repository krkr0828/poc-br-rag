/**
 * IAM Roles and Policies
 *
 * Separate roles for API Gateway Lambda and Step Functions task Lambdas
 */

# ==============================================================================
# Lambda Execution Role (for all Lambda functions)
# ==============================================================================

resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-execution-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-execution-${var.environment}"
  }
}

# CloudWatch Logs permissions
resource "aws_iam_role_policy" "lambda_logging" {
  name = "lambda-logging"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.project_name}-*:*"
      }
    ]
  })
}

# DynamoDB permissions for cache access
resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "lambda-dynamodb"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.cache.arn
      }
    ]
  })
}

# Bedrock permissions
resource "aws_iam_role_policy" "lambda_bedrock" {
  name = "lambda-bedrock"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:ApplyGuardrail"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
          "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:guardrail/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:Retrieve"
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:knowledge-base/*"
      }
    ]
  })
}

# ==============================================================================
# API Handler Lambda Role (additional Step Functions permissions)
# ==============================================================================

resource "aws_iam_role_policy" "api_handler_step_functions" {
  name = "api-handler-step-functions"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution"
        ]
        Resource = "arn:aws:states:${var.aws_region}:${data.aws_caller_identity.current.account_id}:stateMachine:${var.project_name}-*"
      },
      {
        Effect = "Allow"
        Action = [
          "states:DescribeExecution"
        ]
        Resource = "arn:aws:states:${var.aws_region}:${data.aws_caller_identity.current.account_id}:execution:${var.project_name}-*:*"
      }
    ]
  })
}

# ==============================================================================
# Step Functions Execution Role
# ==============================================================================

resource "aws_iam_role" "step_functions_execution" {
  name = "${var.project_name}-step-functions-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-step-functions-${var.environment}"
  }
}

# Step Functions permissions to invoke Lambda functions
resource "aws_iam_role_policy" "step_functions_lambda" {
  name = "step-functions-lambda"
  role = aws_iam_role.step_functions_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-*"
      }
    ]
  })
}

# Step Functions CloudWatch Logs permissions
resource "aws_iam_role_policy" "step_functions_logging" {
  name = "step-functions-logging"
  role = aws_iam_role.step_functions_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
      }
    ]
  })
}

# ==============================================================================
# Outputs
# ==============================================================================

output "lambda_execution_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_execution.arn
}

output "step_functions_execution_role_arn" {
  description = "Step Functions execution role ARN"
  value       = aws_iam_role.step_functions_execution.arn
}
