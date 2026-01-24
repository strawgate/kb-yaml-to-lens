# kb-dashboard-cli

Command-line interface for compiling YAML dashboards to Kibana format and uploading to Kibana.

## Installation

```bash
pip install kb-dashboard-cli
```

This will also install `kb-dashboard-core` and `kb-dashboard-tools` as dependencies.

## Usage

```bash
# Compile dashboards from YAML to NDJSON
kb-dashboard compile --input-dir ./dashboards --output-dir ./output

# Upload dashboards to Kibana
kb-dashboard upload --input-dir ./dashboards --kibana-url https://localhost:5601

# Fetch existing dashboards from Kibana
kb-dashboard fetch --kibana-url https://localhost:5601 --output-dir ./output

# Disassemble Kibana JSON back to YAML
kb-dashboard disassemble --input dashboard.ndjson --output dashboard.yaml
```

## Features

- Compile YAML dashboards to Kibana NDJSON format
- Upload dashboards directly to Kibana
- Fetch existing dashboards from Kibana
- Screenshot dashboards for documentation
- Load sample data for testing

## Related Packages

- **kb-dashboard-core**: Core compiler library (automatically installed)
- **kb-dashboard-lsp**: Language Server Protocol for IDE integration
- **kb-dashboard-tools**: Development tools (automatically installed)
