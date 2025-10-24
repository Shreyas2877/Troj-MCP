#!/bin/bash

# Temporarily disable branch protection to allow merging
# This script removes branch protection from v1.0.0

set -e

REPO="Shreyas2877/Troj-MCP"
BRANCH="v1.0.0"

echo "⚠️  Temporarily Disabling Branch Protection"
echo "==========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed."
    echo "Please install it first: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI."
    echo "Please run 'gh auth login' first."
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

echo "🔄 Removing branch protection rule..."

# Remove the protection rule
if gh api repos/$REPO/branches/$BRANCH/protection \
  --method DELETE; then
    echo "✅ Branch protection rule removed successfully!"
    echo ""
    echo "⚠️  WARNING: Branch protection is now DISABLED"
    echo "You can now merge your PR, but remember to re-enable protection after merging"
    echo ""
    echo "To re-enable protection after merging, run:"
    echo "./scripts/update_branch_protection.sh"
else
    echo "❌ Failed to remove branch protection rule."
    echo ""
    echo "🔧 Manual removal required:"
    echo "1. Go to: https://github.com/$REPO/settings/branches"
    echo "2. Find the v1.0.0 branch protection rule"
    echo "3. Click 'Delete' to remove the protection"
    echo "4. Merge your PR"
    echo "5. Re-enable protection after merging"
fi

echo ""
echo "🔍 Verify at: https://github.com/$REPO/settings/branches"
