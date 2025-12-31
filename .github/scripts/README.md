# GitHub Workflow Helper Scripts

This directory contains reusable bash scripts for common GitHub API operations used across workflows.

## Purpose

These scripts consolidate repetitive GitHub API calls and bash logic that was previously duplicated across multiple workflow files. Benefits:

- **Testability**: Scripts can be tested independently
- **Maintainability**: Update logic in one place instead of multiple workflows
- **Readability**: Workflows become cleaner with high-level script calls
- **Reusability**: Same scripts work in workflows and local development

## Available Scripts

### Review Thread Management

#### `gh-get-review-threads.sh`

Get PR review threads with comments.

```bash
gh-get-review-threads.sh OWNER REPO PR_NUMBER [AUTHOR_FILTER]

# Examples:
gh-get-review-threads.sh strawgate kb-yaml-to-lens 426
gh-get-review-threads.sh strawgate kb-yaml-to-lens 426 "coderabbitai[bot]"
```

#### `gh-resolve-review-thread.sh`

Resolve a review thread by ID.

```bash
gh-resolve-review-thread.sh THREAD_ID

# Example:
gh-resolve-review-thread.sh "RT_kwDONHvqdc4BmRst"
```

### Review Management

#### `gh-get-latest-review.sh`

Get the latest review from a specific author.

```bash
gh-get-latest-review.sh OWNER REPO PR_NUMBER AUTHOR

# Example:
gh-get-latest-review.sh strawgate kb-yaml-to-lens 426 "coderabbitai[bot]"
```

#### `gh-check-latest-review.sh`

Check if a review ID is the latest from a specific author. Exits 0 if latest, 1 if newer exists.

```bash
gh-check-latest-review.sh OWNER REPO PR_NUMBER AUTHOR CURRENT_REVIEW_ID

# Example:
if gh-check-latest-review.sh strawgate kb-yaml-to-lens 426 "coderabbitai[bot]" 12345; then
  echo "Proceeding with work..."
else
  echo "Skipping - newer review exists"
fi
```

### Comment Management

#### `gh-get-comments-since.sh`

Get comments created after a specific timestamp.

```bash
gh-get-comments-since.sh OWNER REPO ISSUE_NUMBER SINCE_TIMESTAMP [AUTHOR_FILTER]

# Examples:
gh-get-comments-since.sh strawgate kb-yaml-to-lens 426 "2025-12-30T22:43:14Z"
gh-get-comments-since.sh strawgate kb-yaml-to-lens 426 "2025-12-30T22:43:14Z" "strawgate"
```

#### `gh-minimize-outdated-comments.sh`

Minimize all but the most recent comment/review from each author.

```bash
gh-minimize-outdated-comments.sh OWNER REPO PR_NUMBER

# Example:
gh-minimize-outdated-comments.sh strawgate kb-yaml-to-lens 426
```

### PR and Issue Management

#### `gh-get-pr-info.sh`

Get PR information via GitHub GraphQL API.

```bash
gh-get-pr-info.sh OWNER REPO PR_NUMBER [FIELD]

# Examples:
gh-get-pr-info.sh strawgate kb-yaml-to-lens 456              # All fields as JSON
gh-get-pr-info.sh strawgate kb-yaml-to-lens 456 headRef     # Just the branch name
gh-get-pr-info.sh strawgate kb-yaml-to-lens 456 isDraft     # Just draft status
```

Available fields: `headRef`, `baseRef`, `author`, `state`, `isDraft`, `title`, `body`, `url`

#### `gh-post-pr-comment.sh`

Post a comment to a PR or issue.

```bash
gh-post-pr-comment.sh OWNER REPO NUMBER BODY

# Example:
gh-post-pr-comment.sh strawgate kb-yaml-to-lens 456 "✅ All checks passed"
```

#### `gh-create-issue-report.sh`

Create a new issue with structured content.

```bash
gh-create-issue-report.sh OWNER REPO TITLE BODY [LABELS]

# Examples:
gh-create-issue-report.sh strawgate kb-yaml-to-lens "Bug Report" "Description here"
gh-create-issue-report.sh strawgate kb-yaml-to-lens "Feature Request" "Description" "enhancement,help-wanted"
```

#### `gh-close-issue-with-comment.sh`

Close an issue with a comment.

```bash
gh-close-issue-with-comment.sh OWNER REPO ISSUE_NUMBER COMMENT

# Example:
gh-close-issue-with-comment.sh strawgate kb-yaml-to-lens 123 "Closing as completed"
```

### Utility Scripts

#### `gh-parse-repo.sh`

Parse repository owner and name from `OWNER/REPO` format.

```bash
gh-parse-repo.sh REPOSITORY [owner|repo|both]

# Examples:
gh-parse-repo.sh strawgate/kb-yaml-to-lens           # Output: strawgate kb-yaml-to-lens
gh-parse-repo.sh strawgate/kb-yaml-to-lens owner     # Output: strawgate
gh-parse-repo.sh strawgate/kb-yaml-to-lens repo      # Output: kb-yaml-to-lens
```

## Usage in Workflows

### Before (Duplicated Logic)

```yaml
# In claude-address-coderabbit-feedback.yml
run: |
  LATEST_REVIEW=$(gh api graphql -f query='...' ...)
  LATEST_REVIEW_ID=$(echo "$LATEST_REVIEW" | jq -r '...')
  # ... 20+ lines of bash
```

### After (Using Helper Scripts)

```yaml
# In workflow file
run: |
  .github/scripts/gh-check-latest-review.sh \
    "${{ github.repository_owner }}" \
    "${{ github.event.repository.name }}" \
    "${{ github.event.pull_request.number }}" \
    "coderabbitai[bot]" \
    "${{ github.event.review.id }}" || exit 0
```

## Environment Requirements

All scripts require:

- `gh` CLI tool (GitHub CLI)
- `jq` for JSON processing
- `GITHUB_TOKEN` environment variable (automatically available in GitHub Actions)

## Testing

Scripts can be tested locally with a GitHub token:

```bash
export GITHUB_TOKEN="your_token_here"

# Test getting review threads
.github/scripts/gh-get-review-threads.sh strawgate kb-yaml-to-lens 426

# Test checking latest review
.github/scripts/gh-check-latest-review.sh strawgate kb-yaml-to-lens 426 "coderabbitai[bot]" 12345
```

## Updating Workflows

To use these scripts in workflows, @copilot can update workflow files (Claude cannot due to GitHub App permissions).

Example request for @copilot:

> @copilot In `.github/workflows/claude-address-coderabbit-feedback.yml`, replace lines 45-78 with:
>
> ```yaml
> run: |
>   .github/scripts/gh-check-latest-review.sh \
>     "${{ github.repository_owner }}" \
>     "${{ github.event.repository.name }}" \
>     "${{ github.event.pull_request.number }}" \
>     "coderabbitai[bot]" \
>     "${{ github.event.review.id }}" || exit 0
> ```

## Contributing

When adding new scripts:

1. Follow the existing naming convention: `gh-{action}-{resource}.sh`
2. Include a header comment with usage, arguments, and output format
3. Use `set -euo pipefail` for safety
4. Validate required arguments with `${VAR:?Error message}`
5. Document the script in this README
6. Make the script executable: `chmod +x .github/scripts/your-script.sh`
