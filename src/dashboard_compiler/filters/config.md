# Filters Configuration

Filters are used to narrow down the data displayed on a dashboard or within individual panels. They are defined as a list of filter objects, typically under the `filters` key of a `dashboard` object or a panel that supports filtering.

## Minimal Configuration Examples

**Exists Filter:** Check if the `error.message` field exists.
```yaml
filters:
  - exists: "error.message"
```

**Phrase Filter:** Find documents where `status.keyword` is exactly "active".
```yaml
filters:
  - field: "status.keyword"
    equals: "active"
```

**Phrases Filter (using `in` alias):** Find documents where `event.category` is "authentication" OR "network".
```yaml
filters:
  - field: "event.category"
    in: ["authentication", "network"]
```

**Range Filter:** Find documents where `response_time` is between 100 (inclusive) and 500 (exclusive).
```yaml
filters:
  - field: "response_time"
    gte: "100" # Values are typically strings, Kibana handles conversion
    lt: "500"
```

## Complex Configuration Example

This example demonstrates a combination of filter types, including logical junctions (`and`, `or`) and a modifier (`not`).

```yaml
filters:
  - alias: "Successful Logins from US or CA"
    and: # `and_filters` in Pydantic, `and` in YAML
      - field: "event.action"
        equals: "user_login"
      - field: "event.outcome"
        equals: "success"
      - or: # `or_filters` in Pydantic, `or` in YAML
          - field: "source.geo.country_iso_code"
            equals: "US"
          - field: "source.geo.country_iso_code"
            equals: "CA"
  - alias: "Exclude test users"
    not: # `not_filter` in Pydantic, `not` in YAML
      field: "user.name"
      in: ["test_user_01", "qa_bot"]
  - exists: "transaction.id"
    disabled: true # This filter is defined but currently disabled
  - dsl:
      query_string:
        query: "message:(*error* OR *exception*) AND NOT logger_name:debug"
```

## Full Configuration Options

All filter types can include the following base fields:

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `alias`    | `string`  | An optional alias for the filter, used for display purposes in Kibana.           | `None`         | No       |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Exists Filter

Checks for the existence of a specific field.

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `exists`   | `string`  | The field name to check for existence.                                           | N/A            | Yes      |
| `alias`    | `string`  | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Phrase Filter

Matches documents where a specific field contains an exact phrase.

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `field`    | `string`  | The field name to apply the filter to.                                           | N/A            | Yes      |
| `equals`   | `string`  | The exact phrase value that the field must match.                                | N/A            | Yes      |
| `alias`    | `string`  | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Phrases Filter

Matches documents where a specific field contains one or more of the specified phrases.

| YAML Key   | Data Type         | Description                                                                      | Kibana Default | Required |
| ---------- | ----------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `field`    | `string`          | The field name to apply the filter to.                                           | N/A            | Yes      |
| `in`       | `list of strings` | A list of phrases. Documents must match at least one of these phrases.           | N/A            | Yes      |
| `alias`    | `string`          | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean`         | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Range Filter

Matches documents where a numeric or date field falls within a specified range. At least one of `gte`, `lte`, `gt`, or `lt` must be provided.

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required                |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | ----------------------- |
| `field`    | `string`  | The field name to apply the filter to.                                           | N/A            | Yes                     |
| `gte`      | `string`  | Greater than or equal to value.                                                  | `None`         | No (but one must exist) |
| `lte`      | `string`  | Less than or equal to value.                                                     | `None`         | No (but one must exist) |
| `gt`       | `string`  | Greater than value.                                                              | `None`         | No (but one must exist) |
| `lt`       | `string`  | Less than value.                                                                 | `None`         | No (but one must exist) |
| `alias`    | `string`  | An optional alias for the filter.                                                | `None`         | No                      |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No                      |

### Custom Filter

Allows for defining a custom Elasticsearch Query DSL filter.

| YAML Key   | Data Type        | Description                                                                      | Kibana Default | Required |
| ---------- | ---------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `dsl`      | `object (dict)`  | The custom Elasticsearch query definition.                                       | N/A            | Yes      |
| `alias`    | `string`         | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean`        | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Negate Filter (`not`)

Excludes documents that match the nested filter. This filter itself does not have `alias` or `disabled` directly; those would apply to the filter it contains or a parent filter.

| YAML Key | Data Type      | Description                                                                      | Kibana Default | Required |
| -------- | -------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `not`    | `FilterTypes`  | The filter object to negate. Can be any of the other filter types or junctions.  | N/A            | Yes      |

### And Filter (`and`)

Matches documents that satisfy ALL of the specified nested filters.

| YAML Key   | Data Type               | Description                                                                      | Kibana Default | Required |
| ---------- | ----------------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `and`      | `list of FilterTypes`   | A list of filter objects. All filters must match for a document to be included.  | N/A            | Yes      |
| `alias`    | `string`                | An optional alias for the AND group.                                             | `None`         | No       |
| `disabled` | `boolean`               | If `true`, the entire AND group is defined but not applied.                      | `false`        | No       |

### Or Filter (`or`)

Matches documents that satisfy AT LEAST ONE of the specified nested filters.

| YAML Key   | Data Type               | Description                                                                      | Kibana Default | Required |
| ---------- | ----------------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `or`       | `list of FilterTypes`   | A list of filter objects. At least one filter must match.                        | N/A            | Yes      |
| `alias`    | `string`                | An optional alias for the OR group.                                              | `None`         | No       |
| `disabled` | `boolean`               | If `true`, the entire OR group is defined but not applied.                       | `false`        | No       |

## Related Documentation

*   [Dashboard Configuration](../dashboard/dashboard.md)
*   [Queries Configuration](../queries/config.md)