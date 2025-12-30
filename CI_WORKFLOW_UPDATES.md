# CI Workflow Updates Required

This document describes the CI workflow changes needed to align with the new Makefile structure.

## Summary of Changes

The Makefile has been restructured to provide clear, simple commands for CI and development:

- **`make ci`** - Run all CI checks (linting + type checking + tests) - useful for local pre-commit checks
- **`make check`** - Alias for `make ci`
- **`make fix`** - Auto-fix all linting issues
- **`make lint-all-check`** - Check all linting (Python + Markdown + YAML)
- **`make test-all`** - Run all tests (unit + smoke + links + extension)

## CI Philosophy: Individual Checks for Clear Reporting

**IMPORTANT:** CI should run **individual jobs** that report separately, not a single monolithic job.

**Why?** When CI fails, GitHub shows which specific job failed, making it immediately obvious what broke (linting vs typecheck vs tests) without having to dig through workflow logs.

**Note:** While `make ci` runs everything in one command (useful for local pre-commit checks), CI workflows should use granular jobs.

## Required Workflow Updates

### Update `.github/workflows/test.yml`

**Current state:**

- ✅ Separate jobs for `lint`, `typecheck`, and `test` (good!)
- ❌ Only runs Python linting (`lint-check`, `format-check`)
- ❌ Missing: Markdown linting, YAML linting

**Recommended changes:**

Keep the individual job structure but update to use new Makefile commands:

#### 1. Update `lint` job to include all linting

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

#### 2. Keep `typecheck` job as-is

```yaml
typecheck:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    - name: Setup Python Environment
      uses: ./.github/actions/setup-python-env
    - name: Run type checking
      run: make typecheck
```

#### 3. Update `test` job (choose one approach)

**Option A: Keep granular test steps** (shows which test type failed)

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    - name: Setup Python Environment
      uses: ./.github/actions/setup-python-env
    - name: Run pytest
      run: make test
    - name: Run smoke tests
      run: make test-smoke
    - name: Run link tests
      run: make test-links
```

**Option B: Use `make test-all`** (simpler, but less granular reporting)

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

## Benefits of New Structure

1. **Clear Reporting**: Individual CI jobs show exactly which check failed
2. **Completeness**: All linters (Python, Markdown, YAML) are checked
3. **Consistency**: CI jobs use the same commands developers run locally
4. **Clarity**: Commands have clear, obvious purposes

## Command Reference

| Use Case | Command | Purpose |
| ------------- | ------------- | --------- |
| **Local pre-commit check** | `make ci` or `make check` | Run all checks (lint-all-check + typecheck + test-all) |
| **CI lint job** | `make lint-all-check` | Check all linting (Python + Markdown + YAML) |
| **CI typecheck job** | `make typecheck` | Run type checking with basedpyright |
| **CI test job** | `make test-all` OR individual test commands | Run all tests or specific test types |
| **Fix linting locally** | `make fix` | Auto-fix all linting issues |

## Migration Checklist for Copilot

**Specific changes needed in `.github/workflows/test.yml`:**

1. **In the `lint` job (starting at line 22):**
   - After line 28 (after `uses: ./.github/actions/setup-python-env`), add:

     ```yaml
     - name: Install Node.js for markdownlint
       uses: actions/setup-node@v4
       with:
         node-version: '20'
     - name: Install markdownlint
       run: npm install -g markdownlint-cli
     ```

   - Replace lines 29-32 (the two make commands) with:

     ```yaml
     - name: Run all linting checks
       run: make lint-all-check
     ```

2. **The `typecheck` job (lines 33-41):** Keep as-is, no changes needed.

3. **The `test` job (lines 11-21):** No changes needed (already runs individual test commands).

## YAML Linting Issues to Fix

The new `make lint-all-check` command revealed YAML linting issues in workflow files:

1. **`.github/workflows/claude-on-issue-mention.yml`**: Lines 29, 31 too long
2. **`.github/workflows/claude-on-open-label.yml`**: Lines 99-100, 106-107, 113 too long
3. **`.github/workflows/claude-on-mention.yml`**: Lines 22-24, 29 too long
4. **`inputs/aerospike-namespace-metrics/metrics-aerospike-namespace-metrics.yaml`**: Line 142 comment indentation

These should be fixed to ensure `make ci` passes cleanly locally, but are not blocking for CI workflows (which will use `make lint-all-check` only after Copilot updates the test.yml workflow).
