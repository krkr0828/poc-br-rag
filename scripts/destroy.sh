#!/bin/bash

#
# Destroy Script
#
# Destroys all Terraform-managed infrastructure
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==================================="
echo "Bedrock RAG System Destroy"
echo "==================================="
echo ""
echo "WARNING: This will destroy all infrastructure!"
echo "This action cannot be undone."
echo ""
read -p "Are you sure you want to destroy? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Destroy cancelled."
    exit 0
fi

echo ""
echo "Destroying infrastructure..."
cd terraform
terraform destroy

cd "$PROJECT_ROOT"

echo ""
echo "==================================="
echo "Destruction complete!"
echo "==================================="
echo ""
echo "Manual cleanup required:"
echo "1. Delete Knowledge Base in Bedrock Console"
echo "2. Delete Guardrails in Bedrock Console"
echo "3. Delete OpenSearch Serverless collection (if created)"
echo "4. Delete S3 bucket with Knowledge Base documents"
echo ""
