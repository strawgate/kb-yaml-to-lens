#!/usr/bin/env bash
set -euo pipefail

# Close an issue with a comment
#
# Usage:
#   gh-close-issue-with-comment.sh OWNER REPO ISSUE_NUMBER COMMENT
#
# Arguments:
#   OWNER         - Repository owner
#   REPO          - Repository name
#   ISSUE_NUMBER  - Issue number to close
#   COMMENT       - Comment to post when closing (markdown supported)
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   Success message with issue URL

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
ISSUE_NUMBER="${3:?Issue number required}"
COMMENT="${4:?Comment required}"

# Post the comment
gh issue comment "$ISSUE_NUMBER" \
  --repo "$OWNER/$REPO" \
  --body "$COMMENT"

# Close the issue
gh issue close "$ISSUE_NUMBER" \
  --repo "$OWNER/$REPO"

echo "Issue #$ISSUE_NUMBER closed with comment"
