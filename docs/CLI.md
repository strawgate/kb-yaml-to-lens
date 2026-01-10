# Dashboard Compiler CLI

The `kb-dashboard` CLI tool allows you to compile YAML dashboard configurations to Kibana's NDJSON format and optionally upload them directly to Kibana.

## Prerequisites

- **Python 3.12+** - Required for CLI usage
- **[uv](https://github.com/astral-sh/uv)** (recommended) or pip for dependency management

**Note:** The VS Code Extension does not require Python - it includes a bundled binary. See [VS Code Extension Documentation](vscode-extension.md) for zero-configuration setup.

## When to Use the CLI

**Use the CLI when:**

- ✅ Building CI/CD pipelines for dashboard deployment
- ✅ Batch processing multiple dashboards
- ✅ Scripting dashboard generation (e.g., templates, dynamic data)
- ✅ Integrating with other automation tools
- ✅ Running in headless/server environments without GUI
- ✅ Using Docker containers or serverless functions

**Use the VS Code Extension when:**

- ✅ Developing dashboards interactively
- ✅ Learning the YAML schema
- ✅ Making frequent visual adjustments
- ✅ Needing live preview and validation

**See:** [VS Code Extension Documentation](vscode-extension.md) for interactive development workflow.

---

## Installation

After installing the project dependencies, the CLI will be available:

```bash
uv sync
```

## Basic Usage

### Compile Dashboards

Compile YAML dashboards to NDJSON format:

```bash
kb-dashboard compile
```

This will:

- Find all YAML files in `inputs/` (by default)
- Compile them to Kibana JSON format
- Output NDJSON files to `output/` directory
- Create individual NDJSON files per scenario
- Create a combined `compiled_dashboards.ndjson` file

### Compile and Upload to Kibana

Compile dashboards and upload them directly to Kibana:

```bash
kb-dashboard compile --upload
```

This will compile the dashboards and upload them to a local Kibana instance.

### Screenshot Dashboards

Generate a PNG screenshot of a dashboard:

```bash
kb-dashboard screenshot --dashboard-id <id> --output <file.png>
```

This will use Kibana's Reporting API to take a screenshot.

### Export Dashboard for Issue

Export a dashboard from Kibana and create a pre-filled GitHub issue:

```bash
kb-dashboard export-for-issue --dashboard-id <id>
```

This will export the dashboard and open your browser with a pre-filled GitHub issue containing the dashboard JSON.

### Disassemble Dashboards

Break down a Kibana dashboard JSON into components for easier LLM-based conversion:

```bash
kb-dashboard disassemble dashboard.ndjson -o output_dir
```

This will extract the dashboard into separate files:

- `metadata.json` - Dashboard metadata (id, title, description, version)
- `options.json` - Dashboard display options
- `controls.json` - Control group configuration
- `filters.json` - Dashboard-level filters
- `references.json` - Data view references
- `panels/` - Individual panel JSON files

For a comprehensive guide on using this tool to convert dashboards from JSON to YAML, see the [Dashboard Decompiling Guide](dashboard-decompiling-guide.md).

## Configuration

### Environment Variables

The CLI supports configuration via environment variables:

```bash
export KIBANA_URL=http://localhost:5601
export KIBANA_USERNAME=elastic
export KIBANA_PASSWORD=changeme
export KIBANA_SPACE_ID=my-space  # Optional: target a specific Kibana space
# OR use API key instead
export KIBANA_API_KEY=your-api-key-here
```

Then simply run:

```bash
kb-dashboard compile --upload
```

### Command-Line Options

All options can also be specified on the command line:

```bash
kb-dashboard compile \
  --upload \
  --kibana-url http://localhost:5601 \
  --kibana-username elastic \
  --kibana-password changeme
```

To upload to a specific Kibana space:

```bash
kb-dashboard compile --upload --kibana-space-id production
```

Or with environment variables:

```bash
export KIBANA_SPACE_ID=staging
kb-dashboard compile --upload
```

## Command Reference

The following commands are available in the `kb-dashboard` CLI. For detailed information about each command and its options, see the auto-generated reference below.

::: mkdocs-click
    :module: dashboard_compiler.cli
    :command: cli
    :prog_name: kb-dashboard
    :depth: 2
    :style: table

## Makefile Shortcuts

The project includes convenient Makefile targets (run from `compiler/` directory):

```bash
# Compile only
cd compiler && make compile

# Compile and upload (uses environment variables for Kibana config)
cd compiler && make upload
```

Or use the CLI directly from anywhere with uv:

```bash
cd compiler && uv run kb-dashboard compile
cd compiler && uv run kb-dashboard compile --upload
```

## Authentication

The CLI supports two authentication methods:

### Basic Authentication

Use username and password:

```bash
kb-dashboard compile \
  --upload \
  --kibana-username elastic \
  --kibana-password changeme
```

Or via environment variables:

```bash
export KIBANA_USERNAME=elastic
export KIBANA_PASSWORD=changeme
kb-dashboard compile --upload
```

### API Key Authentication

Use a Kibana API key:

```bash
kb-dashboard compile \
  --upload \
  --kibana-api-key "your-base64-encoded-key"
```

Or via environment variable:

```bash
export KIBANA_API_KEY="your-base64-encoded-key"
kb-dashboard compile --upload
```

To create an API key in Kibana:

1. Go to Stack Management → API Keys
2. Click "Create API key"
3. Give it a name and set appropriate privileges
4. Copy the encoded key and use it with the CLI

## Troubleshooting

### Connection Refused

If you get a connection refused error:

- Verify Kibana is running: `curl http://localhost:5601/api/status`
- Check the Kibana URL is correct
- Ensure there are no firewall rules blocking the connection

### Authentication Failed

If you get authentication errors:

- Verify your credentials are correct
- Check that the user has appropriate permissions
- For API keys, ensure the key hasn't expired

### Upload Errors

If objects fail to upload:

- Check the Kibana logs for detailed error messages
- Verify the NDJSON format is valid
- Use `--no-overwrite` if you want to preserve existing objects
