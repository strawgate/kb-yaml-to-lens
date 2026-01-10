<!-- markdownlint-disable MD041 -->
![project-banner-smaller](https://github.com/user-attachments/assets/2cf8c18b-32e1-4b32-9a15-41f0d0d657f7)

# YAML ➤ Lens Dashboard Compiler

Build Kibana dashboards from human-friendly YAML and compile to NDJSON.

## Features

- **YAML-based Dashboard Definition** – Define dashboards, panels, filters, and queries in simple YAML
- **Rich Panel Support** – Lens visualizations (metric, pie, XY charts), Markdown, Links, Image panels, and more
- **Advanced Controls** – Control groups with options lists, range sliders, and time sliders with chaining
- **Filter Support** – Exists, phrase, range, and custom DSL with AND/OR/NOT operators
- **Direct Upload** – Optional direct upload to Kibana with authentication support

## Prerequisites

**VS Code extension (recommended):**
- VS Code 1.85.0+ or compatible editor
- Bundled binary (no Python required)

**CLI (automation/CI):**
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)

## Quick Start

### Option 1: ⭐ VS Code Extension (Recommended)

**Best for:** Interactive development, visual editing, live preview

Includes snippets, live preview, drag-and-drop grid editor, and one-click upload. The LSP server binary is bundled.

#### Installation

**From OpenVSX Registry (Cursor, VS Code forks):**
1. Open Extensions view (Ctrl+Shift+X)
2. Search for "Kibana Dashboard Compiler"
3. Click Install

**Manual VSIX Install:**
Download platform-specific `.vsix` from [releases page](https://github.com/strawgate/kb-yaml-to-lens/releases)

#### Verify Installation

1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "YAML Dashboard" to see the commands
3. Create `test-dashboard.yaml`
4. Type `dashboard` and press Tab to insert a snippet

If commands don't appear, restart VS Code and check Output → "Kibana Dashboard Compiler".

#### Your First Dashboard in VS Code

1. Create `my-dashboard.yaml`
2. Type `dashboard` and press Tab
3. Save (auto-compiles)
4. Run **"YAML Dashboard: Preview Dashboard"**
5. Set Kibana URL, then run **"YAML Dashboard: Open in Kibana"**

**Learn more:** [VS Code Extension Documentation](https://strawgate.github.io/kb-yaml-to-lens/vscode-extension)

---

### Option 2: CLI (Automation & CI/CD)

**Best for:** Scripting, pipelines, batch processing, programmatic usage

The CLI provides three installation methods:

<details>
<summary><b>Click to expand CLI installation options</b></summary>

#### Using uv (Recommended for Development)

Install dependencies:

```bash
uv sync
```

#### Using Docker

Run in a container without installing Python or dependencies:

```bash
# Pull the pre-built image
docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest

# Or build locally
cd compiler && make docker-build
```

#### Standalone Binary

Download a platform-specific binary from the [releases page](https://github.com/strawgate/kb-yaml-to-lens/releases):

- Linux (x64): `kb-dashboard-linux-x64`
- macOS (Intel): `kb-dashboard-darwin-x64`
- macOS (Apple Silicon): `kb-dashboard-darwin-arm64`
- Windows (x64): `kb-dashboard-windows-x64.exe`

No Python installation required.

</details>

#### Compile Your First Dashboard (CLI)

1. Create a YAML dashboard file in `inputs/`:

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

2. Compile to NDJSON:

If using uv: `uv run kb-dashboard compile --input-dir inputs --output-dir output`

If using Docker:
```bash
docker run --rm -v $(pwd)/inputs:/inputs -v $(pwd)/output:/output \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  compile --input-dir inputs --output-dir output
```

If using standalone binary: `./kb-dashboard-<platform> compile --input-dir inputs --output-dir output`

3. (Optional) Upload directly to Kibana:

Add `--upload --kibana-url http://localhost:5601 --kibana-username elastic --kibana-password changeme` to the compile command. The `--upload` flag opens the dashboard on success.

**Learn more:** [CLI Documentation](https://strawgate.github.io/kb-yaml-to-lens/CLI)

## Documentation

### Getting Started
- **[VS Code Extension Guide](https://strawgate.github.io/kb-yaml-to-lens/vscode-extension)** - Visual dashboard development
- **[CLI Reference](https://strawgate.github.io/kb-yaml-to-lens/CLI)** - Command-line compilation and automation
- **[Complete Examples](https://strawgate.github.io/kb-yaml-to-lens/examples/)** - Sample dashboards

### Deep Dive
- **[Full Documentation Site](https://strawgate.github.io/kb-yaml-to-lens/)** - User guide and API reference
- **[Programmatic Usage Guide](https://strawgate.github.io/kb-yaml-to-lens/programmatic-usage)** - Build dashboards in Python
- **[Architecture](https://strawgate.github.io/kb-yaml-to-lens/architecture)** - Design and data flow
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute

## License

MIT

## Support

For issues and feature requests, please refer to the repository's issue tracker.
