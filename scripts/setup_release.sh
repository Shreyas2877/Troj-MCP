#!/bin/bash

# Complete setup script for Troj-MCP v1.0.0 release
# This script helps you set up everything needed for the release

set -e

REPO="Shreyas2877/Troj-MCP"
DOCKER_USERNAME="trojan2877"

echo "🚀 Setting up Troj-MCP v1.0.0 Release"
echo "======================================"
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

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "v1.0.0" ]; then
    echo "⚠️  Warning: You're not on the v1.0.0 branch (currently on: $CURRENT_BRANCH)"
    echo "Switching to v1.0.0 branch..."
    git checkout v1.0.0
fi

echo "✅ On v1.0.0 branch"
echo ""

# Set up branch protection
echo "🔒 Setting up branch protection rules..."
./scripts/setup_branch_protection.sh

echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. 🔐 Configure GitHub Secrets:"
echo "   Go to: https://github.com/$REPO/settings/secrets/actions"
echo "   Add these secrets:"
echo "   - DOCKER_USERNAME: $DOCKER_USERNAME"
echo "   - DOCKER_PASSWORD: [your-docker-hub-password-or-token]"
echo ""
echo "2. 🧪 Test the Pipeline:"
echo "   Make a small change and push to v1.0.0:"
echo "   git add ."
echo "   git commit -m 'test: trigger CI/CD pipeline'"
echo "   git push origin v1.0.0"
echo ""
echo "3. 📊 Monitor the Pipeline:"
echo "   - GitHub Actions: https://github.com/$REPO/actions"
echo "   - Docker Hub: https://hub.docker.com/r/$DOCKER_USERNAME/troj-mcp"
echo ""
echo "4. 🚀 Release Process:"
echo "   - Merge from development: git merge development"
echo "   - Push to trigger deployment: git push origin v1.0.0"
echo "   - Docker image will be automatically built and pushed"
echo "   - GitHub release will be created automatically"
echo ""
echo "📖 For detailed information, see RELEASE.md"
echo ""
echo "✅ Setup complete! Your v1.0.0 release branch is ready."
