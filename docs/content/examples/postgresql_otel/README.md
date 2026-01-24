# PostgreSQL OpenTelemetry Receiver Dashboards

Dashboards for monitoring PostgreSQL databases using OpenTelemetry's PostgreSQL receiver.

## Overview

This dashboard provides visibility into PostgreSQL database performance, connections, transactions, and I/O metrics.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `02-overview-esql.yaml` | ES\|QL-based overview with KPIs, time series charts, and database metrics |

## Prerequisites

- **PostgreSQL**: PostgreSQL database server
- **OpenTelemetry Collector**: Collector with PostgreSQL receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `postgresqlreceiver.otel`
- **Data view**: `metrics-*`

## Usage

1. Configure the PostgreSQL receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboard:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/postgresql_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry PostgreSQL Receiver Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/postgresqlreceiver)
- [Dashboard Compiler Documentation](../../index.md)
