# CrowdStrike Modern Dashboards

Modern, workflow-centric security operations dashboards for CrowdStrike EDR data streams.

## Overview

This directory contains 4 workflow-centric dashboards designed for modern security operations workflows, replacing the traditional dataset-centric approach with a user-focused, task-oriented design.

### Design Philosophy

**Workflow-Centric vs Dataset-Centric:**

- **Traditional Approach** (existing `crowdstrike/` dashboards): Organized by data source (Alert, Falcon, FDR, Host, Vulnerability) - 6 dashboards
- **Modern Approach** (these dashboards): Organized by security workflow and user task - 4 dashboards

**Key Improvements:**

1. **Progressive Disclosure Pattern**: Context → Controls → Summary → Analysis → Detail
2. **Unified Navigation**: All dashboards link to each other via horizontal links panel
3. **Control Filters**: Multi-tenant filtering for host, user, severity, and other dimensions
4. **Minimal Metrics**: 4 total metrics across SOC dashboard only (not repeated elsewhere)
5. **Heavy Categorization**: 16 donut charts for proportional breakdowns
6. **Trend Analysis**: 4 area charts showing time-series patterns
7. **Detail Drill-Down**: 9 horizontal bar charts for "Top N" analysis

## Dashboards

### 1. Security Operations Center (SOC)
**File:** `soc.yaml`
**Dashboard ID:** `crowdstrike-modern-soc-7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d`
**Panels:** 12 (Standard complexity)

**Purpose:** Real-time security event monitoring, alert triage, and incident response coordination.

**Data Sources:** `crowdstrike.alert`, `crowdstrike.falcon`, `crowdstrike.fdr`

**Controls:**
- Host (multi-select)
- User (multi-select)
- Severity (multi-select)

**Key Features:**
- 4 metric cards showing Total Events, Critical Alerts, Active Threats, Affected Hosts
- Security Events Over Time area chart with event category breakdown
- 4 donut charts: Alert Status, Severity Distribution, Event Categories, Platform Distribution
- 2 horizontal bar charts: Top Affected Hosts, Top Users

**Use Cases:**
- Daily security operations monitoring
- Alert triage and prioritization
- Incident detection and initial response
- Multi-tenant SOC operations

---

### 2. Threat Investigation
**File:** `threat-investigation.yaml`
**Dashboard ID:** `crowdstrike-modern-investigation-8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e`
**Panels:** 12 (Standard complexity)

**Purpose:** Deep-dive threat analysis, MITRE ATT&CK mapping, IOC tracking, and threat actor behavior analysis.

**Data Sources:** `crowdstrike.alert`, `crowdstrike.falcon`

**Controls:**
- Threat Technique (multi-select)
- Threat Tactic (multi-select)
- Severity (multi-select)

**Key Features:**
- Threat Detections Over Time area chart with severity breakdown
- 6 donut charts: MITRE Techniques, MITRE Tactics, Severity, IOC Sources, IOC Types, Event Actions
- 4 horizontal bar charts: Top Source IPs, Source Domains, Compromised Hosts, Targeted Files

**Use Cases:**
- Threat hunting and investigation
- MITRE ATT&CK technique mapping
- IOC analysis and tracking
- Threat actor behavior profiling
- Incident investigation and forensics

---

### 3. Asset & Vulnerability Management
**File:** `asset-vulnerability.yaml`
**Dashboard ID:** `crowdstrike-modern-assets-9c0d1e2f-3a4b-5c6d-7e8f-9a0b1c2d3e4f`
**Panels:** 10 (Standard complexity)

**Purpose:** Asset inventory, vulnerability tracking, risk assessment, and patch prioritization.

**Data Sources:** `crowdstrike.host`, `crowdstrike.vulnerability`

**Controls:**
- Vulnerability Severity (multi-select)
- Vulnerability Status (multi-select)
- OS Platform (multi-select)

**Key Features:**
- Vulnerability Detections Over Time area chart with severity breakdown
- 4 donut charts: Severity Distribution, Status, Confidence, Platform Distribution
- 4 horizontal bar charts: Top CVEs, Most Vulnerable Hosts, OS Versions, Host IPs

**Use Cases:**
- Vulnerability management and tracking
- Patch prioritization by severity
- Asset inventory and OS version tracking
- Risk assessment and reporting
- Compliance vulnerability scanning

---

### 4. Compliance & Audit
**File:** `compliance-audit.yaml`
**Dashboard ID:** `crowdstrike-modern-compliance-0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5a`
**Panels:** 12 (Standard complexity)

**Purpose:** Compliance monitoring, audit trail analysis, user activity tracking, and regulatory reporting.

**Data Sources:** `crowdstrike.alert`, `crowdstrike.falcon`, `crowdstrike.fdr`

**Controls:**
- Event Action (multi-select)
- Event Category (multi-select)
- User (multi-select)

**Key Features:**
- Security Audit Events Over Time area chart with event kind breakdown
- 6 donut charts: Event Categories, Event Kinds, FDR Categories, Alert Status, Falcon Status, Platform Coverage
- 4 horizontal bar charts: Top Event Actions, Top Users, Most Active Hosts, Top Devices

**Use Cases:**
- Compliance reporting (SOC 2, ISO 27001, PCI DSS)
- Audit trail analysis and review
- User activity monitoring and anomaly detection
- Access pattern analysis
- Regulatory compliance verification

---

## Dashboard Structure

All dashboards follow the same 5-layer structure as defined in the [Dashboard Style Guide](../../../docs/dashboard-style-guide.md):

### 1. Context Layer (y: 0)
- **Navigation Panel**: Horizontal links to all 4 dashboards
- Full width (48 columns), minimal height (4 grid units)

**Navigation Panel Example:**
```yaml
- title: Dashboard Navigation
  grid:
    x: 0
    y: 0
    w: 48
    h: 4
  links:
    layout: horizontal
    items:
      - label: SOC Dashboard
        dashboard: crowdstrike-modern-soc-...
      - label: Threat Investigation
        dashboard: crowdstrike-modern-investigation-...
```

### 2. Control Layer (Immediately after navigation)
- **Control Filters**: Dashboard-specific filters for multi-dimensional analysis
- 3 controls per dashboard (2 medium width, 1 small width)
- Positioned at top after navigation

### 3. Summary Layer (SOC only)
- **Metric Cards**: 4 key performance indicators
- 12 columns each, horizontal layout
- Only SOC dashboard includes metrics (other dashboards emphasize analysis over summary)

### 4. Analysis Layer
- **Time Series Charts**: 1 area chart per dashboard showing events over time with breakdowns
- **Donut Charts**: 4-6 categorical breakdowns (appearance: donut medium, 12-16 column width)
- **Proportional Analysis**: Top 5-10 categories for each dimension

### 5. Detail Layer (Bottom)
- **Horizontal Bar Charts**: "Top 10" analyses for drill-down investigation
- 24-column width, 15 grid unit height
- Long labels (hostnames, users, CVEs, domains) displayed horizontally

---

## Grid Layout

All dashboards use the **48-column grid system** with standard widths:

| Panel Type | Width | Height | Use Case |
|------------|-------|--------|----------|
| Navigation Links | 48 cols | 4 units | Full-width navigation |
| Metric Cards | 12 cols | 8 units | Individual KPIs (SOC only) |
| Donut Charts | 12-16 cols | 15 units | Categorical breakdowns |
| Area Charts | 48 cols | 15 units | Time series with breakdowns |
| Horizontal Bars | 24 cols | 15 units | "Top N" rankings |

**Layout Validation:**
- No overlapping panels (x + w ≤ 48)
- Vertical flow with no gaps
- Panels align to standard column widths

---

## Field Reference

### Common Fields (All Dashboards)
```yaml
@timestamp                    # Event timestamp
event.action                  # Specific action taken
event.category                # ECS event category
event.kind                    # ECS event kind
host.name                     # Hostname
host.hostname                 # Alternative hostname field
host.ip                       # Host IP address
host.os.platform              # OS platform (Windows, Linux, macOS)
host.os.full                  # Full OS version string
user.name                     # Username
device.id                     # CrowdStrike device ID
data_stream.dataset           # Dataset filter
```

### Alert Dataset (`crowdstrike.alert`)
```yaml
crowdstrike.alert.status      # Alert status (new, in_progress, closed)
crowdstrike.alert.severity    # Severity level (critical, high, medium, low)
crowdstrike.alert.confidence  # Detection confidence
crowdstrike.alert.ioc_source  # IOC source
crowdstrike.alert.ioc_type    # IOC type
source.ip                     # Source IP address
source.domain                 # Source domain
destination.domain            # Destination domain
```

### Falcon Dataset (`crowdstrike.falcon`)
```yaml
crowdstrike.event.Category    # Falcon event category
crowdstrike.event.SeverityName # Severity name
crowdstrike.event.Status      # Event status
threat.technique.name         # MITRE ATT&CK technique
threat.tactic.name            # MITRE ATT&CK tactic
```

### FDR Dataset (`crowdstrike.fdr`)
```yaml
event.kind                    # Event kind
file.name                     # File name
crowdstrike.event.Category    # FDR event category
```

### Vulnerability Dataset (`crowdstrike.vulnerability`)
```yaml
vulnerability.id              # CVE identifier
vulnerability.severity        # CVSS severity
crowdstrike.vulnerability.status      # Remediation status
crowdstrike.vulnerability.confidence  # Detection confidence
```

### Host Dataset (`crowdstrike.host`)
```yaml
device.id                     # Device identifier
host.name                     # Hostname
host.os.platform              # OS platform
host.os.full                  # Full OS version
```

---

## Compilation

### Compile Individual Dashboard

```bash
# From project root
make compile

# From compiler directory
cd compiler
make compile
```

All dashboards in `compiler/inputs/crowdstrike-modern/` will be compiled to NDJSON format in `compiler/outputs/`.

### Output Files

Compiled dashboards are written to:
```
compiler/outputs/crowdstrike-modern-soc.ndjson
compiler/outputs/crowdstrike-modern-investigation.ndjson
compiler/outputs/crowdstrike-modern-assets.ndjson
compiler/outputs/crowdstrike-modern-compliance.ndjson
```

### Import to Kibana

**Option 1: Combine and import as single file**

```bash
# Combine all NDJSON files and import
cat compiler/outputs/crowdstrike-modern-*.ndjson > combined.ndjson
curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@combined.ndjson
```

**Option 2: Import each file separately**

```bash
# Import each dashboard file individually
for file in compiler/outputs/crowdstrike-modern-*.ndjson; do
  curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
    -H "kbn-xsrf: true" \
    --form file=@"$file"
done
```

**Option 3: Use Kibana UI**
1. Navigate to **Stack Management** → **Saved Objects**
2. Click **Import**
3. Select the NDJSON files
4. Click **Import**

---

## Comparison to Existing Dashboards

### Existing Dataset-Centric Dashboards (`compiler/inputs/crowdstrike/`)

| Dashboard | Panels | Focus | Data Source |
|-----------|--------|-------|-------------|
| Alert | 16 | Alert dataset analysis | crowdstrike.alert |
| Falcon Overview | 8 | Incident and event overview | crowdstrike.falcon |
| FDR Overview | 6 | Flight data recorder events | crowdstrike.fdr |
| Host | 5 | Host/device information | crowdstrike.host |
| Vulnerability | 7 | Vulnerability tracking | crowdstrike.vulnerability |
| Overview | 6 | General CrowdStrike overview | Multiple datasets |

**Total:** 6 dashboards, 48 panels

### Modern Workflow-Centric Dashboards (This Directory)

| Dashboard | Panels | Focus | Data Sources |
|-----------|--------|-------|--------------|
| SOC | 12 | Daily operations and triage | alert, falcon, fdr |
| Threat Investigation | 12 | Threat hunting and analysis | alert, falcon |
| Asset & Vulnerability | 10 | Asset and vuln management | host, vulnerability |
| Compliance & Audit | 12 | Compliance and audit trails | alert, falcon, fdr |

**Total:** 4 dashboards, 46 panels

### Key Differences

| Aspect | Existing | Modern |
|--------|----------|--------|
| **Organization** | By data source | By workflow |
| **Navigation** | Markdown with links | Links panels (horizontal) |
| **Controls** | None | 3 per dashboard |
| **Metrics** | Minimal | 4 (SOC only) |
| **Donut Charts** | 8 total | 16 total |
| **Time Charts** | Line/bar mix | Stacked area (consistent) |
| **Cross-Dataset** | Single dataset per dashboard | Multiple datasets per workflow |
| **Time Ranges** | Generic | Workflow-specific (24h, 7d, 30d, 90d) |
| **User Focus** | Data exploration | Task completion |

### When to Use Which

**Use Existing Dashboards When:**
- Deep-dive analysis of a specific data source
- Troubleshooting data ingestion issues
- Exploring all fields in a single dataset
- Dataset-specific testing and validation

**Use Modern Dashboards When:**
- Daily security operations workflows
- Incident investigation and response
- Compliance reporting and auditing
- Executive-level overview and KPIs
- Multi-tenant environments (using controls)
- Task-oriented security analysis

---

## Design Principles

These dashboards follow the [Dashboard Style Guide](../../../docs/dashboard-style-guide.md) best practices:

1. **Predictable Organization**: Same structure across all 4 dashboards
2. **Visualization Clarity**: Chart types match data characteristics
3. **Progressive Disclosure**: Context → Controls → Summary → Analysis → Detail
4. **Functional Minimalism**: Every panel serves a specific workflow purpose
5. **Consistent Conventions**: Standard naming, sizing, and positioning

### Visualization Distribution

| Visualization Type | Count | Usage Pattern |
|-------------------|-------|---------------|
| Links Panel | 4 | Navigation (1 per dashboard) |
| Metric Cards | 4 | Summary KPIs (SOC only) |
| Area Charts | 4 | Time series trends (1 per dashboard) |
| Donut Charts | 16 | Categorical breakdowns (4 per dashboard avg) |
| Horizontal Bar Charts | 18 | "Top N" details (4-5 per dashboard) |

**Total Panels:** 46 panels across 4 dashboards

---

## Customization

### Modifying Controls

To add or remove control filters, edit the `controls` section:

```yaml
controls:
  - type: options
    label: Your Filter Label
    width: medium  # small, medium, large
    data_view: logs-*
    field: field.name
    match_technique: contains  # exact, contains, prefix
```

### Adding Data Sources

To include additional CrowdStrike datasets, update the global filter:

```yaml
filters:
  - or:
      - field: data_stream.dataset
        equals: crowdstrike.alert
      - field: data_stream.dataset
        equals: crowdstrike.falcon
      - field: data_stream.dataset
        equals: crowdstrike.new_dataset
```

### Panel Customization

To modify visualization appearance:

```yaml
lens:
  type: pie  # or donut
  appearance:
    donut: medium  # small, medium, large
  dimensions:
    - field: your.field
      type: values
      size: 10  # Top N count
```

### Complete Minimal Dashboard Example

The following shows how all components integrate into a complete dashboard:

```yaml
---
dashboards:
  - id: crowdstrike-custom-minimal
    name: '[CrowdStrike] Minimal Dashboard'
    description: Minimal dashboard template showing core components
    filters:
      - field: data_stream.dataset
        equals: crowdstrike.alert
    controls:
      - type: options
        label: Severity
        width: medium
        data_view: logs-*
        field: crowdstrike.alert.severity
        match_technique: exact
    panels:
      - title: Alert Count
        grid:
          x: 0
          y: 0
          w: 12
          h: 8
        lens:
          type: metric
          data_view: logs-*
          metrics:
            - aggregation: count
              label: Total Alerts
      - title: Alerts by Severity
        grid:
          x: 12
          y: 0
          w: 12
          h: 15
        lens:
          type: pie
          data_view: logs-*
          appearance:
            donut: medium
          dimensions:
            - field: crowdstrike.alert.severity
              type: values
              size: 5
              sort:
                by: Count
                direction: desc
          metrics:
            - aggregation: count
              label: Count
```

This example demonstrates:
- Dashboard metadata (id, name, description)
- Global filters applied to all panels
- Interactive control filters for user selection
- Panel definitions with grid positioning
- Different visualization types (metric, pie chart)

### Complex Dashboard Example

The following shows advanced features including multi-dataset filtering, nested logical operators, breakdowns, and panel-specific filters:

```yaml
---
dashboards:
  - id: crowdstrike-complex-example
    name: '[CrowdStrike] Complex Dashboard'
    description: Complex dashboard demonstrating advanced features
    filters:
      - or:
          - field: data_stream.dataset
            equals: crowdstrike.alert
          - field: data_stream.dataset
            equals: crowdstrike.falcon
    controls:
      - type: options
        label: Host
        width: medium
        data_view: logs-*
        field: host.name
        match_technique: contains
      - type: options
        label: Severity
        width: small
        data_view: logs-*
        field: crowdstrike.alert.severity
        match_technique: exact
    panels:
      # Stacked area chart with breakdown dimension
      - title: Events Over Time by Severity
        grid:
          x: 0
          y: 0
          w: 48
          h: 15
        lens:
          type: area
          mode: stacked
          data_view: logs-*
          dimension:
            field: '@timestamp'
            type: date_histogram
            label: Time
          breakdown:
            field: crowdstrike.alert.severity
            type: values
            size: 5
            sort:
              by: Event Count
              direction: desc
            other_bucket: true
          metrics:
            - aggregation: count
              label: Event Count
      # Donut chart with other_bucket and panel-specific filter
      - title: Critical Alert Sources
        grid:
          x: 0
          y: 15
          w: 24
          h: 15
        lens:
          type: pie
          data_view: logs-*
          appearance:
            donut: medium
          dimensions:
            - field: source.ip
              type: values
              size: 10
              sort:
                by: Count
                direction: desc
              other_bucket: true
              missing_bucket: false
          metrics:
            - aggregation: count
              label: Count
          filters:
            - field: crowdstrike.alert.severity
              equals: critical
      # Horizontal bar chart with negation filter
      - title: Non-Alert Events by Action
        grid:
          x: 24
          y: 15
          w: 24
          h: 15
        lens:
          type: bar
          data_view: logs-*
          dimension:
            field: event.action
            type: values
            size: 10
            sort:
              by: Count
              direction: desc
          metrics:
            - aggregation: count
              label: Count
          filters:
            - not:
                field: event.kind
                equals: alert
```

This complex example demonstrates:
- **Multi-dataset filtering**: `or` operator to combine crowdstrike.alert and crowdstrike.falcon datasets
- **Stacked area chart**: Time series with `breakdown` dimension showing severity distribution over time
- **Other bucket**: Capturing values beyond top N in the "Other" category
- **Panel-specific filters**: Narrowing data for individual panels (e.g., critical alerts only)
- **Negation filters**: Using `not` operator to exclude alert events
- **Match techniques**: Using `contains` for flexible text matching in controls

### Configuration Options Reference

The following table provides a comprehensive reference for all configuration keys used in the examples above:

| YAML Key | Data Type | Description | Default | Required |
|----------|-----------|-------------|---------|----------|
| `controls[]` | array | List of interactive filter controls | `[]` | No |
| `controls[].type` | string | Control type (`options` for dropdown, `range` for slider) | - | Yes |
| `controls[].label` | string | Display label shown to users | - | Yes |
| `controls[].width` | string | Control width (`small`, `medium`, `large`) | `medium` | No |
| `controls[].data_view` | string | Data view pattern to query (e.g., `logs-*`) | - | Yes |
| `controls[].field` | string | Field name to filter on | - | Yes |
| `controls[].match_technique` | string | Match type (`exact`, `contains`, `prefix`) | `exact` | No |
| `filters[]` | array | Dashboard-level filters applied to all panels | `[]` | No |
| `filters[].field` | string | Field name to filter | - | Yes |
| `filters[].equals` | string | Value to match | - | Yes (unless using `or`/`and`) |
| `filters[].or` | array | Logical OR of multiple filter conditions | - | No |
| `filters[].and` | array | Logical AND of multiple filter conditions | - | No |
| `filters[].not` | object | Negation of a filter condition | - | No |
| `lens` | object | Lens visualization configuration | - | Yes (for panels) |
| `lens.type` | string | Visualization type (`pie`, `bar`, `line`, `metric`, `area`) | - | Yes |
| `lens.mode` | string | Chart mode (e.g., `stacked` for bar/area charts) | varies | No |
| `lens.data_view` | string | Data view pattern (e.g., `logs-*`) | - | Yes |
| `lens.appearance` | object | Visual styling options | - | No |
| `lens.appearance.donut` | string | Donut size for pie charts (`small`, `medium`, `large`) | - | No |
| `lens.dimensions[]` | array | Chart dimensions (x-axis, categories) | - | Yes (except metric) |
| `lens.dimensions[].field` | string | Field name for dimension | - | Yes |
| `lens.dimensions[].type` | string | Dimension type (`values`, `date_histogram`, `range`) | - | Yes |
| `lens.dimensions[].size` | integer | Maximum number of values to show (for `values` type) | `5` | No |
| `lens.dimensions[].label` | string | Custom label for dimension | field name | No |
| `lens.dimensions[].sort` | object | Sort configuration | - | No |
| `lens.dimensions[].sort.by` | string | Field or metric to sort by | - | Yes (if sort used) |
| `lens.dimensions[].sort.direction` | string | Sort direction (`asc`, `desc`) | `desc` | No |
| `lens.dimensions[].other_bucket` | boolean | Include "Other" bucket for remaining values | `false` | No |
| `lens.dimensions[].missing_bucket` | boolean | Include bucket for missing values | `false` | No |
| `lens.breakdown` | object | Breakdown dimension for stacked/multi-series charts | - | No |
| `lens.breakdown.field` | string | Field name for breakdown | - | Yes (if breakdown used) |
| `lens.breakdown.type` | string | Breakdown type (`values`) | - | Yes (if breakdown used) |
| `lens.breakdown.size` | integer | Maximum number of breakdown values | `5` | No |
| `lens.metrics[]` | array | Metric calculations (y-axis, values) | - | Yes |
| `lens.metrics[].aggregation` | string | Aggregation type (`count`, `sum`, `avg`, `max`, `min`, etc.) | - | Yes |
| `lens.metrics[].label` | string | Custom label for metric | aggregation name | No |
| `lens.metrics[].field` | string | Field name (required for aggregations other than `count`) | - | Conditional |
| `lens.filters[]` | array | Panel-specific filters (in addition to dashboard filters) | `[]` | No |

**Notes:**
- All filter keys (`filters[].field`, `filters[].equals`, etc.) also apply to `lens.filters[]` for panel-specific filtering
- For `controls[]`, the `match_technique` determines how the filter matches: `exact` for exact equality, `contains` for substring match, `prefix` for starts-with match
- Dashboard-level `filters[]` apply to all panels; panel-level `lens.filters[]` apply only to that panel
- The `or` and `and` filter operators allow combining multiple conditions; each contains an array of filter objects

---

## References

### Internal Documentation
- [Dashboard Style Guide](../../../docs/dashboard-style-guide.md) - Design principles and patterns
- [Controls Configuration](../../../docs/controls/config.md) - Control filter syntax
- [Lens Panel Configuration](../../../docs/panels/lens.md) - Chart configuration options
- [Filters Documentation](../../../docs/filters/config.md) - Filter and query syntax

### External Resources
- [Elastic Common Schema (ECS)](https://www.elastic.co/guide/en/ecs/current/index.html) - Field reference
- [Kibana Lens Documentation](https://www.elastic.co/docs/explore-analyze/visualize/lens) - Visualization guide
- [CrowdStrike Integration](https://docs.elastic.co/integrations/crowdstrike) - Data source documentation
- [MITRE ATT&CK Framework](https://attack.mitre.org/) - Threat technique reference

---

## Support

For issues, questions, or contributions:
- Review the [Contributing Guide](../../../CONTRIBUTING.md)
- Check the [Architecture Documentation](../../../docs/architecture.md)
- Open an issue on GitHub

---

**Version:** 1.0
**Last Updated:** 2026-01-09
**Dashboard Complexity:** Standard (7-12 panels per dashboard)
**Total Dashboards:** 4
**Total Panels:** 46
