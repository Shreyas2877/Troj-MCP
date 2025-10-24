#!/bin/bash

# Check what status checks are actually being reported for the v1.0.0 branch
# This helps debug why the branch protection is waiting for status checks

set -e

REPO="Shreyas2877/Troj-MCP"
BRANCH="v1.0.0"

echo "🔍 Checking Status Checks for v1.0.0 Branch"
echo "=========================================="
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

echo "🔄 Checking current branch protection settings..."

# Get current branch protection settings
PROTECTION=$(gh api repos/$REPO/branches/$BRANCH/protection 2>/dev/null || echo "No protection")

if [ "$PROTECTION" != "No protection" ]; then
    echo "📋 Current branch protection settings:"
    echo "$PROTECTION" | jq -r '.required_status_checks.contexts[]' 2>/dev/null || echo "No contexts found"
    echo ""
fi

echo "🔄 Checking recent commits and their status checks..."

# Get the latest commit on v1.0.0
LATEST_COMMIT=$(gh api repos/$REPO/branches/$BRANCH | jq -r '.commit.sha')

echo "Latest commit: $LATEST_COMMIT"
echo ""

# Get status checks for the latest commit
echo "📊 Status checks for latest commit:"
gh api repos/$REPO/commits/$LATEST_COMMIT/status 2>/dev/null | jq -r '.statuses[] | "\(.context): \(.state)"' || echo "No status checks found"

echo ""
echo "🔄 Checking recent workflow runs..."

# Get recent workflow runs
echo "📊 Recent workflow runs:"
gh run list --branch $BRANCH --limit 5 --json conclusion,status,name,headBranch | jq -r '.[] | "\(.name): \(.status) (\(.conclusion // "running"))"' || echo "No workflow runs found"

echo ""
echo "💡 If you see workflow runs that are 'completed' but the branch protection is still waiting,"
echo "   the issue might be that the job names don't match the expected status check names."
echo ""
echo "🔧 To fix this, you can:"
echo "1. Check the actual job names in the workflow"
echo "2. Update the branch protection to match the actual job names"
echo "3. Or temporarily disable branch protection to merge"
