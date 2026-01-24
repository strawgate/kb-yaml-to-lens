# AWS VPC Flow Logs OTEL Dashboards

DevOps/SRE monitoring dashboards for AWS VPC Flow Logs collected via OpenTelemetry.

## Usage

```bash
# Compile to NDJSON
kb-dashboard compile --input-dir docs/content/examples/aws_vpcflow_otel --output-dir output

# Compile and upload to Kibana (requires credentials)
kb-dashboard compile --input-dir docs/content/examples/aws_vpcflow_otel --output-dir output --upload
```

## Data Requirements

- **Data View:** `logs-*`
- **Dataset:** `data_stream.dataset == "aws.vpcflow.otel"`
- **Required Fields:** `@timestamp`, `aws.vpc.flow.action`, `aws.vpc.flow.bytes`, `aws.vpc.flow.packets`, `source.address`, `source.port`, `destination.address`, `destination.port`, `network.protocol.name`, `network.interface.name`, `cloud.account.id`

## Dashboards

| Dashboard | ID | Description |
| --------- | -- | ----------- |
| VPC Flow Logs Overview | `aws_vpcflow_otel-overview` | High-level KPIs and time-series trends |
| Traffic Analysis | `aws_vpcflow_otel-traffic` | Traffic distribution, source analysis, and security deep dive |
| Interface Analysis | `aws_vpcflow_otel-interface` | Per-interface analysis and account metrics |

## Source

Based on the [aws_vpcflow_otel](https://github.com/elastic/integrations/tree/main/packages/aws_vpcflow_otel) package from elastic/integrations.
