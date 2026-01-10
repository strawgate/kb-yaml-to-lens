# YAML ➤ Lens Dashboard Compiler

Convert human-friendly YAML dashboard definitions into Kibana NDJSON format.

![The Chameleon mascot](./images/project-banner-smaller.png)

This tool simplifies the process of creating and managing Kibana dashboards by
allowing you to define them in a clean, maintainable YAML format instead of
hand-crafting complex JSON.

```mermaid
graph TB
    YAML[YAML Definition]

    subgraph "Interactive Development"
        EXT[VS Code Extension]
        YAML --> EXT
        EXT --> PREVIEW[Live Preview]
        EXT --> KIBANA[Direct Upload to Kibana]
    end

    subgraph "Automation/CI"
        CLI[CLI Compiler]
        YAML --> CLI
        CLI --> NDJSON[NDJSON Files]
        NDJSON --> KIBANA
    end
```

## Features

- **YAML-based Definition** – Define dashboards, panels, filters, and queries in simple, readable YAML.
- **Kibana Integration** – Compile to NDJSON format compatible with Kibana 8+.
- **Rich Panel Support** – Support for Lens (metric, pie, XY charts), Markdown, Links, Image, and Search panels.
- **Color Palettes** – Choose from color-blind safe, brand, and other built-in color palettes.
- **Interactive Controls** – Add options lists, range sliders, and time sliders with chaining support.
- **Flexible Filtering** – Use a comprehensive filter DSL (exists, phrase, range) or raw KQL/Lucene/ESQL queries.
- **Direct Upload** – Compile and upload to Kibana in one step, with support for authentication and API keys.
- **Screenshot Export** – Generate high-quality PNG screenshots of your dashboards programmatically.

## Getting Started

### Choose Your Path

#### ⭐ VS Code Extension (Recommended)

**Best for interactive development** - Live preview, visual editing, built-in snippets

**No Python installation required!** The extension includes a bundled LSP server binary.

**Installation:**

1. **Install the extension:**
   - **OpenVSX Registry** (Cursor, VS Code forks): Search "Kibana Dashboard Compiler"
   - **Manual**: Download `.vsix` from [releases](https://github.com/strawgate/kb-yaml-to-lens/releases)

2. **Create your first dashboard:**
   - Create new file: `my-dashboard.yaml`
   - Type `dashboard` and press Tab to insert snippet
   - Modify the template with your content
   - Save (Ctrl+S) to auto-compile

3. **Verify installation:**
   - Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
   - Type "YAML Dashboard" - you should see extension commands
   - Create test file, type `dashboard` + Tab to verify snippets work

4. **Preview and upload:**
   - Command Palette (Ctrl+Shift+P): **"YAML Dashboard: Preview Dashboard"**
   - Configure Kibana URL in VS Code settings
   - Command: **"YAML Dashboard: Open in Kibana"**

**Full guide:** [VS Code Extension Documentation](vscode-extension.md)

---

#### CLI (For Automation & Scripting)

**Best for:** CI/CD pipelines, batch processing, programmatic usage

**Installation:** Requires Python 3.12+

Using [uv](https://github.com/astral-sh/uv):

```bash
cd compiler
uv sync
```

**Your First Dashboard:**

1. Create `inputs/my-dashboard.yaml`:

   ```yaml
   dashboards:
   - name: My First Dashboard
     description: A simple dashboard
     panels:
       - title: Welcome
         grid: { x: 0, y: 0, w: 24, h: 15 }
         markdown:
           content: |
             # Welcome to Kibana!
   ```

2. Compile:

   ```bash
   cd compiler
   uv run kb-dashboard compile
   ```

3. Upload to Kibana:

   ```bash
   uv run kb-dashboard compile --upload --kibana-url http://localhost:5601
   ```

**Full guide:** [CLI Documentation](CLI.md)

---

### Example Dashboards

Both the extension and CLI use the same YAML format. Here are some examples:

#### Example 1: Simple Markdown Panel

Here's a dashboard with a single markdown panel:

```yaml
dashboards:
- name: My First Dashboard
  description: A simple dashboard with markdown
  panels:
    - title: Hello Panel
      markdown:
        content: |
          # Hello, Kibana!

          This is my first markdown panel.
      grid: { x: 0, y: 0, w: 24, h: 15 }  # Half-width on 48-column grid
```

#### Example 2: Simple Lens Metric Panel

Here's a dashboard with a single Lens metric panel displaying a count:

```yaml
dashboards:
-
  name: Metric Dashboard
  description: A dashboard with a single metric panel
  panels:
    - title: Document Count
      type: lens
      grid: { x: 0, y: 0, w: 24, h: 15 }  # Half-width on 48-column grid
      index_pattern: your-index-pattern-*
      chart:
        type: metric
        metrics:
          - type: count
            label: Total Documents
```

### Programmatic Alternative

While this guide focuses on YAML, you can also create dashboards entirely in Python code! This approach offers:

- Dynamic dashboard generation based on runtime data
- Type safety with Pydantic models
- Reusable dashboard templates and components
- Integration with existing Python workflows

See the [Programmatic Usage Guide](programmatic-usage.md) for examples and patterns.

## Next Steps

### Enhance Your Workflow

- **[VS Code Extension Features](vscode-extension.md)** - Visual grid editor, code snippets, keyboard shortcuts
- **[CLI Advanced Usage](CLI.md)** - Environment variables, API keys, CI/CD integration
- **[Dashboard Decompiling Guide](dashboard-decompiling-guide.md)** - Convert existing Kibana JSON dashboards to YAML
- **[Complete Examples](examples/index.md)** - Production-ready dashboard templates

### User Guide

Reference documentation for YAML dashboard syntax:

- **[Dashboard Configuration](dashboard/dashboard.md)** - Dashboard-level settings and options.
- **[Panel Types](panels/base.md)** - Available panel types (Markdown, Charts, Images, Links, etc.).
- **[Dashboard Controls](controls/config.md)** - Interactive filtering controls.
- **[Filters & Queries](filters/config.md)** - Data filtering and query configuration.

### Developer Guide

Advanced documentation for contributors and programmatic usage:

- **[Architecture Overview](architecture.md)** - Technical design and data flow.
- **[Programmatic Usage](programmatic-usage.md)** - Using the Python API directly to generate dashboards.
- **[API Reference](api/index.md)** - Auto-generated Python API documentation.
- **[Contributing Guide](https://github.com/strawgate/kb-yaml-to-lens/blob/main/CONTRIBUTING.md)** - How to contribute and add new capabilities.
- **[Kibana Architecture Reference](kibana-architecture.md)** - Understanding Kibana's internal structure.
- **[Fixture Generator Guide](kibana-fixture-generator-guide.md)** - Generating test fixtures from live Kibana instances.

## Requirements

- Python 3.12+

## License

MIT

### Third-Party Content

Some example dashboards in `docs/examples/` are derived from the [Elastic integrations repository](https://github.com/elastic/integrations) and are licensed under the [Elastic License 2.0](https://github.com/strawgate/kb-yaml-to-lens/blob/main/licenses/ELASTIC-LICENSE-2.0.txt). Specifically:

- `docs/examples/system_otel/` - System monitoring dashboards for OpenTelemetry
- `docs/examples/docker_otel/` - Docker container monitoring dashboards for OpenTelemetry

See [licenses/README.md](https://github.com/strawgate/kb-yaml-to-lens/blob/main/licenses/README.md) for the complete list of affected files.

## Support

For issues and feature requests, please refer to the repository's issue tracker.
