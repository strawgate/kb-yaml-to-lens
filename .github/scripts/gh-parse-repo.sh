#!/usr/bin/env bash
set -euo pipefail

# Parse repository owner and name from OWNER/REPO format
#
# Usage:
#   gh-parse-repo.sh REPOSITORY [owner|repo]
#
# Arguments:
#   REPOSITORY - Repository in "owner/repo" format
#   [owner|repo] - Optional: specify which part to return (default: both as "OWNER REPO")
#
# Output:
#   If no second arg: prints "OWNER REPO" (space-separated)
#   If "owner": prints owner only
#   If "repo": prints repo only

REPOSITORY="${1:?Repository required (format: owner/repo)}"
PART="${2:-both}"

OWNER=$(echo "$REPOSITORY" | cut -d'/' -f1)
REPO=$(echo "$REPOSITORY" | cut -d'/' -f2)

case "$PART" in
  owner)
    echo "$OWNER"
    ;;
  repo)
    echo "$REPO"
    ;;
  both)
    echo "$OWNER $REPO"
    ;;
  *)
    echo "Error: Invalid part '$PART'. Use 'owner', 'repo', or 'both'" >&2
    exit 1
    ;;
esac
