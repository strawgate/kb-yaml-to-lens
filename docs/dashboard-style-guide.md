# Kibana Dashboard Style Guide

**Based on:** Analysis of Elastic Integrations repository dashboards
**Last Updated:** 2026-01-08
**Version:** 1.0

---

## Introduction

This style guide documents best practices for designing Kibana dashboards, based on analysis of production dashboards from the Elastic integrations repository. Following these conventions will help create dashboards that are consistent, intuitive, and effective.

### Who This Guide Is For

- Dashboard creators using kb-yaml-to-lens
- Teams standardizing dashboard design
- Anyone creating Kibana dashboards for Elastic integrations

### Key Principles

1. **Predictable Organization** - Users should navigate any dashboard using the same mental model
2. **Visualization Clarity** - Choose chart types based on data characteristics, not aesthetics
3. **Progressive Disclosure** - Flow from overview to detail (metrics → charts → tables)
4. **Functional Minimalism** - Every panel serves a purpose; avoid decorative elements
5. **Consistent Conventions** - Follow patterns for naming, sizing, and positioning

---

## Dashboard Structure

### Standard Layout Hierarchy

All dashboards should follow this top-to-bottom structure:

```
1. Context Layer    - Navigation, title, description
2. Control Layer    - Interactive filters (when needed)
3. Summary Layer    - Key metrics and KPIs
4. Analysis Layer   - Charts and visualizations
5. Detail Layer     - Data tables for drill-down
```

**Example Flow:**
```
[Navigation Links - Markdown Panel]
[Control: Filter by Host] [Control: Filter by Event Type]
[Metric: Total Events] [Metric: Success Rate]
[Chart: Events Over Time] [Chart: Event Category Distribution]
[Table: Top 10 Events by Count]
```

### Grid Layout (48-Column System)

Kibana uses a 48-column grid. Standard panel widths:

| Panel Type | Width (columns) | Use Case |
|-----------|----------------|----------|
| Full-width markdown | 48 | Navigation, section headers |
| Single metric card | 8-12 | Individual KPIs |
| Small chart | 12-16 | Pie/donut charts |
| Medium chart | 24 | Half-width time series |
| Full chart | 48 | Primary time series, maps |
| Data table | 48 | Detail drill-down |

**Best Practice:** Arrange charts in horizontal rows of 2-3 panels for easy comparison.

---

## Naming Conventions

### Dashboard Titles

**Format:** `[Category PackageName] Specific Focus`

**Examples:**
- `[Logs IIS] Access and error logs`
- `[Metrics Golang] Heap`
- `[Auditd Manager] Sockets`
- `[Logs Cisco Secure Email Gateway] AMP Engine`

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

**Good Examples:**
- "Socket Syscalls Time Series"
- "Top 10 Malware Threats"
- "Browsers Breakdown"
- "Response Codes Over Time"

**Avoid:**
- "Chart showing socket syscalls over time"
- "A graph of the top 10 malware threats"
- "Browser distribution pie chart"

---

## Visualization Selection

### Decision Tree

Use this guide to select the appropriate visualization type:

```
What are you visualizing?
│
├─ Single KPI/Count
│  └─ Use: Metric Card
│     Example: Total Requests, Active Users
│
├─ Categorical Proportions (parts of a whole)
│  └─ Use: Pie or Donut Chart
│     Example: File types, browsers, protocols, status codes
│
├─ Categorical Ranking (ordered comparison)
│  ├─ Short labels → Use: Vertical Bar Chart
│  └─ Long labels → Use: Horizontal Bar Chart
│     Example: Top users, top URLs, top regions
│
├─ Time Series Data
│  ├─ Event counts by category
│  │  └─ Use: Stacked Area Chart
│  │     Example: Events by type over time
│  │
│  ├─ Discrete time events
│  │  └─ Use: Stacked Bar Chart
│  │     Example: HTTP status codes over time
│  │
│  └─ Continuous metrics (precise values)
│     └─ Use: Line Chart
│        Example: Memory usage, CPU utilization
│
├─ Top N with Details
│  └─ Use: Data Table
│     Example: Top 10 threats, top users with counts
│
├─ Recent Events/Logs
│  └─ Use: Data Table (searchable)
│     Example: Audit logs, access logs
│
└─ Geographic Distribution
   └─ Use: Map
      Example: Access by country, network sources
```

### Visualization-Specific Guidelines

#### Metric Cards

**When to Use:**
- High-level KPIs at the top of the dashboard
- Single counts or aggregated values
- Status breakdowns (success/failure counts)

**Patterns:**
- Group related metrics in a horizontal row
- Use sparingly (0-6 per dashboard)
- Position before detailed visualizations

**Example Configuration:**
```yaml
- title: Total Requests
  grid: {x: 0, y: 3, w: 12, h: 8}
  lens:
    type: metric
    data_view: logs-*
    primary:
      aggregation: count
```

#### Pie and Donut Charts

**When to Use:**
- Showing proportional distribution of categories
- Comparing parts of a whole
- "Top N" categorical breakdowns

**Best Practices:**
- Show top 5-10 categories (not all categories)
- Display as percentages
- Use donut over pie for cleaner appearance
- Width: 12-16 columns

**Common Use Cases:**
- File type distribution
- Browser/OS breakdown
- Protocol distribution
- Event category proportions

**Example Configuration:**
```yaml
- title: File Type Distribution
  grid: {x: 0, y: 15, w: 16, h: 15}
  lens:
    type: pie
    data_view: logs-*
    dimensions:
      - field: file.extension
        type: values
        size: 5
    metrics:
      - aggregation: count
```

#### Time Series Charts (XY Charts)

**Chart Type Selection:**

**Area Charts** (Most Common):
- Use for: Event frequency over time, volume trends
- Stacking: Show categorical breakdown while maintaining total volume
- Visual weight: Filled area indicates volume

**Line Charts**:
- Use for: Precise metric tracking, performance monitoring
- Best for: Memory usage, CPU metrics, latency
- Dual-axis: Compare different metric scales

**Bar Charts**:
- Use for: Discrete time-bucketed events
- Stacking: Show status code or category distribution
- Best for: HTTP responses, error counts

**Best Practices:**
- Use automatic time interval binning (most common)
- Add legends on the right side
- Stack when showing categorical breakdowns
- Use 30-day moving averages for smoothing trends (performance dashboards)

**Example Configuration:**
```yaml
- title: Events Over Time by Category
  grid: {x: 0, y: 30, w: 48, h: 15}
  lens:
    type: area
    data_view: logs-*
    dimensions:
      - field: '@timestamp'
        type: date_histogram
    breakdown:
      - field: event.category
        type: values
        size: 10
    metrics:
      - aggregation: count
    display:
      stacked: true
```

#### Data Tables

**When to Use:**
- Detail drill-down at the bottom of dashboards
- "Top N" lists with multiple dimensions
- Searchable log/event details

**Best Practices:**
- Always position at the bottom (100% consistency)
- Use 10 rows per page (standard pagination)
- Sort by count descending for "Top N" tables
- Include 3-6 columns for summaries, 5-10+ for comprehensive logs

**Column Layout:**
- Count/frequency column (first or last)
- Primary dimension (what happened)
- Secondary dimensions (who, where, when)

**Example Configuration:**
```yaml
- title: Top 10 Users by Failed Login
  grid: {x: 0, y: 60, w: 48, h: 15}
  lens:
    type: table
    data_view: logs-*
    dimensions:
      - field: user.name
        type: values
        size: 10
    metrics:
      - aggregation: count
        label: Failed Attempts
```

#### Bar Charts (Non-Time-Series)

**Orientation Guidelines:**

**Horizontal Bars:**
- Use when: Labels are long (URLs, usernames, regions)
- Benefit: Better readability for text-heavy categories
- Example: Top users, top URLs

**Vertical Bars:**
- Use when: Short category labels
- Use for: Standard category comparisons
- Stacking more common with vertical orientation

#### Maps

**When to Use:**
- Geographic distribution is relevant for analysis
- Security context (network sources)
- Global access patterns

**Required Fields:**
- `source.geo.location` or similar geo field
- Access/event volume for sizing

**Best Practices:**
- Use color and size scaling based on volume
- Position in middle section (not top or bottom)

---

## Dashboard Components

### Markdown Panels

**Purpose:** Navigation and context

**Positioning:** Always at the top

**Content Types:**

1. **Navigation Links**
   - Links to related dashboards in the package
   - Table of contents for multi-dashboard sets

2. **Section Headers**
   - Visual separation between dashboard areas
   - Use sparingly

3. **Context Information**
   - Brief explanations when title isn't self-explanatory

**Example:**
```yaml
- markdown:
    content: |
      ## Navigation

      Related Dashboards:
      - [Overview Dashboard](#/dashboard/overview-id)
      - [Detailed Analysis](#/dashboard/detail-id)
  grid: {x: 0, y: 0, w: 48, h: 3}
```

### Control Filters

**When to Use:**
- Multi-tenant scenarios
- Multi-system dashboards
- Need for dimensional filtering across all panels

**When NOT to Use:**
- Single-source dashboards
- Pre-filtered dashboards with specific scope

**Types:**

1. **Options List** (Most Common)
   - Host/service filters
   - Event type filters
   - Method/protocol filters

2. **Range Slider**
   - Status code ranges
   - Numeric value filters

**Best Practices:**
- Position at the top, immediately after navigation
- Use 2-4 controls (not too many)
- Support hierarchical selections
- Enable exclusion when relevant

**Example:**
```yaml
controls:
  - type: options
    label: Filter by Host
    data_view: logs-*
    field: host.name
    width: medium

  - type: range
    label: HTTP Status Code
    data_view: logs-*
    field: http.response.status_code
    min: 100
    max: 599
```

---

## Filters and Queries

### Global Dashboard Filters

**Standard Pattern:** Filter by dataset

**Best Practice:**
```yaml
filters:
  - field: data_stream.dataset
    value: package.dataset_name
```

**Multiple Datasets:**
```yaml
filters:
  - query: "data_stream.dataset: (iis.access OR iis.error)"
```

### Panel-Level Filters

**Common Patterns:**
- Event type/category filters
- Status code filters
- Field existence checks

**Example:**
```yaml
filters:
  - field: event.type
    value: connection
  - field: auditd.data.syscall
    value: bind
  - query: "NOT auditd.data.addr: netlink"
```

### Query Language

**Standard:** Use KQL (Kibana Query Language) for consistency

---

## Color and Styling

### Color Schemes

**Best Practice:** Use Kibana's default color palette

**Avoid:**
- Custom color overrides (use sparingly)
- Too many colors (limit to 5-10 categories)

### Legend Positioning

**Standard:** Right-side placement

**Exception:** Bottom placement when charts are narrow

### Number Formatting

| Data Type | Format | Example |
|-----------|--------|---------|
| Bytes | 2 decimal precision | 1.23 GB |
| Counts | Integer | 1,234 |
| Percentages | Display on pie/donut | 45.2% |
| Dates | ISO format | 2024-01-15T10:30:00Z |

---

## Dashboard Types and Patterns

### Security Dashboards

**Characteristics:**
- Heavy use of categorical breakdowns (pie/donut charts)
- Focus on "Top N" patterns (threats, users, actions)
- Data tables for audit trails
- Control filters for multi-tenant scenarios

**Example Layout:**
```
[Navigation]
[Controls: By Host, By Event Type]
[Chart: Events Over Time] [Pie: Event Categories]
[Pie: Top Users] [Pie: Top Actions]
[Table: Detailed Audit Log]
```

### Performance Dashboards

**Characteristics:**
- Exclusive use of line charts for precision
- Dual-axis comparisons
- Moving averages for smoothing
- No pie charts (metrics don't have categorical proportions)

**Example Layout:**
```
[Navigation]
[Control: By Service]
[Chart: CPU Over Time] [Chart: Memory Over Time]
[Chart: GC Activity] [Chart: Thread Count]
[Chart: Latency] [Chart: Throughput]
```

### Infrastructure Dashboards

**Characteristics:**
- Mix of metrics, time series, and categorical breakdowns
- Geographic maps when relevant
- Browser/OS distribution analysis
- Error rate and status code tracking

**Example Layout:**
```
[Navigation]
[Metrics: Total Requests, Avg Response Time, Error Rate]
[Map: Geographic Access Distribution]
[Chart: Requests Over Time] [Pie: Status Codes]
[Pie: Browsers] [Pie: Operating Systems]
[Table: Top URLs by Response Code]
```

---

## Time Configuration

### Time Range

**Default Ranges:**
- Infrastructure monitoring: 15 minutes
- Security dashboards: User-selected (flexible)
- Performance monitoring: 1 hour to 24 hours

**Best Practice:** Enable time range restoration

### Time Synchronization

**Standard:** Enable cursor synchronization across time-series panels

**Configuration:**
```yaml
sync_cursor: true
sync_tooltips: false
```

---

## Accessibility and Usability

### Panel Sizing

**Minimum Heights:**
- Metric cards: 8 grid units
- Charts: 12-15 grid units
- Tables: 15-20 grid units (allow for pagination)

### Panel Ordering

**Vertical Flow Best Practices:**
1. Navigation and context (top)
2. Controls (immediately after navigation)
3. Key metrics (before detailed charts)
4. Primary visualizations (middle)
5. Detail tables (bottom)

### Responsive Considerations

**Best Practices:**
- Avoid panels narrower than 12 columns
- Test dashboard at different screen sizes
- Ensure tables have horizontal scroll when needed

---

## Examples and Templates

### Basic Dashboard Template

```yaml
dashboards:
  - name: "[Logs Package] Dashboard Name"
    description: Brief description of dashboard purpose

    panels:
      # Navigation
      - markdown:
          content: |
            ## Navigation
            - [Related Dashboard](#/dashboard/id)
        grid: {x: 0, y: 0, w: 48, h: 3}

      # Key Metrics
      - title: Total Events
        grid: {x: 0, y: 3, w: 12, h: 8}
        lens:
          type: metric
          data_view: logs-*
          primary:
            aggregation: count

      # Time Series
      - title: Events Over Time
        grid: {x: 0, y: 11, w: 48, h: 15}
        lens:
          type: area
          data_view: logs-*
          dimensions:
            - field: '@timestamp'
              type: date_histogram
          metrics:
            - aggregation: count

      # Categorical Breakdown
      - title: Event Categories
        grid: {x: 0, y: 26, w: 24, h: 15}
        lens:
          type: pie
          data_view: logs-*
          dimensions:
            - field: event.category
              type: values
              size: 5
          metrics:
            - aggregation: count

      # Detail Table
      - title: Recent Events
        grid: {x: 0, y: 41, w: 48, h: 15}
        lens:
          type: table
          data_view: logs-*
          dimensions:
            - field: '@timestamp'
              type: date_histogram
            - field: event.action
              type: values
            - field: user.name
              type: values
          metrics:
            - aggregation: count

    filters:
      - field: data_stream.dataset
        value: package.dataset_name
```

### Security Dashboard Template

```yaml
dashboards:
  - name: "[Security Package] Threat Analysis"
    description: Security event monitoring and threat detection

    controls:
      - type: options
        label: Filter by Host
        data_view: logs-*
        field: host.name
        width: medium

      - type: options
        label: Filter by Event Type
        data_view: logs-*
        field: event.type
        width: medium

    panels:
      - markdown:
          content: |
            ## Security Dashboards
            - [Overview](#/dashboard/overview)
            - [Threat Details](#/dashboard/threats)
        grid: {x: 0, y: 0, w: 48, h: 3}

      - title: Events by Severity Over Time
        grid: {x: 0, y: 3, w: 48, h: 15}
        lens:
          type: area
          data_view: logs-*
          dimensions:
            - field: '@timestamp'
              type: date_histogram
          breakdown:
            - field: event.severity
              type: values
          metrics:
            - aggregation: count
          display:
            stacked: true

      - title: Top 10 Threat Types
        grid: {x: 0, y: 18, w: 24, h: 15}
        lens:
          type: pie
          data_view: logs-*
          dimensions:
            - field: threat.technique.name
              type: values
              size: 10
          metrics:
            - aggregation: count

      - title: Top Affected Users
        grid: {x: 24, y: 18, w: 24, h: 15}
        lens:
          type: pie
          data_view: logs-*
          dimensions:
            - field: user.name
              type: values
              size: 10
          metrics:
            - aggregation: count

      - title: Detailed Security Events
        grid: {x: 0, y: 33, w: 48, h: 20}
        lens:
          type: table
          data_view: logs-*
          dimensions:
            - field: '@timestamp'
              type: date_histogram
            - field: event.action
              type: values
            - field: user.name
              type: values
            - field: source.ip
              type: values
            - field: event.severity
              type: values
          metrics:
            - aggregation: count
              label: Count
```

### Performance Monitoring Template

```yaml
dashboards:
  - name: "[Metrics Application] Performance Overview"
    description: Application performance metrics and resource utilization

    panels:
      - markdown:
          content: |
            ## Performance Metrics
            - [CPU Analysis](#/dashboard/cpu)
            - [Memory Analysis](#/dashboard/memory)
        grid: {x: 0, y: 0, w: 48, h: 3}

      - title: CPU Usage
        grid: {x: 0, y: 3, w: 24, h: 15}
        lens:
          type: line
          data_view: metrics-*
          dimensions:
            - field: '@timestamp'
              type: date_histogram
          metrics:
            - field: system.cpu.total.norm.pct
              aggregation: average
              label: CPU %

      - title: Memory Usage
        grid: {x: 24, y: 3, w: 24, h: 15}
        lens:
          type: line
          data_view: metrics-*
          dimensions:
            - field: '@timestamp'
              type: date_histogram
          metrics:
            - field: system.memory.used.bytes
              aggregation: average
              label: Memory Used
              format: bytes

      - title: Garbage Collection Activity
        grid: {x: 0, y: 18, w: 48, h: 15}
        lens:
          type: line
          data_view: metrics-*
          dimensions:
            - field: '@timestamp'
              type: date_histogram
          metrics:
            - field: golang.heap.gc.next_gc_limit
              aggregation: average
              label: GC Limit
            - field: golang.heap.gc.total_count
              aggregation: sum
              label: GC Count
```

---

## Checklist

Use this checklist when creating or reviewing dashboards:

### Structure
- [ ] Title follows `[Category Package] Focus` format
- [ ] Description added when title needs context
- [ ] Panels follow top-to-bottom hierarchy (context → control → summary → analysis → detail)
- [ ] Markdown navigation at top (if multi-dashboard)
- [ ] Data tables positioned at bottom

### Visualizations
- [ ] Visualization types match data characteristics (not aesthetic preference)
- [ ] Area charts used for time-series event counts
- [ ] Line charts used for precise metrics
- [ ] Pie/donut charts used for categorical proportions
- [ ] Data tables used for drill-down details
- [ ] Metric cards used sparingly (0-6 per dashboard)

### Naming
- [ ] Panel titles are concise and descriptive
- [ ] No redundant prefixes ("Chart of", "Graph of")
- [ ] Field labels are human-readable

### Layout
- [ ] Panels use standard widths (12, 16, 24, or 48 columns)
- [ ] Related visualizations grouped together
- [ ] No panels narrower than 12 columns
- [ ] Charts have appropriate heights (12-15 grid units minimum)

### Filters and Controls
- [ ] Global filter for `data_stream.dataset`
- [ ] Controls used only when needed (multi-tenant/multi-system)
- [ ] Panel-level filters are specific and purposeful
- [ ] KQL syntax used consistently

### Accessibility
- [ ] Legend positioning doesn't obscure data
- [ ] Number formatting appropriate for data type
- [ ] Time range configured appropriately
- [ ] Cursor synchronization enabled for time-series

### Testing
- [ ] Dashboard tested at different time ranges
- [ ] All filters work correctly
- [ ] Tables paginate properly (10 rows default)
- [ ] No errors in browser console

---

## Common Mistakes to Avoid

### Structural Issues

❌ **Wrong:** Placing tables in the middle of the dashboard
✅ **Right:** Always position tables at the bottom

❌ **Wrong:** Too many metric cards (10+)
✅ **Right:** Use 0-6 metric cards, focus on visualizations

❌ **Wrong:** No navigation for multi-dashboard packages
✅ **Right:** Add markdown panel with links to related dashboards

### Visualization Choices

❌ **Wrong:** Line charts for event counts
✅ **Right:** Area charts for event counts (visual weight)

❌ **Wrong:** Pie charts with 20+ categories
✅ **Right:** Show top 5-10 categories only

❌ **Wrong:** Vertical bar charts with long labels
✅ **Right:** Horizontal bar charts for long labels (URLs, usernames)

### Naming Issues

❌ **Wrong:** "Chart showing the number of requests over time"
✅ **Right:** "Requests Over Time"

❌ **Wrong:** "data.field.name.value"
✅ **Right:** "Field Name" (human-readable label)

### Layout Problems

❌ **Wrong:** Panels with widths like 13, 19, 27
✅ **Right:** Use standard widths: 12, 16, 24, 48 columns

❌ **Wrong:** Random panel placement
✅ **Right:** Follow vertical flow hierarchy

---

## Additional Resources

### Related Documentation
- [Dashboard Decompiling Guide](dashboard-decompiling-guide.md) - Converting Kibana JSON to YAML
- [Panel Types Documentation](panels/base.md) - Detailed panel configuration
- [Controls Documentation](controls/config.md) - Dashboard control configuration
- [Filters Documentation](filters/config.md) - Filter and query configuration

### Analysis Reference
- [Dashboard Pattern Analysis](../dashboard-pattern-analysis.md) - Detailed analysis of Elastic dashboards

### External Resources
- [Kibana Lens Documentation](https://www.elastic.co/guide/en/kibana/current/lens.html)
- [Elastic Common Schema (ECS)](https://www.elastic.co/guide/en/ecs/current/index.html)
- [Kibana Query Language (KQL)](https://www.elastic.co/guide/en/kibana/current/kuery-query.html)

---

## Changelog

### Version 1.0 (2026-01-08)
- Initial release based on analysis of 7 Elastic integration dashboards
- Documented visualization selection patterns
- Established naming conventions
- Created dashboard templates
- Added checklist and common mistakes section
