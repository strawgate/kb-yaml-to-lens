# kb-dashboard-tools

Development tools for kb-dashboard including disassemble and comparison utilities.

## Installation

```bash
pip install kb-dashboard-tools
```

## Usage

### Disassemble

Convert Kibana dashboard JSON back to YAML format:

```python
from kb_dashboard.tools.disassemble import disassemble_dashboard

# Disassemble a dashboard NDJSON file
yaml_content = disassemble_dashboard('dashboard.ndjson')
```

## Features

- Disassemble Kibana JSON dashboards to YAML
- Dashboard comparison utilities (planned)
- Panel analysis tools (planned)

## Related Packages

- **kb-dashboard-core**: Core compiler library (automatically installed)
- **kb-dashboard-cli**: Command-line interface
- **kb-dashboard-lsp**: Language Server Protocol for IDE integration
- **kb-dashboard-compiler**: Meta-package installing all components
