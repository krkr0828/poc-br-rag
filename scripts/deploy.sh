#!/bin/bash

#
# Deploy Script
#
# Packages Lambda functions and deploys infrastructure with Terraform
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==================================="
echo "Bedrock RAG System Deployment"
echo "==================================="
echo ""

# Check prerequisites
echo "[1/4] Checking prerequisites..."

if [ ! -f "terraform/terraform.tfvars" ]; then
    echo "ERROR: terraform/terraform.tfvars not found!"
    echo "Please create it from terraform.tfvars.example and set Knowledge Base ID and Guardrails ID"
    echo "See SETUP.md for instructions"
    exit 1
fi

# Package Lambda functions
echo "[2/4] Packaging Lambda functions..."
./scripts/package_lambdas.sh

# Initialize Terraform (if needed)
echo "[3/4] Initializing Terraform..."
cd terraform
if [ ! -d ".terraform" ]; then
    terraform init
fi

# Apply infrastructure
echo "[4/4] Deploying infrastructure..."
terraform apply

cd "$PROJECT_ROOT"

echo ""
echo "==================================="
echo "Deployment complete!"
echo "==================================="
echo ""
echo "API Endpoint:"
terraform -chdir=terraform output -raw api_gateway_url
echo ""
echo ""
echo "Test with:"
echo "./scripts/test_api.sh \"What is AWS Bedrock?\""
echo ""
