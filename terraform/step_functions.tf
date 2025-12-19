/**
 * Step Functions State Machine
 *
 * Orchestrates the RAG workflow:
 * 1. Guardrails check (input)
 * 2. Knowledge Base query
 * 3. Bedrock invoke (with output guardrails)
 * 4. Cache response
 */

resource "aws_sfn_state_machine" "rag_workflow" {
  name     = "${var.project_name}-rag-workflow-${var.environment}"
  role_arn = aws_iam_role.step_functions_execution.arn

  definition = jsonencode({
    Comment = "RAG workflow with Bedrock, Knowledge Base, and Guardrails"
    StartAt = "GuardrailsCheck"

    States = {
      # Step 1: Check input with Guardrails
      GuardrailsCheck = {
        Type     = "Task"
        Resource = aws_lambda_function.guardrails_check.arn
        Retry = [
          {
            ErrorEquals = [
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["GuardrailsError"]
            ResultPath  = "$.guardrails_error"
            Next        = "GuardrailsBlocked"
          },
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "HandleError"
          }
        ]
        Next = "KnowledgeBaseQuery"
      }

      # Step 2: Query Knowledge Base
      KnowledgeBaseQuery = {
        Type     = "Task"
        Resource = aws_lambda_function.kb_query.arn
        Retry = [
          {
            ErrorEquals = [
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.kb_error"
            Next        = "UseEmptyContext"
          }
        ]
        Next = "BedrockInvoke"
      }

      UseEmptyContext = {
        Type       = "Pass"
        ResultPath = "$"
        Parameters = {
          "query.$"             = "$.query"
          "request_id.$"        = "$.request_id"
          "start_time.$"        = "$.start_time"
          "guardrails_passed.$" = "$.guardrails_passed"
          "guardrails_action.$" = "$.guardrails_action"
          "context"             = ""
          "kb_results"          = []
          "kb_results_count"    = 0
        }
        Next = "BedrockInvoke"
      }

      # Step 3: Invoke Bedrock model (includes output guardrails)
      BedrockInvoke = {
        Type     = "Task"
        Resource = aws_lambda_function.bedrock_invoke.arn
        Retry = [
          {
            ErrorEquals = [
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        Catch = [
          {
            ErrorEquals = ["GuardrailsError"]
            ResultPath  = "$.guardrails_error"
            Next        = "GuardrailsBlocked"
          },
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "HandleError"
          }
        ]
        Next = "CacheResponse"
      }

      # Step 4: Cache response
      CacheResponse = {
        Type     = "Task"
        Resource = aws_lambda_function.cache_response.arn
        Retry = [
          {
            ErrorEquals = [
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException"
            ]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
        # Cache failures are non-critical, continue to success
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.cache_error"
            Next        = "Success"
          }
        ]
        Next = "Success"
      }

      # Success state
      Success = {
        Type = "Succeed"
      }

      GuardrailsBlocked = {
        Type  = "Fail"
        Cause = "Content blocked by guardrails"
        Error = "GuardrailsBlocked"
      }

      # Error handler
      HandleError = {
        Type = "Fail"
        Cause = "Workflow failed"
        Error = "WorkflowExecutionError"
      }
    }
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.step_functions.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  tags = {
    Name = "${var.project_name}-rag-workflow"
  }
}

# ==============================================================================
# Outputs
# ==============================================================================

output "state_machine_arn" {
  description = "Step Functions state machine ARN"
  value       = aws_sfn_state_machine.rag_workflow.arn
}

output "state_machine_name" {
  description = "Step Functions state machine name"
  value       = aws_sfn_state_machine.rag_workflow.name
}
