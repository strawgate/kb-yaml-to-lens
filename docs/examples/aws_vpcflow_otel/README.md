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

## Dashboard Controls

| Control | Field | Purpose |
|---------|-------|---------|
| Cloud Account ID | `cloud.account.id` | Filter by AWS account |
| Network Interface | `network.interface.name` | Filter by ENI |
| Action | `aws.vpc.flow.action` | Filter ACCEPT/REJECT |

## Panels (16 total)

### KPI Metrics
- **Total Flow Records** - Count of all flow logs
- **Rejection Rate** - Percentage of rejected flows
- **Total Bandwidth** - Sum of bytes transferred
- **Active Interfaces** - Count of unique ENIs

### Traffic Distribution
- **Top Protocols** - Pie chart by protocol
- **Top Interfaces by Traffic** - Bar chart by bytes
- **Top Destination Ports** - Bar chart by flow count

### Time-Series
- **Traffic Volume Over Time** - Stacked area chart (ACCEPT/REJECT)
- **Bandwidth Usage Over Time** - Line chart of bytes

### Source Analysis
- **Top Source IPs** - Datatable with flows, bytes, rejection rate

### Security
- **Rejected Traffic by Protocol** - Bar chart
- **Top Rejected Ports** - Bar chart
- **Detailed Rejection Logs** - Datatable with full log details

### Performance & Account
- **Interface Traffic Analysis** - Stacked bar by interface and action
- **Traffic by Cloud Account** - Multi-account metrics datatable

## Source

Based on the [aws_vpcflow_otel](https://github.com/elastic/integrations/tree/main/packages/aws_vpcflow_otel) package from elastic/integrations.
