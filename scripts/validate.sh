#!/bin/bash

#
# Validation Script
#
# Validates that all prerequisites are met before deployment
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==================================="
echo "Bedrock RAG System Validation"
echo "==================================="
echo ""

ERRORS=0

# Check AWS CLI
echo "[1/7] Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1)
    echo "✓ AWS CLI installed: $AWS_VERSION"
else
    echo "✗ AWS CLI not found"
    ERRORS=$((ERRORS + 1))
fi

# Check AWS credentials
echo "[2/7] Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region || echo "NOT_SET")
    echo "✓ AWS credentials configured"
    echo "  Account: $AWS_ACCOUNT"
    echo "  Region: $AWS_REGION"
else
    echo "✗ AWS credentials not configured"
    ERRORS=$((ERRORS + 1))
fi

# Check Terraform
echo "[3/7] Checking Terraform..."
if command -v terraform &> /dev/null; then
    TF_VERSION=$(terraform version -json | jq -r '.terraform_version')
    echo "✓ Terraform installed: v$TF_VERSION"
else
    echo "✗ Terraform not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Python
echo "[4/7] Checking Python..."
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python installed: $PY_VERSION"
else
    echo "✗ Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi

# Check pip
echo "[5/7] Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo "✓ pip installed: $PIP_VERSION"
else
    echo "✗ pip not found"
    ERRORS=$((ERRORS + 1))
fi

# Check terraform.tfvars
echo "[6/7] Checking terraform.tfvars..."
if [ -f "terraform/terraform.tfvars" ]; then
    KB_ID=$(grep -E "^knowledge_base_id" terraform/terraform.tfvars | cut -d'"' -f2 || echo "")
    GR_ID=$(grep -E "^guardrails_id" terraform/terraform.tfvars | cut -d'"' -f2 || echo "")

    if [ -n "$KB_ID" ] && [ "$KB_ID" != "" ]; then
        echo "✓ Knowledge Base ID configured: $KB_ID"
    else
        echo "✗ Knowledge Base ID not set in terraform.tfvars"
        ERRORS=$((ERRORS + 1))
    fi

    if [ -n "$GR_ID" ] && [ "$GR_ID" != "" ]; then
        echo "✓ Guardrails ID configured: $GR_ID"
    else
        echo "✗ Guardrails ID not set in terraform.tfvars"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "✗ terraform/terraform.tfvars not found"
    echo "  Copy terraform.tfvars.example and configure"
    ERRORS=$((ERRORS + 1))
fi

# Check Bedrock model access
echo "[7/7] Checking Bedrock model access..."
if aws bedrock list-foundation-models --region ap-northeast-1 &> /dev/null; then
    CLAUDE_ACCESS=$(aws bedrock list-foundation-models \
        --region ap-northeast-1\
        --by-provider anthropic \
        --query 'modelSummaries[?modelId==`anthropic.claude-3-haiku-20240307-v1:0`].modelId' \
        --output text 2>/dev/null || echo "")

    if [ -n "$CLAUDE_ACCESS" ]; then
        echo "✓ Bedrock access confirmed (Claude 3 Haiku available)"
    else
        echo "⚠ Claude 3 Haiku access not verified"
        echo "  Enable model access in Bedrock Console"
    fi
else
    echo "⚠ Could not check Bedrock access"
    echo "  Verify permissions and model access in Console"
fi

echo ""
echo "==================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ Validation passed!"
    echo "==================================="
    echo ""
    echo "Ready to deploy:"
    echo "  ./scripts/deploy.sh"
else
    echo "✗ Validation failed with $ERRORS error(s)"
    echo "==================================="
    echo ""
    echo "Please fix the errors above before deploying"
    echo "See SETUP.md for setup instructions"
    exit 1
fi
