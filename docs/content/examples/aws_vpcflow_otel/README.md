# AWS VPC Flow Logs OTEL Dashboards

DevOps/SRE monitoring dashboards for AWS VPC Flow Logs collected via OpenTelemetry.

## Overview

Based on the [aws_vpcflow_otel](https://github.com/elastic/integrations/tree/main/packages/aws_vpcflow_otel) package from elastic/integrations.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **VPC Flow Logs Overview** | `overview.yaml` | High-level KPIs and time-series trends |
| **Traffic Analysis** | `traffic.yaml` | Traffic distribution, source analysis, and security deep dive |
| **Interface Analysis** | `interface.yaml` | Per-interface analysis and account metrics |

## Prerequisites

- **AWS VPC Flow Logs**: Configured for OpenTelemetry collection
- **OpenTelemetry Collector**: Configured for VPC Flow Logs
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `aws.vpcflow.otel`
- **Data view**: `logs-*`

## Usage

1. Configure OpenTelemetry Collector for AWS VPC Flow Logs
2. Ensure logs are being sent to Elasticsearch
3. Compile and upload the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/aws_vpcflow_otel/ --upload
   ```
