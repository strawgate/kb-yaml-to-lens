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
- **Kibana**: Version 9.2 or later (dashboards use ES|QL TS command)

## Data Requirements

- **Data stream dataset**: `postgresqlreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

```yaml
receivers:
  postgresql:
    endpoint: localhost:5432
    transport: tcp
    username: ${env:POSTGRES_USER}
    password: ${env:POSTGRES_PASSWORD}
    databases:
      - postgres
      - myapp_db
    collection_interval: 60s
    metrics:
      postgresql.backends:
        enabled: true
      postgresql.connection.max:
        enabled: true
      postgresql.database.count:
        enabled: true
      postgresql.commits:
        enabled: true
      postgresql.rollbacks:
        enabled: true
      postgresql.blocks_read:
        enabled: true
      postgresql.db_size:
        enabled: true
      postgresql.operations:
        enabled: true
```

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

## Related Resources

- [OpenTelemetry PostgreSQL Receiver Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/postgresqlreceiver)
- [Dashboard Compiler Documentation](../../index.md)
