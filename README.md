# Dashboard Compiler

Convert human-friendly YAML dashboard definitions into Kibana NDJSON format.

This tool simplifies the process of creating and managing Kibana dashboards by allowing you to define them in a clean, maintainable YAML format instead of hand-crafting complex JSON.

## Features

- **YAML-based Dashboard Definition** – Define dashboards, panels, filters, and queries in simple YAML
- **Kibana Integration** – Compile to NDJSON format compatible with Kibana 8+
- **Rich Panel Support** – Lens visualizations (metric, pie, XY charts), Markdown, Links, Image panels, and Search panels (in development)
- **Advanced Controls** – Control groups with options lists, range sliders, and time sliders with chaining
- **Flexible Filtering** – Comprehensive filter DSL supporting exists, phrase, range, and custom DSL with AND/OR/NOT operators
- **Multiple Query Types** – KQL, Lucene, and ESQL query support
- **Direct Upload** – Optional direct upload to Kibana with authentication support

## Quick Start

### Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management:

```bash
uv sync --group dev
```

For more information, see the [uv documentation](https://docs.astral.sh/uv/).

### Compile Your First Dashboard

1. Create a YAML dashboard file in `inputs/` directory:

```yaml
dashboard:
  title: My First Dashboard
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

The `--upload` flag will automatically open your dashboard in the browser upon successful upload.

## Documentation

- **[Online Documentation](https://strawgate.github.io/kb-yaml-to-lens/)** – Full documentation site with API reference
- **[Quickstart Guide](docs/quickstart.md)** – Step-by-step guide for creating your first dashboard
- **[Architecture](docs/architecture.md)** – Technical design and data flow overview
- **[YAML Reference](yaml_reference.md)** – Complete schema documentation for all dashboard elements
- **[ES|QL Pie Chart Capabilities](docs/esql-pie-chart-capabilities.md)** – Comprehensive feature comparison and usage guide
- **[Contributing Guide](CONTRIBUTING.md)** – How to contribute and add new capabilities

## CLI Commands

### Compile Dashboards

Compile YAML files to NDJSON format:

```bash
kb-dashboard compile [OPTIONS]
```

**Options:**

- `--input-dir PATH` – Directory containing YAML files (default: `tests/dashboards/scenarios`)
- `--output-dir PATH` – Output directory for NDJSON files (default: `output`)
- `--output-file NAME` – Combined output filename (default: `compiled_dashboards.ndjson`)
- `--upload` – Upload to Kibana after compilation
- `--kibana-url URL` – Kibana URL (default: `http://localhost:5601`, or set `KIBANA_URL` env var)
- `--kibana-username USER` – Username for basic auth (or set `KIBANA_USERNAME` env var)
- `--kibana-password PASS` – Password for basic auth (or set `KIBANA_PASSWORD` env var)
- `--kibana-api-key KEY` – API key for authentication (or set `KIBANA_API_KEY` env var)
- `--no-browser` – Don't open browser after upload
- `--overwrite/--no-overwrite` – Overwrite existing dashboards (default: `--overwrite`)

## Project Structure

```
src/dashboard_compiler/
├── cli.py                 # Command-line interface
├── dashboard_compiler.py  # Main compilation logic
├── kibana_client.py       # Kibana API client
├── dashboard/             # Dashboard compilation
├── panels/                # Panel compilers (Lens, Markdown, Links, Images)
├── controls/              # Control group compilation
├── filters/               # Filter compilation
├── queries/               # Query compilation
└── shared/                # Shared utilities and models
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for Python linting and formatting, and [markdownlint](https://github.com/DavidAnson/markdownlint) for markdown files:

```bash
# Run all linters and formatters
make lint

# Check Python code quality
uv run ruff check .

# Format Python code
uv run ruff format .

# Lint markdown files
markdownlint --fix -c .markdownlint.jsonc .
```

### Documentation

Build and preview the documentation locally:

```bash
# Install documentation dependencies
uv sync --extra docs

# Serve documentation locally
make docs-serve

# Build static documentation site
make docs-build

# Deploy to GitHub Pages
make docs-deploy
```

### Adding New Features

See [CONTRIBUTING.md](CONTRIBUTING.md) for the process of adding new dashboard capabilities.

## Requirements

- Python 3.12+
- PyYAML 6.0+
- Pydantic 2.11.3+
- beartype 0.20.2+
- Node.js/npm (for markdown linting, development only)

## License

MIT

## Support

For issues and feature requests, please refer to the repository's issue tracker.
