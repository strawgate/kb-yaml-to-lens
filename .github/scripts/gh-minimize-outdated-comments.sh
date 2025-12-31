#!/usr/bin/env bash
set -euo pipefail

# Minimize all but the most recent comment/review from each author on a PR
#
# Usage:
#   gh-minimize-outdated-comments.sh OWNER REPO PR_NUMBER
#
# Arguments:
#   OWNER      - Repository owner
#   REPO       - Repository name
#   PR_NUMBER  - Pull request number
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   Status messages showing what was minimized

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
PR_NUMBER="${3:?PR number required}"

echo "Fetching comments and reviews for PR #${PR_NUMBER}..."

QUERY='
query($owner: String!, $repo: String!, $prNumber: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $prNumber) {
      comments(first: 100) {
        nodes {
          id
          author { login }
          createdAt
          isMinimized
        }
      }
      reviews(first: 100) {
        nodes {
          id
          author { login }
          createdAt
          comments(first: 100) {
            nodes {
              id
              author { login }
              createdAt
              isMinimized
            }
          }
        }
      }
    }
  }
}'

RESPONSE=$(gh api graphql -f query="$QUERY" -f owner="$OWNER" -f repo="$REPO" -F prNumber="$PR_NUMBER")

TO_MINIMIZE=$(echo "$RESPONSE" | jq -r '
  # Extract all comments with their metadata
  [
    (.data.repository.pullRequest.comments.nodes // []) +
    (.data.repository.pullRequest.reviews.nodes // [] | map(.comments.nodes // []) | add // []) +
    (.data.repository.pullRequest.reviews.nodes // [])
  ] | add
  # Filter out already minimized and null authors
  | map(select(.isMinimized == false and .author != null))
  # Group by author login
  | group_by(.author.login)
  # For each author, sort by createdAt and take all but the last
  | map(sort_by(.createdAt) | .[:-1])
  # Flatten and extract IDs
  | add // []
  | map(.id)
  | .[]
')

MINIMIZED_COUNT=0
for ID in $TO_MINIMIZE; do
  echo "Minimizing comment/review: $ID"
  MUTATION='
  mutation($subjectId: ID!) {
    minimizeComment(input: {
      subjectId: $subjectId,
      classifier: OUTDATED
    }) {
      minimizedComment {
        isMinimized
      }
    }
  }'
  gh api graphql -f query="$MUTATION" -f subjectId="$ID" > /dev/null
  MINIMIZED_COUNT=$((MINIMIZED_COUNT + 1))
done

echo "Successfully minimized $MINIMIZED_COUNT comments/reviews"
echo "Kept the most recent comment/review from each user visible"
