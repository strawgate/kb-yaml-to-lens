# PyPI Publishing Guide

This guide explains how the `dashboard-compiler` package is published to PyPI using automated workflows.

## Overview

The project uses **GitHub Actions with PyPI Trusted Publishing** for secure, token-free package deployment. This is the modern standard for Python package publishing as of 2026.

### Key Features

- **Automated Publishing** - Triggered automatically on GitHub releases
- **Trusted Publishing** - No API tokens to manage or rotate
- **OIDC Authentication** - Secure authentication via GitHub OIDC tokens
- **Test Environment** - TestPyPI workflow for pre-release testing

## Package Configuration

The package is configured in `pyproject.toml`:

- **Package name**: `dashboard-compiler`
- **Build backend**: `uv_build`
- **CLI entry point**: `kb-dashboard`

## Publishing Workflows

### Production PyPI

**Workflow**: `.github/workflows/publish-to-pypi.yml`

**Trigger**: GitHub release publication

**Steps**:

1. Checkout repository
2. Set up Python environment with uv
3. Build package: `uv build`
4. Publish to PyPI: `uv publish`

### TestPyPI (Testing)

**Workflow**: `.github/workflows/publish-to-testpypi.yml`

**Trigger**: Git tags matching `test-v*` pattern

**Steps**: Same as production, but publishes to TestPyPI

## Setup Instructions

### 1. Configure PyPI Trusted Publisher

Before the first release, configure the Trusted Publisher on PyPI:

1. Go to <https://pypi.org/manage/account/publishing/>
2. Click "Add a new pending publisher"
3. Configure:
   - **PyPI project name**: `dashboard-compiler`
   - **Owner**: `strawgate`
   - **Repository name**: `kb-yaml-to-lens`
   - **Workflow name**: `publish-to-pypi.yml`
   - **Environment name**: `pypi`

The first time you publish, PyPI will automatically create the project using this configuration.

### 2. Create GitHub Environment

1. Go to repository Settings → Environments
2. Click "New environment"
3. Name: `pypi`
4. Add protection rules (recommended):
   - Required reviewers (at least 1)
   - Wait timer (optional, e.g., 5 minutes)

This ensures manual approval before publishing to PyPI.

### 3. Optional: Configure TestPyPI

For testing before production releases:

1. Go to <https://test.pypi.org/manage/account/publishing/>
2. Add pending publisher with same settings:
   - **Workflow name**: `publish-to-testpypi.yml`
   - **Environment name**: `testpypi`
3. Create `testpypi` GitHub environment

## Publishing a Release

### Production Release

1. Update version in `pyproject.toml` (if needed)
2. Commit and push changes
3. Create a git tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

4. Create a GitHub Release from the tag
5. The workflow triggers automatically
6. Approve the deployment (if protection rules are configured)
7. Package publishes to PyPI

### Test Release (TestPyPI)

To test the publishing process before production:

1. Create a test tag:

   ```bash
   git tag test-v0.1.0
   git push origin test-v0.1.0
   ```

2. The TestPyPI workflow triggers automatically
3. Package publishes to TestPyPI

## Verification

After successful publication:

1. Visit <https://pypi.org/project/dashboard-compiler/>
2. Test installation:

   ```bash
   pip install dashboard-compiler
   kb-dashboard --help
   ```

## Troubleshooting

### Publication Fails

- **Check Trusted Publisher configuration** - Ensure owner, repository, workflow name, and environment match exactly
- **Check GitHub environment** - Verify the environment exists and has the correct name
- **Review workflow logs** - Check the GitHub Actions run for specific errors

### First Publication

The first time you publish:

- PyPI requires a pending publisher configuration
- The package will be created automatically on first successful publish
- Subsequent publishes update the existing package

## Security Notes

- **No secrets required** - Trusted Publishing uses OIDC tokens
- **Environment protection** - Use GitHub environment protection rules to control releases
- **Permissions** - Workflow only has `id-token: write` and `contents: read` permissions
- **Manual approval** - Consider requiring manual approval for production releases

## References

- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [uv Publishing Guide](https://docs.astral.sh/uv/guides/publish/)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
