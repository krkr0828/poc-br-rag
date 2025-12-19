variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-northeast-1" # Tokyo
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "bedrock-rag"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention period in days"
  type        = number
  default     = 30
}

variable "cache_ttl_seconds" {
  description = "DynamoDB cache TTL in seconds"
  type        = number
  default     = 86400 # 24 hours
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID (created manually in AWS Console)"
  type        = string
  default     = ""
}

variable "guardrails_id" {
  description = "Bedrock Guardrails ID (created manually in AWS Console)"
  type        = string
  default     = ""
}
