# Recommended CI Workflow Updates

This document describes the recommended updates to CI workflows to use the new Makefile targets. These changes could not be applied automatically due to GitHub App permissions restrictions on `.github/workflows/` files.

## Benefits

- **Consistency**: CI runs the same commands developers run locally
- **Maintainability**: Changes to linting/testing commands only need to be made in the Makefile
- **Simplicity**: Single source of truth for all build/test/lint commands

## Recommended Changes

### 1. `.github/workflows/test.yml`

**Current:**

```yaml
- name: Run pytest
  run: |
    uv run pytest -v

- name: Run smoke tests
  run: |
    uv run kb-dashboard --help
```

**Recommended:**

```yaml
- name: Run pytest
  run: make test

- name: Run smoke tests
  run: make test-smoke
```

---

**Current:**

```yaml
- name: Run linting
  run: |
    uv run ruff check .
    uv run ruff format . --check
```

**Recommended:**

```yaml
- name: Run linting
  run: make lint-check

- name: Check formatting
  run: make format-check
```

---

**Current:**

```yaml
- name: Run type checking
  run: |
    uv run basedpyright
```

**Recommended:**

```yaml
- name: Run type checking
  run: make typecheck
```

### 2. `.github/workflows/test-vscode-extension.yml`

**Current:**

```yaml
- name: Run Python tests for extension
  run: |
    uv run python -m pytest vscode-extension/python/test_*.py -v
```

**Recommended:**

```yaml
- name: Run Python tests for extension
  run: make test-extension-python
```

### 3. `.github/workflows/docs.yml`

**Current:**

```yaml
- name: Build and deploy documentation
  run: |
    uv run python scripts/compile_docs.py
    uv run --group docs mkdocs gh-deploy --force
```

**Recommended:**

```yaml
- name: Build and deploy documentation
  run: make docs-deploy
```

## Optional: Comprehensive Check

You could also add a single comprehensive check job that runs everything:

```yaml
comprehensive-check:
  runs-on: ubuntu-latest
  steps:
  - name: Checkout repository
    uses: actions/checkout@v4

  - name: Setup Python Environment
    uses: ./.github/actions/setup-python-env

  - name: Run comprehensive validation
    run: make check
```

This would run all validation (lint-check, format-check, lint-markdown-check, typecheck, test, test-links, test-smoke, test-extension-python, test-extension-typescript) in a single job.

## Implementation Notes

1. These changes require manual updates by a repository maintainer with workflow permissions
2. The Makefile targets are already tested and working
3. CI behavior will remain identical - these changes only improve maintainability
4. Consider testing on a non-main branch first before deploying to production workflows
