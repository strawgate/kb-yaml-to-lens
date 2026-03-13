# Developing

This guide covers development workflows for **contributors** to the kb-yaml-to-lens project.

> **End users:** You don't need to clone this repository to use the CLI. Simply run `uvx kb-dashboard-cli compile --help` to get started. See the [CLI Documentation](https://strawgate.github.io/kb-yaml-to-lens/CLI) for usage details.

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
- **[just](https://github.com/casey/just)** (command runner)
  - Install: `brew install just` (macOS), `cargo install just` (Rust), or see [installation docs](https://github.com/casey/just#installation)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/strawgate/kb-yaml-to-lens
cd kb-yaml-to-lens

# Install all dependencies
just all install
just docs install  # For markdownlint-cli

# Run all checks (lint + typecheck + tests)
just all ci
just lint-markdown-check
just lint-yaml-check
```

## Essential Commands

Run these from the **repository root**:

| Command | Purpose |
| ------- | ------- |
| `just all install` | Install all component dependencies |
| `just all ci` | Run CI checks in all components |
| `just all fix` | Auto-fix linting issues across all components |
| `just all clean` | Clean cache and temporary files |
| `just lint-markdown-check` | Check markdown linting (repo-wide) |
| `just lint-yaml-check` | Check YAML linting (repo-wide) |
| `just docs ci` | Check documentation (markdown lint + link verification) |
| `kb-dashboard-lint check --input-file <file>` | Check dashboard YAML for best practices |

**Troubleshooting CI failures:** Run `just all ci` + lint commands locally to reproduce CI checks.

## Component Pass-Through Commands

Run any component-specific target from the repository root:

| Command | Purpose |
| ------- | ------- |
| `just all <target>` | Run target in all components (cli + core + lint + tools + vscode) |
| `just cli <target>` | Run target in `packages/kb-dashboard-cli/` |
| `just core <target>` | Run target in `packages/kb-dashboard-core/` |
| `just lint <target>` | Run target in `packages/kb-dashboard-lint/` |
| `just tools <target>` | Run target in `packages/kb-dashboard-tools/` |
| `just vscode <target>` | Run target in `packages/vscode-extension/` |
| `just docs <target>` | Run target in `packages/kb-dashboard-docs/` |
| `just gh <target>` | Run target in `.github/scripts/` |

**Examples:**

```bash
# Run across all components (parallel)
just all ci           # Run CI in cli + core + lint + tools + vscode
just all fix          # Auto-fix linting in all components
just all clean        # Clean all components

# Run in specific component
just cli test            # Run CLI tests
just cli test-e2e         # Run CLI E2E tests (includes Docker tests if available)
just core test           # Run core tests
just vscode test-unit    # Run VS Code unit tests
just vscode test-e2e     # Run VS Code E2E tests
just docs serve          # Start docs server
just cli help            # Show all CLI targets
```

## Component Development

See component-specific DEVELOPING.md files for detailed workflows:

- **CLI:** [packages/kb-dashboard-cli/DEVELOPING.md](packages/kb-dashboard-cli/DEVELOPING.md)
- **Core:** [packages/kb-dashboard-core/DEVELOPING.md](packages/kb-dashboard-core/DEVELOPING.md)
- **Lint:** `packages/kb-dashboard-lint/` — follows same patterns as CLI/Core (`just lint ci`)
- **Tools:** `packages/kb-dashboard-tools/` — follows same patterns as CLI/Core (`just tools ci`)
- **VS Code Extension:** [packages/vscode-extension/DEVELOPING.md](packages/vscode-extension/DEVELOPING.md)
- **Documentation:** [packages/kb-dashboard-docs/DEVELOPING.md](packages/kb-dashboard-docs/DEVELOPING.md)

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | [packages/kb-dashboard-docs/content/architecture.md](packages/kb-dashboard-docs/content/architecture.md) |
| Getting started | [packages/kb-dashboard-docs/content/index.md](packages/kb-dashboard-docs/content/index.md) |
| CLI documentation | [packages/kb-dashboard-docs/content/CLI.md](packages/kb-dashboard-docs/content/CLI.md) |
| Release process | [RELEASE.md](RELEASE.md) |
