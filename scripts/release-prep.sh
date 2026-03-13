#!/bin/bash
# Release Preparation Script
#
# Opens GitHub issues for pre-release review tasks. Each issue is designed
# to be triaged and worked on independently (e.g., by Claude Code via auto-triage).
#
# Usage:
#   ./scripts/release-prep.sh [version]
#
# Examples:
#   ./scripts/release-prep.sh 0.3.0
#   ./scripts/release-prep.sh          # uses current version from pyproject.toml

set -euo pipefail

REPO="strawgate/kb-yaml-to-lens"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Get version from argument or pyproject.toml
if [ $# -ge 1 ]; then
    VERSION="$1"
else
    VERSION=$(grep '^version' "$ROOT_DIR/pyproject.toml" | head -1 | sed 's/.*= *"\(.*\)"/\1/')
fi

echo "Preparing release v${VERSION}"

# Determine the last release tag for diff-scoped reviews
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
    DIFF_RANGE="${LAST_TAG}..HEAD"
    echo "Last release: ${LAST_TAG}"
    echo "Review scope: ${DIFF_RANGE}"
else
    DIFF_RANGE=""
    echo "No previous release tag found — issues will review the full codebase"
fi

echo "Creating pre-release review issues..."
echo

# Label for all release-prep issues
LABEL="release-prep"

# Ensure the label exists
gh label create "$LABEL" --repo "$REPO" --color "D4C5F9" --description "Pre-release preparation tasks" 2>/dev/null || true

# Build reusable diff context for issue bodies
if [ -n "$DIFF_RANGE" ]; then
    COMMIT_LOG=$(git log "$DIFF_RANGE" --oneline)
    COMMIT_COUNT=$(git rev-list --count "$DIFF_RANGE")
    CHANGED_FILES=$(git diff --stat "$DIFF_RANGE" | tail -1)
    CHANGED_DOCS=$(git diff --name-only "$DIFF_RANGE" -- '*.md' 'RELEASE.md' 'DEVELOPING.md' 'CONTRIBUTING.md' || true)
    RANGE_TEXT="since \`${LAST_TAG}\`"

    DIFF_CONTEXT_HEADER="### Scope

This review covers changes between \`${LAST_TAG}\` and \`HEAD\` (${COMMIT_COUNT} commits, ${CHANGED_FILES}).

<details>
<summary>Commit log</summary>

\`\`\`
${COMMIT_LOG}
\`\`\`

</details>"
else
    CHANGED_DOCS=""
    DIFF_CONTEXT_HEADER=""
    RANGE_TEXT="for the full codebase (no previous tag)"
fi

# ============================================================================
# Issue 1: Documentation Review
# ============================================================================
echo "Creating issue: Documentation Review..."

# Build doc-specific file list
if [ -n "$CHANGED_DOCS" ]; then
    DOC_FILE_LIST=$(echo "$CHANGED_DOCS" | sed 's/^/- [ ] `/' | sed 's/$/`/')
    DOC_SCOPE_NOTE="The following documentation files were modified ${RANGE_TEXT} and should be reviewed for accuracy:

${DOC_FILE_LIST}

Also check that any new features introduced in this release are documented."
else
    DOC_SCOPE_NOTE="No documentation files were modified ${RANGE_TEXT}. Check that any new features introduced in this release have adequate documentation."
fi

DOC_BODY="## Task

Review documentation for accuracy ahead of the v${VERSION} release.

${DIFF_CONTEXT_HEADER}

### Focus areas

${DOC_SCOPE_NOTE}

### What to look for

- Commands that reference \`make\` instead of \`just\` (or vice versa)
- Outdated version numbers or package names
- Broken links or references to removed files
- Missing documentation for new features
- Setup instructions that skip required steps
- Examples that no longer work

### How to find changed docs

\`\`\`bash
# Docs modified since last release
git diff --name-only ${DIFF_RANGE:-HEAD} -- '*.md'

# All commits touching docs
git log ${DIFF_RANGE:-HEAD} --oneline -- '*.md'
\`\`\`

### Definition of done

Open a PR fixing any issues found, or comment confirming all docs are accurate."

gh issue create --repo "$REPO" \
    --label "$LABEL" \
    --title "Release v${VERSION}: Documentation review" \
    --body "$DOC_BODY"

# ============================================================================
# Issue 2: Release Dry Run
# ============================================================================
echo "Creating issue: Release Dry Run..."

DRY_RUN_BODY="## Task

Perform a dry run of the release process to catch issues before tagging v${VERSION}.

${DIFF_CONTEXT_HEADER}

### Steps

1. **Version bump dry run**
   \`\`\`bash
   uv run scripts/bump-version.py patch --dry-run
   \`\`\`
   Verify all files that would be updated look correct.

2. **Full CI check**
   \`\`\`bash
   just all ci
   \`\`\`
   All tests, lints, and type checks must pass.

3. **Build all packages**
   \`\`\`bash
   just core build
   just tools build
   just lint build
   just cli build
   just vscode package
   \`\`\`
   Verify all packages build successfully.

4. **Docker build test**
   \`\`\`bash
   docker build -f packages/kb-dashboard-cli/Dockerfile -t kb-dashboard-compiler:test .
   \`\`\`

5. **Version consistency check**
   Verify all \`pyproject.toml\` and \`package.json\` files have the same version.

6. **Dependency pin check**
   Verify internal dependencies (e.g., kb-dashboard-core in kb-dashboard-cli) are pinned to the correct version.

### Definition of done

Comment with results of each step. If any step fails, open a PR to fix it."

gh issue create --repo "$REPO" \
    --label "$LABEL" \
    --title "Release v${VERSION}: Dry run of release steps" \
    --body "$DRY_RUN_BODY"

# ============================================================================
# Issue 3: Code Quality Scan
# ============================================================================
echo "Creating issue: Code Quality Scan..."

# Build changed-files context for code quality
QUALITY_FILE_CONTEXT=""
if [ -n "$DIFF_RANGE" ]; then
    QUALITY_FILE_CONTEXT="### Changed files to focus on

\`\`\`bash
# Python files changed ${RANGE_TEXT}
git diff --name-only ${DIFF_RANGE} -- '*.py'

# TypeScript files changed ${RANGE_TEXT}
git diff --name-only ${DIFF_RANGE} -- '*.ts' '*.tsx'

# Full diff for review
git diff ${DIFF_RANGE} -- '*.py' '*.ts' '*.tsx'
\`\`\`"
fi

QUALITY_BODY="## Task

Scan code changed ${RANGE_TEXT} for code smells, dead code, and quality issues before the v${VERSION} release.

${DIFF_CONTEXT_HEADER}

${QUALITY_FILE_CONTEXT}

### Areas to check (focused on changed code)

- [ ] **Dead code**: Unused functions, classes, imports, or variables in changed files
- [ ] **TODO/FIXME/HACK comments**: Review and resolve or convert to issues
- [ ] **Commented-out code**: Remove or restore
- [ ] **Inconsistent error handling**: Missing error messages, swallowed exceptions
- [ ] **Type safety**: Any \`type: ignore\` comments that can be resolved, \`Any\` types that should be narrowed
- [ ] **Test coverage gaps**: Important code paths without tests (especially new features)
- [ ] **Dependency health**: Outdated or vulnerable dependencies

### Commands to run

\`\`\`bash
# Find TODOs/FIXMEs in changed files
git diff --name-only ${DIFF_RANGE:-HEAD} -- '*.py' '*.ts' | xargs rg 'TODO|FIXME|HACK|XXX' || true

# Find type: ignore in changed Python files
git diff --name-only ${DIFF_RANGE:-HEAD} -- '*.py' | xargs rg 'type: ignore' || true

# Run linters (full suite)
just core lint
just cli lint
just tools lint
just lint lint
just vscode lint
\`\`\`

### Definition of done

Open PRs for any fixes, or comment confirming the changed code is clean."

gh issue create --repo "$REPO" \
    --label "$LABEL" \
    --title "Release v${VERSION}: Code quality scan" \
    --body "$QUALITY_BODY"

# ============================================================================
# Issue 4: Test Suite Review
# ============================================================================
echo "Creating issue: Test Suite Review..."

TEST_BODY="## Task

Review the test suite for completeness and reliability before the v${VERSION} release, with focus on changes ${RANGE_TEXT}.

${DIFF_CONTEXT_HEADER}

### Checks

- [ ] **All tests pass**: \`just all ci\`
- [ ] **New/modified features have tests**: Review changed source files and verify test coverage
- [ ] **New/modified tests are correct**: Review changed test files for correctness
- [ ] **Flaky tests**: Identify any tests that fail intermittently
- [ ] **Example dashboards compile**: All YAML files in \`packages/kb-dashboard-docs/content/examples/\` should compile without errors
- [ ] **E2E tests**: Run \`just cli test-e2e\` and \`just vscode test-e2e\` if environments are available

### How to find what changed

\`\`\`bash
# Test files changed ${RANGE_TEXT}
git diff --name-only ${DIFF_RANGE:-HEAD} -- '*test*' '*tests*'

# Source files changed (check these have test coverage)
git diff --name-only ${DIFF_RANGE:-HEAD} -- '*.py' '*.ts' | grep -v test

# Feature commits that should have tests
git log ${DIFF_RANGE:-HEAD} --oneline --grep='feat:'
\`\`\`

### Commands

\`\`\`bash
# Run all unit tests
just core test
just cli test
just tools test
just lint test

# Test example dashboards
just cli test-e2e

# Run doctest examples
just core test  # includes doctests
\`\`\`

### Definition of done

Comment confirming all tests pass and coverage is adequate for new features."

gh issue create --repo "$REPO" \
    --label "$LABEL" \
    --title "Release v${VERSION}: Test suite review" \
    --body "$TEST_BODY"

# ============================================================================
# Issue 5: CHANGELOG / Release Notes Draft
# ============================================================================
echo "Creating issue: Release Notes Draft..."
RELEASE_NOTES_BODY="## Task

Draft release notes for v${VERSION} based on changes ${RANGE_TEXT}.

${DIFF_CONTEXT_HEADER}

### Steps

1. Review commits since last tag:
   \`\`\`bash
   git log ${DIFF_RANGE:-HEAD} --oneline
   git diff --stat ${DIFF_RANGE:-HEAD}
   \`\`\`

2. Categorize changes:
   - **New Features**: \`feat:\` commits
   - **Bug Fixes**: \`fix:\` commits
   - **Breaking Changes**: Any API or config format changes
   - **Documentation**: \`docs:\` commits
   - **Internal**: \`refactor:\`, \`chore:\`, \`ci:\` commits

3. Write user-facing release notes highlighting:
   - What's new and why it matters
   - Migration steps for any breaking changes
   - Notable bug fixes

4. Post the draft as a comment on this issue for review.

### Definition of done

Release notes draft reviewed and approved."
gh issue create --repo "$REPO" \
    --label "$LABEL" \
    --title "Release v${VERSION}: Draft release notes" \
    --body "$RELEASE_NOTES_BODY"

echo
echo "Done! Created 5 release-prep issues for v${VERSION}."
echo "View them at: https://github.com/${REPO}/labels/release-prep"
