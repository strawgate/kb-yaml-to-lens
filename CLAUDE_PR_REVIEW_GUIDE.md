# GitHub PR Review Interaction - Quick Reference

This document provides a quick reference for using Claude's new PR review interaction capabilities.

## Overview

Claude can now interact with pull request reviews, including:
- ✅ Replying to CodeRabbit feedback
- ✅ Replying to any PR review comments
- ✅ Resolving review conversation threads
- ✅ Unresolving review conversation threads
- ✅ Viewing all review threads and their status

## How to Use

### Step 1: Mention Claude in a PR Comment

Simply mention `@claude` in any PR comment or review, and Claude will be invoked with access to the PR review tools.

### Step 2: Claude Automatically Uses the Tools

When Claude processes your request, it has access to these MCP server tools:

#### `get_pr_review_threads(owner, repo, pull_number)`
Get all review threads with their resolved status and thread IDs. Useful for finding what needs to be addressed.

#### `get_pr_review_comments(owner, repo, pull_number)`
Get all review comments with comment IDs needed for replying.

#### `reply_to_review_comment(owner, repo, pull_number, comment_id, body)`
Reply to a specific review comment (including CodeRabbit's feedback).

#### `resolve_review_thread(thread_id)`
Mark a review thread as resolved after addressing the feedback.

#### `unresolve_review_thread(thread_id)`
Reopen a previously resolved review thread.

## Example Workflows

### Example 1: Reply to CodeRabbit Feedback
```
@claude please address the CodeRabbit feedback about error handling in utils.py
```

Claude will:
1. Get the PR review comments
2. Find CodeRabbit's comment about error handling
3. Make the necessary code changes
4. Reply to CodeRabbit's comment explaining the fix
5. Resolve the conversation thread

### Example 2: Resolve Multiple Conversations
```
@claude please review all open CodeRabbit threads and resolve the ones that have been addressed
```

Claude will:
1. Get all review threads
2. Check which ones have been addressed in the code
3. Reply to each with confirmation
4. Resolve the threads

### Example 3: Discuss Feedback
```
@claude what do you think about CodeRabbit's suggestion to use a different data structure?
```

Claude will:
1. Get the review comments
2. Analyze the suggestion
3. Reply to CodeRabbit's comment with its analysis
4. Keep the thread open for further discussion

## Technical Details

### MCP Server Implementation

The PR review functionality is provided by a custom MCP server located at:
```
scripts/github_pr_mcp_server.py
```

This server uses:
- **GitHub REST API** for replying to comments
- **GitHub GraphQL API** for resolving/unresolving threads

### Workflow Integration

The MCP server is configured in:
- `.github/workflows/claude-on-mention.yml`
- `.github/workflows/claude-on-open-label.yml`

Required dependencies:
- `fastmcp` - MCP server framework
- `httpx` - Async HTTP client

### Permissions

The server uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions with:
- `pull-requests: write` - For creating comments and resolving threads
- `contents: read` - For reading repository content

## Troubleshooting

### Claude says it can't interact with reviews
- Check that the workflow has `pull-requests: write` permission
- Verify the MCP server script is present in `scripts/` directory
- Ensure `fastmcp` and `httpx` are installed in the workflow

### Thread resolution doesn't work
- Thread IDs must be the GraphQL node ID (starts with "PRRT_")
- Use `get_pr_review_threads` to get the correct thread IDs

### Comment replies aren't appearing
- Comment IDs must be the REST API ID (numeric)
- Use `get_pr_review_comments` to get comment IDs

## For More Details

See `CODERABBIT_INTERACTION_REQUIREMENTS.md` for:
- Complete implementation details
- API reference
- Alternative implementation options
- Troubleshooting guide
