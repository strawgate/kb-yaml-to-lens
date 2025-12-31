# Updated Workflow Files

This directory contains updated GitHub workflow files that use the helper scripts in `.github/scripts/`.

## Files

### tidy-pr.yml

**Original size:** 110 lines
**New size:** 28 lines
**Reduction:** ~75%

Simplified workflow that uses `gh-minimize-outdated-comments.sh` to minimize all but the most recent comment from each author on a PR.

**Benefits:**

- Dramatically reduced code complexity
- Centralized logic in tested helper script
- Easier to maintain and understand
- More readable workflow file

### claude-address-coderabbit-feedback.yml

**Original size:** 222 lines
**New size:** 140 lines
**Reduction:** 37%

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

## Migration Instructions

To apply these updated workflows:

1. **Review the changes** - Compare the files in this directory with `.github/workflows/`
2. **Test locally** - The helper scripts can be tested independently using `make` targets
3. **Replace workflows** - Copy these files to `.github/workflows/`:

   ```bash
   mkdir -p .github/workflows
   cp GitHub/tidy-pr.yml .github/workflows/
   cp GitHub/claude-address-coderabbit-feedback.yml .github/workflows/
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

## Migration Guide

For detailed step-by-step instructions on migrating other workflows, see `.github/scripts/MIGRATION_GUIDE.md`.
