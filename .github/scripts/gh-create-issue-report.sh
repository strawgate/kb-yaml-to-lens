#!/usr/bin/env bash
set -euo pipefail

# Create a new issue with structured content
#
# Usage:
#   gh-create-issue-report.sh OWNER REPO TITLE BODY [LABELS]
#
# Arguments:
#   OWNER    - Repository owner
#   REPO     - Repository name
#   TITLE    - Issue title
#   BODY     - Issue body (markdown supported)
#   LABELS   - Optional: comma-separated list of labels (e.g., "bug,urgent")
#
# Environment:
#   GITHUB_TOKEN - GitHub API token (required for gh cli)
#
# Output:
#   Issue URL on success

OWNER="${1:?Owner required}"
REPO="${2:?Repo required}"
TITLE="${3:?Title required}"
BODY="${4:?Body required}"
LABELS="${5:-}"

ARGS=(--repo "$OWNER/$REPO" --title "$TITLE" --body "$BODY")

if [ -n "$LABELS" ]; then
  ARGS+=(--label "$LABELS")
fi

gh issue create "${ARGS[@]}"
