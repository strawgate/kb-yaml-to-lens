# Shared just configuration
# Common settings and helper recipes used across all justfiles
# Import this file with: import '../../shared.just' (or adjust path accordingly)

# Shell settings for cross-platform compatibility
# just handles exit codes natively, simplifying the migration from PIPESTATUS handling
set shell := ["bash", "-euo", "pipefail", "-c"]
set windows-shell := ["C:/Program Files/Git/bin/bash.exe", "-euo", "pipefail", "-c"]

# Export all variables as environment variables
set export := true

# Allow positional arguments in recipes
set positional-arguments := true

# Repository root directory (detected from this file's location)
# justfile_directory() returns the directory containing the justfile being run
# For the root justfile, this is the repo root; for component justfiles, it's the component directory
ROOT := justfile_directory()

# Components for pass-through commands
COMPONENTS := "packages/kb-dashboard-cli packages/kb-dashboard-core packages/kb-dashboard-lint packages/kb-dashboard-tools packages/vscode-extension"

# YAML linting exclusions
YAMLFIX_EXCLUDE := '--exclude ".venv/**/*.yaml" --exclude ".venv/**/*.yml" --exclude "packages/kb-dashboard-cli/.venv/**/*.yaml" --exclude "packages/kb-dashboard-cli/.venv/**/*.yml" --exclude "packages/kb-dashboard-core/.venv/**/*.yaml" --exclude "packages/kb-dashboard-core/.venv/**/*.yml" --exclude "packages/kb-dashboard-lint/.venv/**/*.yaml" --exclude "packages/kb-dashboard-lint/.venv/**/*.yml" --exclude "packages/kb-dashboard-tools/.venv/**/*.yaml" --exclude "packages/kb-dashboard-tools/.venv/**/*.yml" --exclude "node_modules/**/*.yaml" --exclude "node_modules/**/*.yml" --exclude "packages/vscode-extension/node_modules/**/*.yaml" --exclude "packages/vscode-extension/node_modules/**/*.yml" --exclude "packages/vscode-extension/.vscode-test/**/*.yaml" --exclude "packages/vscode-extension/.vscode-test/**/*.yml"'

# Helper recipe for consistent start message formatting
# Usage: just _print-start "Action description"
[private]
_print-start msg:
    @printf "→ %s...\n" "{{msg}}"

# Helper recipe for consistent end message formatting
# Usage: just _print-end "Success message"
[private]
_print-end msg:
    @printf "✓ %s\n" "{{msg}}"
