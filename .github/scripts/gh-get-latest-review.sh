#!/usr/bin/env bash
set -euo pipefail

# Get the latest review from a specific author on a PR
#
# Usage:
#   gh-get-latest-review.sh OWNER REPO PR_NUMBER AUTHOR
#
# Arguments:
#   OWNER      - Repository owner
#   REPO       - Repository name
#   PR_NUMBER  - Pull request number
#   AUTHOR     - Review author login to filter by (e.g., "coderabbitai[bot]")
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   JSON object with latest review from specified author, or empty if none found
#   Fields: databaseId, createdAt, author.login
#
# Limitations:
#   - Only checks the last 10 reviews (older reviews are not considered)
#   - This limit optimizes performance for typical PR review workflows

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
PR_NUMBER="${3:?PR number required}"
AUTHOR="${4:?Author required}"

gh api graphql -f query='
  query($owner: String!, $repo: String!, $prNumber: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $prNumber) {
        reviews(last: 10, states: [CHANGES_REQUESTED, APPROVED, COMMENTED]) {
          nodes {
            databaseId
            createdAt
            author { login }
          }
        }
      }
    }
  }' -F owner="$OWNER" \
     -F repo="$REPO" \
     -F prNumber="$PR_NUMBER" \
     --jq '.data.repository.pullRequest.reviews.nodes' | \
jq --arg author "$AUTHOR" '
  map(select(.author.login == $author))
  | sort_by(.createdAt)
  | last // empty'
