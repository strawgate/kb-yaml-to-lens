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

**For ⭐ VS Code Extension (Recommended):**
- VS Code 1.85.0+ or compatible editor (Cursor, VSCodium, etc.)
- No Python installation required - bundled binary included!

**For CLI (Automation/CI):**
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

## Quick Start

### Option 1: ⭐ VS Code Extension (Recommended for Getting Started)

**Best for:** Interactive dashboard development, visual editing, live preview

The VS Code extension is the fastest way to start building Kibana dashboards. It includes:
- Pre-built snippets for quick dashboard scaffolding
- Live preview as you type
- Visual drag-and-drop grid editor
- One-click upload to Kibana
- **No Python installation required** - LSP server binary is bundled

#### Installation

**From OpenVSX Registry (Cursor, VS Code forks):**
1. Open Extensions view (Ctrl+Shift+X)
2. Search for "Kibana Dashboard Compiler"
3. Click Install

**Manual VSIX Install:**
Download platform-specific `.vsix` from [releases page](https://github.com/strawgate/kb-yaml-to-lens/releases)

#### Verify Installation

After installation, verify the extension is working:

1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "YAML Dashboard" - you should see all extension commands
3. Create a test file: `test-dashboard.yaml`
4. Type `dashboard` and press Tab - a snippet should insert

If commands don't appear, restart VS Code and check the Output panel (View → Output → "Kibana Dashboard Compiler").

#### Your First Dashboard in VS Code

1. Create a new file: `my-dashboard.yaml`
2. Start typing `dashboard` and press Tab to insert snippet
3. Save (Ctrl+S) - auto-compiles in background
4. Run command (Ctrl+Shift+P): **"YAML Dashboard: Preview Dashboard"**
5. Configure Kibana URL in settings, then run: **"YAML Dashboard: Open in Kibana"**

**Learn more:** [VS Code Extension Documentation](https://strawgate.github.io/kb-yaml-to-lens/vscode-extension)

---

### Option 2: CLI (Best for Automation & CI/CD)

**Best for:** Scripting, CI/CD pipelines, batch processing, programmatic usage

The CLI provides three installation methods:

<details>
<summary><b>Click to expand CLI installation options</b></summary>

#### Using uv (Recommended for Development)

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

**For basic usage (compiling dashboards):**

```bash
uv sync
```

#### Using Docker

Run the compiler in a container without installing Python or dependencies:

```bash
# Pull the pre-built image
docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest

# Or build locally (from repo root)
make compiler docker-build
```

#### Standalone Binary

Download a platform-specific binary from the [releases page](https://github.com/strawgate/kb-yaml-to-lens/releases):

- Linux (x64): `kb-dashboard-linux-x64`
- macOS (Intel): `kb-dashboard-darwin-x64`
- macOS (Apple Silicon): `kb-dashboard-darwin-arm64`
- Windows (x64): `kb-dashboard-windows-x64.exe`

No Python installation required!

</details>

#### Compile Your First Dashboard (CLI)

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

Add `--upload --kibana-url http://localhost:5601 --kibana-username elastic --kibana-password changeme` to the compile command above.

The `--upload` flag will automatically open your dashboard in the browser upon successful upload.

**Learn more:** [CLI Documentation](https://strawgate.github.io/kb-yaml-to-lens/CLI)

## Documentation

### Getting Started
- **[VS Code Extension Guide](https://strawgate.github.io/kb-yaml-to-lens/vscode-extension)** - Visual dashboard development (recommended for beginners)
- **[CLI Reference](https://strawgate.github.io/kb-yaml-to-lens/CLI)** - Command-line compilation and automation
- **[Complete Examples](https://strawgate.github.io/kb-yaml-to-lens/examples/)** - Real-world dashboard examples you can copy

### Deep Dive
- **[Full Documentation Site](https://strawgate.github.io/kb-yaml-to-lens/)** - Complete user guide and API reference
- **[Programmatic Usage Guide](https://strawgate.github.io/kb-yaml-to-lens/programmatic-usage)** - Create dashboards entirely in Python code
- **[Architecture](https://strawgate.github.io/kb-yaml-to-lens/architecture)** - Technical design and data flow overview
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute and add new capabilities

## License

MIT

## Support

For issues and feature requests, please refer to the repository's issue tracker.
