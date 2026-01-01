# PyPI Publishing Guide

The project uses **GitHub Actions with PyPI Trusted Publishing** for secure, token-free package deployment.

## Publishing Workflow

**Workflow**: `.github/workflows/publish-to-pypi.yml`

**Trigger**: GitHub release publication

## Publishing a Release

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

## Verification

After successful publication:

1. Visit <https://pypi.org/project/dashboard-compiler/>
2. Test installation:

   ```bash
   pip install dashboard-compiler
   kb-dashboard --help
   ```

## References

- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [uv Publishing Guide](https://docs.astral.sh/uv/guides/publish/)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
