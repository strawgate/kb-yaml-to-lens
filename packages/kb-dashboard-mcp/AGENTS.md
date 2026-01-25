# Agent Guidelines: kb-dashboard-mcp

> MCP server for Kibana dashboard building with Elasticsearch data exploration

---

## Introduction

@README.md

---

## Development Guide

@DEVELOPING.md

---

## Code Style

@CODE_STYLE.md

---

## Key Implementation Notes

### MCP Server Architecture

The server uses FastMCP to register tools that LLMs can invoke:

- **Tools** are registered with the FastMCP server in `server.py`
- **Models** for request/response are defined in `models.py`
- **Tool implementations** are in the `tools/` directory

### Kibana Client

This package uses the `KibanaClient` from `kb-dashboard-compiler` to proxy requests through Kibana's console API. This enables:

- Unified authentication through Kibana
- Access to Kibana-specific features (screenshots, etc.)
- Simpler configuration (just Kibana URL, no ES URL needed)

```python
from dashboard_compiler.kibana_client import KibanaClient

async def build_mcp_server(client: KibanaClient) -> FastMCP:
    mcp = FastMCP(name='kb-dashboard-mcp')

    async def my_tool(param: str) -> MyResult:
        # Use `client` from closure
        result = await client.esql_query_raw(query='...')
        return MyResult(...)

    mcp.add_tool(Tool.from_function(my_tool))
    return mcp
```

### Error Handling

- Validate inputs before making Kibana calls
- Return structured error responses for tool failures
- Use Pydantic validation for input models

### Testing

- Mock the `KibanaClient` from `dashboard_compiler` in tests
- Test tool registration and invocation
- Verify Pydantic model serialization
