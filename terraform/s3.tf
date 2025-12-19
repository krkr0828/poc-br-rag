/**
 * S3 Bucket for Lambda Deployment Packages
 *
 * Stores Lambda function deployment packages (.zip files)
 */

resource "aws_s3_bucket" "lambda_deployments" {
  bucket = "${var.project_name}-lambda-deployments-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.project_name}-lambda-deployments-${var.environment}"
  }
}

resource "aws_s3_bucket_versioning" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

/**
 * S3 Bucket for Knowledge Base documents
 */

resource "aws_s3_bucket" "documents" {
  bucket        = "${var.project_name}-${var.environment}-documents"
  force_destroy = true

  tags = {
    Name = "${var.project_name}-${var.environment}-documents"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "lambda_deployment_bucket_name" {
  description = "S3 bucket name for Lambda deployments"
  value       = aws_s3_bucket.lambda_deployments.bucket
}

output "lambda_deployment_bucket_arn" {
  description = "S3 bucket ARN for Lambda deployments"
  value       = aws_s3_bucket.lambda_deployments.arn
}

output "documents_bucket_name" {
  description = "S3 bucket for Knowledge Base documents"
  value       = aws_s3_bucket.documents.bucket
}

output "documents_bucket_arn" {
  description = "S3 bucket ARN for Knowledge Base documents"
  value       = aws_s3_bucket.documents.arn
}
