#!/usr/bin/env bash
set -euo pipefail

# Resolve a GitHub PR review thread
#
# Usage:
#   gh-resolve-review-thread.sh THREAD_ID
#
# Arguments:
#   THREAD_ID - The GraphQL node ID of the review thread to resolve
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   JSON response with thread resolution status

THREAD_ID="${1:?Thread ID required}"

gh api graphql -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: {threadId: $threadId}) {
      thread {
        id
        isResolved
      }
    }
  }' -f threadId="$THREAD_ID" --jq '.data.resolveReviewThread.thread'
