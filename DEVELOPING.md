# Developing

This guide covers development workflows for the kb-yaml-to-lens project.

## Project Structure

```text
kb-yaml-to-lens/
├── compiler/              # Python YAML → JSON compiler
│   └── src/dashboard_compiler/
├── vscode-extension/      # VS Code extension
│   └── src/
└── docs/                  # User documentation
```

| Directory | Technology | Purpose |
| --------- | ---------- | ------- |
| `compiler/` | Python 3.12+, Pydantic, uv | Dashboard compilation engine |
| `vscode-extension/` | TypeScript, Node.js | VS Code extension with live preview |
| `docs/` | MkDocs | User-facing documentation site |

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
make install

# Run all checks (lint + typecheck + tests)
make check
```

## Essential Commands

Run these from the **repository root**:

| Command | Purpose |
| ------- | ------- |
| `make install` | Install all dependencies (Python + Node.js) |
| `make check` | **Run before committing** (lint + typecheck + unit tests) |
| `make ci` | Comprehensive CI checks (matches GitHub Actions) |
| `make fix` | Auto-fix linting issues |
| `make test-unit` | Run unit tests only |
| `make test-e2e` | Run end-to-end tests |
| `make clean` | Clean cache and temporary files |

**Troubleshooting CI failures:** Run `make ci` locally to reproduce exact CI checks.

## Component Development

See component-specific DEVELOPING.md files for detailed workflows:

- **Compiler:** [compiler/DEVELOPING.md](compiler/DEVELOPING.md)
- **VS Code Extension:** [vscode-extension/DEVELOPING.md](vscode-extension/DEVELOPING.md)
- **Documentation:** [docs/DEVELOPING.md](docs/DEVELOPING.md)

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Getting started | [docs/index.md](docs/index.md) |
| CLI documentation | [docs/CLI.md](docs/CLI.md) |
| Release process | [RELEASE.md](RELEASE.md) |
