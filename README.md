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
- **Screenshot Export** – Generate PNG screenshots of dashboards with custom time ranges using Kibana's Reporting API

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

The `--upload` flag will automatically open your dashboard in the browser upon successful upload.

## Documentation

- **[Online Documentation](https://strawgate.github.io/kb-yaml-to-lens/)** – Full documentation site with API reference
- **[Quickstart Guide](docs/quickstart.md)** – Step-by-step guide for creating your first dashboard
- **[Architecture](docs/architecture.md)** – Technical design and data flow overview
- **[YAML Reference](yaml_reference.md)** – Complete schema documentation for all dashboard elements
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

### Screenshot Dashboard

Generate a PNG screenshot of a Kibana dashboard using the Kibana Reporting API:

```bash
kb-dashboard screenshot --dashboard-id DASHBOARD_ID --output OUTPUT_FILE [OPTIONS]
```

**Required Options:**

- `--dashboard-id ID` – The Kibana dashboard ID to screenshot
- `--output PATH` – Output PNG file path

**Options:**

- `--time-from TIME` – Start time for dashboard time range (ISO 8601 format or relative like "now-7d")
- `--time-to TIME` – End time for dashboard time range (ISO 8601 format or relative like "now")
- `--width PIXELS` – Screenshot width in pixels (default: 1920)
- `--height PIXELS` – Screenshot height in pixels (default: 1080)
- `--browser-timezone TZ` – Timezone for the screenshot (default: UTC)
- `--timeout SECONDS` – Maximum seconds to wait for screenshot generation (default: 300)
- `--kibana-url URL` – Kibana URL (default: `http://localhost:5601`, or set `KIBANA_URL` env var)
- `--kibana-username USER` – Username for basic auth (or set `KIBANA_USERNAME` env var)
- `--kibana-password PASS` – Password for basic auth (or set `KIBANA_PASSWORD` env var)
- `--kibana-api-key KEY` – API key for authentication (or set `KIBANA_API_KEY` env var)

**Examples:**

```bash
# Screenshot with default settings
kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png

# Screenshot with custom time range (absolute)
kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
  --time-from "2024-01-01T00:00:00Z" --time-to "2024-12-31T23:59:59Z"

# Screenshot with relative time range
kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
  --time-from "now-7d" --time-to "now"

# Screenshot with custom dimensions (4K)
kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
  --width 3840 --height 2160

# Screenshot with API key authentication
export KIBANA_API_KEY="your-api-key"
kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png
```

**Note:** This feature requires a Kibana instance with the Reporting plugin enabled (included by default in most Kibana distributions).

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
