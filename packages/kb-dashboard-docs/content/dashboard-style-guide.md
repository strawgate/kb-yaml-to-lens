# Kibana Dashboard Style Guide

**Based on:** Analysis of Elastic Integrations repository dashboards
**Last Updated:** 2026-01-09
**Version:** 2.0

---

## Introduction

This guide documents best practices for designing Kibana dashboards, derived from analysis of 49 production dashboards across 37 Elastic integration packages. Follow these conventions to create dashboards that are consistent, intuitive, and effective for dashboard creators using kb-yaml-to-lens, teams standardizing dashboard design, and anyone building Kibana dashboards for Elastic integrations.

### Key Principles

1. **Predictable Organization** - Users navigate any dashboard using the same mental model
2. **Visualization Clarity** - Choose chart types based on data characteristics, not aesthetics
3. **Progressive Disclosure** - Flow from overview to detail (metrics → charts → tables)
4. **Functional Minimalism** - Every panel serves a purpose; avoid decorative elements
5. **Consistent Conventions** - Follow patterns for naming, sizing, and positioning

---

## Dashboard Structure

### Standard Layout Hierarchy

All dashboards follow this top-to-bottom structure:

1. **Context Layer** - Navigation, title, description
2. **Summary Layer** - Key metrics and KPIs
3. **Analysis Layer** - Charts and visualizations
4. **Detail Layer** - Data tables for drill-down

### Grid Layout (48-Column System)

Kibana uses a 48-column grid with standard panel widths:

| Panel Type | Width (columns) | Use Case |
| ---------- | --------------- | -------- |
| Full-width markdown | 48 | Navigation, section headers |
| Single metric card | 8-12 | Individual KPIs |
| Small chart | 12-16 | Pie/donut charts |
| Medium chart | 24 | Half-width time series |
| Full chart | 48 | Primary time series, maps |
| Data table | 48 | Detail drill-down |

Arrange charts in horizontal rows of 2-3 panels for easy comparison.

---

## Naming Conventions

### Dashboard Titles

**Format:** `[Category PackageName] Specific Focus`

**Generic Examples:**

- `[Logs WebServer] Access and error logs`
- `[Metrics Application] Heap`
- `[Logs Firewall] Connection analysis`
- `[Security EmailGateway] Threat detection`

**Category Prefixes:**

- `[Logs ...]` - Log analysis dashboards
- `[Metrics ...]` - Performance/metric dashboards
- `[Traces ...]` - APM trace dashboards
- Package name without prefix - When it's the only dashboard type

### Panel Titles

**Guidelines:**

- Be concise and descriptive
- Avoid redundant prefixes like "Chart of" or "Graph of"
- Include the dimension when relevant (e.g., "by Time", "by Category")

**Effective Examples:**

- "Socket Syscalls Time Series"
- "Top 10 Malware Threats"
- "Browsers Breakdown"
- "Response Codes Over Time"

---

## Visualization Selection

### Decision Framework

| Data Characteristic | Visualization | Example Use Case |
| ------------------- | ------------- | ---------------- |
| Single KPI/Count | Metric Card | Total Requests, Active Users |
| Categorical Proportions | Pie/Donut Chart | File types, browsers, protocols |
| Categorical Ranking (short labels) | Vertical Bar Chart | Category comparison |
| Categorical Ranking (long labels) | Horizontal Bar Chart | Top users, top URLs, top regions |
| Time Series - Event counts | Stacked Area Chart | Events by type over time |
| Time Series - Discrete events | Stacked Bar Chart | HTTP status codes over time |
| Time Series - Continuous metrics | Line Chart | Memory usage, CPU utilization |
| Hierarchical Categories | Treemap | Event categories with subcategories |
| Bounded Metrics (0-100%) | Gauge Chart | Memory usage %, disk capacity % |
| Performance Percentiles | Heatmap | 95th percentile latency over time |
| Top N with Details | Data Table | Top 10 threats with counts |
| Recent Events/Logs | Data Table | Audit logs, access logs |
| Geographic Distribution | Map | Access by country, network sources |

---

## Visualization Guidelines

Complete configuration details are available in [Lens Panel Configuration](panels/lens.md).

### Metric Cards

**When to Use:** High-level KPIs, single counts, status breakdowns at dashboard top.

**Best Practices:** Use sparingly (0-4 typical, 78% use zero). Group horizontally, position before detailed visualizations. Modern dashboards prefer charts over standalone metrics. When the `primary_label` text matches or closely resembles the panel `title`, set `hide_title: true` to avoid displaying redundant text.

```yaml
- title: Total Requests
  hide_title: true  # primary_label "Requests" conveys the same meaning as the title
  lens:
    type: metric
    metric:
      primary_label: "Requests"
```

### Pie and Donut Charts

**When to Use:** Proportional distribution, "Top N" breakdowns (file types, browser/OS, protocols, event categories).

**Best Practices:** Show top 5-10 categories as percentages, prefer donut over pie, width 12-16 columns.

### Time Series Charts (XY Charts)

**Area Charts** (Most Common):

- Event frequency over time, volume trends
- Stacking shows categorical breakdown while maintaining total volume
- Filled area indicates volume

**Line Charts:**

- Precise metric tracking, performance monitoring
- Memory usage, CPU metrics, latency
- Dual-axis for comparing different metric scales

**Bar Charts:**

- Discrete time-bucketed events
- HTTP responses, error counts
- Stacking shows status code or category distribution

**Best Practices:**

- Use automatic time interval binning
- Add legends on the right side
- Stack when showing categorical breakdowns
- Use 30-day moving averages for smoothing trends (performance dashboards)

**ES|QL Breakdown Labels:** ES|QL charts support only one breakdown field, but you can concatenate multiple dimensions into a single breakdown label:

```esql
# Concatenate multiple dimensions for richer breakdown labels
TS metrics-*
|| STATS cpu_usage = AVG(container.cpu.utilization) / 100
  BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend),
     container.id, container.name, cpu_mode
|| EVAL container_id_short = SUBSTRING(TO_STRING(container.id), 0, 6)
|| EVAL breakdown_label = CONCAT(cpu_mode, " - ", container.name, " - ", container_id_short)
|| STATS cpu_usage = AVG(cpu_usage) BY time_bucket, breakdown_label
```

This pattern is especially useful for detailed charts showing multiple dimensions (e.g., "kernelmode - mycontainer - abc123").

### Data Tables

**When to Use:** Detail drill-down, "Top N" lists, searchable log/event details.

**Best Practices:** Position at bottom (~60% preference) or intermixed with charts (security/log dashboards). Use 10 rows/page, sort by count descending, 3-6 columns for summaries. Column layout: count/frequency + primary dimension + secondary dimensions (who, where, when).

### Bar Charts (Non-Time-Series)

**Horizontal:** Long labels (URLs, usernames, regions), percentile distributions, better text readability.

**Vertical:** Short category labels, standard comparisons, stacking more common.

### Maps

**Point-Based:** Plot IP addresses/coordinates, security context, user access patterns. Panel type: `map`. Usage: 30% of dashboards.

**Choropleth:** Country/region-level aggregations, administrative boundaries. Visualization type: `lnsChoropleth`. Color intensity represents metric values.

### Treemap Charts

**When to Use:** Hierarchical categorical data (firewall events, network protocols, file systems, security classification).

**Best Practices:** Show parent-child category structure with proportions at each level. Effective for network/security dashboards.

### Heatmap Charts

**When to Use:** Performance analysis, percentile tracking (95th/99th), latency distributions, multi-dimensional correlations.

**Best Practices:** Combine time with categorical dimension. Common for request duration, response sizes, query performance, API latency by region/endpoint.

### Gauge Charts

**When to Use:** Bounded metrics (0-100%), utilization/capacity indicators (memory, disk, connection pools, cache hit rate, thread pools).

**Best Practices:** Clear min/max bounds, visual arc indicator, position in summary layer, limit to 3-6 per dashboard.

---

## Dashboard Components

### Markdown Panels

**Purpose:** Navigation and context.

**Positioning:** Always at the top.

**When to Use:**

- Standard for multi-dashboard packages (3+ dashboards)
- Position at top-left (x: 0, y: 0)
- Typical width: 10-18 columns for navigation, 48 columns for section headers

**Content Types:**

1. **Navigation Links** (Most Common)
   - Links to related dashboards in the package
   - Table of contents for multi-dashboard sets
   - Header: "Navigation" or "Table of Contents"
   - Bulleted list of dashboard links

2. **Section Headers**
   - Visual separation between dashboard areas
   - Use sparingly

3. **Context Information**
   - Brief explanations when title isn't self-explanatory

Single-purpose dashboards may omit navigation, but multi-dashboard packages should consistently provide navigation links for discoverability.

### Links Panels

For packages with multiple dashboards, links panels provide an alternative to markdown navigation. Pattern observed in 16% of multi-dashboard packages. Position at top with standard 12-column width.

### Control Filters

**Usage Pattern:** Control filters ARE used in approximately 25% of Elastic integration dashboards when multi-dimensional filtering adds value.

**Common Types:**

- Options list (dropdown selections)
- Range slider (numeric/date ranges)
- Hierarchical controls (nested categories)

**Positioning:** Top of dashboard after navigation

**When to Use:**

- Multi-tenant scenarios (filter by host, service, user)
- Complex dashboards requiring dynamic filtering across multiple dimensions
- Security dashboards with varied analysis perspectives

**Alternative Filtering Approaches:**

- Time picker (global time range selection)
- Dashboard-level filters (data stream, package filters)
- Panel-level filters (specific to individual visualizations)

---

## Filters and Queries

### Global Dashboard Filters

**Standard Pattern:** Filter by dataset using KQL syntax.

Single dataset:

```yaml
filters:
  - equals: package.dataset_name
    field: data_stream.dataset
```

Multiple datasets:

```yaml
filters:
  - query: "data_stream.dataset: (webserver.access OR webserver.error)"
```

### Panel-Level Filters

**Common Patterns:** Event type/category filters, status code filters, field existence checks.

Example:

```yaml
filters:
  - equals: connection
    field: event.type
  - equals: bind
    field: auditd.data.syscall
  - query: "NOT auditd.data.addr: netlink"
```

### Query Language

**Standard:** Use KQL (Kibana Query Language) for consistency.

---

## Color and Styling

### Color Schemes

Use Kibana's default color palette. Avoid custom color overrides (use sparingly) and too many colors (limit to 5-10 categories).

### Legend Positioning

**Standard:** Right-side placement
**Exception:** Bottom placement when charts are narrow

### Number Formatting

| Data Type | Format | Example |
| --------- | ------ | ------- |
| Bytes | 2 decimal precision | 1.23 GB |
| Counts | Integer | 1,234 |
| Percentages | Display on pie/donut | 45.2% |
| Dates | ISO format | 2024-01-15T10:30:00Z |

---

## Dashboard Types and Patterns

### Security Dashboards

Heavy use of categorical breakdowns (pie/donut charts), focus on "Top N" patterns (threats, users, actions), data tables for audit trails, control filters for multi-tenant scenarios.

**Flow:** Navigation → Controls → Events over time → Event categories → Top users/actions → Audit log

### Performance Dashboards

Exclusive use of line charts for precision, dual-axis comparisons, moving averages for smoothing. No pie charts (metrics don't have categorical proportions).

**Flow:** Navigation → Control → CPU/Memory over time → GC activity/Thread count → Latency/Throughput

### Infrastructure Dashboards

Mix of metrics, time series, and categorical breakdowns. Geographic maps when relevant, browser/OS distribution analysis, error rate and status code tracking.

**Flow:** Navigation → Metrics → Geographic distribution → Requests over time → Status codes → Browser/OS → Top URLs table

### Dashboard Complexity Spectrum

| Complexity | Panels | Viz Types | Panel Mix | Use Cases |
| ---------- | ------ | --------- | --------- | --------- |
| **Simple** | 3-6 | 1-2 | 0-2 metrics, 2-4 charts, 0-1 tables | Specialized performance tracking, single-service monitoring |
| **Standard** | 7-12 | 3-4 | 2-4 metrics, 4-6 charts, 1-2 tables | General-purpose monitoring, package overviews |
| **Complex** | 13+ | 5-6 | 3-6 metrics, 7-12 charts, 2-4 tables, controls | Enterprise monitoring, multi-dimensional analysis, security operations |

**Complex dashboard considerations:** Use markdown sections to separate areas, group related visualizations, maintain logical vertical flow. Consider breaking into multiple dashboards if exceeding 20 panels.

---

## Time Configuration

### Time Range

**Default Ranges:**

- Infrastructure monitoring: 15 minutes
- Security dashboards: User-selected (flexible)
- Performance monitoring: 1 hour to 24 hours

Enable time range restoration as best practice.

### Time Synchronization

**Standard:** Enable cursor synchronization across time-series panels.

```yaml
sync_cursor: true
sync_tooltips: false
```

---

## Accessibility and Usability

### Panel Sizing

**Minimum Heights:**

- Metric cards: 4 grid units
- Charts: 12-15 grid units
- Tables: 15-20 grid units (allow for pagination)
- Markdown headers (at default font_size 12):
  - Headers h4-h6: 2 grid units
  - Headers h1-h3: 3 grid units
  - Header with one line of text below: 5 grid units

### Panel Ordering

**Vertical Flow Best Practices:**

1. Navigation and context (top)
2. Controls (immediately after navigation, when used)
3. Key metrics (before detailed charts)
4. Primary visualizations (middle)
5. Detail tables (bottom preferred, intermixed when contextually relevant)

### Responsive Considerations

- Avoid panels narrower than 12 columns
- Test dashboard at different screen sizes
- Ensure tables have horizontal scroll when needed

---

## Examples and Templates

Reference the `packages/kb-dashboard-docs/content/examples/` directory for complete dashboard examples demonstrating these patterns (aerospike, apache_otel, aws_cloudtrail_otel, crowdstrike, elasticsearch_otel, k8s_cluster_otel, memcached_otel, and more). Templates show navigation panels, metric cards, time series charts, categorical breakdowns, and detail tables in standard configurations.

---

## Checklist

**Structure & Layout:**

- [ ] Title: `[Category Package] Focus` format, description when needed
- [ ] Hierarchy: context → control → summary → analysis → detail
- [ ] Navigation at top (multi-dashboard packages), tables at bottom (preferred)
- [ ] Standard widths (12, 16, 24, 48 columns), min 12 columns, charts 12-15 grid units

**Visualizations:**

- [ ] Chart types match data characteristics (area for events, line for metrics, pie for proportions)
- [ ] Metric cards: 0-4 per dashboard, pie/donut: top 5-10 only
- [ ] Specialized: treemap (hierarchical), heatmap (percentiles), gauge (0-100%)

**Naming & Formatting:**

- [ ] Panel titles concise, no redundant prefixes, field labels human-readable
- [ ] Number formatting appropriate, legends positioned correctly

**Filters & Controls:**

- [ ] Global filter for `data_stream.dataset`, panel filters specific, KQL syntax consistent
- [ ] Controls used when multi-dimensional filtering adds value

**Configuration & Testing:**

- [ ] Time range appropriate, cursor sync enabled for time-series
- [ ] Tested at different time ranges, filters work, tables paginate (10 rows), no console errors

---

## Additional Resources

### Related Documentation

- [Dashboard Decompiling Guide](dashboard-decompiling-guide.md) - Converting Kibana JSON to YAML
- [Panel Types Documentation](panels/base.md) - Detailed panel configuration
- [Lens Panel Configuration](panels/lens.md) - Complete field descriptions and options
- [Controls Documentation](controls/config.md) - Dashboard control configuration
- [Filters Documentation](filters/config.md) - Filter and query configuration

### External Resources

- [Kibana Lens Documentation](https://www.elastic.co/docs/explore-analyze/visualize/lens)
- [Elastic Common Schema (ECS)](https://www.elastic.co/guide/en/ecs/current/index.html)
- [Kibana Query Language (KQL)](https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql)
- [Elasticsearch Query Language (ESQL)](https://www.elastic.co/docs/reference/query-languages/esql)
