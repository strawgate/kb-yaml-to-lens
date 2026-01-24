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

### Elasticsearch Client

The `AsyncElasticsearch` client is injected into tool closures:

```python
async def build_mcp_server(es: AsyncElasticsearch) -> FastMCP:
    mcp = FastMCP(name='kb-dashboard-mcp')

    async def my_tool(param: str) -> MyResult:
        # Use `es` from closure
        result = await es.some_operation()
        return MyResult(...)

    mcp.add_tool(Tool.from_function(my_tool))
    return mcp
```

### Error Handling

- Validate inputs before making ES calls
- Return structured error responses for tool failures
- Use Pydantic validation for input models

### Testing

- Mock the `AsyncElasticsearch` client in tests
- Test tool registration and invocation
- Verify Pydantic model serialization
