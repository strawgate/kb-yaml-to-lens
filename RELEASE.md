# Release Process

Releases are **tag-based and fully automated**. Push a version tag (`v*`) to trigger:

- GitHub release with changelog and binaries (4 unified binaries)
- Docker image (multi-arch: `ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler`)
- PyPI package (`kb-dashboard-compiler`)
- VS Code extension (marketplace + Open VSX)

## Quick Start

```bash
# 1. Bump version (updates all components atomically)
make bump-patch    # or bump-minor/bump-major
# Or set explicit version: uv run scripts/bump-version.py set 1.0.0
# Preview changes first: uv run scripts/bump-version.py patch --dry-run

# 2. Commit and tag
git add compiler/pyproject.toml vscode-extension/package.json fixture-generator/package.json pyproject.toml
git commit -m "chore: Bump version to 1.0.0"
git tag v1.0.0
git push origin main && git push origin v1.0.0

# 3. Monitor workflows at github.com/strawgate/kb-yaml-to-lens/actions
# 4. Verify release at github.com/strawgate/kb-yaml-to-lens/releases
```

## Version Format

Follow [SemVer](https://semver.org/): `v{major}.{minor}.{patch}`

- **Major**: Breaking changes
- **Minor**: New features (backward-compatible)
- **Patch**: Bug fixes

**Pre-releases**: `v1.0.0-rc1`, `v1.0.0-alpha1`, `v1.0.0-beta1` (auto-marked in GitHub)

## Release Checklist

**Before tagging:**

- [ ] All PRs merged to `main`
- [ ] CI passes: `make ci`
- [ ] Versions updated: `make bump-patch` (or `bump-minor`/`bump-major`)

**After tagging:**

- [ ] All workflows complete (~10-15 min total)
- [ ] GitHub release has 4 binaries attached
- [ ] Docker: `docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0`
- [ ] PyPI: `pip install kb-dashboard-compiler==1.0.0`
- [ ] VS Code extension updated on marketplace

## Troubleshooting

**Workflow failed?**

1. Check logs in GitHub Actions
2. Fix issue, then recreate tag:

   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   git tag v1.0.0
   git push origin v1.0.0
   ```

**Common issues:**

- Binary builds: Check Python/UV setup in workflow logs
- PyPI: Version may already exist (increment version)
- VS Code: Check marketplace secrets
- Docker: Verify Dockerfile and base images

**Manual publishing** (if automation fails):

```bash
# PyPI (uses Makefile targets)
cd compiler && make build && make publish

# Docker (multi-arch - prefer re-running workflow)
# Manual single-arch build for testing only:
cd compiler && docker build -t ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0 .

# VS Code (publishes to both VS Code Marketplace and Open VSX)
cd vscode-extension && make package && npx vsce publish && npx ovsx publish *.vsix
```

**Do not delete tags/releases** - breaks user installations. Instead: mark as pre-release or publish patch.
