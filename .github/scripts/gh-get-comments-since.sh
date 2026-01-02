#!/usr/bin/env bash
set -euo pipefail

# Get PR/issue comments created after a specific timestamp
#
# Usage:
#   gh-get-comments-since.sh [--pr] OWNER REPO ISSUE_NUMBER SINCE_TIMESTAMP [AUTHOR_FILTER]
#
# Arguments:
#   --pr            - Optional: also fetch PR review comments (for PRs only)
#   OWNER           - Repository owner
#   REPO            - Repository name
#   ISSUE_NUMBER    - Issue or PR number
#   SINCE_TIMESTAMP - ISO 8601 timestamp (e.g., "2025-12-30T22:43:14Z")
#   AUTHOR_FILTER   - Optional: filter comments by author login
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   JSON array of comments created after the timestamp

# Check for --pr flag
IS_PR=false
if [[ "${1:-}" == "--pr" ]]; then
  IS_PR=true
  shift
fi

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
ISSUE_NUMBER="${3:?Issue number required}"
SINCE_TIMESTAMP="${4:?Since timestamp required}"

# Basic ISO 8601 validation (YYYY-MM-DDTHH:MM:SSZ)
if [[ ! "$SINCE_TIMESTAMP" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
  echo "Error: SINCE_TIMESTAMP must be in ISO 8601 format (e.g., 2025-12-30T22:43:14Z)" >&2
  exit 1
fi

AUTHOR_FILTER="${5:-}"

if [[ "$IS_PR" == true ]]; then
  # For PRs: fetch both issue comments AND PR review comments, then merge and sort
  ISSUE_COMMENTS=$(gh api "/repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/comments?since=$SINCE_TIMESTAMP")
  PR_REVIEW_COMMENTS=$(gh api "/repos/$OWNER/$REPO/pulls/$ISSUE_NUMBER/comments?since=$SINCE_TIMESTAMP")

  # Merge both arrays, sort by created_at, and apply author filter
  jq --arg author "$AUTHOR_FILTER" -s '
    (.[0] + .[1]) |
    sort_by(.created_at) |
    if $author != "" then map(select(.user.login == $author)) else . end
  ' <(echo "$ISSUE_COMMENTS") <(echo "$PR_REVIEW_COMMENTS")
else
  # For issues: only fetch issue comments
  gh api "/repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/comments?since=$SINCE_TIMESTAMP" | \
  jq --arg author "$AUTHOR_FILTER" 'if $author != "" then map(select(.user.login == $author)) else . end'
fi
