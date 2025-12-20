# Queries Configuration

Queries are used to define the search criteria for retrieving data. They can be applied globally at the dashboard level or specifically to individual panels that support them. This compiler supports KQL (Kibana Query Language), Lucene, and ESQL (Elasticsearch Query Language).

## Minimal Configuration Examples

**KQL Query:**
```yaml
# Applied at the dashboard level
dashboard:
  # ...
  query:
    kql: 'response_code:200 AND "user.id": "test-user"'
```

**Lucene Query:**
```yaml
# Applied at the dashboard level
dashboard:
  # ...
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

| YAML Key | Data Type | Description                                      | Kibana Default | Required |
| -------- | --------- | ------------------------------------------------ | -------------- | -------- |
| `kql`    | `string`  | The KQL query string to apply.                   | N/A            | Yes      |
| `query`  | `object`  | The parent object containing the `kql` key.      | N/A            | Yes      |

**Usage Example (Dashboard Level):**
```yaml
dashboard:
  # ...
  query:
    kql: 'event.action:"user_login" AND event.outcome:success'
```

### Lucene Query

Filters documents using the more expressive, but complex, Lucene query syntax.

| YAML Key | Data Type | Description                                      | Kibana Default | Required |
| -------- | --------- | ------------------------------------------------ | -------------- | -------- |
| `lucene` | `string`  | The Lucene query string to apply.                | N/A            | Yes      |
| `query`  | `object`  | The parent object containing the `lucene` key.   | N/A            | Yes      |

**Usage Example (Dashboard Level):**
```yaml
dashboard:
  # ...
  query:
    lucene: '(geo.src:"US" OR geo.src:"CA") AND tags:"production"'
```

### ESQL Query

Uses Elasticsearch Query Language (ESQL) for data retrieval and aggregation. ESQL queries are typically used by specific panel types that are designed to work with ESQL's tabular results (e.g., ESQL-driven charts or tables). The configuration is a direct string under the `query` key for such panels.

| YAML Key | Data Type | Description                                                                 | Kibana Default | Required |
| -------- | --------- | --------------------------------------------------------------------------- | -------------- | -------- |
| `query`  | `string`  | The ESQL query string. The Pydantic model uses `root` for this direct string. | N/A            | Yes      |

**Usage Example (Panel Level - for a hypothetical ESQL panel):**
```yaml
panels:
  - type: esql_backed_chart # This panel type would be designed to use ESQL
    title: "Top User Agents by Count"
    query: |
      FROM "web-logs-*"
      | STATS count = COUNT(user_agent.name) BY user_agent.name
      | SORT count DESC
      | LIMIT 10
    # ... other panel-specific configurations
```

## Query Scope

*   **Dashboard Level Query**: Defined under `dashboard.query`. This query is applied globally to all panels that do not explicitly override it or ignore global queries. KQL and Lucene are supported at this level.
*   **Panel Level Query**: Defined under `panel.query` (for panels that support it, e.g., Lens panels, ESQL panels). This query is specific to the panel and is often combined with (or can override) the dashboard-level query, depending on the panel's behavior.
    *   Lens panels typically use KQL for their panel-specific query.
    *   ESQL-specific panels will use an ESQL query string.

## Related Documentation

*   [Dashboard Configuration](../dashboard/dashboard.md)
*   [Filters Configuration](../filters/config.md)
*   [Panel Documentation (e.g., Lens, ESQL specific panels)](../panels/base.md)