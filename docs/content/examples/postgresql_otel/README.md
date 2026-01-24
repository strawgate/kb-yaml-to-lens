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

## Metrics Reference

### Key PostgreSQL Metrics

| Metric | Type | Description |
| ------ | ---- | ----------- |
| `postgresql.backends` | Gauge | Number of active connections/backends |
| `postgresql.connection.max` | Gauge | Maximum configured connections |
| `postgresql.database.count` | Gauge | Total number of databases |
| `postgresql.commits` | Counter | Total transaction commits |
| `postgresql.rollbacks` | Counter | Total transaction rollbacks |
| `postgresql.blocks_read` | Counter | Blocks read from disk and cache |
| `postgresql.db_size` | Gauge | Database size in bytes |
| `postgresql.operations` | Counter | Database operations (insert, update, delete, hot update) |

### Attributes

| Attribute | Description |
| --------- | ----------- |
| `resource.attributes.postgresql.database.name` | Database name |
| `resource.attributes.host.name` | Host name |
| `attributes.source` | Block I/O source (heap_hit, heap_read, idx_hit, idx_read) |
| `attributes.operation` | Operation type (ins, upd, del, hot_upd) |
| `attributes.state` | Connection state |

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
