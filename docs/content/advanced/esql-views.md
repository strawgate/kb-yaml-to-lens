# ES|QL Query Reuse with YAML Anchors

When building dashboards with multiple ES|QL panels, you often need to query the same data source with similar filters across different visualizations. YAML anchors provide a way to define reusable query components that can be shared across panels, reducing duplication and making dashboards easier to maintain.

## How It Works

ES|QL queries can be defined as an array of strings instead of a single string. The compiler automatically joins array elements with the ES|QL pipe operator (`|`):

```yaml
# Array format
query:
  - FROM logs-*
  - WHERE status >= 200
  - STATS count = COUNT()

# Compiles to: FROM logs-* | WHERE status >= 200 | STATS count = COUNT()
```

Combined with YAML anchors (`&anchor_name`) and aliases (`*anchor_name`), you can define query parts once and reference them in multiple panels.

## Pattern 1: Shared Data Source

Define the data source once and reuse it across all panels:

```yaml
# Define the base data source
.base_query: &logs_source
  - FROM logs-*
  - WHERE @timestamp > NOW() - 24h

dashboards:
  - name: "Application Logs"
    panels:
      - title: "Total Requests"
        size: {w: 16, h: 8}
        esql:
          type: metric
          query:
            - *logs_source
            - STATS total = COUNT()
          primary:
            field: total

      - title: "Requests by Status"
        size: {w: 16, h: 8}
        position: {x: 16, y: 0}
        esql:
          type: pie
          query:
            - *logs_source
            - STATS count = COUNT() BY http.response.status_code
          metrics:
            - field: count
          dimensions:
            - field: http.response.status_code

      - title: "Average Response Time"
        size: {w: 16, h: 8}
        position: {x: 32, y: 0}
        esql:
          type: metric
          query:
            - *logs_source
            - STATS avg_time = AVG(http.response.time)
          primary:
            field: avg_time
```

All three panels share the same data source and time filter, but each has its own aggregation.

## Pattern 2: Shared Filters

Define common filter conditions that apply to multiple panels:

```yaml
# Define reusable filter conditions
.filters:
  production: &prod_filter
    - WHERE environment == "production"
  successful: &success_filter
    - WHERE http.response.status_code >= 200 AND http.response.status_code < 400
  errors: &error_filter
    - WHERE http.response.status_code >= 400

dashboards:
  - name: "Production Metrics"
    panels:
      - title: "Successful Requests"
        size: {w: 24, h: 8}
        esql:
          type: metric
          query:
            - FROM logs-*
            - *prod_filter
            - *success_filter
            - STATS count = COUNT()
          primary:
            field: count

      - title: "Error Rate"
        size: {w: 24, h: 8}
        position: {x: 24, y: 0}
        esql:
          type: metric
          query:
            - FROM logs-*
            - *prod_filter
            - *error_filter
            - STATS errors = COUNT()
          primary:
            field: errors
```

## Pattern 3: Pseudo ES|QL Views

Create "view-like" abstractions by combining data source, filters, and common transformations:

```yaml
# Define a "view" as a complete base query
.views:
  api_requests: &api_view
    - FROM logs-*
    - WHERE service.type == "api"
    - WHERE @timestamp > NOW() - 1h
    - EVAL response_time_ms = http.response.time / 1000000

dashboards:
  - name: "API Dashboard"
    panels:
      - title: "Request Volume"
        size: {w: 16, h: 8}
        esql:
          type: metric
          query:
            - *api_view
            - STATS requests = COUNT()
          primary:
            field: requests

      - title: "P95 Response Time"
        size: {w: 16, h: 8}
        position: {x: 16, y: 0}
        esql:
          type: metric
          query:
            - *api_view
            - STATS p95 = PERCENTILE(response_time_ms, 95)
          primary:
            field: p95

      - title: "Requests by Endpoint"
        size: {w: 16, h: 8}
        position: {x: 32, y: 0}
        esql:
          type: pie
          query:
            - *api_view
            - STATS count = COUNT() BY url.path
            - SORT count DESC
            - LIMIT 10
          metrics:
            - field: count
          dimensions:
            - field: url.path
```

## Pattern 4: Composable Query Parts

Build complex queries from multiple reusable components:

```yaml
.query_parts:
  metrics_source: &source
    - FROM metrics-*
  time_filter: &time
    - WHERE @timestamp > NOW() - 6h
  host_filter: &host
    - WHERE host.name IS NOT NULL

dashboards:
  - name: "Host Metrics"
    panels:
      - title: "CPU by Host"
        size: {w: 24, h: 12}
        esql:
          type: datatable
          query:
            - *source
            - *time
            - *host
            - STATS avg_cpu = AVG(system.cpu.total.pct) BY host.name
            - SORT avg_cpu DESC

      - title: "Memory by Host"
        size: {w: 24, h: 12}
        position: {x: 24, y: 0}
        esql:
          type: datatable
          query:
            - *source
            - *time
            - *host
            - STATS avg_mem = AVG(system.memory.used.pct) BY host.name
            - SORT avg_mem DESC
```

## Best Practices

1. **Use descriptive anchor names**: Names like `&api_logs_base` are clearer than `&base1`.

2. **Prefix anchors with a dot**: Using `.views:` or `.filters:` at the top level keeps these definitions clearly separate from actual dashboard content. Keys starting with `.` are ignored by the compiler.

3. **Keep anchors at the top**: Define all anchors at the beginning of your YAML file for easy reference.

4. **Document your views**: Add comments explaining what each anchor represents.

5. **Balance reuse with readability**: Don't over-abstract—if a query is used only once, inline it.

## Limitations

- YAML anchors work only within a single file. For multi-file dashboards, consider using a pre-processor or templating tool.
- Anchors cannot be modified when referenced—you can only extend an array by adding more elements after the alias.

## Related Documentation

- [Queries Configuration](../queries/config.md)
- [ESQL Panel Configuration](../panels/esql.md)
