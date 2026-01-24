# kb-dashboard-core

Core compiler library for converting YAML dashboard definitions to Kibana Lens format.

## Installation

```bash
pip install kb-dashboard-core
```

## Usage

```python
from kb_dashboard.core import load, render, dump

# Load a dashboard from YAML
dashboard = load('path/to/dashboard.yaml')

# Render to Kibana JSON format
kibana_json = render(dashboard)

# Dump to NDJSON file
dump(dashboard, 'output.ndjson')
```

## Features

- Pure YAML → Kibana JSON compilation
- Pydantic-based configuration validation
- Support for all Lens chart types (XY, Pie, Metric, Gauge, Heatmap, etc.)
- Dashboard filters and controls
- ES|QL query support

## Related Packages

- **kb-dashboard-cli**: Command-line interface for compilation and Kibana uploads
- **kb-dashboard-lsp**: Language Server Protocol for IDE integration
- **kb-dashboard-tools**: Development tools (disassemble, compare)
