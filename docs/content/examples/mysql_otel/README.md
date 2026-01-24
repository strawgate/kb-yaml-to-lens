# MySQL OpenTelemetry Dashboards

MySQL database monitoring dashboards using OpenTelemetry MySQL receiver metrics.

## Overview

These dashboards provide comprehensive monitoring for MySQL database instances, including connections, buffer pool efficiency, query performance, and InnoDB metrics.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `mysql-overview-esql.yaml` | Comprehensive MySQL metrics using ES\|QL queries |
| **Extended** | `mysql-extended-esql.yaml` | Extended MySQL metrics for optional/disabled metrics |

Both dashboards include navigation links for easy switching between views.

## Prerequisites

- **MySQL**: MySQL 5.7+ or 8.x database server
- **OpenTelemetry Collector**: Collector Contrib with MySQL receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `mysqlreceiver.otel`
- **Data view**: `metrics-*`

## Usage

1. Configure the MySQL receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/mysql_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry MySQL Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/mysqlreceiver)
