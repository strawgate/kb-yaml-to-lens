# GitHub Pages Migration Implementation Plan

## Overview

This document provides **exact, line-by-line instructions** for migrating from legacy GitHub Pages deployment (gh-pages branch) to the modern GitHub Actions artifact-based deployment method.

**Target audience**: @copilot-swe-agent[bot]

**Why this migration?**

- Eliminates the `gh-pages` branch and its commit history
- Uses GitHub's official deployment actions with OIDC tokens
- Better security (no need for `contents: write` permission)
- Aligns with GitHub's 2025 best practices

---

## Prerequisites

### Step 1: Update Repository Settings

**IMPORTANT**: This step must be completed **BEFORE** merging the workflow changes, or the deployment will fail.

1. Navigate to: `https://github.com/strawgate/kb-yaml-to-lens/settings/pages`
2. Under **"Build and deployment"** → **"Source"**
3. Change from **"Deploy from a branch"** to **"GitHub Actions"**

This enables the repository to accept deployments from GitHub Actions instead of the gh-pages branch.

---

## Implementation Instructions for Copilot

### File to Modify

**File path**: `.github/workflows/docs.yml`

**Current state**: Uses `mkdocs gh-deploy --force` to push to gh-pages branch (lines 34-43)

**Target state**: Use GitHub Actions artifacts with official `actions/deploy-pages` action

---

### Exact Changes Required

#### Change 1: Update Permissions Section

**Location**: Lines 13-14

**Current content**:

```yaml
permissions:
  contents: write
```

**Replace with**:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

**Explanation**: Modern deployment uses OIDC tokens (`id-token: write`) and Pages API (`pages: write`) instead of pushing commits (`contents: write`).

---

#### Change 2: Add Concurrency Control

**Location**: After the permissions section (insert new lines after line 14)

**Current content**: (concurrency section exists at lines 16-18)

**Keep existing**:

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

**Explanation**: Already correct - prevents concurrent deployments to Pages.

---

#### Change 3: Add Environment to Job

**Location**: Line 22 (after `runs-on: ubuntu-latest`)

**Current content**:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
```

**Replace with**:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
```

**Explanation**: Declares the deployment environment for GitHub Pages tracking.

---

#### Change 4: Remove Git Configuration Step

**Location**: Lines 34-37

**Current content**:

```yaml
      - name: Configure Git for deployment
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
```

**Action**: **DELETE these lines entirely**

**Explanation**: Git configuration is no longer needed since we're not pushing to a branch.

---

#### Change 5: Replace Deployment Step with Modern Actions

**Location**: Lines 42-43

**Current content**:

```yaml
      - name: Build and deploy documentation
        run: make docs-deploy
```

**Replace with**:

```yaml
      - name: Build documentation
        run: make docs-build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'site'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Explanation**:

- `make docs-build` builds the site to `site/` directory (instead of `make docs-deploy` which uses `mkdocs gh-deploy`)
- `actions/configure-pages@v4` configures Pages metadata
- `actions/upload-pages-artifact@v3` packages the `site/` directory as a deployment artifact
- `actions/deploy-pages@v4` deploys the artifact to GitHub Pages
- The `id: deployment` is referenced in the environment URL

---

### Complete Final File

After applying all changes above, `.github/workflows/docs.yml` should look like this:

```yaml
name: Deploy MkDocs to GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - 'src/**'
      - '.github/workflows/docs.yml'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python Environment
        uses: ./.github/actions/setup-python-env

      - name: Install documentation dependencies
        run: |
          uv sync --group docs

      - name: Compile documentation reference
        run: make compile-docs

      - name: Build documentation
        run: make docs-build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'site'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## Testing Instructions

After implementing the changes above:

### 1. Verify Workflow Syntax

The workflow file should be valid YAML with proper indentation.

### 2. Test the Deployment

1. Push the changes to the main branch
2. Navigate to: `https://github.com/strawgate/kb-yaml-to-lens/actions`
3. Verify the "Deploy MkDocs to GitHub Pages" workflow runs successfully
4. Check that all steps complete without errors
5. Verify the site is accessible at `https://strawgate.com`

### 3. Verify Custom Domain

The CNAME file in `docs/CNAME` containing `strawgate.com` will automatically be included in the built site and should continue to work.

---

## Rollback Plan

If the new workflow fails:

1. Revert the workflow file changes
2. Change repository settings back to "Deploy from a branch" → `gh-pages`
3. The gh-pages branch still exists (unless explicitly deleted) and can be used again

---

## Optional Cleanup (After Successful Deployment)

After confirming the new workflow works for at least one successful deployment:

```bash
# Delete the gh-pages branch
git push origin --delete gh-pages
```

This is optional and can be deferred until you're confident the new approach works.

---

## Files That Don't Need Changes

The following files work correctly with the new approach and should **NOT** be modified:

- `mkdocs.yml` - MkDocs configuration (no changes needed)
- `scripts/compile_docs.py` - Documentation compilation script (no changes needed)
- `docs/CNAME` - Custom domain configuration (automatically preserved in build)
- `Makefile` - All existing targets work correctly (we use `docs-build` instead of `docs-deploy`)

---

## Benefits of This Migration

| Benefit | Description |
|---------|-------------|
| **No branch pollution** | Eliminates the gh-pages branch and its commit history |
| **Better security** | Uses OIDC tokens instead of requiring write access to repository contents |
| **Official support** | Uses GitHub's official deployment actions |
| **Cleaner history** | Build artifacts aren't committed to version control |
| **Standard approach** | Aligns with GitHub's documented best practices for 2025 |

---

## References

- [Configuring a publishing source for GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [actions/deploy-pages](https://github.com/actions/deploy-pages)
- [MkDocs Material - Publishing your site](https://squidfunk.github.io/mkdocs-material/publishing-your-site/)

---

## Summary for Copilot

**@copilot**: Please update `.github/workflows/docs.yml` following the exact changes outlined in the "Exact Changes Required" section above:

1. Update permissions (lines 13-14)
2. Add environment to job (after line 22)
3. Delete git configuration step (lines 34-37)
4. Replace deployment step with modern actions (lines 42-43)

The complete final file structure is provided in the "Complete Final File" section for reference.
