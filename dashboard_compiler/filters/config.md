# Filters and Queries

This document describes the structure for defining filters and queries.

## Filters

Filters are used to narrow down the data displayed on a dashboard or within a panel. They are defined as a list of filter objects.

```yaml
filters: list         # (Optional) A list of filters to apply. Can be empty.
  - # Filter object (see Filter Types below)
```

### Base Filter Fields

All filter types inherit from a base filter with the following optional fields:

*   `alias` (optional, string): An optional alias for the filter, used for display purposes.
*   `disabled` (optional, boolean): Indicates whether the filter is disabled. If `true`, the filter will not be applied. Defaults to `false`.

### Filter Types

The following filter types are available:

*   **Exists Filter**: Filters documents based on whether a field exists or not.
    ```yaml
    - exists: string    # (Required) The field name to check for existence.
      # Base filter fields also apply
    ```
    *   **Fields:**
        *   `exists` (required, string): The field name to check for existence. If the field exists in a document, it will match that document.
    *   **Example:**
        ```yaml
        - exists: error.message
        ```

*   **Phrase Filter**: Filters documents where a specific field exactly matches a single value.
    ```yaml
    - field: string     # (Required) The field name to apply the filter to.
      equals: any       # (Required) The exact phrase value that the field must match.
      # Base filter fields also apply
    ```
    *   **Fields:**
        *   `field` (required, string): The field name to apply the filter to.
        *   `equals` (required, any): The exact phrase value that the field must match.
    *   **Example:**
        ```yaml
        - field: status.keyword
          equals: active
        ```

*   **Phrases Filter**: Filters documents where a specific field matches any of the values in a list.
    ```yaml
    - field: string     # (Required) The field name to apply the filter to.
      in: list          # (Required) A list of phrases.
      # Base filter fields also apply
    ```
    *   **Fields:**
        *   `field` (required, string): The field name to apply the filter to.
        *   `in` (required, list of any): A list of phrases. Documents must match at least one of these phrases in the specified field.
    *   **Example:**
        ```yaml
        - field: event.category
          in: ["authentication", "network"]
        ```

*   **Range Filter**: Filters documents where a numeric or date field falls within a specified range. At least one of `gte`, `gt`, `lte`, or `lt` must be provided.
    ```yaml
    - field: string     # (Required) The field name to apply the filter to.
      gte: any          # (Optional) Greater than or equal to value.
      gt: any           # (Optional) Greater than value.
      lte: any          # (Optional) Less than or equal to value.
      lt: any           # (Optional) Less than value.
      # Base filter fields also apply
    ```
    *   **Fields:**
        *   `field` (required, string): The field name to apply the filter to.
        *   `gte` (optional, any): Greater than or equal to value for the range filter.
        *   `gt` (optional, any): Greater than value for the range filter.
        *   `lte` (optional, any): Less than or equal to value for the range filter.
        *   `lt` (optional, any): Less than value for the range filter.
    *   **Example:**
        ```yaml
        - field: response_time
          gte: 100
          lt: 500
        ```

*   **Custom Filter**: Allows for defining a custom Elasticsearch query as a filter.
    ```yaml
    - dsl: object       # (Required) The custom query definition.
      # Base filter fields also apply
    ```
    *   **Fields:**
        *   `dsl` (required, object): The custom query definition. This should be a valid Elasticsearch query object.
    *   **Example:**
        ```yaml
        - dsl:
            query_string:
              query: "response:200 OR response:404"
        ```

### Filter Junctions

Filter junctions combine multiple filters using boolean logic.

*   **And Filter**: Matches documents that satisfy all of the specified filters.
    ```yaml
    - and: list         # (Required) A list of filters to combine with AND logic.
      # Base filter fields also apply
    ```
    *   **Fields:**
        *   `and` (required, list of filter objects): A list of filters. All filters must match for a document to be included.
    *   **Example:**
        ```yaml
        - and:
          - field: status.keyword
            equals: active
          - field: event.category
            in: ["authentication", "network"]
        ```

*   **Or Filter**: Matches documents that satisfy at least one of the specified filters.
    ```yaml
    - or: list          # (Required) A list of filters to combine with OR logic.
      # Base filter fields also apply
    ```
    *   **Fields:**
        *   `or` (required, list of filter objects): A list of filters. At least one filter must match for a document to be included.
    *   **Example:**
        ```yaml
        - or:
          - field: http.response.status_code
            equals: 404
          - field: http.response.status_code
            equals: 500
        ```

### Filter Modifiers

Filter modifiers alter the behavior of a single nested filter.

*   **Negate Filter**: Excludes documents that match the nested filter.
    ```yaml
    - not: object       # (Required) The filter to negate.
    ```
    *   **Fields:**
        *   `not` (required, filter object): The filter to negate. Can be any of the filter types or junction types.
    *   **Example:**
        ```yaml
        - not:
            field: event.outcome
            equals: success
        ```

## Queries

Queries are used to define the search criteria for retrieving data. See [Queries Documentation](./queries/config.md) for more details.