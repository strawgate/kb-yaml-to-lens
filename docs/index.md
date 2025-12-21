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
  Markdown, Links, Image panels, and Search panels (in development)
- **Advanced Controls** – Control groups with options lists, range sliders,
  and time sliders with chaining
- **Flexible Filtering** – Comprehensive filter DSL supporting exists, phrase,
  range, and custom DSL with AND/OR/NOT operators
- **Multiple Query Types** – KQL, Lucene, and ESQL query support
- **Direct Upload** – Optional direct upload to Kibana with authentication
  support

## Quick Start

### Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable
Python package management:

```bash
uv sync --all-extras
```

For more information, see the [uv documentation](https://docs.astral.sh/uv/).

### Compile Your First Dashboard

1. Create a YAML dashboard file in `inputs/` directory:

```yaml
dashboard:
  name: My First Dashboard
  description: A simple dashboard with markdown
  panels:
    - panel:
        type: markdown
        grid: { x: 0, y: 0, w: 24, h: 15 }
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

## Documentation

- **[Quickstart Guide](quickstart.md)** – Step-by-step guide for creating your
  first dashboard
- **[Architecture](architecture.md)** – Technical design and data flow overview
- **[YAML Reference](yaml_reference.md)** – Complete schema documentation for
  all dashboard elements
- **[Contributing Guide](CONTRIBUTING.md)** – How to contribute and add new
  capabilities

## Requirements

- Python 3.12+
- PyYAML 6.0+
- Pydantic 2.11.3+
- beartype 0.20.2+

## License

MIT

## Support

For issues and feature requests, please refer to the repository's issue tracker.
