# Developing

This guide covers development workflows for the kb-yaml-to-lens project.

## Project Structure

```text
kb-yaml-to-lens/
├── packages/kb-dashboard-compiler/ # Python YAML → JSON compiler
│   └── src/dashboard_compiler/
├── packages/vscode-extension/ # VS Code extension
│   └── src/
└── packages/kb-dashboard-docs/  # User documentation
```

| Directory | Technology | Purpose |
| --------- | ---------- | ------- |
| `packages/kb-dashboard-compiler/` | Python 3.12+, Pydantic, uv | Dashboard compilation engine |
| `packages/vscode-extension/` | TypeScript, Node.js | VS Code extension with live preview |
| `packages/kb-dashboard-docs/` | MkDocs | User-facing documentation site |

## Prerequisites

- **Python 3.12+** (for compiler development)
- **Node.js 20+** (for extension development)
- **[uv](https://github.com/astral-sh/uv)** (Python package manager)
- **make** (build automation)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/strawgate/kb-yaml-to-lens
cd kb-yaml-to-lens

# Install all dependencies
make all install
make docs install  # For markdownlint-cli

# Run all checks (lint + typecheck + tests)
make all ci
make lint-markdown-check
make lint-yaml-check
```

## Essential Commands

Run these from the **repository root**:

| Command | Purpose |
| ------- | ------- |
| `make all install` | Install all component dependencies |
| `make all ci` | Run CI checks in all components |
| `make all fix` | Auto-fix linting issues across all components |
| `make all clean` | Clean cache and temporary files |
| `make lint-markdown-check` | Check markdown linting (repo-wide) |
| `make lint-yaml-check` | Check YAML linting (repo-wide) |
| `make docs ci` | Check documentation (markdown lint + link verification) |

**Troubleshooting CI failures:** Run `make all ci` + lint commands locally to reproduce CI checks.

## Component Pass-Through Commands

Run any component-specific target from the repository root:

| Command | Purpose |
| ------- | ------- |
| `make all <target>` | Run target in all components (compiler + vscode) |
| `make compiler <target>` | Run target in `packages/kb-dashboard-compiler/` |
| `make vscode <target>` | Run target in `packages/vscode-extension/` |
| `make docs <target>` | Run target in `packages/kb-dashboard-docs/` |
| `make gh <target>` | Run target in `.github/scripts/` |

**Examples:**

```bash
# Run across all components (parallel)
make all ci           # Run CI in compiler + vscode
make all fix          # Auto-fix linting in all components
make all clean        # Clean all components

# Run in specific component
make compiler test       # Run compiler tests
make compiler test-smoke # Run compiler smoke tests
make vscode test-unit    # Run VS Code unit tests
make vscode test-e2e     # Run VS Code E2E tests
make docs serve          # Start docs server
make compiler help       # Show all compiler targets
```

## Component Development

See component-specific DEVELOPING.md files for detailed workflows:

- **Compiler:** [packages/kb-dashboard-compiler/DEVELOPING.md](packages/kb-dashboard-compiler/DEVELOPING.md)
- **VS Code Extension:** [packages/vscode-extension/DEVELOPING.md](packages/vscode-extension/DEVELOPING.md)
- **Documentation:** [packages/kb-dashboard-docs/DEVELOPING.md](packages/kb-dashboard-docs/DEVELOPING.md)

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | [packages/kb-dashboard-docs/content/architecture.md](packages/kb-dashboard-docs/content/architecture.md) |
| Getting started | [packages/kb-dashboard-docs/content/index.md](packages/kb-dashboard-docs/content/index.md) |
| CLI documentation | [packages/kb-dashboard-docs/content/CLI.md](packages/kb-dashboard-docs/content/CLI.md) |
| Release process | [RELEASE.md](RELEASE.md) |
