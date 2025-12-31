#!/usr/bin/env bash
set -euo pipefail

# Get PR review threads with comments via GitHub GraphQL API
#
# Usage:
#   gh-get-review-threads.sh OWNER REPO PR_NUMBER [FILTER]
#
# Arguments:
#   OWNER       - Repository owner
#   REPO        - Repository name
#   PR_NUMBER   - Pull request number
#   FILTER      - Optional: filter for unresolved threads from specific author
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   JSON array of review threads with nested comments

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
PR_NUMBER="${3:?PR number required}"
FILTER="${4:-}" # Optional: e.g., "coderabbitai[bot]" for unresolved CodeRabbit threads

gh api graphql -f query='
  query($owner: String!, $repo: String!, $prNumber: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $prNumber) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            isOutdated
            path
            line
            comments(first: 10) {
              nodes {
                id
                body
                author { login }
                createdAt
              }
            }
          }
        }
      }
    }
  }' -F owner="$OWNER" \
     -F repo="$REPO" \
     -F prNumber="$PR_NUMBER" \
     --jq '.data.repository.pullRequest.reviewThreads.nodes' | \
if [ -n "$FILTER" ]; then
  jq --arg author "$FILTER" '
    map(select(
      .isResolved == false and
      .comments.nodes | any(.author.login == $author)
    ))'
else
  cat
fi
