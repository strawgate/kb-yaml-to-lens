#!/usr/bin/env bash
set -euo pipefail

# Check for repository activity since a given timestamp
#
# Note: Activity counts are capped at 100 items per category (issues, PRs, merged PRs).
# For repositories with >100 items in any category, counts will be understated.
#
# Usage: gh-check-repo-activity.sh OWNER REPO SINCE_TIMESTAMP [THRESHOLD]
#
# Arguments:
#   OWNER           Repository owner
#   REPO            Repository name
#   SINCE_TIMESTAMP ISO 8601 timestamp to check activity since
#   THRESHOLD       Minimum activity count to meet threshold (default: 3)
#
# Output:
#   Prints activity counts to stdout
#   Returns exit 0 if threshold is met, exit 1 if not met
#
# Example:
#   gh-check-repo-activity.sh strawgate kb-yaml-to-lens "2025-12-30T09:00:00Z" 5

OWNER="${1:?Error: OWNER required}"
REPO="${2:?Error: REPO required}"
SINCE_TIMESTAMP="${3:?Error: SINCE_TIMESTAMP required}"
THRESHOLD="${4:-3}"  # Default threshold is 3

# Validate ISO 8601 timestamp format (basic validation)
if [[ ! "$SINCE_TIMESTAMP" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
  echo "Error: SINCE_TIMESTAMP must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)" >&2
  exit 1
fi

# Check for commits since timestamp
COMMIT_COUNT=$(git log --since="$SINCE_TIMESTAMP" --oneline 2>/dev/null | wc -l || echo 0)

# Check for new issues (excluding project-manager label)
NEW_ISSUES=$(gh issue list \
  --repo "$OWNER/$REPO" \
  --search "created:>=$SINCE_TIMESTAMP -label:project-manager" \
  --limit 100 \
  --json number \
  --jq 'length')

# Check for new PRs
NEW_PRS=$(gh pr list \
  --repo "$OWNER/$REPO" \
  --search "created:>=$SINCE_TIMESTAMP" \
  --limit 100 \
  --json number \
  --jq 'length')

# Check for merged PRs
MERGED_PRS=$(gh pr list \
  --repo "$OWNER/$REPO" \
  --search "merged:>=$SINCE_TIMESTAMP" \
  --limit 100 \
  --json number \
  --jq 'length')

TOTAL_ACTIVITY=$((COMMIT_COUNT + NEW_ISSUES + NEW_PRS + MERGED_PRS))

# Print activity counts
echo "Activity since $SINCE_TIMESTAMP:"
echo "  Commits: $COMMIT_COUNT"
echo "  New Issues: $NEW_ISSUES"
echo "  New PRs: $NEW_PRS"
echo "  Merged PRs: $MERGED_PRS"
echo "  Total: $TOTAL_ACTIVITY"

# Return exit code based on threshold
if [ "$TOTAL_ACTIVITY" -lt "$THRESHOLD" ]; then
  echo "Activity ($TOTAL_ACTIVITY) does not meet threshold ($THRESHOLD)"
  exit 1
else
  echo "Activity ($TOTAL_ACTIVITY) meets threshold ($THRESHOLD)"
  exit 0
fi
