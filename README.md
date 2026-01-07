<!-- markdownlint-disable MD041 -->
![project-banner-smaller](https://github.com/user-attachments/assets/2cf8c18b-32e1-4b32-9a15-41f0d0d657f7)

# YAML ➤ Lens Dashboard Compiler

Making Dashboards in Kibana is so much fun! Sometimes though, it's nice to build dashboards and visualizations without clicking and clacking in a web browser.

That's where the Yaml ➤ Lens Dashboard Compiler comes in. It converts human-friendly YAML dashboard definitions into Kibana NDJSON format:

## Features

- **YAML-based Dashboard Definition** – Define dashboards, panels, filters, and queries in simple YAML
- **Rich Panel Support** – Lens visualizations (metric, pie, XY charts), Markdown, Links, Image panels, and more
- **Advanced Controls** – Control groups with options lists, range sliders, and time sliders with chaining
- **Filter Support** – Exists, phrase, range, and custom DSL with AND/OR/NOT operators
- **Direct Upload** – Optional direct upload to Kibana with authentication support
- **Screenshot Export** – Generate PNG screenshots of dashboards with custom time ranges using Kibana's Reporting API

## Prerequisites

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** (recommended for dependency management)

## Quick Start

### Installation Options

#### Option 1: Using uv (Recommended for Development)

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

**For basic usage (compiling dashboards):**

```bash
uv sync
```

**For development (includes testing, linting, type checking):**

```bash
uv sync --group dev
```

Or simply use the convenience command:

```bash
make install
```

#### Option 2: Using Docker

Run the compiler in a container without installing Python or dependencies:

```bash
# Pull the pre-built image
docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest

# Or build locally
cd compiler && make docker-build
```

#### Option 3: Standalone Binary

Download a platform-specific binary from the [releases page](https://github.com/strawgate/kb-yaml-to-lens/releases):

- Linux (x64): `kb-dashboard-linux-x64`
- macOS (Intel): `kb-dashboard-darwin-x64`
- macOS (Apple Silicon): `kb-dashboard-darwin-arm64`
- Windows (x64): `kb-dashboard-windows-x64.exe`

No Python installation required!

### Compile Your First Dashboard

1. Create a YAML dashboard file in `inputs/` directory:

```yaml
dashboards:
- name: My First Dashboard
  description: A simple dashboard with markdown
  panels:
    - title: Welcome
      grid: { x: 0, y: 0, w: 24, h: 15 }  # Position and size on 48-column grid
      markdown:
        content: |
          # Welcome to Kibana!

          This is my first dashboard compiled from YAML.
```

1. Compile to NDJSON:

**Using uv:**

```bash
uv run kb-dashboard compile --input-dir inputs --output-dir output
```

**Using Docker:**

```bash
docker run --rm -v $(pwd)/inputs:/inputs -v $(pwd)/output:/output \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  compile --input-dir /inputs --output-dir /output
```

**Using standalone binary:**

```bash
./kb-dashboard-linux-x64 compile --input-dir inputs --output-dir output
```

1. (Optional) Upload directly to Kibana:

**Using uv:**

```bash
uv run kb-dashboard compile \
  --input-dir inputs \
  --output-dir output \
  --upload \
  --kibana-url http://localhost:5601 \
  --kibana-username elastic \
  --kibana-password changeme
```

**Using Docker:**

```bash
docker run --rm -v $(pwd)/inputs:/inputs \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  compile --input-dir /inputs --upload \
  --kibana-url http://host.docker.internal:5601 \
  --kibana-username elastic --kibana-password changeme
```

**Using standalone binary:**

```bash
./kb-dashboard-linux-x64 compile \
  --input-dir inputs \
  --output-dir output \
  --upload \
  --kibana-url http://localhost:5601 \
  --kibana-username elastic \
  --kibana-password changeme
```

The `--upload` flag will automatically open your dashboard in the browser upon successful upload.

## Documentation

- **[Online Documentation](https://strawgate.github.io/kb-yaml-to-lens/)** – Full documentation site with getting started guide and API reference
- **[Programmatic Usage Guide](docs/programmatic-usage.md)** – Create dashboards entirely in Python code
- **[Architecture](docs/architecture.md)** – Technical design and data flow overview
- **[Contributing Guide](CONTRIBUTING.md)** – How to contribute and add new capabilities

## CLI Commands

### Compile Dashboards

Compile YAML files to NDJSON format:

```bash
uv run kb-dashboard compile [OPTIONS]
```

**Options:**

- `--input-dir PATH` – Directory containing YAML files (default: `inputs`)
- `--output-dir PATH` – Output directory for NDJSON files (default: `output`)
- `--output-file NAME` – Combined output filename (default: `compiled_dashboards.ndjson`)
- `--upload` – Upload to Kibana after compilation
- `--kibana-url URL` – Kibana URL (default: `http://localhost:5601`, or set `KIBANA_URL` env var)
- `--kibana-username USER` – Username for basic auth (or set `KIBANA_USERNAME` env var)
- `--kibana-password PASS` – Password for basic auth (or set `KIBANA_PASSWORD` env var)
- `--kibana-api-key KEY` – API key for authentication (or set `KIBANA_API_KEY` env var)
- `--no-browser` – Don't open browser after upload
- `--overwrite/--no-overwrite` – Overwrite existing dashboards (default: `--overwrite`)
- `--kibana-no-ssl-verify` – Disable SSL certificate verification

### Screenshot Dashboard

Generate a PNG screenshot of a Kibana dashboard using the Kibana Reporting API:

```bash
uv run kb-dashboard screenshot --dashboard-id DASHBOARD_ID --output OUTPUT_FILE [OPTIONS]
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
uv run kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png

# Screenshot with custom time range (absolute)
uv run kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
  --time-from "2024-01-01T00:00:00Z" --time-to "2024-12-31T23:59:59Z"

# Screenshot with relative time range
uv run kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
  --time-from "now-7d" --time-to "now"

# Screenshot with custom dimensions (4K)
uv run kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png \
  --width 3840 --height 2160

# Screenshot with API key authentication
export KIBANA_API_KEY="your-api-key"
uv run kb-dashboard screenshot --dashboard-id my-dashboard --output dashboard.png
```

**Note:** This feature requires a Kibana instance with the Reporting plugin enabled (included by default in most Kibana distributions).

## License

MIT

## Support

For issues and feature requests, please refer to the repository's issue tracker.
