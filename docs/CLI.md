# Dashboard Compiler CLI

The `kb-dashboard` CLI tool allows you to compile YAML dashboard configurations to Kibana's NDJSON format and optionally upload them directly to Kibana.

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

## Full Command Reference

### `kb-dashboard compile`

Compile YAML dashboard configurations to NDJSON format.

**Options:**

- `--input-dir PATH` - Directory containing YAML dashboard files (default: `inputs/`)
- `--output-dir PATH` - Directory to write compiled NDJSON files (default: `output/`)
- `--output-file NAME` - Name of the combined output NDJSON file (default: `compiled_dashboards.ndjson`)
- `--upload` - Upload compiled dashboards to Kibana after compilation
- `--kibana-url URL` - Kibana base URL (default: `http://localhost:5601`, can use `KIBANA_URL` env var)
- `--kibana-username USER` - Kibana username for basic auth (can use `KIBANA_USERNAME` env var)
- `--kibana-password PASS` - Kibana password for basic auth (can use `KIBANA_PASSWORD` env var)
- `--kibana-api-key KEY` - Kibana API key for authentication (can use `KIBANA_API_KEY` env var)
- `--no-browser` - Do not open browser after upload
- `--overwrite/--no-overwrite` - Overwrite existing dashboards in Kibana (default: `--overwrite`)
- `--kibana-no-ssl-verify` - Disable SSL certificate verification

### `kb-dashboard screenshot`

Generate a PNG screenshot of a Kibana dashboard.

**Options:**

- `--dashboard-id TEXT` - Kibana dashboard ID to capture (required)
- `--output PATH` - Path where the PNG screenshot will be saved (required)
- `--time-from TEXT` - Start time for dashboard data range (e.g., "2024-01-01T00:00:00Z" or "now-7d")
- `--time-to TEXT` - End time for dashboard data range (e.g., "now")
- `--width INTEGER` - Screenshot width in pixels (default: 1920)
- `--height INTEGER` - Screenshot height in pixels (default: 1080)
- `--browser-timezone TEXT` - Browser timezone (default: UTC)
- `--timeout INTEGER` - Maximum time in seconds to wait (default: 300)
- `--kibana-url URL` - Kibana base URL (default: `http://localhost:5601`)
- `--kibana-username USER` - Kibana username
- `--kibana-password PASS` - Kibana password
- `--kibana-api-key KEY` - Kibana API key
- `--kibana-no-ssl-verify` - Disable SSL certificate verification

### `kb-dashboard export-for-issue`

Export a dashboard from Kibana and create a pre-filled GitHub issue for requesting compilation support.

**Options:**

- `--dashboard-id TEXT` - Kibana dashboard ID to export (required)
- `--kibana-url URL` - Kibana base URL (default: `http://localhost:5601`)
- `--kibana-username USER` - Kibana username
- `--kibana-password PASS` - Kibana password
- `--kibana-api-key KEY` - Kibana API key
- `--no-browser` - Do not open browser automatically
- `--kibana-no-ssl-verify` - Disable SSL certificate verification

### `kb-dashboard disassemble`

Disassemble a Kibana dashboard NDJSON file into components for easier LLM processing.

**Usage:**

```bash
kb-dashboard disassemble [input] -o <output_dir>
```

**Arguments:**

- `input` - Path to the dashboard NDJSON file (optional, reads from stdin if omitted)
- `-o, --output` - Output directory for component files (required)

**Output Structure:**

The tool creates the following files in the output directory:

- `metadata.json` - Dashboard metadata including id, title, description, version, and timestamps
- `options.json` - Dashboard display options (margins, color sync, cursor sync, etc.)
- `controls.json` - Control group configuration with control panels
- `filters.json` - Dashboard-level filters (only created if filters exist)
- `references.json` - Data view and index pattern references
- `panels/` - Directory containing individual panel JSON files, named as `NNN_panelId_type.json`

## Examples

### Compile only

```bash
kb-dashboard compile
```

### Compile and upload with basic auth

```bash
kb-dashboard compile \
  --upload \
  --kibana-url https://kibana.example.com \
  --kibana-username admin \
  --kibana-password secret
```

### Compile and upload with API key

```bash
kb-dashboard compile \
  --upload \
  --kibana-url https://kibana.example.com \
  --kibana-api-key "VnVhQm5Yb0JDZGJrUW0tZTVoT3k6dWkybHAyYXhUTm1zeWFrdzl0dk5udw=="
```

### Custom input and output directories

```bash
kb-dashboard compile \
  --input-dir ./my-dashboards \
  --output-dir ./compiled \
  --output-file my-dashboards.ndjson
```

### Upload without opening browser

```bash
kb-dashboard compile \
  --upload \
  --no-browser
```

### Export dashboard for GitHub issue

```bash
# Export dashboard and open pre-filled issue in browser
kb-dashboard export-for-issue --dashboard-id my-dashboard-id

# Export with API key and don't open browser
kb-dashboard export-for-issue \
  --dashboard-id my-dashboard-id \
  --kibana-api-key "your-api-key" \
  --no-browser
```

### Disassemble a dashboard for LLM conversion

```bash
# Download a dashboard from Kibana
curl -u elastic:changeme http://localhost:5601/api/saved_objects/dashboard/my-dashboard-id > dashboard.ndjson

# Disassemble it into components
kb-dashboard disassemble dashboard.ndjson -o dashboard_parts/

# Now you can feed individual parts to an LLM for conversion
cat dashboard_parts/panels/000_panel-1_lens.json | llm "Convert this Kibana panel to our YAML schema"
```

### Disassemble from stdin

```bash
curl -u elastic:changeme http://localhost:5601/api/saved_objects/dashboard/my-id | \
  kb-dashboard disassemble -o output/
```

For a complete workflow guide on converting these disassembled components to YAML, see the [Dashboard Decompiling Guide](dashboard-decompiling-guide.md).

## Makefile Shortcuts

The project includes convenient Makefile targets:

```bash
# Compile only
make compile

# Compile and upload (uses environment variables for Kibana config)
make upload
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
