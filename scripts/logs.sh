#!/bin/bash

#
# Logs Script
#
# View CloudWatch logs for Lambda functions
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Function to list
FUNCTION_NAME="${1:-api-handler}"

# Get full function name from Terraform
cd "$PROJECT_ROOT/terraform"
FULL_NAME=$(terraform output -json lambda_function_arns 2>/dev/null | jq -r ".[\"$FUNCTION_NAME\"]" | cut -d: -f7)

if [ -z "$FULL_NAME" ] || [ "$FULL_NAME" = "null" ]; then
    echo "ERROR: Lambda function '$FUNCTION_NAME' not found"
    echo ""
    echo "Available functions:"
    echo "  - api-handler"
    echo "  - guardrails-check"
    echo "  - kb-query"
    echo "  - bedrock-invoke"
    echo "  - cache-response"
    echo ""
    echo "Usage: ./scripts/logs.sh [function-name]"
    exit 1
fi

LOG_GROUP="/aws/lambda/$FULL_NAME"

echo "==================================="
echo "Lambda Logs: $FUNCTION_NAME"
echo "==================================="
echo ""
echo "Log Group: $LOG_GROUP"
echo ""
echo "Fetching latest logs..."
echo ""

# Tail logs
aws logs tail "$LOG_GROUP" --follow --format short
