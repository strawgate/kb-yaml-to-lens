# kb-dashboard-lint

Linting rules for Kibana dashboard YAML configurations.

## Overview

This package provides a configurable linting system that flags potentially problematic
dashboard configurations based on best practices and style guidelines. It works with
validated Pydantic models from `kb-dashboard-compiler`.

## Installation

```bash
pip install kb-dashboard-lint
```

Or with uv:

```bash
uv add kb-dashboard-lint
```

## Usage

### CLI

```bash
# Check dashboards in a directory
kb-dashboard-lint check --input-dir ./inputs

# Check a single file
kb-dashboard-lint check --input-file dashboard.yaml

# Use custom configuration
kb-dashboard-lint check --config .dashboard-lint.yaml

# Only fail on errors (not warnings)
kb-dashboard-lint check --severity-threshold error
```

### Programmatic API

```python
from dashboard_lint import check_dashboard
from dashboard_compiler import load

# Load dashboards
dashboards = load('inputs/')

# Run linting
violations = check_dashboard(dashboards)

for violation in violations:
    print(f"{violation.severity}: {violation.rule_id} - {violation.message}")
```

## Built-in Rules

| Rule ID | Description | Default |
|---------|-------------|---------|
| `markdown-header-height` | Markdown panels with headers must have height >= 3 | warning |
| `metric-redundant-label` | Metric primary label matching title should use `hide_title: true` | warning |
| `dashboard-dataset-filter` | Dashboard should have a `data_stream.dataset` filter | warning |
| `esql-where-clause` | ES\|QL queries should include a WHERE clause | info |
| `dimension-missing-label` | Dimensions should have explicit labels | info |

## Configuration

Create a `.dashboard-lint.yaml` file:

```yaml
extends: default

rules:
  markdown-header-height:
    severity: error
  esql-where-clause:
    enabled: false
```

## Development

```bash
# Install dependencies
make install

# Run CI checks
make ci

# Run tests
make test
```

## License

MIT
