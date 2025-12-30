# Dashboard Compiler

Convert human-friendly YAML dashboard definitions into Kibana NDJSON format.

This tool simplifies the process of creating and managing Kibana dashboards by
allowing you to define them in a clean, maintainable YAML format instead of
hand-crafting complex JSON.

## Features

- **YAML-based Dashboard Definition** – Define dashboards, panels, filters,
  and queries in simple YAML
- **Kibana Integration** – Compile to NDJSON format compatible with Kibana 8+
- **Rich Panel Support** – Lens visualizations (metric, pie, XY charts),
  Markdown, Links, and Image panels; Search panels (in development)
- **Advanced Controls** – Control groups with options lists, range sliders,
  and time sliders with chaining
- **Flexible Filtering** – Comprehensive filter DSL supporting exists, phrase,
  range, and custom DSL with AND/OR/NOT operators
- **Multiple Query Types** – KQL, Lucene, and ESQL query support
- **Direct Upload** – Optional direct upload to Kibana with authentication
  support
- **Screenshot Export** – Generate PNG screenshots of dashboards with custom
  time ranges using Kibana's Reporting API

## Quick Start

### Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable
Python package management:

```bash
# For development (includes testing, linting, type checking)
uv sync --group dev

# For building documentation
uv sync --group dev --group docs

# For runtime usage only
uv sync
```

For more information, see the [uv documentation](https://docs.astral.sh/uv/).

### Compile Your First Dashboard

1. Create a YAML dashboard file in `inputs/` directory:

```yaml
dashboards:
-
  name: My First Dashboard
  description: A simple dashboard with markdown
  panels:
    - title: Welcome
      grid: { x: 0, y: 0, w: 24, h: 15 }
      markdown:
        content: |
          # Welcome to Kibana!

          This is my first dashboard compiled from YAML.
```

1. Compile to NDJSON:

```bash
kb-dashboard compile --input-dir inputs --output-dir output
```

1. (Optional) Upload directly to Kibana:

```bash
kb-dashboard compile \
  --input-dir inputs \
  --output-dir output \
  --upload \
  --kibana-url http://localhost:5601 \
  --kibana-username elastic \
  --kibana-password changeme
```

The `--upload` flag will automatically open your dashboard in the browser upon
successful upload.

## Where to Start

- **New to kb-yaml-to-lens?** → Start with the [Quickstart Guide](quickstart.md)
- **Building dashboards?** → Browse the [User Guide](#user-guide) for YAML reference and panel documentation
- **Contributing or extending?** → Check the [Developer Guide](#developer-guide) for architecture and API documentation

## Documentation Sections

### Getting Started

New users should begin here to learn the basics:

- **[Quickstart Guide](quickstart.md)** – Step-by-step guide for creating your first dashboard
- **[CLI Reference](CLI.md)** – Command-line interface documentation

### User Guide

Reference documentation for building dashboards in YAML:

- **[Dashboard Configuration](dashboard/dashboard.md)** – Dashboard-level settings and options
- **[Panel Types](panels/base.md)** – Available panel types (Markdown, Charts, Images, Links, etc.)
- **[Dashboard Controls](controls/config.md)** – Interactive filtering controls
- **[Filters & Queries](filters/config.md)** – Data filtering and query configuration
- **[Complete Examples](examples/index.md)** – Real-world YAML dashboard examples

### Developer Guide

Advanced documentation for contributors and programmatic usage:

- **[Architecture Overview](architecture.md)** – Technical design and data flow
- **[Programmatic Usage](programmatic-usage.md)** – Using the Python API directly
- **[API Reference](api/index.md)** – Auto-generated Python API documentation
- **[Contributing Guide](https://github.com/strawgate/kb-yaml-to-lens/blob/main/CONTRIBUTING.md)** – How to contribute and add new capabilities
- **[Kibana Architecture Reference](kibana-architecture.md)** – Understanding Kibana's internal structure
- **[Fixture Generator Guide](kibana-fixture-generator-guide.md)** – Generating test fixtures from live Kibana instances

## Requirements

- Python 3.12+
- PyYAML 6.0+
- Pydantic 2.11.3+
- beartype 0.20.2+

## License

MIT

## Support

For issues and feature requests, please refer to the repository's issue tracker.
