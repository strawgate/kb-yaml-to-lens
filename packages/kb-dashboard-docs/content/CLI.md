# Dashboard Compiler CLI

The `kb-dashboard` CLI tool allows you to compile YAML dashboard configurations to Kibana's NDJSON format and optionally upload them directly to Kibana.

## Prerequisites

- **[uv](https://github.com/astral-sh/uv)** (recommended) - Enables running the CLI via `uvx` with zero setup
- Or **Python 3.12+** with pip for traditional installation

**Note:** When using `uvx`, Python and all dependencies are handled automatically. The VS Code Extension does not require Python either - it includes a bundled binary. See [VS Code Extension Documentation](vscode-extension.md) for zero-configuration setup.

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

### Using uvx (Recommended)

Run the CLI directly without cloning or installing anything:

```bash
uvx kb-dashboard-cli compile --help
```

This downloads and runs the published package automatically. No Python environment setup required!

### Development Installation

For contributors or development workflows, clone the repository:

```bash
git clone https://github.com/strawgate/kb-yaml-to-lens
cd kb-yaml-to-lens
make cli install
```

See [DEVELOPING.md](https://github.com/strawgate/kb-yaml-to-lens/blob/main/DEVELOPING.md) for full development setup.

## Basic Usage

### Compile Dashboards

Compile YAML dashboards to NDJSON format:

```bash
uvx kb-dashboard-cli compile
```

This will:

- Find all YAML files in `inputs/` (by default)
- Compile them to Kibana JSON format
- Output NDJSON files to `output/` directory
- Create individual NDJSON files per scenario
- Create a combined `compiled_dashboards.ndjson` file

### Compile a Single File

Compile a specific YAML file without scanning a directory:

```bash
uvx kb-dashboard-cli compile --input-file ./dashboards/example.yaml
```

When `--input-file` is provided, `--input-dir` is ignored.

### Export Individual JSON Files

For workflows that require individual JSON files per dashboard (e.g., Fleet integration):

```bash
uvx kb-dashboard-cli compile --format json --output-dir ./output
```

This will:

- Create one pretty-printed JSON file per dashboard
- Name files based on the dashboard title (sanitized for filesystem safety)

### CI Sync Detection

Use the `--exit-non-zero-on-change` flag to detect when YAML and JSON files are out of sync in CI pipelines:

```bash
uvx kb-dashboard-cli compile --format json --output-dir ./dashboards --exit-non-zero-on-change
if [ $? -ne 0 ]; then
    echo "Dashboard JSON files are out of sync with YAML sources"
    exit 1
fi
```

When this flag is enabled, the exit code equals the number of files that changed (capped at 125). By default, the command exits with code 0 on success regardless of whether files changed.

### Compile and Upload to Kibana

Compile dashboards and upload them directly to Kibana:

```bash
uvx kb-dashboard-cli compile --upload
```

This will compile the dashboards and upload them to a local Kibana instance.

### Screenshot Dashboards

Generate a PNG screenshot of a dashboard:

```bash
uvx kb-dashboard-cli screenshot --dashboard-id <id> --output <file.png>
```

This will use Kibana's Reporting API to take a screenshot.

### Export Dashboard for Issue

Export a dashboard from Kibana and create a pre-filled GitHub issue:

```bash
uvx kb-dashboard-cli export-for-issue --dashboard-id <id>
```

This will export the dashboard and open your browser with a pre-filled GitHub issue containing the dashboard JSON.

### Disassemble Dashboards

Break down a Kibana dashboard JSON into components for easier LLM-based conversion:

```bash
uvx kb-dashboard-cli disassemble dashboard.ndjson -o output_dir
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
uvx kb-dashboard-cli compile --upload
```

### Command-Line Options

All options can also be specified on the command line:

```bash
uvx kb-dashboard-cli compile \
  --upload \
  --kibana-url http://localhost:5601 \
  --kibana-username elastic \
  --kibana-password changeme
```

To upload to a specific Kibana space:

```bash
uvx kb-dashboard-cli compile --upload --kibana-space-id production
```

Or with environment variables:

```bash
export KIBANA_SPACE_ID=staging
uvx kb-dashboard-cli compile --upload
```

## Command Reference

The following commands are available in the `kb-dashboard` CLI. For detailed information about each command and its options, see the auto-generated reference below.

::: mkdocs-click
    :module: dashboard_compiler.cli
    :command: cli
    :prog_name: kb-dashboard
    :depth: 2
    :style: table

## Makefile Shortcuts (Development)

For contributors working from a cloned repository, the project includes convenient Makefile targets:

```bash
# Compile only
make cli compile

# Compile and upload (uses environment variables for Kibana config)
make cli upload
```

See [DEVELOPING.md](https://github.com/strawgate/kb-yaml-to-lens/blob/main/DEVELOPING.md) for the full development workflow.

## Authentication

The CLI supports two authentication methods:

### Basic Authentication

Use username and password:

```bash
uvx kb-dashboard-cli compile \
  --upload \
  --kibana-username elastic \
  --kibana-password changeme
```

Or via environment variables:

```bash
export KIBANA_USERNAME=elastic
export KIBANA_PASSWORD=changeme
uvx kb-dashboard-cli compile --upload
```

### API Key Authentication

Use a Kibana API key:

```bash
uvx kb-dashboard-cli compile \
  --upload \
  --kibana-api-key "your-base64-encoded-key"
```

Or via environment variable:

```bash
export KIBANA_API_KEY="your-base64-encoded-key"
uvx kb-dashboard-cli compile --upload
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

---

## Dashboard Linter CLI

The `kb-dashboard-lint` CLI tool checks YAML dashboard configurations for best practices and common issues.

### Basic Usage

Check a single dashboard file:

```bash
uvx kb-dashboard-lint check --input-file ./dashboards/example.yaml
```

Check all dashboards in a directory:

```bash
uvx kb-dashboard-lint check --input-dir ./dashboards
```

### Severity Levels

The linter reports issues at three severity levels:

| Level | Description |
| ----- | ----------- |
| **error** | Critical issues that should be fixed |
| **warning** | Problems that may affect usability |
| **info** | Suggestions for improvement |

By default, the linter exits with code 0 for info-only results. Use `--severity-threshold` to fail on warnings:

```bash
uvx kb-dashboard-lint check --input-file dashboard.yaml --severity-threshold warning
```

### List Available Rules

See all lint rules and their descriptions:

```bash
uvx kb-dashboard-lint list-rules
```

### Configuration

Create a `.dashboard-lint.yaml` file to customize rule behavior:

```bash
uvx kb-dashboard-lint check --config .dashboard-lint.yaml
```

### Output Formats

Get machine-readable output for CI integration:

```bash
uvx kb-dashboard-lint check --input-dir ./dashboards --format json
```

### Linter Command Reference

::: mkdocs-click
    :module: dashboard_lint.cli
    :command: cli
    :prog_name: kb-dashboard-lint
    :depth: 2
    :style: table
