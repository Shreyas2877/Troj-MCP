#!/bin/bash

# Setup branch protection for v1.0.0 release branch
# This script requires GitHub CLI to be installed and authenticated

set -e

REPO="Shreyas2877/Troj-MCP"
BRANCH="v1.0.0"

echo "Setting up branch protection for $BRANCH in $REPO..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed. Please install it first."
    echo "Visit: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI. Please run 'gh auth login' first."
    exit 1
fi

# Create branch protection rule
echo "Creating branch protection rule..."

# Create the protection rule using the correct API format
gh api repos/$REPO/branches/$BRANCH/protection \
  --method PUT \
  --input - << EOF
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
  "restrictions": {
    "users": ["Shreyas2877"],
    "teams": [],
    "apps": []
  },
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "✅ Branch protection rule created successfully!"
echo ""
echo "Branch protection settings:"
echo "- ✅ Require status checks to pass before merging"
echo "- ✅ Require branches to be up to date before merging"
echo "- ✅ Require pull request reviews before merging (1 approval required)"
echo "- ✅ Dismiss stale pull request approvals when new commits are pushed"
echo "- ✅ Restrict pushes to specified users (Shreyas2877 only)"
echo "- ✅ Do not allow force pushes"
echo "- ✅ Do not allow branch deletion"
echo ""
echo "Required status checks:"
echo "- test (Run Tests job)"
echo "- build-and-deploy (Build and Deploy to Docker Hub job)"
echo ""
echo "🔒 The v1.0.0 branch is now protected!"
echo "Only you (Shreyas2877) can push to this branch, and all tests must pass before merging."
