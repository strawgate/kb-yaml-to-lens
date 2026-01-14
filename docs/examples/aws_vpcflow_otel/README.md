# AWS VPC Flow Logs OTEL Dashboards

DevOps/SRE monitoring dashboards for AWS VPC Flow Logs collected via OpenTelemetry.

## Usage

```bash
# Compile to NDJSON
kb-dashboard compile --input-dir docs/examples/aws_vpcflow_otel --output-dir output

# Compile and upload to Kibana (requires credentials)
kb-dashboard compile --input-dir docs/examples/aws_vpcflow_otel --output-dir output --upload
```

**Note:** The `--upload` option requires `KIBANA_URL` and either `KIBANA_USERNAME`/`KIBANA_PASSWORD` or `KIBANA_API_KEY`. See [CLI Configuration](../../CLI.md#configuration).

## Data Requirements

- **Data View:** `logs-*`
- **Dataset:** `data_stream.dataset == "aws.vpcflow.otel"`
- **Required Fields:**
  - `@timestamp`, `aws.vpc.flow.action`, `aws.vpc.flow.bytes`, `aws.vpc.flow.packets`
  - `source.address`, `source.port`, `destination.address`, `destination.port`
  - `network.protocol.name`, `network.interface.name`, `cloud.account.id`

## Dashboards

All 3 dashboards are in a single YAML file with navigation links between them.

| Dashboard ID | Name | Panels | Controls |
|--------------|------|--------|----------|
| `aws-vpcflow-otel-overview` | VPC Flow Logs Overview | 10 | 3 |
| `aws-vpcflow-otel-traffic` | Traffic Analysis | 14 | 7 |
| `aws-vpcflow-otel-interface` | Interface Analysis | 7 | 3 |

### 1. VPC Flow Logs Overview

High-level KPIs and time-series trends for quick status assessment.

**Controls (3):** Cloud Account ID, Network Interface, Action

**Panels:**
- Navigation Links (links to all 3 dashboards)
- KPI Metrics (5 metrics + 1 header)
  - Total Flow Records, Rejection Rate, Total Bandwidth, Active Interfaces, Cloud Accounts
- Time-Series Trends (2 charts + 1 header)
  - Traffic Volume Over Time (stacked area - ACCEPT/REJECT)
  - Bandwidth Usage Over Time (line chart)

### 2. Traffic Analysis

Detailed traffic distribution, source analysis, and security deep dive.

**Controls (7):** Cloud Account ID, Network Interface, Action, Source IP, Destination IP, Source Port, Destination Port

**Panels:**
- Navigation Links
- Traffic Distribution (3 charts + 1 header)
  - Top Protocols (pie), Top Interfaces by Traffic (bar), Top Destination Ports (bar)
- Volume Change Detection (1 table + 1 header)
  - Significant Volume Changes by Source IP
- Source Analysis (1 table + 1 header)
  - Top Source IPs - Detailed
- Security Deep Dive (3 panels + 1 header)
  - Rejected Traffic by Protocol (bar), Top Rejected Ports (bar), Detailed Rejection Logs (table)

### 3. Interface Analysis

Per-interface and per-account metrics for infrastructure analysis.

**Controls (3):** Cloud Account ID, Network Interface, Action

**Panels:**
- Navigation Links
- Volume Change Detection (1 table + 1 header)
  - Significant Volume Changes by Interface
- Interface Analysis (1 chart + 1 header)
  - Interface Traffic Analysis (stacked bar - ACCEPT/REJECT)
- Account Analysis (1 table + 1 header)
  - Traffic by Cloud Account

## Features

- **Dashboard navigation**: Links panel at the top of each dashboard for easy navigation
- **Color coding**: REJECT traffic is shown in red (#BD271E), ACCEPT in green (#00BF6F)
- **Section headers**: Markdown panels organize each dashboard into logical sections
- **Compact metrics**: KPI metrics use `hide_title: true` for a cleaner look
- **Auto-layout**: Panels use only `size` - positions are calculated automatically
- **Volume change detection**: Compares a 30-minute baseline window with current window (on Traffic and Interface dashboards)

## Source

Based on the [aws_vpcflow_otel](https://github.com/elastic/integrations/tree/main/packages/aws_vpcflow_otel) package from elastic/integrations.
