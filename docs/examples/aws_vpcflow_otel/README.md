# AWS VPC Flow Logs OTEL Dashboard

DevOps/SRE monitoring dashboard for AWS VPC Flow Logs collected via OpenTelemetry.

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

## Dashboard Controls (7)

| Control | Field | Purpose |
|---------|-------|---------|
| Cloud Account ID | `cloud.account.id` | Filter by AWS account |
| Network Interface | `network.interface.name` | Filter by ENI |
| Action | `aws.vpc.flow.action` | Filter ACCEPT/REJECT |
| Source IP | `source.address` | Filter by source IP |
| Destination IP | `destination.address` | Filter by destination IP |
| Source Port | `source.port` | Filter by source port |
| Destination Port | `destination.port` | Filter by destination port |

## Panels (22 total)

### KPI Metrics (5 metrics + 1 header)
- **Total Flow Records** - Count of all flow logs
- **Rejection Rate** - Percentage of rejected flows
- **Total Bandwidth** - Sum of bytes transferred
- **Active Interfaces** - Count of unique ENIs
- **Cloud Accounts** - Count of unique AWS accounts

### Traffic Distribution (3 charts + 1 header)
- **Top Protocols** - Pie chart by protocol
- **Top Interfaces by Traffic** - Bar chart by bytes
- **Top Destination Ports** - Bar chart by flow count

### Time-Series Trends (2 charts + 1 header)
- **Traffic Volume Over Time** - Stacked area chart (ACCEPT/REJECT) with color coding
- **Bandwidth Usage Over Time** - Line chart of bytes

### Volume Change Detection (1 table + 1 header)
- **Significant Volume Changes by Interface** - Compares baseline period vs current period to detect traffic anomalies

### Source Analysis (1 table + 1 header)
- **Top Source IPs** - Datatable with flows, bytes, rejection rate

### Security Deep Dive (3 panels + 1 header)
- **Rejected Traffic by Protocol** - Bar chart (red color)
- **Top Rejected Ports** - Bar chart (red color)
- **Detailed Rejection Logs** - Datatable with full log details

### Interface Analysis (1 chart + 1 header)
- **Interface Traffic Analysis** - Stacked bar by interface with ACCEPT (green) / REJECT (red) breakdown

### Account Analysis (1 table + 1 header)
- **Traffic by Cloud Account** - Multi-account metrics datatable

## Features

- **Color coding**: REJECT traffic is shown in red (#BD271E), ACCEPT in green (#00BF6F)
- **Section headers**: Thin markdown panels organize the dashboard into logical sections
- **Compact metrics**: KPI metrics use `hide_title: true` for a cleaner look
- **Volume change detection**: Compares a 30-minute baseline window (10-40 min after time picker start) with current window (40-10 min before time picker end)

## Source

Based on the [aws_vpcflow_otel](https://github.com/elastic/integrations/tree/main/packages/aws_vpcflow_otel) package from elastic/integrations.
