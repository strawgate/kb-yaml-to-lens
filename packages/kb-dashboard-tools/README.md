# kb-dashboard-tools

Shared utilities for Kibana operations, authentication, and workflows. This package provides common functionality used across the kb-yaml-to-lens ecosystem, including CLI tools, Language Server Protocol (LSP) servers, and future MCP servers.

## Features

- **KibanaClient**: HTTP client for interacting with Kibana's Saved Objects API and Elasticsearch APIs
- **Authentication utilities**: Credential normalization and URL redaction for safe logging
- **Result pattern**: Type-safe error handling without exceptions
- **ES|QL support**: Models for ES|QL query execution and results

## Installation

```bash
pip install kb-dashboard-tools
```

## Usage

### Kibana Client

```python
from kb_dashboard_tools import KibanaClient

# Note: ssl_verify=False is only for local development with self-signed certificates.
# Always use ssl_verify=True (the default) in production environments.
async with KibanaClient(
    url='https://localhost:5601',
    username='elastic',
    password='changeme',
    ssl_verify=False,  # Only for local dev with self-signed certs
) as client:
    # Upload a dashboard
    result = await client.upload_ndjson('dashboard.ndjson')

    # Execute ES|QL query
    esql_result = await client.execute_esql('FROM logs | LIMIT 10')
    print(f'Found {esql_result.row_count} rows')
```

### Authentication Utilities

```python
from kb_dashboard_tools import normalize_credentials, redact_url

# Normalize credentials (converts empty strings to None)
api_key = normalize_credentials(user_input)

# Redact credentials from URLs for safe logging
safe_url = redact_url('https://user:pass@example.com:9200/path')
# Returns: 'https://example.com:9200/path'
```

### Result Pattern

```python
from kb_dashboard_tools import Result

def divide(a: int, b: int) -> Result[float]:
    if b == 0:
        return Result.fail('Division by zero')
    return Result.ok(a / b)

result = divide(10, 2)
if result.success:
    print(f'Result: {result.unwrap()}')
else:
    print(f'Error: {result.error}')
```

## Development

See the main repository's [DEVELOPING.md](../../DEVELOPING.md) for development setup.

```bash
# Install dependencies
make install

# Run CI checks
make ci

# Run tests
make test
```

## License

MIT
