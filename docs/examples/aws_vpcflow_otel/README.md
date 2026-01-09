# AWS VPC Flow Logs OTEL Dashboard

This dashboard visualizes AWS VPC Flow Logs data collected via OpenTelemetry (OTEL).

## How to Use This Example

The dashboard YAML is located at `docs/examples/aws_vpcflow_otel/dashboards.yaml` and defines the **[AWS VPC OTEL] VPC Flow Logs Overview** dashboard.

To compile this example:

```bash
kb-dashboard compile --input-dir docs/examples/aws_vpcflow_otel --output-dir output
```

This produces NDJSON (newline-delimited JSON) output in the `output/` directory. The output file will be named based on the dashboard name.

To upload the compiled dashboard directly to Kibana (requires [Kibana credentials](../../CLI.md#configuration) to be configured via environment variables):

```bash
kb-dashboard compile --input-dir docs/examples/aws_vpcflow_otel --output-dir output --upload
```

**Note:** The `--upload` option requires `KIBANA_URL` and either `KIBANA_USERNAME`/`KIBANA_PASSWORD` or `KIBANA_API_KEY` environment variables to be set. See the [CLI Configuration](../../CLI.md#configuration) documentation for details.

For more details on using the compiler, see the [main examples documentation](../index.md#how-to-use-these-examples).

## Dashboard Overview

**[AWS VPC OTEL] VPC Flow Logs Overview** provides insights into VPC network traffic patterns, including:

- Overview of flow log records over time by action (ACCEPT/REJECT)
- Top source IP addresses generating traffic
- Detailed view of rejected connection attempts

## Data Requirements

- **Data View:** `logs-*`
- **Required Fields:**
  - `@timestamp` - Timestamp of the flow log record
  - `data_stream.dataset` - Should be `aws.vpcflow.otel`
  - `aws.vpc.flow.action` - Action taken (ACCEPT/REJECT)
  - `aws.vpc.flow.bytes` - Number of bytes transferred
  - `source.address` - Source IP address
  - `source.port` - Source port number

## Panels

### 1. Header (Markdown)

Provides dashboard overview and usage guidance.

### 2. Top 10 IP Source Addresses (ES|QL Bar Chart)

Horizontal bar chart showing the top 10 source IP addresses by flow log record count.

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND source.address IS NOT NULL
| STATS total = COUNT() BY source.address
| KEEP total, source.address
| SORT total DESC
| LIMIT 10
```

### 3. VPC Flow Total Requests (ES|QL Area Chart)

Stacked area chart showing flow log records over time, broken down by action (ACCEPT/REJECT).

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.action IS NOT NULL
| STATS total = COUNT() by aws.vpc.flow.action, time_bucket = BUCKET(@timestamp, 50, ?_tstart, ?_tend)
| KEEP total, aws.vpc.flow.action, time_bucket
| SORT time_bucket ASC
```

### 4. VPC Flow Reject Logs (ES|QL Datatable)

Table showing detailed information about rejected connection attempts.

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.action == "REJECT"
| KEEP @timestamp, source.address, source.port, aws.vpc.flow.bytes
| SORT @timestamp DESC
```

## Use Cases

This dashboard helps you:

- **Diagnose overly restrictive security group rules** - Identify patterns in rejected connections
- **Monitor traffic patterns** - Understand which sources are generating the most traffic
- **Investigate security incidents** - Review detailed logs of rejected connection attempts
- **Analyze bandwidth usage** - Track bytes transferred by rejected connections

## Technical Details

### ES|QL Features Used

- **STATS aggregations** - Count records and group by fields
- **BUCKET function** - Create time-based buckets for area chart
- **WHERE clauses** - Filter data by action type
- **SORT and LIMIT** - Order and restrict result sets
- **KEEP clause** - Select specific fields for display

### Dashboard Filter

A dashboard-level filter ensures only AWS VPC Flow Logs OTEL data is displayed:

```yaml
dashboards:
  - name: '[AWS VPC OTEL] VPC Flow Logs Overview'
    filters:
      - field: data_stream.dataset
        equals: aws.vpcflow.otel
```

## Related Examples

- [System OTEL Dashboards](../system_otel/) - Similar monitoring patterns for system metrics
- [Docker OTEL Dashboards](../docker_otel/) - Container monitoring with OTEL data

## Source

Original dashboard from the [elastic/integrations](https://github.com/elastic/integrations) repository:

- Package: `aws_vpcflow_otel`
- Dashboard ID: `ef16a22e-304a-4afa-a8d9-edcd504f15ae`
