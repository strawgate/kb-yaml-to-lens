# Updated Workflow Files

This directory contains updated GitHub workflow files that use the helper scripts in `.github/scripts/`.

## Files

### tidy-pr.yml

**Original size:** 110 lines
**New size:** 32 lines
**Reduction:** ~71%

Simplified workflow that uses `gh-minimize-outdated-comments.sh` to minimize all but the most recent comment from each author on a PR.

**Benefits:**

- Dramatically reduced code complexity
- Centralized logic in tested helper script
- Easier to maintain and understand
- More readable workflow file

### claude-address-coderabbit-feedback.yml

**Original size:** 222 lines
**New size:** 136 lines
**Reduction:** 39%

Refactored workflow that uses helper scripts for common GitHub API operations:

- `gh-check-latest-review.sh` - Check if a review is the most recent
- `gh-get-latest-review.sh` - Get the latest review from an author
- `gh-get-review-threads.sh` - Fetch review threads with optional author filter
- `gh-resolve-review-thread.sh` - Resolve a review thread

**Benefits:**

- Reduced duplication of bash/GraphQL code
- Consistent error handling across operations
- Testable helper scripts
- More maintainable prompt text

### claude-project-manager-report.yml

**Original size:** 208 lines
**New size:** 211 lines
**Changes:** Updated to use helper scripts

Workflow that generates daily project manager reports. Updated to use:

- `make gh-close-issue-with-comment` - Close previous PM issue with comment
- `make gh-create-issue-report` - Create new PM report issue

**Benefits:**

- Consistent with other workflows in using helper scripts
- More maintainable and testable GitHub API operations
- Clearer separation of concerns

### claude-on-mention-create-issues.yml

**Original size:** 55 lines
**New size:** 53 lines
**Changes:** Updated prompt to reference helper scripts

Workflow for creating issues via @claude-issue mentions. Updated prompt to document:

- `make gh-create-issue-report` - Create issues with proper formatting

**Benefits:**

- Claude now knows to use the standardized helper instead of raw `gh issue create`
- More consistent issue creation across workflows

### claude-on-mention-assist.yml

**Original size:** 50 lines
**New size:** 60 lines
**Changes:** Added helper script documentation to prompt

Workflow for @claude mentions. Updated prompt to document all available GitHub helpers:

- `make gh-get-pr-info` - Get PR information
- `make gh-post-pr-comment` - Post PR comments
- `make gh-create-issue-report` - Create issues
- `make gh-close-issue-with-comment` - Close issues with comments
- `make gh-get-review-threads` - Get review threads
- `make gh-resolve-review-thread` - Resolve review threads
- `make gh-get-latest-review` - Get latest review
- `make gh-check-latest-review` - Check if review is latest

**Benefits:**

- Claude is aware of all available helper scripts
- Encourages use of standardized helpers over raw API calls
- Better documentation for users reading the workflow

### claude-on-merge-conflict.yml

**Original size:** 103 lines
**New size:** 110 lines
**Changes:** Updated to use helper scripts

Workflow for automatic merge conflict resolution. Updated to use:

- `make gh-post-pr-comment` - Post resolution status to PR

**Benefits:**

- Consistent PR commenting across workflows
- Simpler and more maintainable

### claude-on-open-or-label.yml

**Original size:** 118 lines
**New size:** 117 lines
**Changes:** No changes (workflow doesn't make direct GitHub API calls)

Issue triage workflow. This workflow doesn't make GitHub API calls directly in the workflow file, so no changes were needed. Claude will use the helper scripts when appropriate based on its allowed-tools configuration.

## Migration Instructions

To apply these updated workflows:

1. **Review the changes** - Compare the files in this directory with `.github/workflows/`
2. **Test locally** - The helper scripts can be tested independently using `make` targets
3. **Replace workflows** - Copy these files to `.github/workflows/`:

   ```bash
   mkdir -p .github/workflows
   cp GitHub/tidy-pr.yml .github/workflows/
   cp GitHub/claude-address-coderabbit-feedback.yml .github/workflows/
   cp GitHub/claude-project-manager-report.yml .github/workflows/
   cp GitHub/claude-on-mention-create-issues.yml .github/workflows/
   cp GitHub/claude-on-mention-assist.yml .github/workflows/
   cp GitHub/claude-on-merge-conflict.yml .github/workflows/
   cp GitHub/claude-on-open-or-label.yml .github/workflows/
   ```

4. **Commit and test** - Commit the changes and verify workflows run correctly

## Testing

The helper scripts have been tested for:

- ✅ Syntax validation (bash -n)
- ✅ Error handling (missing arguments)
- ✅ Basic functionality (parsing, output format)

**Note:** Full integration testing requires a valid GITHUB_TOKEN and actual PR/issue data.

## Helper Script Documentation

See `.github/scripts/README.md` for comprehensive documentation on all helper scripts, including:

- Usage examples
- Input/output formats
- Error handling
- Local testing instructions
