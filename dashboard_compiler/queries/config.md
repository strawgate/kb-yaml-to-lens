# Queries

This document describes the structure for defining queries at both the dashboard and panel levels.

## Dashboard Queries

Dashboard queries are applied globally to all panels on the dashboard. They are defined within the `query` object at the top level of the `dashboard` object.

```yaml
dashboard:
  query: object         # (Optional) A query string to filter the dashboard data. Defaults to an empty KQL query.
    # Choose one of the following query types:
    kql: string         # (Required if query type is kql) KQL query string.
    lucene: string      # (Required if query type is lucene) Lucene query string.
```

### Query Types

*   **KQL Query**: Filters documents using the Kibana Query Language.
    ```yaml
    query:
      kql: 'event.dataset: "apache.access" and http.response.status_code >= 500'
    ```
*   **Lucene Query**: Filters documents using the Lucene query syntax.
    ```yaml
    query:
      lucene: 'status:500 OR status:404'
    ```

## Panel Queries

Panel queries are applied only to the specific panel they are defined within, in addition to any global dashboard query. They are defined within the `query` field of a panel object (currently only supported for `lens` panels).

```yaml
- panel:
    type: lens
    query: string         # (Optional) Panel-specific KQL query. Defaults to "".
```

### Fields

*   `query` (optional, string): A KQL query string specific to this panel. Defaults to an empty string.

### Example

```yaml
panels:
  - panel:
      type: lens
      # ... other panel fields ...
      query: 'user.id: "kibana_user"'