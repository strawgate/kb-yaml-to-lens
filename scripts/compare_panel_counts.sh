#!/bin/bash
# Compare panel counts and types between two NDJSON dashboard files
#
# Usage:
#   scripts/compare_panel_counts.sh original.ndjson compiled.ndjson

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 original.ndjson compiled.ndjson"
    exit 1
fi

ORIGINAL="$1"
COMPILED="$2"

if [ ! -f "$ORIGINAL" ]; then
    echo "Error: Original file not found: $ORIGINAL"
    exit 1
fi

if [ ! -f "$COMPILED" ]; then
    echo "Error: Compiled file not found: $COMPILED"
    exit 1
fi

echo "Panel Count Comparison:"
echo "======================="
echo -n "Original panels: "
jq '.attributes.panelsJSON | fromjson | length' "$ORIGINAL"
echo -n "Compiled panels: "
jq '.attributes.panelsJSON | fromjson | length' "$COMPILED"
echo

echo "Panel Types (Original):"
echo "======================="
jq -r '.attributes.panelsJSON | fromjson | .[].type' "$ORIGINAL" | sort | uniq -c
echo

echo "Panel Types (Compiled):"
echo "======================="
jq -r '.attributes.panelsJSON | fromjson | .[].type' "$COMPILED" | sort | uniq -c
