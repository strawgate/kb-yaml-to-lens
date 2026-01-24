# kb-dashboard-compiler

Meta-package that installs all kb-dashboard packages for backwards compatibility and convenience.

## Installation

```bash
pip install kb-dashboard-compiler
```

This installs:
- **kb-dashboard-core**: Core compiler library
- **kb-dashboard-cli**: Command-line interface
- **kb-dashboard-tools**: Development tools

## Usage

After installation, you can use the CLI:

```bash
# Compile dashboards
kb-dashboard compile --input-dir ./dashboards --output-dir ./output

# Upload to Kibana
kb-dashboard upload --input-dir ./dashboards --kibana-url https://localhost:5601
```

Or use the Python API:

```python
from kb_dashboard.core import load, render, dump

dashboard = load('dashboard.yaml')
kibana_json = render(dashboard)
```

## Package Structure

The kb-dashboard project is split into several namespace packages:

| Package | Purpose |
|---------|---------|
| `kb-dashboard-core` | Core YAML → Kibana JSON compiler |
| `kb-dashboard-cli` | CLI tool with Kibana/ES integration |
| `kb-dashboard-lsp` | Language Server Protocol for IDEs |
| `kb-dashboard-tools` | Development utilities (disassemble, etc.) |
| `kb-dashboard-compiler` | This meta-package (installs core + cli + tools) |

For minimal installations, install only the packages you need:

```bash
# Just the compiler library
pip install kb-dashboard-core

# CLI with all features
pip install kb-dashboard-cli

# IDE integration
pip install kb-dashboard-lsp
```
