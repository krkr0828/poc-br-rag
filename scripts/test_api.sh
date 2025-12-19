#!/bin/bash

#
# Test API Script
#
# Tests the deployed API Gateway endpoint
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Get API endpoint from Terraform output
cd terraform
API_URL=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")
cd "$PROJECT_ROOT"

if [ -z "$API_URL" ]; then
    echo "ERROR: Could not get API Gateway URL"
    echo "Make sure infrastructure is deployed: ./scripts/deploy.sh"
    exit 1
fi

# Get query from argument or use default
QUERY="${1:-What is AWS Bedrock?}"

echo "==================================="
echo "Testing Bedrock RAG API"
echo "==================================="
echo ""
echo "API URL: $API_URL"
echo "Query: $QUERY"
echo ""
echo "Sending request..."
echo ""

# Send request
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$QUERY\"}")

# Pretty print response
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "==================================="
echo "Test complete!"
echo "==================================="
