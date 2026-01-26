# kb-dashboard-core

Core compilation engine for YAML to Kibana dashboard format.

## Overview

`kb-dashboard-core` is a pure Python library that provides the core compilation functionality for converting YAML dashboard definitions to Kibana's JSON format. This package contains no external service dependencies (no Elasticsearch, Kibana HTTP client, CLI framework, or LSP dependencies).

## Features

- Load dashboard configurations from YAML files
- Compile YAML dashboard definitions to Kibana JSON format
- Support for various panel types (Lens charts, markdown, etc.)
- Control and filter compilation
- Query building and validation

## Installation

```bash
pip install kb-dashboard-core
```

## Usage

```python
from kb_dashboard_core import load, render, dump

# Load dashboards from YAML
dashboards = load('path/to/dashboard.yaml')

# Render to Kibana format
for dashboard in dashboards:
    kibana_json = render(dashboard)
    print(kibana_json.model_dump_json(indent=2))

# Save dashboards back to YAML
dump(dashboards, 'path/to/output.yaml')
```

## Development

See [DEVELOPING.md](../../DEVELOPING.md) for development setup and workflows.

## License

MIT
