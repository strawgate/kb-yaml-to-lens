# Developing

This guide covers development workflows for the kb-yaml-to-lens project.

## Project Structure

```text
kb-yaml-to-lens/
├── packages/kb-dashboard-cli/  # CLI, LSP, and MCP server
│   └── src/dashboard_compiler/
├── packages/kb-dashboard-core/ # Core compilation engine
│   └── src/kb_dashboard_core/
├── packages/kb-dashboard-lint/ # Lint rules and CLI
│   └── src/dashboard_lint/
├── packages/kb-dashboard-tools/ # Kibana client utilities
│   └── src/kb_dashboard_tools/
├── packages/vscode-extension/ # VS Code extension
│   └── src/
└── packages/kb-dashboard-docs/  # User documentation
```

| Directory | Technology | Purpose |
| --------- | ---------- | ------- |
| `packages/kb-dashboard-cli/` | Python 3.12+, Click, pygls | CLI, LSP, and future MCP server |
| `packages/kb-dashboard-core/` | Python 3.12+, Pydantic, uv | Dashboard compilation engine |
| `packages/kb-dashboard-lint/` | Python 3.12+, Pydantic | Lint rules and CLI for dashboard validation |
| `packages/kb-dashboard-tools/` | Python 3.12+, aiohttp | Kibana client and utilities |
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
| `kb-dashboard-lint check --input-file <file>` | Check dashboard YAML for best practices |

**Troubleshooting CI failures:** Run `make all ci` + lint commands locally to reproduce CI checks.

## Component Pass-Through Commands

Run any component-specific target from the repository root:

| Command | Purpose |
| ------- | ------- |
| `make all <target>` | Run target in all components (cli + core + lint + tools + vscode) |
| `make cli <target>` | Run target in `packages/kb-dashboard-cli/` |
| `make core <target>` | Run target in `packages/kb-dashboard-core/` |
| `make lint <target>` | Run target in `packages/kb-dashboard-lint/` |
| `make tools <target>` | Run target in `packages/kb-dashboard-tools/` |
| `make vscode <target>` | Run target in `packages/vscode-extension/` |
| `make docs <target>` | Run target in `packages/kb-dashboard-docs/` |
| `make gh <target>` | Run target in `.github/scripts/` |

**Examples:**

```bash
# Run across all components (parallel)
make all ci           # Run CI in cli + core + lint + tools + vscode
make all fix          # Auto-fix linting in all components
make all clean        # Clean all components

# Run in specific component
make cli test            # Run CLI tests
make cli test-e2e         # Run CLI E2E tests (includes Docker tests if available)
make core test           # Run core tests
make vscode test-unit    # Run VS Code unit tests
make vscode test-e2e     # Run VS Code E2E tests
make docs serve          # Start docs server
make cli help            # Show all CLI targets
```

## Component Development

See component-specific DEVELOPING.md files for detailed workflows:

- **CLI:** [packages/kb-dashboard-cli/DEVELOPING.md](packages/kb-dashboard-cli/DEVELOPING.md)
- **Core:** [packages/kb-dashboard-core/DEVELOPING.md](packages/kb-dashboard-core/DEVELOPING.md)
- **VS Code Extension:** [packages/vscode-extension/DEVELOPING.md](packages/vscode-extension/DEVELOPING.md)
- **Documentation:** [packages/kb-dashboard-docs/DEVELOPING.md](packages/kb-dashboard-docs/DEVELOPING.md)

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | [packages/kb-dashboard-docs/content/architecture.md](packages/kb-dashboard-docs/content/architecture.md) |
| Getting started | [packages/kb-dashboard-docs/content/index.md](packages/kb-dashboard-docs/content/index.md) |
| CLI documentation | [packages/kb-dashboard-docs/content/CLI.md](packages/kb-dashboard-docs/content/CLI.md) |
| Release process | [RELEASE.md](RELEASE.md) |
