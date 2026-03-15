# Release Process

Releases are **tag-based and fully automated**. Push a version tag (`v*`) to trigger:

- GitHub release with changelog
- Docker image (multi-arch: `ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler`)
- PyPI packages:
  - `kb-dashboard-core` (core compilation library)
  - `kb-dashboard-tools` (Kibana client utilities)
  - `kb-dashboard-lint` (dashboard linting)
  - `kb-dashboard-cli` (CLI and LSP server)
- VS Code extension (marketplace + Open VSX)

## Quick Start

```bash
# 1. Bump version (updates all components atomically)
just bump-patch    # or bump-minor/bump-major
# Or set explicit version: uv run scripts/bump-version.py set 1.0.0
# Preview changes first: uv run scripts/bump-version.py patch --dry-run

# 2. Commit and push tag
git add packages/*/pyproject.toml packages/vscode-extension/package.json \
        pyproject.toml uv.lock packages/vscode-extension/package-lock.json
git commit -m "chore: Bump version to 1.0.0"
just release-tag  # Creates and pushes v1.0.0 tag

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
- [ ] CI passes: `just all ci`
- [ ] Versions updated: `just bump-patch` (or `bump-minor`/`bump-major`)

**After tagging:**

- [ ] All workflows complete (~10-15 min total)
- [ ] GitHub release created with changelog
- [ ] Docker: `docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0`
- [ ] PyPI: `pip install kb-dashboard-core==1.0.0 kb-dashboard-tools==1.0.0 kb-dashboard-lint==1.0.0 kb-dashboard-cli==1.0.0`
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

- PyPI: Version may already exist (increment version)
- VS Code: Check marketplace secrets
- Docker: Verify Dockerfile and base images

**Manual publishing** (if automation fails):

```bash
# PyPI (uses justfile targets - publish in dependency order)
# The publish target depends on build, so build is automatic
just core publish    # Core first (no dependencies)
just tools publish   # Tools depend on core
just lint publish    # Lint depends on core
just cli publish     # CLI depends on core + tools

# Docker (multi-arch - prefer re-running workflow)
# Manual single-arch build for testing only:
# Build from repo root with -f flag to specify Dockerfile
docker build -f packages/kb-dashboard-cli/Dockerfile -t ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0 .

# VS Code (publishes to both VS Code Marketplace and Open VSX)
just vscode package && cd packages/vscode-extension && npx vsce publish && npx ovsx publish *.vsix
```

**Do not delete tags/releases** - breaks user installations. Instead: mark as pre-release or publish patch.
