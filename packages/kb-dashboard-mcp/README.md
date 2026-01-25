# kb-dashboard-mcp

MCP (Model Context Protocol) server for Kibana dashboard building with Elasticsearch data exploration.

## Overview

This package provides an MCP server that enables LLMs to explore Elasticsearch cluster data through Kibana's proxy API, making it easier to build dashboards. By routing requests through Kibana, the server can leverage Kibana's authentication and potentially access additional Kibana-specific features.

The server includes tools for:

- **Data Stream Exploration**: Summarize data streams with field information and sample values
- **ES|QL Query Execution**: Execute ES|QL queries against the cluster
- **Pattern Testing**: Test grok and dissect patterns against sample text

## Installation

```bash
pip install kb-dashboard-mcp
```

Or with uv:

```bash
uv add kb-dashboard-mcp
```

## Usage

### Running the MCP Server

```bash
# Using API key authentication
kb-mcp --kibana-url https://your-kibana.example.com:5601 --api-key your-api-key

# Using username/password authentication
kb-mcp --kibana-url https://your-kibana.example.com:5601 --username elastic --password your-password

# Using SSE transport (for web clients)
kb-mcp --kibana-url https://your-kibana.example.com:5601 --api-key your-api-key --transport sse

# Disable SSL verification (for development)
kb-mcp --kibana-url https://localhost:5601 --api-key your-api-key --no-ssl-verify
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `KIBANA_URL` | Kibana server URL |
| `KIBANA_API_KEY` | API key for authentication |
| `KIBANA_USERNAME` | Username for basic authentication |
| `KIBANA_PASSWORD` | Password for basic authentication |

### MCP Client Configuration

Add the server to your MCP client configuration:

```json
{
  "mcpServers": {
    "kb-dashboard-mcp": {
      "command": "kb-mcp",
      "args": ["--kibana-url", "https://your-kibana.example.com:5601"],
      "env": {
        "KIBANA_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Available Tools

### `summarize_data_streams`

Summarize data streams with field information and sample rows.

**Parameters:**

- `data_streams`: List of data stream names to summarize

**Returns:** Field types, sample values (up to 10 per field), and 5 sample rows for each data stream.

### `list_data_streams`

List available data streams in the cluster.

**Parameters:**

- `pattern` (optional): Name pattern to filter data streams (supports wildcards)

**Returns:** List of data stream names with backing indices and timestamp field.

### `execute_esql`

Execute an ES|QL query against the cluster.

**Parameters:**

- `query`: The ES|QL query to execute
- `columnar` (optional): Return results in columnar format (default: false)

**Returns:** Query results with columns and values.

### `test_grok_pattern`

Test a grok pattern against sample text.

**Parameters:**

- `pattern`: The grok pattern to test
- `text`: Sample text to match against
- `custom_patterns` (optional): Dictionary of custom pattern definitions

**Returns:** Matched fields and values.

### `test_dissect_pattern`

Test a dissect pattern against sample documents.

**Parameters:**

- `pattern`: The dissect pattern to test
- `documents`: List of sample documents to match against

**Returns:** Extracted fields and values for each document.

## Development

See [DEVELOPING.md](DEVELOPING.md) for development setup and workflows.

## License

MIT License - see [LICENSE](../../LICENSE) for details.
