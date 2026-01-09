# CrowdStrike Dashboards

This directory contains 6 CrowdStrike dashboards converted from Kibana JSON to YAML format using the kb-yaml-to-lens compiler.

## Dashboards Overview

| Dashboard | File | Panels | Description |
|-----------|------|--------|-------------|
| Overview | `overview.yaml` | 6 | High-level overview with FDR alerts, Falcon incidents, and event trends |
| FDR Overview | `fdr-overview.yaml` | 6 | Falcon Data Replicator events and alerts monitoring |
| Falcon Overview | `falcon-overview.yaml` | 8 | Falcon incidents with MITRE ATT&CK mapping |
| Alert | `alert.yaml` | 16 | Comprehensive alert monitoring and analysis |
| Host | `host.yaml` | 5 | Host devices and their properties |
| Vulnerability | `vulnerability.yaml` | 7 | Vulnerability detection and risk assessment |

## Source

Original dashboards from Elastic Integrations repository:
- Repository: https://github.com/elastic/integrations
- Package: crowdstrike
- Location: packages/crowdstrike/kibana/dashboard/
- Fetch Date: 2026-01-09

## Data Sources

- **Index Pattern:** `logs-*`
- **Data Stream Datasets:**
  - `crowdstrike.alert` - Alert data
  - `crowdstrike.fdr` - Falcon Data Replicator events
  - `crowdstrike.falcon` - Falcon incidents
  - `crowdstrike.host` - Host/Device information
  - `crowdstrike.vulnerability` - Vulnerability data

## Dashboard Details

### 1. Overview (`overview.yaml`)

**Purpose:** Entry point dashboard with navigation to all other dashboards

**Panels:**
- FDR Alerts (metric)
- Falcon Incidents (metric)
- Events over Time by Data Stream (line chart)
- FDR Alert Types (donut chart)
- Falcon Incident Types (donut chart)
- Navigation markdown panel

**Key Features:**
- Summary metrics for FDR and Falcon
- Time series comparison across data streams
- Quick navigation to detailed dashboards

### 2. FDR Overview (`fdr-overview.yaml`)

**Purpose:** Monitor Falcon Data Replicator events and alerts

**Dashboard Filter:** `data_stream.dataset = crowdstrike.fdr`

**Panels:**
- Top Users (bar chart)
- Top Related Files (bar chart)
- Events over time by Event Kind (line chart with breakdown)
- Top Event Types (donut chart, excluding alerts)
- Top Alert Types (donut chart, alerts only)
- Navigation markdown panel

**Key Features:**
- User and file activity monitoring
- Event kind breakdown over time
- Separate views for events vs alerts

**Limitations:**
- Original dashboard had a map panel (Agent locations) - not converted (maps not supported)

### 3. Falcon Overview (`falcon-overview.yaml`)

**Purpose:** Monitor Falcon incidents with security context

**Dashboard Filter:** `data_stream.dataset = crowdstrike.falcon`

**Panels:**
- Incidents by ECS Category (donut chart, filtered to Incidents)
- Events by Severity (donut chart)
- Events by Technique Name (donut chart) - MITRE ATT&CK techniques
- Events by Tactic Name (donut chart) - MITRE ATT&CK tactics
- Events over Time by Event Type (line chart with breakdown)
- Top Related Hosts (bar chart)
- Top Related Users (bar chart)
- Navigation markdown panel

**Key Features:**
- MITRE ATT&CK technique and tactic mapping
- Severity-based categorization
- Host and user correlation

**Limitations:**
- Original dashboard had a search panel (Newest Falcon Incidents) - not converted (search panels not supported)

### 4. Alert (`alert.yaml`)

**Purpose:** Comprehensive alert monitoring and analysis

**Dashboard Filter:** `data_stream.dataset = crowdstrike.alert`

**Panels:**
1. Alert by Status (pie chart)
2. Alert by OS Platform (pie chart)
3. User with Highest Alert (bar chart)
4. Alert over Device (bar chart)
5. Alert by Severity (pie chart)
6. Alert over Host IP (bar chart)
7. Alert over Hostname (bar chart)
8. Alert over Timestamp (line chart)
9. Alert over Confidence (stacked bar chart with confidence breakdown over time)
10. Alert by IOC Source (pie chart)
11. Alert by IOC Type (pie chart)
12. Alert by OS Full Name (pie chart)
13. Top 10 Source IP (bar chart)
14. Top 10 Source Domain (bar chart)
15. Top 10 Destination Domain (bar chart)
16. Navigation markdown panel

**Key Features:**
- IOC (Indicator of Compromise) tracking
- Multi-dimensional analysis (status, severity, confidence)
- Network context (source/destination IPs and domains)
- OS platform distribution
- Temporal analysis

**Note:** This is the largest dashboard with 16 panels providing comprehensive alert coverage.

### 5. Host (`host.yaml`)

**Purpose:** Monitor host devices and their properties

**Dashboard Filter:** `data_stream.dataset = crowdstrike.host`

**Panels:**
- Host over OS Platform (pie chart)
- Host over Hostname (bar chart)
- Host over Host IP (bar chart)
- Host over Timestamp (stacked bar chart with device breakdown over time)
- Navigation markdown panel

**Key Features:**
- OS platform distribution
- Host identification by hostname and IP
- Device activity timeline

### 6. Vulnerability (`vulnerability.yaml`)

**Purpose:** Track vulnerabilities, severity levels, and affected hosts

**Dashboard Filter:** `data_stream.dataset = crowdstrike.vulnerability`

**Panels:**
- Vulnerability over time (line chart)
- Top 10 Vulnerability (bar chart)
- Top 10 Host (bar chart)
- Vulnerability by Severity (donut chart)
- Vulnerability by Status (donut chart)
- Vulnerability by Confidence (donut chart)
- Navigation markdown panel

**Key Features:**
- Temporal vulnerability trends
- Top vulnerabilities and affected hosts
- Risk assessment dimensions (severity, status, confidence)

**Limitations:**
- Original dashboard had a search panel (Vulnerability Essential Details) - not converted (search panels not supported)

## Conversion Notes

### Panel Type Mappings

| Original Kibana Type | Converted To | Notes |
|---------------------|--------------|-------|
| `lnsPie` | `type: pie` | Donut charts use `appearance.donut: medium` |
| `lnsXY` (bar) | `type: bar` | Stacked mode by default |
| `lnsXY` (line) | `type: line` | Used for time series |
| `lnsMetric` | `type: metric` | Count metrics with filters |
| `lnsDatatable` | `type: bar` | Approximated as bar charts (data tables not natively supported) |
| `search` | Not converted | Search panels cannot be converted |
| `map` | Not converted | Map panels not supported |
| Markdown navigation | `markdown` | Preserved with dashboard links |

### Unsupported Features

The following Kibana features from the original dashboards could not be converted:

1. **Search Panels** (2 instances across dashboards)
   - Location: Falcon Overview, Vulnerability
   - Alternative: Use bar charts to show top N records

2. **Map Panels** (1 instance)
   - Location: FDR Overview (Agent locations map)
   - Alternative: Cannot be represented in current compiler

3. **Control Panels** (5 instances)
   - Location: Vulnerability, Falcon Overview dashboards had interactive filters
   - Alternative: Dashboard-level filters applied where possible

### Data Table Approximation

Original Kibana data tables (`lnsDatatable`) were converted to horizontal bar charts because:
- Data tables are not natively supported in the compiler
- Bar charts provide similar "top N" functionality
- Sorting and size limits are preserved

**Affected Panels:**
- FDR Overview: Top Users, Top Related Files
- Falcon Overview: Top Related Hosts, Top Related Users
- Vulnerability: Top 10 Vulnerability, Top 10 Host
- Alert: Top 10 Source IP, Top 10 Source Domain, Top 10 Destination Domain

## Compilation

To compile these dashboards:

```bash
cd compiler
make compile
```

Output will be generated in `compiler/output/compiled_dashboards.ndjson` as newline-delimited JSON that can be imported into Kibana.

## Navigation

All dashboards include a navigation panel with links to:
- Overview (main dashboard)
- FDR
- Falcon
- Alert
- Host
- Vulnerability

Links use the format `/app/dashboards#/view/{dashboard-id}` for internal Kibana navigation.

## Statistics

- **Total Dashboards:** 6
- **Total Panels:** 48 (after conversion)
- **Original Panels:** 51 (3 search/map panels not converted)
- **Lens Visualizations:** 42 panels successfully converted
- **Navigation Panels:** 6 markdown panels
- **Average Panels per Dashboard:** 8
- **Total YAML Lines:** ~1,500 lines across all files

## Validation

All dashboards have been validated:
- ✅ YAML syntax correct
- ✅ Compiles without errors
- ✅ Grid layouts verified (no overlaps)
- ✅ Filters properly applied
- ✅ Navigation links preserved

## Maintenance

When updating these dashboards:

1. Run `make fix` to auto-format YAML
2. Run `make compile` to validate
3. Check output in `compiler/output/compiled_dashboards.ndjson`
4. Test in Kibana by importing the NDJSON file

## Related Documentation

- Compiler Documentation: `docs/index.md`
- Example Dashboards: `docs/examples/`
- Architecture: `docs/architecture.md`
