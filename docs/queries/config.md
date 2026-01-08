# Queries Configuration

Queries are used to define the search criteria for retrieving data. They can be applied globally at the dashboard level or specifically to individual panels that support them. This compiler supports KQL (Kibana Query Language), Lucene, and ESQL (Elasticsearch Query Language).

## Minimal Configuration Examples

**KQL Query:**

```yaml
# Applied at the dashboard level
dashboards:
- # ...
  query:
    kql: 'response_code:200 AND "user.id": "test-user"'
```

**Lucene Query:**

```yaml
# Applied at the dashboard level
dashboards:
- # ...
  query:
    lucene: 'event.module:nginx AND event.dataset:nginx.access'
```

**ESQL Query (typically for specific panel types like ESQL-backed charts):**

```yaml
# Example within a panel configuration that supports ESQL
panels:
  - type: some_esql_panel # Hypothetical panel type
    # ... other panel config
    query: |
      FROM my_index
      | STATS RARE(clientip)
```

## Full Configuration Options

Queries are typically defined under a `query` key, either at the root of the `dashboard` object or within a specific panel's configuration. The structure of the `query` object determines the language.

### KQL Query

Filters documents using the Kibana Query Language (KQL). This is often the default query language in Kibana.

::: dashboard_compiler.queries.config.KqlQuery
    options:
      show_root_heading: false
      heading_level: 4

**Usage Example (Dashboard Level):**

```yaml
dashboards:
- # ...
  query:
    kql: 'event.action:"user_login" AND event.outcome:success'
```

### Lucene Query

Filters documents using the more expressive, but complex, Lucene query syntax.

::: dashboard_compiler.queries.config.LuceneQuery
    options:
      show_root_heading: false
      heading_level: 4

**Usage Example (Dashboard Level):**

```yaml
dashboards:
- # ...
  query:
    lucene: '(geo.src:"US" OR geo.src:"CA") AND tags:"production"'
```

### ESQL Query

Uses Elasticsearch Query Language (ESQL) for data retrieval and aggregation. ESQL queries are typically used by specific panel types that are designed to work with ESQL's tabular results (e.g., ESQL-driven charts or tables).

::: dashboard_compiler.queries.config.ESQLQuery
    options:
      show_root_heading: false
      heading_level: 4

**Usage Example (Panel Level - String Format):**

```yaml
panels:
  - type: esql_backed_chart
    title: "Top User Agents by Count"
    query: |
      FROM "web-logs-*"
      | STATS count = COUNT(user_agent.name) BY user_agent.name
      | SORT count DESC
      | LIMIT 10
```

**Usage Example (Panel Level - Array Format):**

```yaml
panels:
  - type: esql_backed_chart
    title: "Top User Agents by Count"
    query:
      - FROM "web-logs-*"
      - STATS count = COUNT(user_agent.name) BY user_agent.name
      - SORT count DESC
      - LIMIT 10
```

When using the array format, query parts are automatically joined with the ES|QL pipe operator (`|`). Nested arrays produced by YAML anchor expansion are automatically flattened before joining, allowing flexible composition of query components. This enables powerful query reuse patterns with YAML anchors.

!!! tip "Advanced: ES|QL Query Reuse with YAML Anchors"
    You can use YAML anchors (`&` and `*`) to create reusable ES|QL query components, reducing duplication when multiple panels query similar data. This pattern lets you define base queries, filters, or complete "view-like" abstractions once and reference them across panels. See [ES|QL Query Reuse with YAML Anchors](../advanced/esql-views.md) for detailed patterns and examples.

## Query Scope

* **Dashboard Level Query**: Defined under `dashboard.query`. This query is applied globally to all panels that do not explicitly override it or ignore global queries. KQL and Lucene are supported at this level.
* **Panel Level Query**: Defined under `panel.query` (for panels that support it, e.g., Lens panels, ESQL panels). This query is specific to the panel and is often combined with (or can override) the dashboard-level query, depending on the panel's behavior.
  * Lens panels typically use KQL for their panel-specific query.
  * ESQL-specific panels will use an ESQL query string.

## Related Documentation

* [Dashboard Configuration](../dashboard/dashboard.md)
* [Filters Configuration](../filters/config.md)
* [Panel Documentation (e.g., Lens, ESQL specific panels)](../panels/base.md)
* [ESQL Panel Configuration](../panels/esql.md)
