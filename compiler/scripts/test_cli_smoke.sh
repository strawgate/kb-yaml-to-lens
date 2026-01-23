#!/usr/bin/env bash
# Smoke tests for CLI to ensure decorator chains execute correctly
# These tests catch issues like double @click.pass_context decorators

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$COMPILER_ROOT/.." && pwd)"

# Force UTF-8 encoding to avoid Windows cp1252 issues with Rich library
# This prevents UnicodeEncodeError when Rich's progress spinner uses Braille characters
export PYTHONUTF8=1

cd "$COMPILER_ROOT"

echo "Running CLI smoke tests..."

# Test 1: Main CLI help
echo "Test 1: Main CLI help"
uv run kb-dashboard --help > /dev/null
echo "✓ Main help command works"

# Test 2: Version check
echo "Test 2: Version check"
uv run kb-dashboard --version > /dev/null
echo "✓ Version command works"

# Test 3: Compile subcommand help
echo "Test 3: Compile subcommand help"
uv run kb-dashboard compile --help > /dev/null
echo "✓ compile --help works"

# Test 4: Screenshot subcommand help
echo "Test 4: Screenshot subcommand help"
uv run kb-dashboard screenshot --help > /dev/null
echo "✓ screenshot --help works"

# Test 5: Fetch subcommand help
echo "Test 5: Fetch subcommand help"
uv run kb-dashboard fetch --help > /dev/null
echo "✓ fetch --help works"

# Test 6: Load-sample-data subcommand help
echo "Test 6: Load-sample-data subcommand help"
uv run kb-dashboard load-sample-data --help > /dev/null
echo "✓ load-sample-data --help works"

# Test 7: Extract-sample-data subcommand help
echo "Test 7: Extract-sample-data subcommand help"
uv run kb-dashboard extract-sample-data --help > /dev/null
echo "✓ extract-sample-data --help works"

# Test 8: Export-for-issue subcommand help
echo "Test 8: Export-for-issue subcommand help"
uv run kb-dashboard export-for-issue --help > /dev/null
echo "✓ export-for-issue --help works"

# Test 9: Disassemble subcommand help
echo "Test 9: Disassemble subcommand help"
uv run kb-dashboard disassemble --help > /dev/null
echo "✓ disassemble --help works"

# Test 10: LSP subcommand help
echo "Test 10: LSP subcommand help"
uv run kb-dashboard lsp --help > /dev/null
echo "✓ lsp --help works"

# Test 11: Actual compilation test
echo "Test 11: Actual compilation test"
TEMP_OUTPUT=$(mktemp -d)
trap 'rm -rf "$TEMP_OUTPUT"' EXIT

# Default behavior: compile returns exit code 0 on success
uv run kb-dashboard compile \
  --input-dir "$PROJECT_ROOT/docs/content/examples" \
  --output-dir "$TEMP_OUTPUT" > /dev/null 2>&1

# Verify output files exist
if [ ! -f "$TEMP_OUTPUT/examples.ndjson" ]; then
  echo "✗ Expected output file not found"
  exit 1
fi
echo "✓ Compilation works and generates output"

# Test 12: Test --exit-non-zero-on-change flag
echo "Test 12: Test --exit-non-zero-on-change flag"
TEMP_OUTPUT_FLAG=$(mktemp -d)
trap 'rm -rf "$TEMP_OUTPUT" "$TEMP_OUTPUT_FLAG"' EXIT

# With --exit-non-zero-on-change, compile returns exit code = number of changed files (capped at 125).
# Since we're writing to a fresh temp dir, all files will be "new" (changed), so we expect non-zero.
compile_exit_code=0
uv run kb-dashboard compile \
  --input-dir "$PROJECT_ROOT/docs/content/examples" \
  --output-dir "$TEMP_OUTPUT_FLAG" \
  --exit-non-zero-on-change > /dev/null 2>&1 || compile_exit_code=$?

# Exit codes 1-125 indicate changed files (success). Exit codes > 125 indicate actual errors.
if [ $compile_exit_code -gt 125 ]; then
  echo "✗ Compilation failed with error code $compile_exit_code"
  exit 1
fi

if [ $compile_exit_code -eq 0 ]; then
  echo "✗ Expected non-zero exit code with --exit-non-zero-on-change flag"
  exit 1
fi

echo "✓ --exit-non-zero-on-change flag works (exit code $compile_exit_code indicates $compile_exit_code changed files)"

# Test 13: Verify NDJSON format
echo "Test 13: Verify NDJSON output format"
if ! grep -q '"type":"dashboard"' "$TEMP_OUTPUT/examples.ndjson"; then
  echo "✗ Output doesn't contain expected dashboard JSON"
  exit 1
fi
echo "✓ Output format is valid NDJSON"

echo ""
echo "✓ All CLI smoke tests passed!"
