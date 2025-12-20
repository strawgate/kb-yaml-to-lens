# Quickstart Guide

This guide will help you get started with creating Kibana dashboards using the simplified YAML schema.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management:

```bash
uv sync --all-extras
```

For more information, see the [uv documentation](https://docs.astral.sh/uv/).

## Basic Dashboard Structure

A basic dashboard YAML file has the following structure:

```yaml
dashboard:
  title: Your Dashboard Title
  description: An optional description
  panels:
    - # Your panel definitions go here
```

## Creating a Simple Markdown Panel

Here's an example of a dashboard with a single markdown panel:

```yaml
dashboard:
  title: My First Dashboard
  description: A simple dashboard with a markdown panel
  panels:
    - panel:
        type: markdown
        grid: { x: 0, y: 0, w: 24, h: 15 }
        content: |
          # Hello, Kibana!

          This is my first markdown panel.
```

## Creating a Simple Lens Metric Panel

Here's an example of a dashboard with a single Lens metric panel displaying a count:

```yaml
dashboard:
  title: Metric Dashboard
  description: A dashboard with a single metric panel
  panels:
    - panel:
        type: lens
        grid: { x: 0, y: 0, w: 24, h: 15 }
        index_pattern: your-index-pattern-*
        chart:
          type: metric
          metrics:
            - type: count
              label: Total Documents
```

## Next Steps

*   Explore the detailed documentation for each object type (dashboard, panels, controls, filters, queries) in the `src/dashboard_compiler/*/` directories.
*   Refer to the example YAML files in the `inputs/` and `tests/dashboards/scenarios/` directories for more complex examples.
*   See the [YAML Reference](yaml_reference.md) for complete schema documentation.
*   Check the [CLI Documentation](docs/CLI.md) for compilation and upload instructions.