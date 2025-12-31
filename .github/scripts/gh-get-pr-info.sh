#!/usr/bin/env bash
set -euo pipefail

# Get PR information via GitHub GraphQL API
#
# Usage:
#   gh-get-pr-info.sh OWNER REPO PR_NUMBER [FIELD]
#
# Arguments:
#   OWNER       - Repository owner
#   REPO        - Repository name
#   PR_NUMBER   - Pull request number
#   FIELD       - Optional: specific field to return (default: all as JSON)
#
# Available fields:
#   headRef     - Head branch name
#   baseRef     - Base branch name
#   author      - Author login
#   state       - PR state (OPEN, CLOSED, MERGED)
#   isDraft     - Draft status (true/false)
#   title       - PR title
#   body        - PR body/description
#   url         - PR URL
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   If no FIELD: JSON object with all PR information
#   If FIELD specified: Just the value of that field

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
PR_NUMBER="${3:?PR number required}"
FIELD="${4:-}"

PR_INFO=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $prNumber: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $prNumber) {
        headRefName
        baseRefName
        author { login }
        state
        isDraft
        title
        body
        url
      }
    }
  }' -F owner="$OWNER" \
     -F repo="$REPO" \
     -F prNumber="$PR_NUMBER" \
     --jq '.data.repository.pullRequest')

if [ -z "$FIELD" ]; then
  echo "$PR_INFO"
else
  case "$FIELD" in
    headRef)
      echo "$PR_INFO" | jq -r '.headRefName'
      ;;
    baseRef)
      echo "$PR_INFO" | jq -r '.baseRefName'
      ;;
    author)
      echo "$PR_INFO" | jq -r '.author.login'
      ;;
    state)
      echo "$PR_INFO" | jq -r '.state'
      ;;
    isDraft)
      echo "$PR_INFO" | jq -r '.isDraft'
      ;;
    title)
      echo "$PR_INFO" | jq -r '.title'
      ;;
    body)
      echo "$PR_INFO" | jq -r '.body'
      ;;
    url)
      echo "$PR_INFO" | jq -r '.url'
      ;;
    *)
      echo "Error: Invalid field '$FIELD'" >&2
      echo "Available fields: headRef, baseRef, author, state, isDraft, title, body, url" >&2
      exit 1
      ;;
  esac
fi
