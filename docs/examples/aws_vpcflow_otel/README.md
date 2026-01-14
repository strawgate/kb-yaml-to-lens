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

This example includes 3 interconnected dashboards with navigation links:

### 1. VPC Flow Logs Overview

**ID:** `aws-vpcflow-otel-overview`

High-level KPIs and time-series trends for quick status assessment.

**Controls (3):** Cloud Account ID, Network Interface, Action

**Panels (12):**

- Navigation (1 links panel)
- KPI Metrics (5 metrics)
  - Total Flow Records, Rejection Rate, Total Bandwidth, Active Interfaces, Cloud Accounts
- Quick Insights (2 charts + 1 header)
  - Top 5 Interfaces by Rejected Traffic, Top 5 Rejected Destination Ports
- Time-Series Trends (2 charts + 1 header)
  - Traffic Volume Over Time (stacked area - ACCEPT/REJECT)
  - Bandwidth Usage Over Time (line chart)

### 2. Traffic Analysis

**ID:** `aws-vpcflow-otel-traffic`

Detailed traffic distribution, source analysis, and security deep dive.

**Controls (6):** Cloud Account ID, Network Interface, Action, Protocol, Destination Port, Source Port

**Panels (13):**

- Navigation (1 links panel)
- Traffic Distribution (3 charts)
  - Top Protocols (pie), Top Destination Ports (bar), Top Interfaces by Bandwidth (bar)
- Source Analysis (1 table + 1 header)
  - Top Source IPs - Detailed
- Volume Change Detection (2 tables + 1 header)
  - Significant Volume Changes by Source IP, Significant Volume Changes by Destination Port
- Security Deep Dive (3 panels + 1 header)
  - Rejected Traffic by Protocol (bar), Top Rejected Ports (bar), Detailed Rejection Logs (table)

### 3. Interface Analysis

**ID:** `aws-vpcflow-otel-interface`

Per-interface analysis for investigating specific network interfaces.

**Controls (5):** Cloud Account ID, Network Interface, Action, Destination Port, Protocol

**Panels (13):**

- Navigation (1 links panel)
- Interface Traffic Analysis (1 stacked bar)
- Top Traffic by Interface (3 charts + 1 header)
  - Top Destination Ports, Top Destination IPs, Top Source IPs
- Traffic Details (2 charts + 1 header)
  - Accepted vs Rejected by Protocol, Bandwidth by Protocol
- Volume Change Detection (1 table + 1 header)
  - Significant Volume Changes by Interface
- Account Analysis (1 table + 1 header)
  - Traffic by Cloud Account

## Features

- **Dashboard Navigation**: Links panel at the top of each dashboard for easy navigation between Overview, Traffic Analysis, and Interface Analysis
- **Color coding**: REJECT traffic is shown in red (#BD271E), ACCEPT in green (#00BF6F)
- **Section headers**: Markdown panels organize each dashboard into logical sections (except the first section)
- **Compact metrics**: KPI metrics use `hide_title: true` for a cleaner look
- **Auto-layout**: Panels use only `size` - positions are calculated automatically
- **Volume change detection**: Compares a 30-minute baseline window with current window to detect anomalies, sorted by absolute change
- **Filter preservation**: Navigation links use `with_time` and `with_filters` to preserve context when navigating
- **Division by zero protection**: Rejection rate calculations use CASE() to avoid NaN values

## Source

Based on the [aws_vpcflow_otel](https://github.com/elastic/integrations/tree/main/packages/aws_vpcflow_otel) package from elastic/integrations.
