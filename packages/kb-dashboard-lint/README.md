# kb-dashboard-lint

Linting rules for Kibana dashboard YAML configurations.

## Overview

This package provides a configurable linting system that flags potentially problematic
dashboard configurations based on best practices and style guidelines. It works with
validated Pydantic models from `kb-dashboard-core`.

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
from kb_dashboard_lint import check_dashboards
from kb_dashboard_core import load

# Load dashboards
dashboards = load('inputs/')

# Run linting
violations = check_dashboards(dashboards)

for violation in violations:
    print(f"{violation.severity}: {violation.rule_id} - {violation.message}")
```

## Built-in Rules

### Dashboard Rules

| Rule ID | Description | Default |
|---------|-------------|---------|
| `dashboard-dataset-filter` | Dashboard should have a `data_stream.dataset` filter | warning |
| `dashboard-missing-description` | Dashboards should have a description for discoverability | info |
| `datatable-at-bottom` | Data table panels should be positioned at the bottom of the dashboard | info |
| `markdown-at-top` | Markdown panels with navigation content should be at the top of the dashboard | info |
| `metric-excessive-count` | Dashboards should not have excessive metric panels (style guide recommends 0-4) | info |

### Panel Rules

| Rule ID | Description | Default |
|---------|-------------|---------|
| `markdown-header-height` | Markdown panels with headers must have height >= 3 | warning |
| `panel-min-width` | Panels should have minimum width for readability | warning |
| `panel-description-recommended` | Panels should have descriptions for accessibility | info |
| `panel-title-redundant-prefix` | Panel titles should not start with redundant prefixes like "Chart of" | info |

### Chart Rules

| Rule ID | Description | Default |
|---------|-------------|---------|
| `gauge-goal-without-max` | Gauge charts with goals should define maximum values | warning |
| `metric-multiple-metrics-width` | Metric panels with multiple metrics should have adequate width | warning |
| `metric-redundant-label` | Metric primary label matching title should use `hide_title: true` | warning |
| `narrow-xy-chart-side-legend` | Narrow XY charts should use bottom legends instead of side legends | warning |
| `panel-height-for-content` | Panels should have minimum height for their chart type | warning |
| `esql-field-escaping` | ES\|QL field names with numeric suffixes need backtick escaping | warning |
| `esql-group-by-syntax` | ES\|QL uses BY within STATS, not GROUP BY | warning |
| `esql-missing-sort-after-bucket` | ES\|QL time series queries with BUCKET should end with SORT for proper ordering | warning |
| `esql-sql-syntax` | ES\|QL queries should not use SQL syntax | warning |
| `datatable-row-density` | Large datatables should consider compact density | info |
| `dimension-missing-label` | Dimensions should have explicit labels | info |
| `esql-dimension-missing-label` | ES\|QL datatable dimensions should have explicit labels | info |
| `esql-dynamic-time-bucket` | ES\|QL queries should use dynamic time bucketing | info |
| `esql-metric-missing-label` | ES\|QL datatable metrics should have explicit labels | info |
| `esql-missing-limit` | ES\|QL queries with SORT DESC should have explicit LIMIT for top-N results | info |
| `esql-where-clause` | ES\|QL queries should include a WHERE clause | info |
| `pie-chart-dimension-count` | Pie charts with multiple dimensions may be hard to read | info |
| `pie-missing-limit` | Pie charts should limit slices shown (recommend 5-10 categories) | info |

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
