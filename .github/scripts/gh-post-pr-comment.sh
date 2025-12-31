#!/usr/bin/env bash
set -euo pipefail

# Post a comment to a PR or issue via GitHub API
#
# Usage:
#   gh-post-pr-comment.sh OWNER REPO NUMBER BODY
#
# Arguments:
#   OWNER    - Repository owner
#   REPO     - Repository name
#   NUMBER   - PR or issue number
#   BODY     - Comment body (markdown supported)
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   Comment URL on success

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
NUMBER="${3:?Issue/PR number required}"
BODY="${4:?Comment body required}"

gh api \
  "repos/$OWNER/$REPO/issues/$NUMBER/comments" \
  -f body="$BODY" \
  --jq '.html_url'
