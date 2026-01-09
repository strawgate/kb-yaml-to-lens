# Modified Workflow Files

These workflow files have been updated to use Makefile commands instead of duplicating logic.

## For Maintainers

To apply these changes, move these files to `.github/workflows/`:

```bash
# From repository root
mv github/workflows/publish-to-pypi.yml .github/workflows/
mv github/workflows/deploy-gh-pages.yml .github/workflows/
mv github/workflows/publish-vscode-extension.yml .github/workflows/
```

## Changes Made

### `publish-to-pypi.yml`

- **Before:** `uv build` and `uv publish` commands directly in workflow
- **After:** `make build` and `make publish` (delegates to `compiler/Makefile`)
- **Benefit:** Publishing logic can now be tested locally with `cd compiler && make build`

### `deploy-gh-pages.yml`

- **Before:** `uv sync --group docs` and `uv run --group docs mkdocs build --strict` inline
- **After:** `make docs-build-strict` (delegates to root `Makefile`)
- **Benefit:** Documentation build with strict mode is now a reusable command

### `publish-vscode-extension.yml`

- **Before:** `npm ci` command directly in workflow (line 84)
- **After:** `make install` (delegates to `vscode-extension/Makefile`)
- **Benefit:** Consistent with other workflow steps that already use `make` commands

## Related Makefile Changes

The following Makefile targets were added to support these workflows:

### Root `Makefile`

- `docs-build-strict` - Build documentation with strict mode (fails on warnings)

### `compiler/Makefile`

- `build` - Build Python package for PyPI
- `publish` - Publish package to PyPI
- `publish-test` - Publish package to TestPyPI (for testing)

All new commands are documented in `CLAUDE.md` and in the respective Makefile help text.
