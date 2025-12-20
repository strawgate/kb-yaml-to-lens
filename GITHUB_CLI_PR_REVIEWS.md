# GitHub PR Review Interaction via GitHub CLI

This document explains how Claude interacts with pull request reviews using the GitHub CLI (`gh`).

## Overview

Claude can interact with pull request reviews, including:
- ✅ Adding comments to PRs
- ✅ Replying to CodeRabbit feedback
- ✅ Adding review comments
- ✅ Resolving review conversation threads
- ✅ Approving PRs

## Implementation

Claude has access to `gh` CLI commands through the Bash tool allowlist in the GitHub Actions workflows.

### Enabled Commands

The workflows allow Claude to run any `gh` command:
```yaml
--allowed-tools Bash(make:*,gh:*)
```

### Key Commands

#### Add a comment to a PR
```bash
gh pr comment <pr-number> --body "Your comment text"
```

#### Add a review comment
```bash
gh pr review <pr-number> --comment --body "Your review comment"
```

#### Approve a PR
```bash
gh pr review <pr-number> --approve
```

#### Get review threads (including CodeRabbit comments)
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

#### Resolve a review thread
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

## Usage Example

Simply mention `@claude` in a PR comment:

```
@claude please address the CodeRabbit feedback about error handling
```

Claude will:
1. Use `gh api graphql` to fetch review threads and find CodeRabbit's comments
2. Make necessary code changes
3. Use `gh pr comment` to reply to the feedback
4. Use `gh api graphql` to resolve the conversation thread

## Advantages of the GitHub CLI Approach

- **No custom code**: Uses the standard GitHub CLI already available in GitHub Actions
- **Simple**: No dependencies to install (besides `gh` which is pre-installed)
- **Flexible**: Full access to GitHub's REST and GraphQL APIs
- **Maintainable**: GitHub maintains the CLI, we don't maintain custom code
- **Well-documented**: Extensive documentation at https://cli.github.com/

## Permissions

The workflows already have the necessary permissions:
- `pull-requests: write` - For creating comments and reviews
- `contents: write` - For making code changes

## Environment

The `GITHUB_TOKEN` is automatically provided by GitHub Actions with appropriate permissions.
