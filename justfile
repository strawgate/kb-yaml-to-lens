# Root justfile - Global orchestration for all components
# Component-specific commands are in each component's justfile

# Import shared configuration
import 'shared.just'

# Module declarations for component namespacing
mod cli 'packages/kb-dashboard-cli'
mod core 'packages/kb-dashboard-core'
mod lint 'packages/kb-dashboard-lint'
mod tools 'packages/kb-dashboard-tools'
mod vscode 'packages/vscode-extension'
mod docs 'packages/kb-dashboard-docs'

# Default recipe - show help
default:
    @just --list

# Show help
help:
    @echo "Root justfile - Global Commands"
    @echo ""
    @echo "=== Component Pass-Through Commands ==="
    @echo ""
    @echo "Run target in all components:"
    @echo "  just all <target>       - Run in cli + core + lint + tools + vscode"
    @echo ""
    @echo "Run target in single component:"
    @echo "  just cli <target>       - Run in packages/kb-dashboard-cli/"
    @echo "  just core <target>      - Run in packages/kb-dashboard-core/"
    @echo "  just lint <target>      - Run in packages/kb-dashboard-lint/"
    @echo "  just tools <target>     - Run in packages/kb-dashboard-tools/"
    @echo "  just vscode <target>    - Run in packages/vscode-extension/"
    @echo "  just docs <target>      - Run in packages/kb-dashboard-docs/"
    @echo ""
    @echo "Common Examples:"
    @echo "  just all install          - Install root + all component dependencies"
    @echo "  just all ci               - Run CI checks (root linting + all components)"
    @echo "  just all fix              - Auto-fix linting (root + all components)"
    @echo "  just all clean            - Clean all components"
    @echo "  just root ci              - Run root-level CI checks (markdown + YAML lint)"
    @echo "  just root fix             - Auto-fix root-level linting"
    @echo "  just root install         - Install root-level dependencies"
    @echo "  just cli test-e2e         - Run CLI E2E tests (includes Docker tests if available)"
    @echo "  just vscode test-e2e      - Run VS Code E2E tests"
    @echo "  just docs ci              - Check docs (markdown lint + links)"
    @echo "  just docs serve           - Start docs server"
    @echo ""
    @echo "=== Global Linting ==="
    @echo ""
    @echo "  lint-markdown       - Auto-fix markdown issues"
    @echo "  lint-markdown-check - Check markdown without fixing"
    @echo "  lint-yaml           - Auto-fix YAML issues"
    @echo "  lint-yaml-check     - Check YAML without fixing"
    @echo ""
    @echo "=== Version Bumping ==="
    @echo ""
    @echo "  bump-patch         - Bump patch version (x.y.Z)"
    @echo "  bump-minor         - Bump minor version (x.Y.0)"
    @echo "  bump-major         - Bump major version (X.0.0)"
    @echo "  bump-version-show  - Show current version"
    @echo ""
    @echo "=== Release ==="
    @echo ""
    @echo "  release-prep       - Open GitHub issues for pre-release review tasks"
    @echo "  release-tag        - Create and push git tag from pyproject.toml version"
    @echo ""
    @echo "=== Git Helpers ==="
    @echo ""
    @echo "  check-merge-conflicts [branch] - Check for merge conflicts with branch (default: origin/main)"
    @echo "  explore-bootstrap [version]    - Bootstrap ES/Kibana and seed explore data"

# Run target across root + all components
# Usage: just all <target>
all target:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{target}}" = "ci" ] || [ "{{target}}" = "fix" ] || [ "{{target}}" = "install" ]; then
        printf "Root\n"
        just root-{{target}}
        echo ""
    fi
    for component in {{COMPONENTS}}; do
        printf "Component: %s\n" "$component"
        just --justfile "$component/justfile" {{target}}
        echo ""
    done
    printf "✓ All components: %s complete\n" "{{target}}"

# Root-level targets
root-ci:
    just _print-start "Running root-level CI checks"
    @echo ""
    just lint-markdown-check
    @echo ""
    just lint-yaml-check
    @echo ""
    just _print-end "Root-level CI checks passed"

root-fix:
    just _print-start "Running root-level lint fixes"
    @echo ""
    just lint-markdown
    @echo ""
    just lint-yaml
    @echo ""
    just _print-end "Root-level lint fixes complete"

root-install:
    #!/usr/bin/env bash
    set -euo pipefail
    printf "→ Installing root-level dependencies...\n"
    if command -v npm > /dev/null 2>&1; then
        if ! command -v markdownlint > /dev/null 2>&1; then
            npm install -g markdownlint-cli
            printf "✓ markdownlint-cli installed\n"
        else
            printf "✓ markdownlint-cli already installed\n"
        fi
    else
        echo "⚠ npm not found - markdownlint-cli will not be installed"
        echo "  Install Node.js to enable markdown linting"
    fi
    printf "✓ Root-level dependencies installed\n"

# Root passthrough (allows "just root <target>")
root target:
    just root-{{target}}

# Markdown linting (global)
lint-markdown:
    just _print-start "Running markdownlint --fix"
    markdownlint --fix -c .markdownlint.jsonc .
    just _print-end "Markdown linting complete"

lint-markdown-check:
    just _print-start "Running markdownlint"
    markdownlint -c .markdownlint.jsonc .
    just _print-end "Markdown checks passed"

# YAML linting (global)
lint-yaml:
    just _print-start "Running yamlfix"
    uv run --group dev yamlfix {{YAMLFIX_EXCLUDE}} .
    just _print-end "YAML linting complete"

lint-yaml-check:
    just _print-start "Running yamlfix --check"
    uv run --group dev yamlfix --check {{YAMLFIX_EXCLUDE}} .
    just _print-end "YAML checks passed"

# Version bumping
bump-patch:
    uv run scripts/bump-version.py patch

bump-minor:
    uv run scripts/bump-version.py minor

bump-major:
    uv run scripts/bump-version.py major

bump-version-show:
    uv run scripts/bump-version.py show

# Open GitHub issues for pre-release review (docs, dry run, code quality, tests, release notes)
release-prep version="":
    bash scripts/release-prep.sh {{version}}

# Release
release-tag:
    #!/usr/bin/env bash
    set -euo pipefail
    VERSION=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    TAG="v$VERSION"
    echo "Current version: $VERSION"
    echo "Creating tag: $TAG"
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "Error: Tag $TAG already exists"
        exit 1
    fi
    git tag -a "$TAG" -m "Release $VERSION"
    echo "Tag $TAG created"
    echo "Pushing tag to origin..."
    git push origin "$TAG"
    echo "✓ Tag $TAG pushed successfully"

# Git helpers
check-merge-conflicts branch="origin/main":
    bash scripts/check-merge-conflicts.sh {{branch}}

# Explore workflow helpers
explore-bootstrap version="9.3.0":
    bash scripts/bootstrap-explore-kibana.sh {{version}}
