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

### Exists Filter

Checks for the existence of a specific field.

::: dashboard_compiler.filters.config.ExistsFilter
    options:
      show_root_heading: false
      heading_level: 4

### Phrase Filter

Matches documents where a specific field contains an exact phrase.

::: dashboard_compiler.filters.config.PhraseFilter
    options:
      show_root_heading: false
      heading_level: 4

### Phrases Filter

Matches documents where a specific field contains one or more of the specified phrases.

::: dashboard_compiler.filters.config.PhrasesFilter
    options:
      show_root_heading: false
      heading_level: 4

### Range Filter

Matches documents where a numeric or date field falls within a specified range. At least one of `gte`, `lte`, `gt`, or `lt` must be provided.

::: dashboard_compiler.filters.config.RangeFilter
    options:
      show_root_heading: false
      heading_level: 4

### Custom Filter

Allows for defining a custom Elasticsearch Query DSL filter.

::: dashboard_compiler.filters.config.CustomFilter
    options:
      show_root_heading: false
      heading_level: 4

### Negate Filter (`not`)

Excludes documents that match the nested filter.

::: dashboard_compiler.filters.config.NegateFilter
    options:
      show_root_heading: false
      heading_level: 4

### And Filter (`and`)

Matches documents that satisfy ALL of the specified nested filters.

::: dashboard_compiler.filters.config.AndFilter
    options:
      show_root_heading: false
      heading_level: 4

### Or Filter (`or`)

Matches documents that satisfy AT LEAST ONE of the specified nested filters.

::: dashboard_compiler.filters.config.OrFilter
    options:
      show_root_heading: false
      heading_level: 4

## Related Documentation

* [Dashboard Configuration](../dashboard/dashboard.md)
* [Queries Configuration](../queries/config.md)
