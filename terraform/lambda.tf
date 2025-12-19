/**
 * Lambda Functions
 *
 * Defines all Lambda functions for the RAG workflow
 */

# ==============================================================================
# Lambda Deployment Package (placeholder - will be updated after packaging)
# ==============================================================================

# API Handler Lambda
resource "aws_lambda_function" "api_handler" {
  function_name = "${var.project_name}-api-handler-${var.environment}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "src.handlers.api_handler.lambda_handler"
  runtime       = "python3.11"

  # Placeholder - will be updated after packaging
  filename         = "../lambda_deployment.zip"
  source_code_hash = fileexists("../lambda_deployment.zip") ? filebase64sha256("../lambda_deployment.zip") : ""

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      KB_ID               = var.knowledge_base_id
      GUARDRAILS_ID       = var.guardrails_id
      GUARDRAILS_VERSION  = "DRAFT"
      CACHE_TABLE_NAME    = aws_dynamodb_table.cache.name
      STATE_MACHINE_ARN   = aws_sfn_state_machine.rag_workflow.arn
      MODEL_ID            = "anthropic.claude-3-haiku-20240307-v1:0"
      MAX_TOKENS          = "1024"
      KB_MAX_RESULTS      = "5"
      CACHE_TTL_SECONDS   = tostring(var.cache_ttl_seconds)
      CACHE_ENABLED       = "true"
      LOG_LEVEL           = "INFO"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_api_handler,
    aws_sfn_state_machine.rag_workflow
  ]

  tags = {
    Name = "${var.project_name}-api-handler"
  }
}

# Guardrails Check Lambda
resource "aws_lambda_function" "guardrails_check" {
  function_name = "${var.project_name}-guardrails-check-${var.environment}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "src.handlers.guardrails_check.lambda_handler"
  runtime       = "python3.11"

  filename         = "../lambda_deployment.zip"
  source_code_hash = fileexists("../lambda_deployment.zip") ? filebase64sha256("../lambda_deployment.zip") : ""

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      GUARDRAILS_ID      = var.guardrails_id
      GUARDRAILS_VERSION = "DRAFT"
      LOG_LEVEL          = "INFO"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda_guardrails_check]

  tags = {
    Name = "${var.project_name}-guardrails-check"
  }
}

# Knowledge Base Query Lambda
resource "aws_lambda_function" "kb_query" {
  function_name = "${var.project_name}-kb-query-${var.environment}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "src.handlers.kb_query.lambda_handler"
  runtime       = "python3.11"

  filename         = "../lambda_deployment.zip"
  source_code_hash = fileexists("../lambda_deployment.zip") ? filebase64sha256("../lambda_deployment.zip") : ""

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      KB_ID          = var.knowledge_base_id
      KB_MAX_RESULTS = "5"
      LOG_LEVEL      = "INFO"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda_kb_query]

  tags = {
    Name = "${var.project_name}-kb-query"
  }
}

# Bedrock Invoke Lambda
resource "aws_lambda_function" "bedrock_invoke" {
  function_name = "${var.project_name}-bedrock-invoke-${var.environment}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "src.handlers.bedrock_invoke.lambda_handler"
  runtime       = "python3.11"

  filename         = "../lambda_deployment.zip"
  source_code_hash = fileexists("../lambda_deployment.zip") ? filebase64sha256("../lambda_deployment.zip") : ""

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      MODEL_ID           = "anthropic.claude-3-haiku-20240307-v1:0"
      MAX_TOKENS         = "1024"
      GUARDRAILS_ID      = var.guardrails_id
      GUARDRAILS_VERSION = "DRAFT"
      LOG_LEVEL          = "INFO"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda_bedrock_invoke]

  tags = {
    Name = "${var.project_name}-bedrock-invoke"
  }
}

# Cache Response Lambda
resource "aws_lambda_function" "cache_response" {
  function_name = "${var.project_name}-cache-response-${var.environment}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "src.handlers.cache_response.lambda_handler"
  runtime       = "python3.11"

  filename         = "../lambda_deployment.zip"
  source_code_hash = fileexists("../lambda_deployment.zip") ? filebase64sha256("../lambda_deployment.zip") : ""

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      CACHE_TABLE_NAME  = aws_dynamodb_table.cache.name
      CACHE_TTL_SECONDS = tostring(var.cache_ttl_seconds)
      CACHE_ENABLED     = "true"
      LOG_LEVEL         = "INFO"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda_cache_response]

  tags = {
    Name = "${var.project_name}-cache-response"
  }
}

# ==============================================================================
# Outputs
# ==============================================================================

output "lambda_function_arns" {
  description = "Lambda function ARNs"
  value = {
    api_handler       = aws_lambda_function.api_handler.arn
    guardrails_check  = aws_lambda_function.guardrails_check.arn
    kb_query          = aws_lambda_function.kb_query.arn
    bedrock_invoke    = aws_lambda_function.bedrock_invoke.arn
    cache_response    = aws_lambda_function.cache_response.arn
  }
}
