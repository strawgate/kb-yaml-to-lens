# CI Workflow Updates Required

This document describes the CI workflow changes needed to align with the new Makefile structure.

## Summary of Changes

The Makefile has been restructured to provide clear, simple commands for CI and development:

- **`make ci`** - Run all CI checks (linting + type checking + tests) without auto-fix
- **`make check`** - Alias for `make ci` (what developers run locally)
- **`make fix`** - Auto-fix all linting issues
- **`make lint-all-check`** - Check all linting (Python + Markdown + YAML)
- **`make test-all`** - Run all tests (unit + smoke + links + extension)

## Required Workflow Updates

### 1. Update `.github/workflows/test.yml`

**Current state:**
- Separate jobs for `lint` and `typecheck`
- Only runs Python linting (`lint-check`, `format-check`)
- Missing: Markdown linting, YAML linting

**Recommended change:**

Replace the `lint` and `typecheck` jobs with a single `quality-checks` job:

```yaml
quality-checks:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    - name: Setup Python Environment
      uses: ./.github/actions/setup-python-env
    - name: Install Node.js for markdownlint
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    - name: Install markdownlint
      run: npm install -g markdownlint-cli
    - name: Run all linting and type checks
      run: make lint-all-check typecheck
```

**Alternative (keep separate jobs but add missing linters):**

Update the `lint` job to use the new comprehensive linting command:

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    - name: Setup Python Environment
      uses: ./.github/actions/setup-python-env
    - name: Install Node.js for markdownlint
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    - name: Install markdownlint
      run: npm install -g markdownlint-cli
    - name: Run all linting checks
      run: make lint-all-check
```

### 2. Simplify test job

The test job can now use the comprehensive `test-all` command:

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    - name: Setup Python Environment
      uses: ./.github/actions/setup-python-env
    - name: Install Node.js for extension tests
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    - name: Run all tests
      run: make test-all
```

**Note:** This consolidates unit tests, smoke tests, link tests, and extension tests into a single command.

### 3. Alternative: Single CI job

For maximum simplicity, you could replace all jobs with a single comprehensive CI job:

```yaml
ci:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    - name: Setup Python Environment
      uses: ./.github/actions/setup-python-env
    - name: Install Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    - name: Install markdownlint
      run: npm install -g markdownlint-cli
    - name: Run all CI checks
      run: make ci
```

This single job runs: `lint-all-check + typecheck + test-all`

## Benefits of New Structure

1. **Consistency**: CI runs exactly what `make ci` runs locally
2. **Completeness**: All linters (Python, Markdown, YAML) are checked
3. **Clarity**: Commands have clear, obvious purposes
4. **Simplicity**: Fewer CI jobs to maintain

## Command Reference

| Old Pattern | New Command | Purpose |
|-------------|-------------|---------|
| `make lint-check && make format-check` | `make lint-all-check` | Check all linting |
| `make test && make test-smoke && ...` | `make test-all` | Run all tests |
| `make lint-check && make typecheck && make test` | `make ci` | Run all CI checks |
| N/A | `make fix` | Auto-fix all linting issues |

## Migration Checklist

- [ ] Update `.github/workflows/test.yml` to use new commands
- [ ] Verify CI runs markdown linting
- [ ] Verify CI runs YAML linting
- [ ] Verify CI fails when linting issues are found
- [ ] Update `CLAUDE.md` to reference `make ci` instead of `make check`
- [ ] Consider consolidating CI jobs for simplicity

## YAML Linting Issues to Fix

The new `make lint-all-check` command revealed YAML linting issues in workflow files:

1. **`.github/workflows/claude-on-issue-mention.yml`**: Lines 29, 31 too long
2. **`.github/workflows/claude-on-open-label.yml`**: Lines 99-100, 106-107, 113 too long
3. **`.github/workflows/claude-on-mention.yml`**: Lines 22-24, 29 too long
4. **`inputs/aerospike-namespace-metrics/metrics-aerospike-namespace-metrics.yaml`**: Line 142 comment indentation

These should be fixed to ensure `make ci` passes cleanly.
