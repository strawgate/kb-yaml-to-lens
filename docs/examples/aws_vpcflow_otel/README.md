# AWS VPC Flow Logs OTEL Dashboard

This dashboard provides comprehensive DevOps/SRE monitoring for AWS VPC Flow Logs data collected via OpenTelemetry (OTEL). It offers actionable insights into network traffic patterns, security threats, and performance metrics across your AWS infrastructure.

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

**[AWS VPC OTEL] VPC Flow Logs Overview** is a comprehensive DevOps/SRE monitoring dashboard that provides deep visibility into VPC network traffic, security, and performance. It includes 18 visualization panels organized into 8 functional sections:

1. **Navigation & Controls** - Dashboard controls and contextual information
2. **KPI Metrics** - High-level key performance indicators
3. **Distribution Analysis** - Traffic distribution patterns
4. **Time-Series Trends** - Historical traffic patterns
5. **Source Analysis** - Source IP-level traffic analysis
6. **Security Deep Dive** - Security threat investigation
7. **Performance Analysis** - Interface-level performance metrics
8. **Account Analysis** - Multi-account traffic monitoring

## Dashboard Controls

Three interactive controls allow you to filter the entire dashboard:

- **Cloud Account ID** - Filter by specific AWS account(s)
- **Network Interface** - Filter by specific network interface(s)
- **Action** - Filter by ACCEPT or REJECT actions

These controls help you drill down into specific network segments or investigate specific security incidents.

## Data Requirements

- **Data View:** `logs-*`
- **Dataset Filter:** All queries filter to `data_stream.dataset == "aws.vpcflow.otel"`
- **Required Fields:**
  - `@timestamp` - Timestamp of the flow log record
  - `data_stream.dataset` - Should be `aws.vpcflow.otel`
  - `aws.vpc.flow.action` - Action taken (ACCEPT/REJECT)
  - `aws.vpc.flow.bytes` - Number of bytes transferred
  - `aws.vpc.flow.packets` - Number of packets transferred
  - `source.address` - Source IP address
  - `source.port` - Source port number
  - `destination.address` - Destination IP address
  - `destination.port` - Destination port number
  - `network.protocol.name` - Protocol name (TCP, UDP, etc.)
  - `network.interface.name` - Network interface name
  - `cloud.account.id` - AWS account ID

## Panels

### Section 1: Navigation & Context

#### 1. Navigation Links (ES|QL Links Panel)

Provides navigation to related dashboards (expandable for future multi-dashboard navigation).

**Grid Position:** `x: 0, y: 0, w: 48, h: 2`

#### 2. Overview Markdown

Contextual information explaining the dashboard's purpose, organization, and quick insights. Helps users understand what insights each section provides.

**Grid Position:** `x: 0, y: 2, w: 48, h: 3`

### Section 2: KPI Metrics

High-level key performance indicators providing at-a-glance visibility into network health.

#### 3. Total Flow Records (ES|QL Metric)

Total count of all VPC flow log records in the selected time range.

**Grid Position:** `x: 0, y: 5, w: 12, h: 6`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel"
| STATS total_flows = COUNT()
```

**Use Case:** Understand overall traffic volume and detect unusual spikes or drops in network activity.

#### 4. Rejection Rate (ES|QL Metric)

Percentage of rejected flows out of total flows, calculated as `(rejected_flows / total_flows) * 100`.

**Grid Position:** `x: 12, y: 5, w: 12, h: 6`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel"
| STATS total_flows = COUNT(), rejected_flows = COUNT(*) WHERE aws.vpc.flow.action == "REJECT"
| EVAL rejection_rate = (rejected_flows / total_flows) * 100
```

**Use Case:** Monitor security posture by tracking the rate of rejected connections. High rejection rates may indicate security threats or misconfigured security groups.

#### 5. Total Bandwidth (ES|QL Metric)

Total bytes transferred across all flows, formatted as human-readable bytes (KB, MB, GB, etc.).

**Grid Position:** `x: 24, y: 5, w: 12, h: 6`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.bytes IS NOT NULL
| STATS total_bytes = SUM(aws.vpc.flow.bytes)
```

**Use Case:** Track bandwidth consumption for capacity planning and cost optimization.

#### 6. Unique Active Interfaces (ES|QL Metric)

Count of distinct network interfaces that have processed traffic in the selected time range.

**Grid Position:** `x: 36, y: 5, w: 12, h: 6`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND network.interface.name IS NOT NULL
| STATS unique_interfaces = COUNT_DISTINCT(network.interface.name)
```

**Use Case:** Monitor infrastructure scale and identify unused or underutilized network interfaces.

### Section 3: Traffic Distribution

Analyze how traffic is distributed across protocols, interfaces, and ports.

#### 7. Top Protocols (ES|QL Pie Chart)

Distribution of flow records by network protocol (TCP, UDP, ICMP, etc.). Limited to top 10 protocols.

**Grid Position:** `x: 0, y: 11, w: 16, h: 12`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND network.protocol.name IS NOT NULL
| STATS flow_count = COUNT() BY network.protocol.name
| SORT flow_count DESC
| LIMIT 10
```

**Use Case:** Understand protocol mix and identify unusual protocol usage that might indicate security threats or application issues.

#### 8. Top Interfaces by Traffic (ES|QL Bar Chart)

Top 10 network interfaces ranked by total bytes transferred. Shows which interfaces handle the most bandwidth.

**Grid Position:** `x: 16, y: 11, w: 16, h: 12`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND network.interface.name IS NOT NULL AND aws.vpc.flow.bytes IS NOT NULL
| STATS total_bytes = SUM(aws.vpc.flow.bytes) BY network.interface.name
| SORT total_bytes DESC
| LIMIT 10
```

**Use Case:** Identify high-traffic interfaces for capacity planning and performance optimization. Detect interfaces with unexpectedly high traffic.

#### 9. Top Destination Ports (ES|QL Bar Chart)

Top 10 destination ports by flow count. Identifies which services are receiving the most connection attempts.

**Grid Position:** `x: 32, y: 11, w: 16, h: 12`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND destination.port IS NOT NULL
| STATS flow_count = COUNT() BY destination.port
| SORT flow_count DESC
| LIMIT 10
```

**Use Case:** Identify frequently accessed services and detect unusual port access patterns that might indicate scanning or attacks.

### Section 4: Time-Series Trends

Visualize traffic patterns over time to identify trends, anomalies, and periodic patterns.

#### 10. Traffic Volume Over Time (ES|QL Area Chart)

Stacked area chart showing flow count over time, broken down by action (ACCEPT/REJECT). Uses 50 time buckets across the selected time range.

**Grid Position:** `x: 0, y: 23, w: 48, h: 14`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.action IS NOT NULL
| STATS flow_count = COUNT() BY aws.vpc.flow.action, time_bucket = BUCKET(@timestamp, 50, ?_tstart, ?_tend)
| SORT time_bucket ASC
```

**Use Case:** Monitor traffic patterns over time, identify traffic spikes or drops, and correlate rejected traffic with security incidents. The breakdown by action helps distinguish between accepted and rejected flows.

#### 11. Bandwidth Usage Over Time (ES|QL Line Chart)

Line chart showing total bandwidth (bytes) over time. Uses 50 time buckets across the selected time range.

**Grid Position:** `x: 0, y: 37, w: 48, h: 14`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.bytes IS NOT NULL
| STATS total_bytes = SUM(aws.vpc.flow.bytes) BY time_bucket = BUCKET(@timestamp, 50, ?_tstart, ?_tend)
| SORT time_bucket ASC
```

**Use Case:** Track bandwidth consumption trends, identify bandwidth spikes that might indicate data exfiltration or application issues, and plan capacity upgrades.

### Section 5: Source Analysis

Deep dive into traffic sources to identify top contributors and analyze IP range patterns.

#### 12. Top Source IPs - Detailed (ES|QL Datatable)

Detailed table showing top 20 source IPs with comprehensive metrics: total flows, accepted flows, rejected flows, rejection rate percentage, bytes, and packets. Paginated with 20 rows per page.

**Grid Position:** `x: 0, y: 51, w: 24, h: 15`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND source.address IS NOT NULL
| STATS total_flows = COUNT(), accepted_flows = COUNT(*) WHERE aws.vpc.flow.action == "ACCEPT", rejected_flows = COUNT(*) WHERE aws.vpc.flow.action == "REJECT", total_bytes = SUM(aws.vpc.flow.bytes), total_packets = SUM(aws.vpc.flow.packets) BY source.address
| EVAL rejection_rate = (rejected_flows / total_flows) * 100
| SORT total_flows DESC
| LIMIT 20
```

**Use Case:** Identify top traffic sources, investigate sources with high rejection rates (potential attackers), and analyze bandwidth consumption by source. Use this to whitelist/blacklist specific IPs or investigate security incidents.

#### 13. Top Source IP Ranges (ES|QL Bar Chart)

Top 10 source IP ranges (aggregated to /16 CIDR blocks) by flow count. Uses ES|QL's SPLIT and CONCAT functions to extract the first two octets and create /16 ranges.

**Grid Position:** `x: 24, y: 51, w: 24, h: 15`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND source.address IS NOT NULL
| EVAL ip_parts = SPLIT(source.address, ".")
| EVAL ip_range = CONCAT(ip_parts[0], ".", ip_parts[1], ".0.0/16")
| STATS flow_count = COUNT() BY ip_range
| SORT flow_count DESC
| LIMIT 10
```

**Use Case:** Identify geographic or organizational traffic patterns by IP range. Useful for detecting distributed attacks or analyzing traffic from specific regions/providers.

### Section 6: Security Deep Dive

Comprehensive security analysis focused on rejected traffic and potential threats.

#### 14. Rejected Traffic by Protocol (ES|QL Bar Chart)

Top 10 protocols for rejected connections. Shows which protocols are most frequently blocked.

**Grid Position:** `x: 0, y: 66, w: 24, h: 15`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.action == "REJECT" AND network.protocol.name IS NOT NULL
| STATS rejected_count = COUNT() BY network.protocol.name
| SORT rejected_count DESC
| LIMIT 10
```

**Use Case:** Identify which protocols are being blocked most frequently. High rejection rates for specific protocols might indicate misconfigured security groups or ongoing attacks.

#### 15. Top Rejected Ports (ES|QL Bar Chart)

Top 10 destination ports for rejected connections. Identifies which services are being targeted.

**Grid Position:** `x: 24, y: 66, w: 24, h: 15`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.action == "REJECT" AND destination.port IS NOT NULL
| STATS rejected_count = COUNT() BY destination.port
| SORT rejected_count DESC
| LIMIT 10
```

**Use Case:** Detect port scanning activity, identify commonly targeted services, and validate that security groups are blocking expected ports. Common attack ports (22, 3389, 445, etc.) appearing here might indicate reconnaissance activity.

#### 16. Detailed Rejection Logs (ES|QL Datatable)

Full detailed logs of rejected connections showing timestamp, source/destination addresses, port, protocol, interface, bytes, and packets. Paginated with 25 rows per page and limited to 1000 most recent records.

**Grid Position:** `x: 0, y: 81, w: 48, h: 15`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND aws.vpc.flow.action == "REJECT"
| KEEP @timestamp, source.address, destination.address, destination.port, network.protocol.name, network.interface.name, aws.vpc.flow.bytes, aws.vpc.flow.packets
| SORT @timestamp DESC
| LIMIT 1000
```

**Use Case:** Investigate specific rejected connections in detail. Correlate rejection patterns with security incidents, validate security group rules, and identify false positives that need whitelisting.

### Section 7: Performance Analysis

Interface-level performance metrics and traffic breakdown.

#### 17. Interface Traffic Analysis (ES|QL Stacked Bar Chart)

Stacked bar chart showing flow count by network interface, broken down by action (ACCEPT/REJECT). Shows which interfaces handle the most traffic and their acceptance/rejection patterns.

**Grid Position:** `x: 0, y: 96, w: 48, h: 15`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND network.interface.name IS NOT NULL AND aws.vpc.flow.action IS NOT NULL
| STATS flow_count = COUNT() BY network.interface.name, aws.vpc.flow.action
| SORT flow_count DESC
```

**Use Case:** Compare traffic patterns across interfaces, identify interfaces with high rejection rates (potential security issues or misconfigurations), and balance traffic across interfaces.

### Section 8: Account Analysis

Multi-account traffic monitoring for organizations with multiple AWS accounts.

#### 18. Traffic by Cloud Account (ES|QL Datatable)

Comprehensive multi-account analysis showing total flows, accepted flows, rejected flows, rejection rate, bytes, unique interfaces, and unique sources per AWS account. Paginated with 20 rows per page.

**Grid Position:** `x: 0, y: 111, w: 48, h: 15`

**ES|QL Query:**

```esql
FROM logs-*
| WHERE data_stream.dataset == "aws.vpcflow.otel" AND cloud.account.id IS NOT NULL
| STATS total_flows = COUNT(), accepted_flows = COUNT(*) WHERE aws.vpc.flow.action == "ACCEPT", rejected_flows = COUNT(*) WHERE aws.vpc.flow.action == "REJECT", total_bytes = SUM(aws.vpc.flow.bytes), unique_interfaces = COUNT_DISTINCT(network.interface.name), unique_sources = COUNT_DISTINCT(source.address) BY cloud.account.id
| EVAL rejection_rate = (rejected_flows / total_flows) * 100
| SORT total_flows DESC
```

**Use Case:** Monitor traffic and security posture across multiple AWS accounts. Identify accounts with high rejection rates, compare bandwidth usage across accounts for cost allocation, and ensure consistent security policies.

## DevOps/SRE Use Cases

This dashboard is designed to support the following operational workflows:

### 1. Daily Network Health Monitoring

- Check KPI metrics (Section 2) for unusual values
- Review time-series trends (Section 4) for traffic anomalies
- Monitor rejection rates across the infrastructure

### 2. Security Incident Investigation

- Start with KPI rejection rate to identify potential security issues
- Use Rejected Traffic by Protocol and Top Rejected Ports (Section 6) to understand attack vectors
- Dive into Detailed Rejection Logs for specific connection details
- Correlate with Top Source IPs to identify attacker sources

### 3. Security Group Validation

- Review Detailed Rejection Logs to identify legitimate traffic being blocked
- Check rejection rates by source IP to distinguish between attacks and misconfigurations
- Use controls to filter by specific interfaces or accounts for targeted analysis

### 4. Capacity Planning

- Monitor Total Bandwidth and Bandwidth Usage Over Time trends
- Identify Top Interfaces by Traffic for infrastructure scaling decisions
- Track growth patterns using time-series visualizations

### 5. Multi-Account Security Posture

- Review Traffic by Cloud Account for rejection rate comparisons
- Identify accounts with unusual traffic patterns or high rejection rates
- Ensure consistent security policies across accounts

### 6. Performance Optimization

- Identify high-traffic interfaces and protocols
- Analyze traffic distribution to optimize network architecture
- Monitor bandwidth trends to plan capacity upgrades

### 7. Attack Detection and Response

- Monitor sudden spikes in rejection rate
- Identify coordinated attacks using Top Source IP Ranges
- Correlate rejected ports with known attack patterns
- Track attacker behavior over time using time-series visualizations

## Technical Details

### ES|QL Features Used

This dashboard demonstrates advanced ES|QL capabilities:

- **STATS aggregations** - COUNT(), SUM(), COUNT_DISTINCT()
- **Conditional aggregations** - `COUNT(*) WHERE condition` pattern
- **EVAL expressions** - Calculate derived metrics like rejection_rate
- **BUCKET function** - Create time-based buckets with `BUCKET(@timestamp, 50, ?_tstart, ?_tend)`
- **String manipulation** - SPLIT() and CONCAT() for IP range extraction
- **WHERE clauses** - Complex filtering with multiple conditions
- **SORT and LIMIT** - Result ordering and pagination
- **KEEP clause** - Explicit field selection for datatables

### Formatting and Display

- **Byte formatting** - Automatic conversion to KB/MB/GB using `format: {type: bytes}`
- **Percentage formatting** - Display with 1 decimal place using `format: {type: percent, decimals: 1}`
- **Pagination** - All datatables use `paging: {enabled: true, page_size: 20-25}`
- **Legend control** - Hidden on simple bar charts, visible on breakdown charts
- **Axis titles** - Custom titles for better context

### Dashboard Filter

A dashboard-level filter ensures only AWS VPC Flow Logs OTEL data is displayed:

```yaml
dashboards:
  - name: '[AWS VPC OTEL] VPC Flow Logs Overview'
    filters:
      - field: data_stream.dataset
        equals: aws.vpcflow.otel
```

All panel queries include the same filter as a WHERE clause for consistency and performance.

## Related Examples

- [System OTEL Dashboards](../system_otel/) - Similar monitoring patterns for system metrics
- [Docker OTEL Dashboards](../docker_otel/) - Container monitoring with OTEL data

## Source

Original dashboard from the [elastic/integrations](https://github.com/elastic/integrations) repository:

- Package: `aws_vpcflow_otel`
- Dashboard ID: `ef16a22e-304a-4afa-a8d9-edcd504f15ae`

This enhanced version expands the original 4-panel dashboard to 18 panels with comprehensive DevOps/SRE monitoring capabilities.
