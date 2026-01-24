# Creating Dashboards from OpenTelemetry Receivers

This guide provides a systematic approach for creating Kibana dashboards that visualize data from OpenTelemetry Collector receivers. Following these guidelines helps avoid common pitfalls discovered through extensive dashboard development and review.

## Before You Start

### 1. Locate the Receiver Documentation

Every OTel receiver has authoritative documentation in the OpenTelemetry Collector Contrib repository:

```text
https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/{receiver}receiver
```

**Critical files to review:**

| File | Purpose |
| ---- | ------- |
| `README.md` | Configuration options and setup |
| `documentation.md` | Complete metrics and attributes reference |
| `metadata.yaml` | Source of truth for metric names, types, and attributes |

### 2. Understand Metric Types

OTel receivers emit metrics with specific types that determine how you query them:

| Metric Type | Description | Query Approach |
| ----------- | ----------- | -------------- |
| **Gauge** | Point-in-time value | See [Gauge Function Selection](#gauge-function-selection) below |
| **Sum (Cumulative)** | Monotonically increasing counter | Use `RATE()` for per-second rates |
| **Sum (Delta)** | Change since last measurement | Use `SUM()` to aggregate |
| **Histogram** | Distribution of values | Query bucket boundaries |

#### Gauge Function Selection

For gauge metrics with the `TS` command, choose the right `*_OVER_TIME()` function:

| Use Case | Function | Examples |
| -------- | -------- | -------- |
| Current state | `LAST_OVER_TIME()` | Connection counts, thread counts, buffer sizes, queue depths |
| Typical value | `AVG_OVER_TIME()` | CPU utilization, memory percentage, load averages |
| Peak detection | `MAX_OVER_TIME()` | Latency spikes, memory high-water marks |

**Rule of thumb:** If the metric answers "how many/much right now?", use `LAST_OVER_TIME()`. If it answers "what's the average/typical level?", use `AVG_OVER_TIME()`.

### 3. Verify Attribute Names

Attributes in `metadata.yaml` may differ from exported field names due to `name_override` configuration. Check `metadata.yaml` for renames:

```yaml
# In metadata.yaml - internal name with name_override
attributes:
  workers_state:
    description: State of the worker
    name_override: state  # <-- This is the actual exported field name

# Use the name_override value in your queries
# Field: attributes.state (NOT attributes.workers_state)
```

---

## Field Reference Patterns

### Standard OTel Field Paths

OpenTelemetry data uses consistent field path patterns:

| Field Type | Path Pattern | Example |
| ---------- | ------------ | ------- |
| Metric value | `{metric.name}` | `apache.requests` |
| Metric attribute | `attributes.{name}` | `attributes.state` |
| Resource attribute | `resource.attributes.{namespace}.{name}` | `resource.attributes.apache.server.name` |
| Data stream | `data_stream.dataset` | `"apachereceiver.otel"` |
| Timestamp | `@timestamp` | Standard time field |

### Common Mistakes

**Wrong:** Using unprefixed attribute names

```text
# WRONG - "threads" doesn't exist as a top-level field
WHERE threads == "connected"

# CORRECT - Attributes require the "attributes." prefix
WHERE attributes.kind == "connected"
```

**Wrong:** Using internal metadata names instead of exported names

```yaml
# WRONG - Uses internal metadata.yaml name
breakdown:
  field: circuit_breaker_name

# CORRECT - Uses actual exported field name (check documentation.md)
breakdown:
  field: name
```

**Wrong:** Using simplified resource attribute paths

```yaml
# WRONG - server.address doesn't exist
filters:
  - field: server.address

# CORRECT - Full resource attribute path
filters:
  - field: resource.attributes.apache.server.name
```

---

## ES|QL Query Patterns for OTel Data

### Time Series Queries

Use the `TS` source command with dynamic bucketing for time series data. Always use `BUCKET(@timestamp, 20, ?_tstart, ?_tend)` so dashboards remain readable across different time ranges:

```esql
TS metrics-*
| WHERE data_stream.dataset == "apachereceiver.otel"
| WHERE apache.requests IS NOT NULL
| STATS rate = SUM(RATE(apache.requests)) BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend)
| SORT time_bucket ASC
```

### Time Bucket Sizing Best Practices

Always use dynamic bucketing with both FROM and TS queries:

```esql
# Recommended pattern for all queries
BUCKET(@timestamp, 20, ?_tstart, ?_tend)
```

| Parameter | Description |
| --------- | ----------- |
| `@timestamp` | The timestamp field to bucket |
| `20` | Target number of buckets (20-50 recommended) |
| `?_tstart` | Kibana time range start (auto-populated) |
| `?_tend` | Kibana time range end (auto-populated) |

**Why dynamic bucketing is essential:**

- Fixed intervals like `BUCKET(@timestamp, 1 minute)` create 10,080 data points for 1 week
- Fixed intervals like `BUCKET(@timestamp, 5 minutes)` create 2,016 data points for 1 week
- `BUCKET(@timestamp, 20, ?_tstart, ?_tend)` creates exactly ~20 data points regardless of time range

**Note:** Avoid `TBUCKET(interval)` as it uses fixed intervals that don't scale with the dashboard time range.

### Counter Metrics

Counters (Sum Cumulative type) track monotonically increasing values. Use `RATE()`:

```esql
# CORRECT - Use RATE() for counter metrics
TS metrics-*
| STATS request_rate = SUM(RATE(apache.requests))

# WRONG - MAX() on a counter gives cumulative total, not rate
FROM metrics-*
| STATS requests = MAX(apache.requests)
```

### Gauge Metrics

Gauges represent point-in-time values. Choose the right `*_OVER_TIME()` function based on the metric semantics:

```esql
# Current state - use LAST_OVER_TIME for "how many right now?"
# Examples: connection counts, thread counts, buffer sizes, queue depths
TS metrics-*
| STATS connections = MAX(LAST_OVER_TIME(apache.current_connections))

# Typical value - use AVG_OVER_TIME for "what's the average level?"
# Examples: CPU utilization, memory percentage, load averages
TS metrics-*
| STATS avg_cpu = MAX(AVG_OVER_TIME(apache.cpu.load))
```

### Escaping Field Names

Field names with numeric suffixes or special characters require backticks:

```esql
# WRONG - Parser interprets .1 as numeric
WHERE apache.load.1 IS NOT NULL

# CORRECT - Backticks escape the field name
WHERE `apache.load.1` IS NOT NULL
| STATS load_1m = AVG(AVG_OVER_TIME(`apache.load.1`))
```

### Dimensional Filtering

When a metric has dimensional attributes, filter using the attribute field:

```esql
# Filter by specific dimension value
TS metrics-*
| WHERE attributes.status == "clean" OR attributes.status == "dirty"
| STATS pages = MAX(mysql.buffer_pool.usage) BY attributes.status

# Group by dimension
TS metrics-*
| STATS operations = SUM(RATE(mysql.operations)) BY attributes.operation
```

---

## Lens Formula Patterns for OTel Data

### Counting Unique Entities

Use `unique_count()` to count distinct entities, not `count()`:

```yaml
# WRONG - Counts metric documents, not unique pods
formula: count()

# CORRECT - Counts unique pod names
formula: unique_count(k8s.pod.name)
```

### Division Safety

Always guard against division by zero:

```yaml
# WRONG - Fails if denominator is zero
formula: average(used) / average(total)

# CORRECT - Add small value to prevent division by zero
formula: average(used) / (average(total) + 0.000001)

# ALTERNATIVE - Use clamp() to ensure minimum denominator
formula: average(used) / clamp(average(total), 1, Infinity)
```

### Dimensional Filtering in Lens

Use KQL filters for dimensional data, not separate metric names:

```yaml
# WRONG - These metrics don't exist as separate fields
metrics:
  - id: active_shards
    field: elasticsearch.cluster.shards.active
  - id: unassigned_shards
    field: elasticsearch.cluster.shards.unassigned

# CORRECT - Filter single metric by dimension
metrics:
  - id: active_shards
    formula: "max(elasticsearch.cluster.shards, kql='shard_state: active')"
  - id: unassigned_shards
    formula: "max(elasticsearch.cluster.shards, kql='shard_state: unassigned')"
```

### Metric Existence Filters

Use `exists` filters when metrics may not always be present:

```yaml
filters:
  - exists: k8s.container.restarts
  - exists: k8s.deployment.name
```

---

## Validation Checklist

Before finalizing a dashboard, verify:

### Metric Names

- [ ] All metric names match `documentation.md` exactly (including singular/plural)
- [ ] No invented metrics based on attribute values

### Attribute Names

- [ ] All attributes use `attributes.` prefix
- [ ] Resource attributes use full `resource.attributes.{namespace}.{name}` path
- [ ] Names match exported values, not internal `metadata.yaml` names
- [ ] Checked for `name_override` in receiver metadata

### Query Correctness

- [ ] Counter metrics use `RATE()`, not `MAX()`/`AVG()`
- [ ] All time bucketing uses `BUCKET(@timestamp, 20, ?_tstart, ?_tend)` for dynamic sizing
- [ ] No fixed-interval bucketing like `TBUCKET(5 minutes)` or `BUCKET(@timestamp, 1 hour)`
- [ ] Field names with special characters are backtick-escaped
- [ ] All queries include NULL checks for optional metrics
- [ ] Use `SORT` not `ORDER` in ES|QL

### Panel Metadata

- [ ] Titles accurately describe the visualization (not "Top 10" without `LIMIT 10`)
- [ ] Labels match aggregation type ("Rate" not "Count" when using `RATE()`)
- [ ] Descriptions match actual query groupings
- [ ] No technical implementation details in user-facing titles (no "(ES|QL)")

### Formula Safety

- [ ] All divisions guard against zero denominators
- [ ] Entity counts use `unique_count()`, not `count()`
- [ ] No unsupported conditional syntax in Lens formulas

---

## Common Receiver Patterns

### JVM Metrics (Shared Across Receivers)

Many receivers (Elasticsearch, Kafka, etc.) emit standard JVM metrics without a service prefix:

```yaml
# CORRECT - Standard JVM metric naming
field: jvm.memory.heap.used
field: jvm.gc.collections.count

# WRONG - Don't add service prefix to JVM metrics
field: elasticsearch.jvm.memory.heap.used
```

### Data Stream Filtering

Always filter by data stream dataset for receiver-specific queries:

```esql
# Filter to specific receiver data
TS metrics-*
| WHERE data_stream.dataset == "elasticsearchreceiver.otel"
```

### Numeric vs String Attribute Values

Some receivers encode enum values as numbers, others as strings. Verify actual data format:

```text
# Some receivers use numeric encoding
WHERE attributes.phase == "1"  # May represent "Pending"

# Others use string encoding
WHERE attributes.phase == "Pending"

# Document encoding expectations in README
```

---

## Dashboard Organization

### Split Large Dashboards

Keep dashboards focused with fewer than 20 panels. Split by concern:

| Dashboard | Focus |
| --------- | ----- |
| Overview | High-level health, key metrics |
| Resource Details | Capacity, allocation, utilization |
| Performance | Latency, throughput, rates |
| Health/Errors | Error rates, failures, alerts |

### Navigation Links

Link related dashboards for drill-down workflows:

```yaml
- title: Related Dashboards
  type: links
  links:
    - label: Cluster Overview
      dashboard: cluster-overview
    - label: Node Details
      dashboard: node-details
```

### Progressive Disclosure

Structure panels from high-level to detailed:

1. **Navigation** - Links to related dashboards
2. **Key Metrics** - 4-6 summary metric cards
3. **Trends** - Time series charts showing patterns
4. **Details** - Tables with sortable, filterable data

---

## Testing Your Dashboard

### 1. Compile and Validate

```bash
# Compile all dashboards in a directory
kb-dashboard compile --input-dir ./my-dashboards

# Compile a single dashboard file
kb-dashboard compile --input-file ./my-dashboard.yaml
```

---

## Additional Resources

- [ES|QL Language Reference](esql-language-reference.md) - Complete ES|QL syntax
- [Dashboard Style Guide](../dashboard-style-guide.md) - Layout and design patterns
- [Complete Examples](../examples/index.md) - Working OTel dashboard bundles
- [OpenTelemetry Collector Contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib) - Upstream receiver documentation
