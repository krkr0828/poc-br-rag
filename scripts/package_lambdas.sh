#!/bin/bash

#
# Lambda Packaging Script
#
# Creates a deployment package with all Python code and dependencies
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==================================="
echo "Lambda Packaging Script"
echo "==================================="
echo ""

# Clean previous builds
echo "[1/5] Cleaning previous builds..."
rm -rf build/
rm -f lambda_deployment.zip
mkdir -p build/package

# Install dependencies
echo "[2/5] Installing dependencies..."
pip3 install -r requirements.txt -t build/package/ --upgrade

# Copy source code
echo "[3/5] Copying source code..."
cp -r src/ build/package/

# Create deployment package
echo "[4/5] Creating deployment package..."
cd build/package
zip -r ../../lambda_deployment.zip . -q
cd "$PROJECT_ROOT"

# Display package info
PACKAGE_SIZE=$(du -h lambda_deployment.zip | cut -f1)
echo "[5/5] Deployment package created: lambda_deployment.zip ($PACKAGE_SIZE)"

echo ""
echo "==================================="
echo "Packaging complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Run 'cd terraform && terraform apply' to deploy Lambda functions"
echo "2. Lambda functions will be updated with the new deployment package"
echo ""
