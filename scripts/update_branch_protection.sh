#!/bin/bash

# Update existing branch protection to remove PR review requirements
# This script updates the v1.0.0 branch protection to work for personal repositories

set -e

REPO="Shreyas2877/Troj-MCP"
BRANCH="v1.0.0"

echo "🔧 Updating Branch Protection for Personal Repository"
echo "=================================================="
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

# Create a temporary JSON file for the updated protection rule
TEMP_FILE=$(mktemp)
cat > "$TEMP_FILE" << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test", "build-and-deploy"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "🔄 Updating branch protection rule..."

# Try to update the protection rule
if gh api repos/$REPO/branches/$BRANCH/protection \
  --method PUT \
  --input "$TEMP_FILE"; then
    echo "✅ Branch protection rule updated successfully!"
    echo ""
    echo "📋 Updated protection settings:"
    echo "- ✅ Require status checks: test, build-and-deploy"
    echo "- ❌ Pull request reviews: Disabled (personal repository)"
    echo "- ✅ No force pushes allowed"
    echo "- ✅ No branch deletion allowed"
    echo ""
    echo "🎉 You can now merge directly once status checks pass!"
else
    echo "❌ Failed to update branch protection rule via API."
    echo ""
    echo "🔧 Manual update required:"
    echo "1. Go to: https://github.com/$REPO/settings/branches"
    echo "2. Find the v1.0.0 branch protection rule"
    echo "3. Disable 'Require a pull request before merging'"
    echo "4. Keep all other settings (status checks, no force pushes, etc.)"
    echo "5. Save changes"
fi

# Clean up
rm -f "$TEMP_FILE"

echo ""
echo "🔍 Verify at: https://github.com/$REPO/settings/branches"
