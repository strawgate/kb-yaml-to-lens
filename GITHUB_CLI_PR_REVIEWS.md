# GitHub PR Review Thread Resolution via GitHub CLI

This document explains how Claude resolves review threads in pull requests using the GitHub CLI (`gh`).

## Overview

Claude can resolve review conversation threads in PRs after addressing feedback from CodeRabbit or other reviewers.

**Important**: Claude will NOT add comments or reviews to PRs. It can only resolve threads after making code changes that address the feedback.

## Implementation

Claude has restricted access to `gh api` commands via the Bash tool allowlist:
```yaml
--allowed-tools Bash(make:*,gh:api:*)
```

This allows only `gh api` for GraphQL operations, preventing Claude from using:
- ❌ `gh pr comment` - Blocked to prevent random comments
- ❌ `gh pr review` - Blocked to prevent unsolicited reviews
- ✅ `gh api graphql` - Allowed for resolving threads only

## Key Commands

### Get review threads (including CodeRabbit comments)
```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: PR_NUMBER) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            path
            line
            comments(first: 10) {
              nodes {
                body
                author { login }
              }
            }
          }
        }
      }
    }
  }' -f owner=OWNER -f name=REPO -F number=PR_NUMBER
```

### Resolve a review thread
```bash
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "THREAD_ID"}) {
      thread {
        id
        isResolved
      }
    }
  }'
```

## Workflow

When Claude is asked to address review feedback:

1. **Read the feedback** - Uses GitHub MCP tools to view the PR and reviews
2. **Make code changes** - Edits files to address the feedback
3. **Fetch thread IDs** - Uses `gh api graphql` to get review threads
4. **Resolve threads** - Uses `gh api graphql` mutation to mark addressed threads as resolved

Claude will **not** add its own comments explaining the changes. The code changes themselves serve as the response to the feedback.

## Usage Example

```
@claude please address the CodeRabbit feedback about error handling
```

Claude will:
1. View the CodeRabbit review comments
2. Make necessary code changes to fix error handling
3. Identify the relevant review thread ID
4. Resolve the thread using GraphQL mutation

**Note**: No comment is added to the PR. The resolved thread status indicates the feedback was addressed.

## Advantages

- ✅ **Focused**: Only thread resolution, no comment spam
- ✅ **Clean**: Code changes speak for themselves
- ✅ **Simple**: Uses GitHub's official CLI
- ✅ **Safe**: Cannot accidentally add unwanted comments or reviews

## Permissions

The workflows have the necessary permissions:
- `pull-requests: write` - For resolving threads
- `contents: write` - For making code changes

The `GITHUB_TOKEN` is automatically provided by GitHub Actions.
