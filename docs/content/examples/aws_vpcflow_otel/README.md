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

## Field Reference

| Field | Description |
|-------|-------------|
| `@timestamp` | Event timestamp |
| `aws.vpc.flow.action` | Allow/Deny action |
| `aws.vpc.flow.bytes` | Bytes transferred |
| `aws.vpc.flow.packets` | Packets transferred |
| `source.address` | Source IP address |
| `source.port` | Source port |
| `destination.address` | Destination IP address |
| `destination.port` | Destination port |
| `network.protocol.name` | Protocol name |
| `network.interface.name` | Network interface name |
| `cloud.account.id` | AWS account ID |
