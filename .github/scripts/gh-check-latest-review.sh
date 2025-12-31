#!/usr/bin/env bash
set -euo pipefail

# Check if a given review ID is the latest review from a specific author
# Exit 0 if it is the latest, exit 1 if a newer review exists
#
# Usage:
#   gh-check-latest-review.sh OWNER REPO PR_NUMBER AUTHOR CURRENT_REVIEW_ID
#
# Arguments:
#   OWNER             - Repository owner
#   REPO              - Repository name
#   PR_NUMBER         - Pull request number
#   AUTHOR            - Review author login to filter by (e.g., "coderabbitai[bot]")
#   CURRENT_REVIEW_ID - The review ID to check
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Exit codes:
#   0 - Current review is the latest
#   1 - A newer review exists
#
# Output:
#   Prints status message to stdout

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
PR_NUMBER="${3:?PR number required}"
AUTHOR="${4:?Author required}"
CURRENT_REVIEW_ID="${5:?Current review ID required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LATEST_REVIEW=$("$SCRIPT_DIR/gh-get-latest-review.sh" "$OWNER" "$REPO" "$PR_NUMBER" "$AUTHOR")

if [ -z "$LATEST_REVIEW" ]; then
  echo "✓ No reviews found from $AUTHOR"
  exit 0
fi

LATEST_REVIEW_ID=$(echo "$LATEST_REVIEW" | jq -r '.databaseId // empty')

if [ -z "$LATEST_REVIEW_ID" ]; then
  echo "✓ No review ID found"
  exit 0
fi

if [ "$LATEST_REVIEW_ID" != "$CURRENT_REVIEW_ID" ]; then
  echo "⚠️ A newer $AUTHOR review exists (ID: $LATEST_REVIEW_ID)"
  echo "⚠️ Current review ID: $CURRENT_REVIEW_ID"
  echo "⚠️ Skipping - the newer review will be or is being processed"
  exit 1
fi

echo "✓ This is the most recent $AUTHOR review (ID: $CURRENT_REVIEW_ID)"
exit 0
