#!/usr/bin/env bash
# Check for merge conflicts without modifying the working tree.
#
# This script uses `git merge-tree` to simulate a merge and detect conflicts
# without actually performing the merge or leaving the repository in a dirty state.
#
# Usage:
#     bash scripts/check-merge-conflicts.sh [branch]
#
# Examples:
#     # Check conflicts with origin/main
#     bash scripts/check-merge-conflicts.sh
#
#     # Check conflicts with a specific branch
#     bash scripts/check-merge-conflicts.sh origin/develop
#
# Exit codes:
#     0 - No conflicts would occur
#     1 - Conflicts would occur
#     2 - Error (invalid branch, not in git repo, etc.)

set -euo pipefail

# Default to origin/main if no branch specified
MERGE_BRANCH="${1:-origin/main}"

# Ensure we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository" >&2
    exit 2
fi

# Fetch latest changes for remote branches
if [[ "$MERGE_BRANCH" == origin/* ]]; then
    echo "Fetching latest changes from $MERGE_BRANCH..." >&2
    git fetch origin > /dev/null 2>&1 || true
fi

# Check if branch exists
if ! git rev-parse --verify "$MERGE_BRANCH" > /dev/null 2>&1; then
    echo "Error: Branch '$MERGE_BRANCH' does not exist" >&2
    exit 2
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ -z "$CURRENT_BRANCH" ]; then
    echo "Error: Not on a branch (detached HEAD)" >&2
    exit 2
fi

echo "Checking for merge conflicts: $CURRENT_BRANCH <- $MERGE_BRANCH" >&2

# Get merge base
MERGE_BASE=$(git merge-base "$CURRENT_BRANCH" "$MERGE_BRANCH" 2>/dev/null)
if [ -z "$MERGE_BASE" ]; then
    echo "Error: Could not find merge base between $CURRENT_BRANCH and $MERGE_BRANCH" >&2
    exit 2
fi

# Get commit SHAs
CURRENT_HEAD=$(git rev-parse HEAD)
MERGE_HEAD=$(git rev-parse "$MERGE_BRANCH")

# Use merge-tree to simulate the merge (doesn't modify working tree)
MERGE_OUTPUT=$(git merge-tree "$MERGE_BASE" "$CURRENT_HEAD" "$MERGE_HEAD" 2>&1) || true

# Check for conflict indicators
CONFLICTED_FILES=()
HAS_CONFLICTS=false

# Parse output for conflict patterns
# git merge-tree outputs conflicts in formats like:
# - "changed in both:  <file>"
# - "CONFLICT (content): Merge conflict in <file>"
# - "  both modified:   <file>"
while IFS= read -r line; do
    # Look for "changed in both" lines (most common format)
    if [[ "$line" =~ ^changed\ in\ both:[[:space:]]+(.+)$ ]]; then
        file="${BASH_REMATCH[1]}"
        CONFLICTED_FILES+=("$file")
        HAS_CONFLICTS=true
    # Look for CONFLICT lines
    elif [[ "$line" =~ ^CONFLICT.*:\ Merge\ conflict\ in[[:space:]]+(.+)$ ]]; then
        file="${BASH_REMATCH[1]}"
        if [[ ! " ${CONFLICTED_FILES[*]} " =~ " ${file} " ]]; then
            CONFLICTED_FILES+=("$file")
        fi
        HAS_CONFLICTS=true
    # Look for "both modified", "both added", "both deleted" patterns
    elif [[ "$line" =~ [[:space:]]+both\ (modified|added|deleted):[[:space:]]+(.+)$ ]]; then
        file="${BASH_REMATCH[2]}"
        if [[ ! " ${CONFLICTED_FILES[*]} " =~ " ${file} " ]]; then
            CONFLICTED_FILES+=("$file")
        fi
        HAS_CONFLICTS=true
    # Look for conflict markers (<<<<<<<, =======, >>>>>>>)
    elif [[ "$line" =~ ^\<{7} ]] || [[ "$line" =~ ^={7} ]] || [[ "$line" =~ ^\>{7} ]]; then
        HAS_CONFLICTS=true
    fi
done <<< "$MERGE_OUTPUT"

# Also check for conflict keywords in the output (case-insensitive)
if echo "$MERGE_OUTPUT" | grep -qiE '(CONFLICT|conflict)'; then
    HAS_CONFLICTS=true
fi

# Output results
if [ "$HAS_CONFLICTS" = true ] || [ ${#CONFLICTED_FILES[@]} -gt 0 ]; then
    echo "" >&2
    echo "⚠️  Merge conflicts detected!" >&2
    if [ ${#CONFLICTED_FILES[@]} -gt 0 ]; then
        echo "" >&2
        echo "Conflicted files (${#CONFLICTED_FILES[@]}):" >&2
        # Sort files for consistent output
        IFS=$'\n' sorted_files=($(sort <<<"${CONFLICTED_FILES[*]}"))
        unset IFS
        for file in "${sorted_files[@]}"; do
            echo "  - $file" >&2
        done
    fi
    exit 1
fi

echo "" >&2
echo "✅ No merge conflicts detected" >&2
exit 0
