# ES|QL Language Reference for Dashboard Creation

This guide provides essential ES|QL (Elasticsearch Query Language) syntax for LLMs creating Kibana dashboards. ES|QL is a piped query language distinct from SQL.

## ES|QL vs SQL: Key Differences

ES|QL is **not** SQL. Common mistakes:

| SQL Syntax (Wrong) | ES|QL Syntax (Correct) |
| ------------------ | --------------------- |
| `SELECT * FROM logs` | `FROM logs-*` |
| `SELECT COUNT(*) FROM logs WHERE status = 200` | `FROM logs-* \| WHERE status == 200 \| STATS COUNT(*)` |
| `SELECT * FROM logs ORDER BY @timestamp DESC LIMIT 10` | `FROM logs-* \| SORT @timestamp DESC \| LIMIT 10` |
| `SELECT host, COUNT(*) FROM logs GROUP BY host` | `FROM logs-* \| STATS COUNT(*) BY host` |
| `SELECT AVG(response_time) AS avg_time FROM logs` | `FROM logs-* \| STATS avg_time = AVG(response_time)` |
| `SELECT * FROM logs WHERE message LIKE '%error%'` | `FROM logs-* \| WHERE message LIKE "*error*"` |

Key differences:

- **Piped syntax**: Commands flow left-to-right with `|` (pipe) operators
- **Equality**: Use `==` not `=` for comparison
- **No SELECT**: Use `KEEP` to select columns, or just aggregate directly
- **No GROUP BY clause**: Use `BY` within `STATS`
- **Wildcards**: Use `*` in patterns, not `%`
- **Index patterns**: FROM uses Elasticsearch index patterns (e.g., `logs-*`)

---

## Source Commands

Every ES|QL query starts with a source command:

### FROM

Retrieves data from Elasticsearch indices, data streams, or aliases.

```esql
FROM logs-*
FROM logs-*, metrics-*
FROM logs-* METADATA _id, _index
```

### ROW

Creates inline data for testing:

```esql
ROW x = 1, y = "test", z = null
```

### SHOW

Returns deployment metadata:

```esql
SHOW INFO
```

### TS (Time Series)

Optimized source command for time series data streams. Available in Elasticsearch 9.2+ (tech preview).

```esql
TS my_metrics
| WHERE @timestamp >= NOW() - 1 day
| STATS SUM(RATE(requests)) BY TBUCKET(1 hour), host
```

---

## Processing Commands

Processing commands transform data. Chain them with `|`:

### WHERE

Filters rows by condition:

```esql
FROM logs-*
| WHERE status == 200
| WHERE response_time > 1000
| WHERE host.name LIKE "prod-*"
| WHERE event.category IN ("authentication", "network")
```

### STATS

Aggregates data with optional grouping:

```esql
# Simple aggregation
FROM logs-*
| STATS total = COUNT(*)

# Grouped aggregation
FROM logs-*
| STATS count = COUNT(*) BY host.name

# Multiple aggregations
FROM logs-*
| STATS
    total = COUNT(*),
    avg_time = AVG(response_time),
    max_time = MAX(response_time)
  BY service.name

# Time bucketing
FROM logs-*
| STATS event_count = COUNT(*) BY time_bucket = BUCKET(@timestamp, 1 hour)
| SORT time_bucket ASC
```

### EVAL

Creates or modifies columns:

```esql
FROM logs-*
| EVAL response_time_ms = response_time * 1000
| EVAL status_category = CASE(
    status >= 500, "error",
    status >= 400, "client_error",
    status >= 300, "redirect",
    "success"
  )
| EVAL is_slow = response_time > 1000
```

### KEEP

Selects and orders columns:

```esql
FROM logs-*
| KEEP @timestamp, host.name, message
| KEEP @timestamp, host.*  # Wildcards supported
```

### DROP

Removes columns:

```esql
FROM logs-*
| DROP password, secret_key
```

### RENAME

Renames columns:

```esql
FROM logs-*
| RENAME old_name AS new_name
| RENAME host.name AS hostname, service.name AS service
```

### SORT

Orders results:

```esql
FROM logs-*
| SORT @timestamp DESC
| SORT status ASC, response_time DESC
| SORT host.name ASC NULLS LAST
```

### LIMIT

Restricts row count (default is 1000):

```esql
FROM logs-*
| LIMIT 100
```

### DISSECT

Extracts fields from strings using delimiter patterns:

```esql
FROM logs-*
| DISSECT message "%{method} %{path} HTTP/%{version}"
```

### GROK

Extracts fields using regex patterns:

```esql
FROM logs-*
| GROK message "%{IP:client_ip} - %{DATA:user}"
```

### MV_EXPAND

Expands multi-valued fields into separate rows:

```esql
FROM logs-*
| MV_EXPAND tags
```

### ENRICH

Adds data from enrichment policies:

```esql
FROM logs-*
| ENRICH ip_location_policy ON client.ip WITH city, country
```

### LOOKUP JOIN

Joins with a lookup index:

```esql
FROM logs-*
| LOOKUP JOIN user_lookup ON user.id
```

---

## Aggregation Functions

Use within STATS:

| Function | Description | Example |
| -------- | ----------- | ------- |
| `COUNT(*)` | Count all rows | `STATS total = COUNT(*)` |
| `COUNT(field)` | Count non-null values | `STATS errors = COUNT(error.code)` |
| `COUNT_DISTINCT(field)` | Unique value count | `STATS unique_users = COUNT_DISTINCT(user.id)` |
| `SUM(field)` | Sum numeric values | `STATS total_bytes = SUM(bytes)` |
| `AVG(field)` | Average value | `STATS avg_time = AVG(response_time)` |
| `MIN(field)` | Minimum value | `STATS min_time = MIN(response_time)` |
| `MAX(field)` | Maximum value | `STATS max_time = MAX(response_time)` |
| `MEDIAN(field)` | Median value | `STATS median_time = MEDIAN(response_time)` |
| `PERCENTILE(field, n)` | Nth percentile | `STATS p95 = PERCENTILE(response_time, 95.0)` |
| `STD_DEV(field)` | Standard deviation | `STATS stddev = STD_DEV(response_time)` |
| `VARIANCE(field)` | Variance | `STATS var = VARIANCE(response_time)` |
| `VALUES(field)` | All unique values | `STATS hosts = VALUES(host.name)` |
| `TOP(field, n, order)` | Top N values | `STATS top_hosts = TOP(host.name, 5, "desc")` |

---

## Time Series Functions

For use with the TS source command (Elasticsearch 9.2+):

| Function | Description | Example |
| -------- | ----------- | ------- |
| `RATE(field)` | Per-second rate of counter increase | `STATS SUM(RATE(requests))` |
| `IRATE(field)` | Instant rate (last two points) | `STATS SUM(IRATE(requests))` |
| `DELTA(field)` | Absolute change of gauge | `STATS SUM(DELTA(temperature))` |
| `IDELTA(field)` | Instant delta (last two points) | `STATS SUM(IDELTA(gauge))` |
| `INCREASE(field)` | Absolute increase of counter | `STATS SUM(INCREASE(total_bytes))` |
| `AVG_OVER_TIME(field)` | Average over time window | `STATS MAX(AVG_OVER_TIME(cpu))` |
| `MAX_OVER_TIME(field)` | Maximum over time window | `STATS MAX(MAX_OVER_TIME(memory))` |
| `MIN_OVER_TIME(field)` | Minimum over time window | `STATS MIN(MIN_OVER_TIME(latency))` |
| `SUM_OVER_TIME(field)` | Sum over time window | `STATS SUM(SUM_OVER_TIME(bytes))` |
| `COUNT_OVER_TIME(field)` | Count over time window | `STATS SUM(COUNT_OVER_TIME(events))` |
| `FIRST_OVER_TIME(field)` | Earliest value by timestamp | `STATS MAX(FIRST_OVER_TIME(value))` |
| `LAST_OVER_TIME(field)` | Latest value by timestamp | `STATS MAX(LAST_OVER_TIME(value))` |

Time bucketing function (for use with TS source command):

| Function | Description | Example |
| -------- | ----------- | ------- |
| `TBUCKET(interval)` | Groups @timestamp into time buckets for time-series aggregations | `BY TBUCKET(1 hour)`, `BY TBUCKET(5minute)` |

**Note:** `TBUCKET` is specialized for `@timestamp` in time-series queries (TS + STATS). For general-purpose bucketing of any date/numeric field, use `BUCKET()` instead (see Date/Time Functions below).

---

## Common Functions

### String Functions

| Function | Description | Example |
| -------- | ----------- | ------- |
| `LENGTH(s)` | String length | `EVAL len = LENGTH(message)` |
| `SUBSTRING(s, start, len)` | Extract substring | `EVAL prefix = SUBSTRING(host, 0, 4)` |
| `CONCAT(s1, s2, ...)` | Concatenate strings | `EVAL full = CONCAT(first, " ", last)` |
| `TO_LOWER(s)` | Lowercase | `EVAL lower = TO_LOWER(name)` |
| `TO_UPPER(s)` | Uppercase | `EVAL upper = TO_UPPER(name)` |
| `TRIM(s)` | Remove whitespace | `EVAL clean = TRIM(input)` |
| `REPLACE(s, old, new)` | Replace substring | `EVAL fixed = REPLACE(msg, "err", "error")` |
| `SPLIT(s, delim)` | Split into array | `EVAL parts = SPLIT(path, "/")` |

### Date/Time Functions

| Function | Description | Example |
| -------- | ----------- | ------- |
| `NOW()` | Current timestamp | `WHERE @timestamp > NOW() - 1 hour` |
| `DATE_EXTRACT(unit, date)` | Extract date part | `EVAL hour = DATE_EXTRACT("hour", @timestamp)` |
| `DATE_TRUNC(unit, date)` | Truncate to unit | `EVAL day = DATE_TRUNC("day", @timestamp)` |
| `DATE_DIFF(unit, d1, d2)` | Difference between dates | `EVAL age_days = DATE_DIFF("day", created, NOW())` |
| `DATE_FORMAT(date, fmt)` | Format date as string | `EVAL formatted = DATE_FORMAT(@timestamp, "yyyy-MM-dd")` |
| `DATE_PARSE(fmt, s)` | Parse string to date | `EVAL parsed = DATE_PARSE("yyyy-MM-dd", date_str)` |
| `BUCKET(field, size)` | General-purpose bucketing for any date/numeric field | `STATS count = COUNT(*) BY BUCKET(@timestamp, 1 hour)` |

### Numeric Functions

| Function | Description | Example |
| -------- | ----------- | ------- |
| `ABS(n)` | Absolute value | `EVAL abs_val = ABS(change)` |
| `CEIL(n)` | Round up | `EVAL ceiling = CEIL(value)` |
| `FLOOR(n)` | Round down | `EVAL floored = FLOOR(value)` |
| `ROUND(n, decimals)` | Round to decimals | `EVAL rounded = ROUND(avg, 2)` |
| `POW(base, exp)` | Power | `EVAL squared = POW(x, 2)` |
| `SQRT(n)` | Square root | `EVAL root = SQRT(variance)` |
| `LOG10(n)` | Base-10 logarithm | `EVAL log = LOG10(value)` |

### Conditional Functions

| Function | Description | Example |
| -------- | ----------- | ------- |
| `CASE(cond1, val1, ...)` | Conditional logic | `EVAL status = CASE(code >= 500, "error", code >= 400, "warn", "ok")` |
| `COALESCE(v1, v2, ...)` | First non-null | `EVAL name = COALESCE(display_name, username, "unknown")` |
| `GREATEST(v1, v2, ...)` | Maximum value | `EVAL max = GREATEST(a, b, c)` |
| `LEAST(v1, v2, ...)` | Minimum value | `EVAL min = LEAST(a, b, c)` |

### Type Conversion Functions

| Function | Description | Example |
| -------- | ----------- | ------- |
| `TO_STRING(v)` | Convert to string | `EVAL str = TO_STRING(status_code)` |
| `TO_INTEGER(v)` | Convert to integer | `EVAL num = TO_INTEGER(count_str)` |
| `TO_DOUBLE(v)` | Convert to double | `EVAL dbl = TO_DOUBLE(value)` |
| `TO_BOOLEAN(v)` | Convert to boolean | `EVAL flag = TO_BOOLEAN(enabled)` |
| `TO_DATETIME(v)` | Convert to datetime | `EVAL ts = TO_DATETIME(timestamp_str)` |
| `TO_IP(v)` | Convert to IP | `EVAL ip = TO_IP(ip_string)` |

---

## Operators

### Comparison Operators

| Operator | Description | Example |
| -------- | ----------- | ------- |
| `==` | Equal | `WHERE status == 200` |
| `!=` | Not equal | `WHERE status != 500` |
| `<` | Less than | `WHERE response_time < 100` |
| `<=` | Less than or equal | `WHERE count <= 10` |
| `>` | Greater than | `WHERE bytes > 1000` |
| `>=` | Greater than or equal | `WHERE score >= 0.5` |
| `LIKE` | Pattern match (wildcards) | `WHERE host LIKE "prod-*"` |
| `RLIKE` | Regex match | `WHERE message RLIKE "error.*timeout"` |
| `IN` | In list | `WHERE status IN (200, 201, 204)` |
| `IS NULL` | Null check | `WHERE error IS NULL` |
| `IS NOT NULL` | Not null check | `WHERE response IS NOT NULL` |

### Logical Operators

| Operator | Description | Example |
| -------- | ----------- | ------- |
| `AND` | Logical AND | `WHERE status == 200 AND response_time < 100` |
| `OR` | Logical OR | `WHERE status == 500 OR status == 503` |
| `NOT` | Logical NOT | `WHERE NOT host LIKE "test-*"` |

### Arithmetic Operators

| Operator | Description | Example |
| -------- | ----------- | ------- |
| `+` | Addition | `EVAL total = sent + received` |
| `-` | Subtraction | `EVAL diff = end - start` |
| `*` | Multiplication | `EVAL bytes = kb * 1024` |
| `/` | Division | `EVAL rate = count / duration` |
| `%` | Modulo | `EVAL remainder = value % 10` |

---

## Dashboard Query Patterns

### Metric Panel Queries

Single-value metrics:

```esql
# Total count
FROM logs-*
| STATS total_events = COUNT(*)

# Average with breakdown
FROM logs-*
| STATS avg_response = AVG(response_time), p95 = PERCENTILE(response_time, 95.0) BY service.name
```

### Time Series Charts

```esql
# Events over time
FROM logs-*
| STATS event_count = COUNT(*) BY time_bucket = BUCKET(@timestamp, 1 hour)
| SORT time_bucket ASC

# Events by category over time
FROM logs-*
| STATS event_count = COUNT(*) BY time_bucket = BUCKET(@timestamp, 1 hour), event.category
| SORT time_bucket ASC

# Bytes transferred over time with breakdown
FROM logs-*
| STATS total_bytes = SUM(bytes) BY time_bucket = BUCKET(@timestamp, 15 minutes), host.name
| SORT time_bucket ASC
```

### Pie/Donut Charts

```esql
# Top 10 event categories
FROM logs-*
| STATS count = COUNT(*) BY event.category
| SORT count DESC
| LIMIT 10

# Browser distribution
FROM logs-*
| STATS users = COUNT_DISTINCT(user.id) BY user_agent.name
| SORT users DESC
| LIMIT 5
```

### Bar Charts

```esql
# Top hosts by request count
FROM logs-*
| STATS requests = COUNT(*) BY host.name
| SORT requests DESC
| LIMIT 10

# Error codes distribution
FROM logs-*
| WHERE status >= 400
| STATS errors = COUNT(*) BY status
| SORT errors DESC
```

### Data Tables

```esql
# Recent errors with context
FROM logs-*
| WHERE log.level == "error"
| KEEP @timestamp, host.name, message, error.type
| SORT @timestamp DESC
| LIMIT 100

# Top talkers summary
FROM logs-*
| STATS
    total_requests = COUNT(*),
    total_bytes = SUM(bytes),
    avg_response = AVG(response_time)
  BY source.ip
| SORT total_requests DESC
| LIMIT 20
```

---

## Common Mistakes to Avoid

1. **Using SQL syntax**: ES|QL is not SQL. No SELECT, FROM comes first, use `|` pipes.

2. **Wrong equality operator**: Use `==` for comparison, not `=`.

3. **Missing pipes**: Commands must be separated by `|`.

4. **GROUP BY in wrong place**: Use `BY` within `STATS`, not as separate clause.

5. **Wrong wildcard character**: Use `*` in LIKE patterns, not `%`.

6. **Forgetting SORT for time series**: Add `SORT time_bucket ASC` for charts.

7. **Using BUCKET as standalone command**: `BUCKET()` must be used within STATS...BY or EVAL, not as a separate command.

8. **Case sensitivity**: Field names are case-sensitive.

9. **Missing time filter**: Add `WHERE @timestamp >= NOW() - 1 day` for performance.

10. **Assuming default order**: Always explicit SORT for predictable results.

11. **Using window functions**: ES|QL has no `ROW_NUMBER() OVER (PARTITION BY ...)`. Use `VALUES()` + `MV_SORT()` + `MV_FIRST()`/`MV_LAST()` for latest-per-group patterns.

---

## Additional Resources

- [ESQL Panel Configuration](../panels/esql.md) - Dashboard panel setup
- [ES|QL Query Reuse with YAML Anchors](../advanced/esql-views.md) - Query patterns
- [Queries Configuration](../queries/config.md#esql-query) - Query format options
- [Elastic ES|QL Reference](https://www.elastic.co/docs/reference/query-languages/esql) - Official documentation
