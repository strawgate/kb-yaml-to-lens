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

All future commands that use uv should start with `uv run kb-dashboard <command>`.

All future commands that use Docker should start with:

```bash
docker run --rm -v $(pwd)/inputs:/inputs -v $(pwd)/output:/output \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest <command>
```

All future commands that use the standalone binary should start with:

```bash
./kb-dashboard-<platform> <command>
```

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

```bash
<compiler-command> compile --input-dir inputs --output-dir output
```

1. (Optional) Upload directly to Kibana:

```bash
<compiler-command> compile --input-dir inputs --output-dir output --upload --kibana-url http://localhost:5601 --kibana-username elastic --kibana-password changeme
```

The `--upload` flag will automatically open your dashboard in the browser upon successful upload.

## Documentation

- **[Online Documentation](https://strawgate.github.io/kb-yaml-to-lens/)** – Full documentation site with getting started guide and API reference
- **[Programmatic Usage Guide](docs/programmatic-usage.md)** – Create dashboards entirely in Python code
- **[Architecture](docs/architecture.md)** – Technical design and data flow overview
- **[Contributing Guide](CONTRIBUTING.md)** – How to contribute and add new capabilities

## License

MIT

## Support

For issues and feature requests, please refer to the repository's issue tracker.
