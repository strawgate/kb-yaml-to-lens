# Workflow Files for Manual Copy

This directory contains GitHub Actions workflow files that cannot be automatically
committed to `.github/workflows/` due to GitHub App permission restrictions.

## How to Apply These Changes

Copy the workflow files to `.github/workflows/`:

```bash
cp github/workflows/*.yml .github/workflows/
```

Then commit and push the changes manually.

## Files

### test-extension-platforms.yml (NEW)

Reusable workflow that tests the VS Code extension on multiple platforms:

- Linux (ubuntu-latest)
- macOS ARM64 (macos-14)
- macOS Intel (macos-13)
- Windows (windows-latest)

Each platform:

1. Downloads the `uv` binary for that platform
2. Bundles the compiler source
3. Runs `kb-dashboard --help` via bundled uv to verify it works
4. Runs TypeScript unit tests

### lint-test-build.yml (MODIFIED)

Updated to call the new `test-extension-platforms.yml` reusable workflow:

- Added `test-extension-platforms` job that depends on `lint-python` and `typecheck-python`
- Added `test-extension-platforms` to the `checks-passed` job's needs list

This ensures multi-platform testing runs on every PR and push to main.
