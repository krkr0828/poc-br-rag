# Main Terraform configuration
# Resources will be added in subsequent tasks

# This file serves as the entry point for the Terraform configuration
# Individual resource types are defined in separate files:
# - dynamodb.tf: DynamoDB table for caching
# - s3.tf: S3 bucket for PDF documents
# - iam.tf: IAM roles and policies
# - cloudwatch.tf: CloudWatch Log Groups
# - knowledge_base.tf: Bedrock Knowledge Base
# - guardrails.tf: Bedrock Guardrails
# - lambda.tf: Lambda functions
# - step_functions.tf: Step Functions state machine
# - api_gateway.tf: API Gateway REST API
