# AWS CloudTrail OTEL Dashboard

YAML dashboard for the AWS CloudTrail OpenTelemetry integration.

## Overview

This dashboard provides visualization of AWS CloudTrail activity logs to identify patterns in API calls, monitor account activity, detect unauthorized behavior, track resource changes, and troubleshoot operational issues.

Based on the dashboard from the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/aws_cloudtrail_otel).

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **CloudTrail Logs Overview** | `cloudtrail-logs-overview.yaml` | CloudTrail activity logs overview |

## Prerequisites

- **AWS CloudTrail**: With data streaming via OpenTelemetry
- **OpenTelemetry Collector**: Configured for CloudTrail logs
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `aws.cloudtrail.otel`
- **Data view**: `logs-*`

## Field Reference

### Core Fields

| Field | Description |
|-------|-------------|
| `@timestamp` | Event timestamp |
| `data_stream.dataset` | Should equal `aws.cloudtrail.otel` |

### AWS CloudTrail Fields

| Field | Description |
|-------|-------------|
| `aws.access_key.id` | AWS access key ID used for the API call |
| `aws.error.code` | Error code if the operation failed |
| `rpc.service` | AWS service name (e.g., s3, ec2) |
| `rpc.system` | Event type/system |
| `rpc.method` | AWS API method/action called |
| `source.address` | Source IP address of the request |
| `user_agent.original` | User agent string of the client |
