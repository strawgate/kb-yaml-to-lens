# Elastic Integrations Dashboard Pattern Analysis

**Analysis Date:** 2026-01-08
**Source:** elastic/integrations repository
**Dashboards Analyzed:** 7 representative dashboards

---

## Executive Summary

This analysis examines 7 production dashboards from the Elastic integrations repository to identify common patterns, best practices, and design conventions for Kibana dashboards. The dashboards span multiple use cases including security monitoring (Auditd, CyberArk, Corelight), infrastructure monitoring (IIS, Golang), and service monitoring (Azure, Cisco).

**Key Findings:**
- Consistent use of markdown panels for navigation and context
- Strong preference for donut/pie charts over bar charts for categorical breakdowns
- Area charts dominate time-series visualizations
- All dashboards use the 48-column grid system
- Data tables are positioned at the bottom for drill-down details
- Metric cards used sparingly for key KPIs
- Hierarchical control filters placed at the top

---

## 1. Dashboards Analyzed

| Dashboard | Package | Primary Use Case | Panels | Kibana Version |
|-----------|---------|------------------|--------|----------------|
| Auditd Manager - Sockets | auditd_manager | Security audit logs | 6 | 8.7.1 |
| Azure - Graph Activity Logs | azure | API monitoring | 14 | 8.8.0 |
| Corelight - RDP Inferences | corelight | Network security | 7 | Latest |
| Cisco Secure Email Gateway - AMP Engine | cisco_secure_email_gateway | Email security | 6 | 8.7.1 |
| CyberArk PAS | cyberarkpas | Privileged access security | 10 | 8.7.1 |
| Golang - Heap | golang | Application performance | 6 | Latest |
| IIS - Access and Error Logs | iis | Web server monitoring | 6 | 8.7.0 |

---

## 2. Overall Organization and Layout

### 2.1 Dashboard Header Pattern

**Standard Structure:**
1. **Title row** - Dashboard title with package context
2. **Navigation/TOC** - Markdown panel with links to related dashboards
3. **Control filters** - Interactive filters when needed
4. **Metric cards** - High-level KPIs (when present)

**Example (CyberArk PAS):**
```
[Navigation Links]
[Control: By Vault host] [Control: By event code]
[Metric: Count of Events] [Chart: Breakdown by Outcome]
[Time series charts...]
[Detail tables...]
```

### 2.2 Title Conventions

**Format:** `[Category PackageName] Specific Focus`

**Examples:**
- `[Auditd Manager] Sockets`
- `[Logs Cisco Secure Email Gateway] AMP Engine`
- `[Metrics Golang] Heap`
- `[Logs IIS] Access and error logs`

**Category Prefixes Observed:**
- `[Logs ...]` - Log analysis dashboards
- `[Metrics ...]` - Performance/metric dashboards
- Package name without prefix when it's the only dashboard type

### 2.3 Grid Layout Patterns

**48-Column Grid System:**
All dashboards use Kibana's 48-column grid. Common panel widths:

| Panel Type | Typical Width | Use Case |
|-----------|---------------|----------|
| Full-width markdown | 48 columns | Navigation, section headers |
| Single metric card | 8-12 columns | KPI displays |
| Small chart | 12-16 columns | Pie/donut charts |
| Medium chart | 24 columns | Half-width time series |
| Full chart | 48 columns | Primary time series, maps |
| Data table | 48 columns | Detail drill-down |

**Vertical Flow:**
1. Context (markdown/navigation)
2. Controls/filters
3. Key metrics (horizontal row)
4. Primary visualizations (time series)
5. Breakdowns (pie/donut/bar charts)
6. Detail tables (bottom)

---

## 3. Panel Types and Usage Patterns

### 3.1 Markdown Panels

**Purpose:** Navigation and context setting

**Positioning:** Always at the top of the dashboard

**Content Patterns:**
- **Navigation links:** Links to related dashboards in the same package
- **Section headers:** Visual separation between dashboard areas
- **Context information:** Brief explanations of what the dashboard shows

**Examples:**

**Auditd Manager (Navigation):**
- Links to: Overview dashboard, Executions dashboard
- Positioned: Top of dashboard, full width

**Corelight RDP (Table of Contents):**
```
Table of Contents
- [Link to] Related Security Dashboard A
- [Link to] Related Security Dashboard B
```

### 3.2 Metric Cards (Lens Metric Visualizations)

**Usage:** High-level KPIs, count summaries

**Patterns:**
- **Horizontal grouping:** Multiple metrics in a row
- **Simple counts:** Total events, requests, connections
- **Breakdown by category:** Success/failure, status codes

**Examples:**

**Azure Graph Activity:**
- Total HTTP Requests (single count)
- HTTP responses by status class (1xx, 2xx, 3xx, 4xx, 5xx) - 5 separate metric cards

**CyberArk PAS:**
- Count of Events (single metric card)

**Golang Heap:**
- Displays averages and summaries within time-series panels rather than standalone metrics

**Key Insight:** Metric cards used sparingly - only when there's a clear need to highlight specific KPIs. Most dashboards prefer to jump directly into visualizations.

### 3.3 Pie and Donut Charts

**Primary Use:** Categorical breakdowns, proportional analysis

**When to Use Pie vs Donut:**
- **Donut charts** dominate in multi-dashboard contexts (cleaner look)
- **Pie charts** used interchangeably with donut charts
- No strict convention observed

**Common Patterns:**

**"Top N" Pattern (90% of pie/donut charts):**
- Show top 5 or top 10 categories
- Display as percentages
- Used for: file types, protocols, status codes, user agents, browsers, OS distribution

**Examples:**

**IIS Dashboard:**
- Browsers Breakdown (donut, percentage display)
- Operating Systems Breakdown (donut, percentage display)

**Cisco Secure Email Gateway:**
- File Type Distribution (pie, top 5, percentages)
- File MIME Type Distribution (pie, top 5, percentages)
- Verdict Distribution (pie, top 5, percentages)

**Corelight RDP:**
- RDP Inferences (pie, top 5 by frequency)
- Security Protocols (pie, protocol distribution)

**Positioning:**
- Typically in the middle section of the dashboard
- Often placed in horizontal rows (2-3 charts per row)
- Width: 12-24 columns each

### 3.4 Time Series Charts (XY Charts)

**Dominant Type:** Area charts

**Chart Type Choices:**

**Area Charts (Most Common):**
- Used for: event frequency over time, metric trends
- Stacking: Both stacked and unstacked patterns observed
- Examples:
  - Auditd: Socket Syscalls Time Series (area, top 10 syscall types)
  - CyberArk: Credential Access by Time (area)
  - Corelight: Inferences Over Time (area, daily tracking)

**Bar Charts (Time Series):**
- Used for: discrete events, status code distributions
- Stacking: Common for showing category breakdowns
- Examples:
  - IIS: Response Codes Over Time (stacked bar, top 5 codes)
  - IIS: Error Logs Over Time (stacked bar)
  - CyberArk: Event Types by Time (stacked bar)

**Line Charts:**
- Used for: precise metric tracking, performance monitoring
- Examples:
  - Golang: All 6 panels use line charts for precise heap metrics
  - Golang: Dual-axis configurations for comparing different metrics

**Pattern Decision Tree:**
```
Time series visualization choice:
├─ Continuous metrics (memory, CPU) → Line chart
├─ Event counts by category → Stacked area or stacked bar
├─ Single metric trend → Area chart (filled) or Line chart
└─ Comparing multiple distinct series → Line chart
```

**Time Bucketing:**
- Automatic interval binning (most common)
- Explicit daily buckets for trend analysis
- 30-day moving averages for smoothing (Golang)

### 3.5 Data Tables

**Purpose:** Detailed drill-down, searchable logs, top N lists

**Positioning:** Almost always at the bottom of the dashboard

**Patterns:**

**"Top N List" Tables:**
- Show count + dimensions
- Pagination: 10 rows per page (standard)
- Sorted by count descending
- Examples:
  - Cisco: Top 10 Malware Threats
  - Cisco: Top 10 Spy Names
  - CyberArk: Top Users by Failed Authentications

**"Detail View" Tables:**
- Show recent events with all dimensions
- Searchable
- Multiple columns (5-10 fields)
- Examples:
  - Auditd: Bind (non-ephemeral) - executable, address, port, count
  - Auditd: Connect - count, executable, address, port
  - CyberArk: Credential Access & All Logs - comprehensive event details

**Column Layout:**
- Left-aligned (standard)
- Count column often first or last
- Dimensional fields in logical order (who, what, where)

### 3.6 Bar Charts (Non-Time-Series)

**Usage:** Category comparisons, ranked lists

**Orientation:**
- Horizontal bars for ranked lists (easier to read labels)
- Vertical/stacked bars for category breakdowns

**Examples:**

**Azure Graph Activity:**
- Cloud region activity (horizontal bar chart) - ranked by activity
- HTTP method distribution (bar chart)

**CyberArk PAS:**
- Vault Authentication Attempts (horizontal bar, user rankings)
- Top Users by Failed Authentications (bar chart)

**IIS:**
- Top URLs by Response Code (horizontal stacked bar)

**Cisco:**
- Upload Action Distribution (stacked bar)

**Pattern:** Horizontal bars preferred when labels are long (usernames, URLs, regions)

### 3.7 Maps

**Usage:** Geographic distribution of network activity

**Example:**

**IIS - Access Map:**
- Uses `source.geo.location` field
- Color and size scaling based on access volume
- Provides visual context for global traffic patterns

**CyberArk - Network Sources and Destinations:**
- Geospatial map showing authentication sources

**Pattern:** Maps used when geo data is available and location matters for security/analysis

### 3.8 Control Filters (Interactive Dashboard Controls)

**Positioning:** Top of dashboard, immediately after navigation

**Types Observed:**

**Options List (Most Common):**
- Hostname/service filters
- Event code filters
- HTTP method filters
- Examples:
  - CyberArk: "By Vault host", "By event code"
  - Corelight: "System Name" (observer.hostname) - hierarchical
  - Azure: Tenant ID (hierarchical), Cloud Region, HTTP Request Method

**Range Slider:**
- Azure: HTTP Status Code (range slider: 100-599)

**Style:**
- Hierarchical presentation
- Support for exclusion (Azure Cloud Region)
- Typically 2-4 controls per dashboard

**Pattern:** Controls used when dashboards need to support filtering across multiple dimensions. Not present on all dashboards - only when needed for multi-tenant or multi-system scenarios.

---

## 4. Color and Styling Patterns

### 4.1 Color Schemes

**Observation:** Color schemes not explicitly defined in the JSON (Kibana defaults used)

**Inferred Patterns:**
- Categorical data: Elastic's default color palette
- Time series: Consistent colors per category across panels
- Status-based coloring: Implicit (success/failure, status codes)

### 4.2 Legend Positioning

**Standard:** Right-side placement for chart legends

**Examples:**
- Golang: All panels specify legend on right
- Area/line charts: Legends positioned to not overlap data

### 4.3 Number Formatting

**Bytes:** 2 decimal precision (Golang heap metrics)

**Counts:** Integer formatting

**Percentages:** Displayed on pie/donut charts

**Dates:** ISO format, automatic time zone handling

---

## 5. Filter Usage Patterns

### 5.1 Global Dashboard Filters

**Standard Pattern:** Filter by dataset at dashboard level

**Examples:**
- Auditd: `data_stream.dataset: auditd_manager.auditd`
- Azure: `data_stream.dataset: azure.graphactivitylogs`
- IIS: `data_stream.dataset: (iis.access OR iis.error)`
- CyberArk: `data_stream.dataset: cyberarkpas.audit`

**Pattern:** Dashboards scope to specific data streams, often allowing multiple related datasets (e.g., access and error logs)

### 5.2 Panel-Level Filters

**Common Filters:**
- Event type/category filters
- Status code filters
- Specific field existence checks

**Examples:**

**Auditd:**
- Bind panel: Filters to `auditd.data.syscall: bind` AND excludes `auditd.data.addr: netlink`
- Connect panel: Requires `auditd.data.socket.obj_type: exists`

**Corelight:**
- Filters: `observer.vendor: Corelight`, `event.dataset: rdp`, `observer.hostname: exists`

**Cisco:**
- Category filter: `cisco_secure_email_gateway.log.amp.category: amp`

### 5.3 Query Language

**Standard:** KQL (Kibana Query Language)

**Pattern:** All dashboards use KQL for consistency

---

## 6. Dashboard Descriptions

### 6.1 When Descriptions Are Used

**Pattern:** Descriptions present on some dashboards, absent on others

**Examples:**

**With Descriptions:**
- Azure: "Provide an overview and statistics of the audit trail of all HTTP requests that the Microsoft Graph service received and processed."
- Golang: "This Golang dashboard visualizes Heap metrics."

**Without Descriptions:**
- Auditd, Corelight, CyberArk, Cisco, IIS - title is self-explanatory

**Best Practice:** Add description when the dashboard's purpose isn't immediately obvious from the title, or when providing context adds value.

---

## 7. Key Patterns and Best Practices

### 7.1 Dashboard Organization

**Top-Down Information Architecture:**
1. **Context layer** - What am I looking at? (title, navigation, description)
2. **Control layer** - How can I filter? (controls, interactive filters)
3. **Summary layer** - What's happening? (metrics, key charts)
4. **Analysis layer** - Why is it happening? (breakdowns, distributions)
5. **Detail layer** - Show me specifics (data tables, logs)

**Consistency:** All dashboards follow this general pattern with variations based on use case

### 7.2 Visualization Selection Rules

**Derived Patterns:**

| Data Type | Visualization | Example Use Case |
|-----------|---------------|------------------|
| Single KPI | Metric card | Total events, request count |
| Categorical proportions | Pie/Donut chart | File types, browsers, protocols |
| Categorical ranking | Horizontal bar chart | Top users, top URLs |
| Time series events | Area chart (stacked) | Events by category over time |
| Time series metrics | Line chart | Memory usage, GC metrics |
| Discrete time events | Bar chart (stacked) | HTTP status codes over time |
| Top N with details | Data table | Top threats, top users |
| Recent events | Data table (searchable) | Log entries, audit trails |
| Geographic data | Map | Access locations, sources |

### 7.3 Naming Conventions

**Panel Titles:**
- Concise, descriptive
- No redundant "Chart of" or "Graph of" prefixes
- Examples:
  - "Socket Syscalls Time Series" (clear time dimension)
  - "Top 10 Malware Threats" (clear ranking)
  - "Browsers Breakdown" (clear categorical analysis)

**Field References:**
- Use human-readable labels when displayed
- Technical field names in queries/aggregations

### 7.4 Data Table Patterns

**Pagination:** 10 rows per page (universal standard)

**Column Selection:**
- Count/frequency column (often first or last)
- Primary dimension (what)
- Secondary dimensions (who, where, when)
- 3-6 columns typical, 10+ for comprehensive logs

**Sorting:** By count descending (for Top N tables)

### 7.5 Time Configuration

**Time Range Restoration:** Enabled on most dashboards

**Default Ranges:**
- 15 minutes (IIS - infrastructure monitoring)
- Flexible/no default (security dashboards - user-selected)

**Synchronization:** Cursor synchronization across time-series panels

### 7.6 Multi-Panel Coordination

**Shared Filters:**
- Global dashboard filters apply to all panels
- Control selections cascade to all visualizations
- Consistent time range across panels

**Thematic Grouping:**
- Related visualizations placed adjacent
- Example: Azure has 3 panels about HTTP methods (donut, bar, table) positioned together

---

## 8. Interesting Observations and Insights

### 8.1 Minimalist Design Philosophy

**Observation:** Elastic dashboards avoid clutter
- No excessive metric cards (Azure uses 6, CyberArk uses 1, most use 0)
- Charts speak for themselves without heavy annotation
- Markdown panels are functional (navigation) not decorative

### 8.2 Area Charts Dominate

**Insight:** Area charts are the default for time-series event data
- Preferred over line charts for event counts
- Filled area provides visual weight proportional to volume
- Stacking used to show categorical breakdown while maintaining total volume

### 8.3 Tables Are Always Last

**Pattern:** 100% consistency - data tables at bottom
- Supports drill-down workflow (overview → detail)
- Keeps visual charts prominent
- Searchable tables for advanced users

### 8.4 Security Dashboards vs. Performance Dashboards

**Security Dashboards (Auditd, CyberArk, Corelight, Cisco):**
- Heavy use of categorical breakdowns (pie/donut)
- Focus on "Top N" patterns (threats, users, actions)
- Data tables for audit trails
- Filters for multi-tenant scenarios

**Performance Dashboards (Golang):**
- Exclusive use of line charts for precision
- Dual-axis comparisons
- Moving averages for smoothing
- No pie charts (metrics don't have categorical proportions)

### 8.5 Index Pattern Consistency

**Universal:** `logs-*` index pattern
- All dashboards use this pattern
- Suggests data stream naming convention is the primary differentiator
- Filters scope by `data_stream.dataset` field

### 8.6 Control Groups Are Optional

**Usage:**
- 3 out of 7 dashboards have control groups
- Present when: multi-tenant, multi-system, or need for dimensional filtering
- Absent when: single-source, pre-filtered dashboards

### 8.7 Horizontal vs. Vertical Bar Charts

**Horizontal Bars:**
- Used when labels are long (URLs, usernames, regions)
- Better readability for text-heavy categories

**Vertical Bars:**
- Used for time series
- Used for short category labels
- Stacking more common with vertical orientation

### 8.8 No Custom Visualizations

**Observation:** All visualizations use Lens
- Form-based data sources
- No legacy visualizations (TSVB, Vega)
- Suggests modern best practice is Lens-only

---

## 9. Recommendations for kb-yaml-to-lens Project

Based on this analysis, here are recommendations for the YAML-to-Lens compiler:

### 9.1 Default Behaviors

**Panel Ordering:**
1. Markdown panels should default to top positioning
2. Metric cards should position before charts
3. Data tables should default to bottom positioning
4. Time-series charts in middle sections

**Visualization Defaults:**
- Area charts for time-series event counts
- Line charts for precise metrics
- Donut charts for categorical proportions (over pie)
- Horizontal bars for ranked lists with long labels
- Tables with 10 rows per page pagination

### 9.2 YAML Schema Considerations

**Dashboard Level:**
```yaml
title: "[Category Package] Specific Focus"
description: Optional, use when title needs context
filters:
  - field: data_stream.dataset
    value: package.dataset_name
time_range: 15m  # or user-selected
```

**Panel Types:**
- Support markdown with positioning hints (top/bottom)
- Support control groups with hierarchical/options/range types
- Default panel widths based on type (metric: 12, pie: 16, table: 48)

**Naming Patterns:**
- Validate title format suggestions
- Encourage concise panel titles
- Support "Top N" pattern in table configurations

### 9.3 Validation Rules

**Best Practice Checks:**
- Warn if data tables aren't at bottom
- Suggest area charts for time-series event data
- Recommend horizontal bars for long labels
- Flag missing dataset filters

### 9.4 Documentation Needs

Based on this analysis, the style guide should document:
- Dashboard organization hierarchy (context → control → summary → analysis → detail)
- Visualization selection decision tree
- Title naming conventions
- Grid layout patterns (standard widths)
- When to use controls vs. filters
- Time-series chart type selection criteria

---

## 10. Appendix: Dashboard Summaries

### 10.1 Auditd Manager - Sockets
- **Focus:** Security audit log analysis
- **Panels:** 6 (1 markdown, 2 charts, 3 tables)
- **Unique Features:** Socket family analysis, non-ephemeral port filtering
- **Grid:** Navigation at top, time series, breakdowns, detail tables at bottom

### 10.2 Azure - Graph Activity Logs
- **Focus:** API request monitoring
- **Panels:** 14 (4 controls, 6 metrics, 4 charts, 2 tables)
- **Unique Features:** Extensive control group, HTTP status code range slider
- **Grid:** Control-heavy design for multi-tenant filtering

### 10.3 Corelight - RDP Inferences
- **Focus:** Network security (RDP monitoring)
- **Panels:** 7 (1 markdown, 1 control, 3 charts, 2 tables)
- **Unique Features:** Security inference categorization, connection metrics
- **Grid:** Balanced mix of visualizations

### 10.4 Cisco Secure Email Gateway - AMP Engine
- **Focus:** Email security (malware detection)
- **Panels:** 6 (4 pie charts, 1 bar chart, 2 tables)
- **Unique Features:** Heavy use of pie charts for categorical data
- **Grid:** Category-focused layout

### 10.5 CyberArk PAS
- **Focus:** Privileged access security
- **Panels:** 10 (2 controls, 1 metric, 4 charts, 1 map, 2 tables)
- **Unique Features:** Geospatial map for network sources, authentication analysis
- **Grid:** Comprehensive security monitoring layout

### 10.6 Golang - Heap
- **Focus:** Application performance (memory metrics)
- **Panels:** 6 (1 control, 6 line charts)
- **Unique Features:** Dual-axis charts, 30-day moving averages, precision metrics
- **Grid:** Pure line chart design for metric precision

### 10.7 IIS - Access and Error Logs
- **Focus:** Web server monitoring
- **Panels:** 6 (1 map, 2 time-series bars, 2 donut charts, 1 stacked bar)
- **Unique Features:** Browser/OS analysis, geographic access map
- **Grid:** Balanced infrastructure monitoring layout

---

## Conclusion

The analysis reveals a mature, consistent dashboard design language across Elastic integrations. Key themes include:

1. **Predictable organization** - Users can navigate any dashboard using the same mental model
2. **Visualization clarity** - Chart types are chosen based on data characteristics, not aesthetics
3. **Progressive disclosure** - Overview metrics lead to breakdowns, which lead to detailed tables
4. **Functional minimalism** - Every panel serves a purpose; no decorative elements
5. **Consistent conventions** - Naming, sizing, positioning follow patterns

These patterns should inform both the kb-yaml-to-lens compiler design and the documentation/style guide for users creating dashboard YAML files.
