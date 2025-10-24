#!/bin/bash

# Simplified branch protection setup for v1.0.0 release branch
# This script uses a simpler approach with individual API calls

set -e

REPO="Shreyas2877/Troj-MCP"
BRANCH="v1.0.0"

echo "🔒 Setting up Branch Protection for v1.0.0 (Simplified)"
echo "======================================================"
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

# Create a temporary JSON file for the protection rule
TEMP_FILE=$(mktemp)
cat > "$TEMP_FILE" << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test", "build-and-deploy"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "🔄 Creating branch protection rule..."

# Try to create the protection rule
if gh api repos/$REPO/branches/$BRANCH/protection \
  --method PUT \
  --input "$TEMP_FILE"; then
    echo "✅ Branch protection rule created successfully!"
else
    echo "❌ Failed to create branch protection rule via API."
    echo ""
    echo "🔧 Manual setup required:"
    echo "1. Go to: https://github.com/$REPO/settings/branches"
    echo "2. Add rule for branch: v1.0.0"
    echo "3. Configure the settings as shown in the manual script"
    echo ""
    echo "Run: ./scripts/setup_branch_protection_manual.sh for detailed instructions"
fi

# Clean up
rm -f "$TEMP_FILE"

echo ""
echo "📋 Branch protection settings configured:"
echo "- ✅ Require status checks: test, build-and-deploy"
echo "- ✅ Require pull request reviews: 1 approval"
echo "- ⚠️  User restrictions: Not available for personal repositories"
echo "- ✅ No force pushes allowed"
echo "- ✅ No branch deletion allowed"
echo ""
echo "ℹ️  Note: Since this is a personal repository, anyone with write access"
echo "   can push to the branch, but all other protection rules still apply."
echo ""
echo "🔍 Verify at: https://github.com/$REPO/settings/branches"
