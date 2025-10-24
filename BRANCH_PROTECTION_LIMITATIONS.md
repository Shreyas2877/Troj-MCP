# Branch Protection Limitations for Personal Repositories

## ⚠️ Important Note

This repository is a **personal repository**, not an organization repository. This means some branch protection features are not available.

## 🚫 Limitations

### User Restrictions Not Available
- ❌ **Cannot restrict pushes to specific users** (e.g., only Shreyas2877)
- ❌ **Cannot restrict pushes to specific teams**
- ❌ **Cannot restrict pushes to specific apps**

These restrictions are only available for **organization repositories**.

## ✅ Available Protection Features

The following protection features **ARE** available for personal repositories:

- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- ✅ **Require pull request reviews before merging**
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ✅ **Require review from code owners** (if CODEOWNERS file exists)
- ✅ **Allow force pushes: No**
- ✅ **Allow deletions: No**

## 🔒 Current Protection Settings

For the `v1.0.0` branch:

- ✅ **Status checks required:** `test`, `build-and-deploy`
- ✅ **Pull request reviews required:** 1 approval
- ✅ **No force pushes allowed**
- ✅ **No branch deletion allowed**
- ⚠️ **User restrictions:** Not available (personal repo limitation)

## 🛡️ Security Considerations

Since user restrictions aren't available, the security model relies on:

1. **Repository access control** - Only collaborators with write access can push
2. **Status checks** - All tests must pass before merging
3. **Pull request reviews** - Changes must be reviewed and approved
4. **Branch protection** - Prevents force pushes and deletions

## 🔄 Workflow

The typical workflow for the `v1.0.0` branch:

1. **Development work** happens on `development` branch
2. **Create pull request** from `development` to `v1.0.0`
3. **All tests must pass** (automated via GitHub Actions)
4. **Pull request must be reviewed** and approved
5. **Merge to v1.0.0** triggers Docker build and deployment
6. **Docker image** is automatically pushed to Docker Hub

## 🏢 If You Need User Restrictions

If you need to restrict pushes to specific users, you would need to:

1. **Transfer the repository to an organization** you own
2. **Or create a new repository under an organization**

However, for most use cases, the current protection settings provide adequate security through:
- Required status checks
- Required pull request reviews
- Prevention of force pushes and deletions

## 📚 References

- [GitHub Documentation: About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Documentation: Restricting who can push to protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-branch-restrictions)
