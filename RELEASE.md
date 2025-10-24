# Release Process for Troj-MCP v1.0.0

## 🚀 Release Branch: v1.0.0

This document outlines the release process for Troj-MCP v1.0.0, including branch protection, CI/CD pipeline, and Docker Hub deployment.

## 📋 Prerequisites

### Required GitHub Secrets

Before the CI/CD pipeline can work, you need to configure the following secrets in your GitHub repository:

1. **Docker Hub Credentials:**
   - `DOCKER_USERNAME`: Your Docker Hub username (`trojan2877`)
   - `DOCKER_PASSWORD`: Your Docker Hub password or access token

### Setting up GitHub Secrets

1. Go to your repository: `https://github.com/Shreyas2877/Troj-MCP`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:
   - Name: `DOCKER_USERNAME`, Value: `trojan2877`
   - Name: `DOCKER_PASSWORD`, Value: `[your-docker-hub-password-or-token]`

## 🔒 Branch Protection Rules

The `v1.0.0` branch is protected with the following rules:

- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- ✅ **Require pull request reviews before merging** (1 approval required)
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ✅ **Restrict pushes to specified users** (Shreyas2877 only)
- ✅ **Do not allow force pushes**
- ✅ **Do not allow branch deletion**

### Required Status Checks

The following status checks must pass before any merge:

1. **test** - Runs all tests with coverage
2. **build-and-deploy** - Builds and pushes Docker image to Docker Hub

## 🔄 CI/CD Pipeline

### Workflow Triggers

The CI/CD pipeline runs on:
- Push to `v1.0.0` branch
- Pull requests to `v1.0.0` branch

### Pipeline Jobs

#### 1. Test Job
- **Runs on:** Ubuntu Latest
- **Steps:**
  - Checkout code
  - Set up Python 3.11
  - Cache pip dependencies
  - Install dependencies
  - Run linting (ruff, black)
  - Run tests with coverage
  - Upload coverage to Codecov

#### 2. Build and Deploy Job
- **Runs on:** Ubuntu Latest
- **Triggers:** Only on push to `v1.0.0` branch
- **Dependencies:** Requires test job to pass
- **Steps:**
  - Checkout code
  - Set up Docker Buildx
  - Log in to Docker Hub
  - Extract metadata
  - Build and push Docker image
  - Create GitHub Release

### Docker Image

- **Repository:** `trojan2877/troj-mcp`
- **Tags:** 
  - `latest` (for v1.0.0 branch)
  - `v1.0.0-<commit-sha>` (specific commit)
  - `v1.0.0` (branch name)

## 🐳 Docker Usage

### Pull and Run

```bash
# Pull the latest image
docker pull trojan2877/troj-mcp:latest

# Run the container
docker run -d \
  --name troj-mcp \
  -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  trojan2877/troj-mcp:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  troj-mcp:
    image: trojan2877/troj-mcp:latest
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-secret-key
    restart: unless-stopped
```

## 📝 Release Process

### 1. Development Workflow

```bash
# Work on development branch
git checkout development
git pull origin development

# Make your changes
# ... make changes ...

# Commit and push
git add .
git commit -m "feat: add new feature"
git push origin development
```

### 2. Creating a Release

```bash
# Switch to v1.0.0 branch
git checkout v1.0.0
git pull origin v1.0.0

# Merge from development (this will trigger CI/CD)
git merge development
git push origin v1.0.0
```

### 3. Automated Deployment

When you push to `v1.0.0`:

1. **Tests run automatically** - All tests must pass
2. **Docker image is built** - Multi-platform build (linux/amd64, linux/arm64)
3. **Image is pushed to Docker Hub** - Available as `trojan2877/troj-mcp:latest`
4. **GitHub Release is created** - With release notes and Docker usage instructions

## 🔧 Manual Setup (One-time)

### Set up Branch Protection

Run the setup script to configure branch protection:

```bash
# Make sure you have GitHub CLI installed and authenticated
gh auth login

# Run the setup script
./scripts/setup_branch_protection.sh
```

### Verify Setup

1. Go to your repository settings
2. Navigate to **Branches** → **Branch protection rules**
3. Verify that `v1.0.0` has protection rules enabled
4. Check that required status checks are configured

## 🚨 Troubleshooting

### Common Issues

1. **Docker Hub Authentication Failed**
   - Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set
   - Check that Docker Hub credentials are correct

2. **Tests Failing**
   - Check the test logs in GitHub Actions
   - Run tests locally: `python -m pytest tests/`
   - Fix any linting issues: `ruff check .`

3. **Branch Protection Issues**
   - Ensure you're pushing as `Shreyas2877`
   - Check that all required status checks are passing
   - Verify pull request has required approvals

### Local Testing

```bash
# Run tests locally
python -m pytest tests/ --cov=src/macro_man

# Run linting
ruff check .
black --check .

# Build Docker image locally
docker build -t troj-mcp:local .
docker run -p 8000:8000 troj-mcp:local
```

## 📊 Monitoring

- **GitHub Actions:** Check the Actions tab for pipeline status
- **Docker Hub:** Monitor image pushes at https://hub.docker.com/r/trojan2877/troj-mcp
- **Code Coverage:** View coverage reports in the Actions logs

## 🎯 Success Criteria

A successful release requires:

- ✅ All tests pass
- ✅ Linting passes (ruff, black)
- ✅ Code coverage meets requirements
- ✅ Docker image builds successfully
- ✅ Docker image pushes to Docker Hub
- ✅ GitHub Release is created
- ✅ Branch protection rules are enforced

---

**Note:** This release process ensures that only high-quality, tested code reaches production, and that Docker images are automatically deployed to Docker Hub for easy consumption.
