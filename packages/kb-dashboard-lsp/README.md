# kb-dashboard-lsp

Language Server Protocol implementation for kb-dashboard YAML files, providing IDE integration.

## Installation

```bash
pip install kb-dashboard-lsp
```

## Usage

The LSP server is typically started by an IDE extension (like the VS Code extension):

```bash
# Start the LSP server
kb-dashboard-lsp
```

Or as a Python module:

```bash
python -m kb_dashboard.lsp.server
```

## Features

- Real-time YAML validation and diagnostics
- Grid position extraction and updates
- Integration with VS Code extension

## Grid Operations

The LSP package also provides standalone grid operation commands:

```bash
# Extract grid positions from YAML
python -m kb_dashboard.lsp.grid_extractor <yaml-file>

# Update grid positions in YAML
python -m kb_dashboard.lsp.grid_updater <yaml-file> <panel-id> <x> <y> <w> <h>
```

## Related Packages

- **kb-dashboard-core**: Core compiler library (automatically installed)
- **kb-dashboard-cli**: Command-line interface (automatically installed)
- **kb-dashboard-tools**: Development tools
- **kb-dashboard-compiler**: Meta-package installing all components
