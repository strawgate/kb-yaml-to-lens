# PostgreSQL OpenTelemetry Receiver Dashboards

Dashboards for monitoring PostgreSQL databases using OpenTelemetry's PostgreSQL receiver.

## Overview

This dashboard provides visibility into PostgreSQL database performance, connections, transactions, and I/O metrics.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `02-overview-esql.yaml` | ES\|QL-based overview with KPIs, time series charts, and database metrics |

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Overview (02-overview-esql.yaml)"

    ```yaml
    --8<-- "examples/postgresql_otel/02-overview-esql.yaml"
    ```
<!-- markdownlint-enable MD046 -->

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

### Default Metrics

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `postgresql.backends` | Sum | `1` | Number of backends | — |
| `postgresql.bgwriter.buffers.allocated` | Sum | `{buffers}` | Number of buffers allocated | — |
| `postgresql.bgwriter.buffers.writes` | Sum | `{buffers}` | Number of buffers written | `source` |
| `postgresql.bgwriter.checkpoint.count` | Sum | `{checkpoints}` | Number of checkpoints performed | `type` |
| `postgresql.bgwriter.duration` | Sum | `ms` | Time spent writing/syncing during checkpoints | `type` |
| `postgresql.bgwriter.maxwritten` | Sum | `1` | Times background writer stopped | — |
| `postgresql.blocks_read` | Sum | `1` | Number of blocks read | `source` |
| `postgresql.commits` | Sum | `1` | Number of commits | — |
| `postgresql.connection.max` | Gauge | `{connections}` | Maximum client connections allowed | — |
| `postgresql.database.count` | Sum | `{databases}` | Number of user databases | — |
| `postgresql.db_size` | Sum | `By` | Database disk usage | — |
| `postgresql.index.scans` | Sum | `{scans}` | Number of index scans on a table | — |
| `postgresql.index.size` | Gauge | `By` | Size of the index on disk | — |
| `postgresql.operations` | Sum | `1` | Number of db row operations | `operation` |
| `postgresql.replication.data_delay` | Gauge | `By` | Amount of data delayed in replication | `replication_client` |
| `postgresql.rollbacks` | Sum | `1` | Number of rollbacks | — |
| `postgresql.rows` | Sum | `1` | Number of rows in the database | `state` |
| `postgresql.table.count` | Sum | `{table}` | Number of user tables in a database | — |
| `postgresql.table.size` | Sum | `By` | Disk space used by a table | — |
| `postgresql.table.vacuum.count` | Sum | `{vacuum}` | Number of times a table has been vacuumed | — |
| `postgresql.wal.age` | Gauge | `s` | Age of oldest WAL file | — |
| `postgresql.wal.lag` | Gauge | `s` | WAL replication lag time | `operation`, `replication_client` |

### Optional Metrics (disabled by default)

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `postgresql.blks_hit` | Sum | `{blks_hit}` | Cache buffer hits | — |
| `postgresql.blks_read` | Sum | `{blks_read}` | Disk blocks read | — |
| `postgresql.database.locks` | Gauge | `{lock}` | Number of database locks | `relation`, `mode`, `lock_type` |
| `postgresql.deadlocks` | Sum | `{deadlock}` | Number of deadlocks | — |
| `postgresql.sequential_scans` | Sum | `{sequential_scan}` | Sequential scan count | — |
| `postgresql.temp.io` | Sum | `By` | Data written to temporary files | — |
| `postgresql.temp_files` | Sum | `{temp_file}` | Number of temp files | — |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `source` (bgwriter) | `backend`, `backend_fsync`, `checkpoints`, `bgwriter` | Buffer write source |
| `source` (blocks_read) | `heap_read`, `heap_hit`, `idx_read`, `idx_hit`, `toast_read`, `toast_hit`, `tidx_read`, `tidx_hit` | Block I/O source |
| `type` (checkpoint) | `requested`, `scheduled` | Checkpoint type |
| `type` (duration) | `sync`, `write` | Duration type |
| `operation` | `ins`, `upd`, `del`, `hot_upd` | Row operation type |
| `state` | `dead`, `live` | Row state |
| `operation` (wal.lag) | `flush`, `replay`, `write` | WAL operation |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `postgresql.database.name` | Database name |
| `postgresql.index.name` | Index name |
| `postgresql.schema.name` | Schema name |
| `postgresql.table.name` | Table name |
| `service.instance.id` | Service instance identifier |

## Metrics Not Used in Dashboards

The following metrics are available from the PostgreSQL receiver but are not currently visualized in the dashboards:

### Default Metrics Not Used

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `postgresql.bgwriter.buffers.allocated` | Sum | `{buffers}` | Number of buffers allocated | — |
| `postgresql.bgwriter.buffers.writes` | Sum | `{buffers}` | Number of buffers written | `source` |
| `postgresql.bgwriter.checkpoint.count` | Sum | `{checkpoints}` | Number of checkpoints performed | `type` |
| `postgresql.bgwriter.duration` | Sum | `ms` | Time spent writing/syncing during checkpoints | `type` |
| `postgresql.bgwriter.maxwritten` | Sum | `1` | Times background writer stopped | — |
| `postgresql.index.scans` | Sum | `{scans}` | Number of index scans on a table | — |
| `postgresql.index.size` | Gauge | `By` | Size of the index on disk | — |
| `postgresql.replication.data_delay` | Gauge | `By` | Amount of data delayed in replication | `replication_client` |
| `postgresql.rows` | Sum | `1` | Number of rows in the database | `state` |
| `postgresql.table.count` | Sum | `{table}` | Number of user tables in a database | — |
| `postgresql.table.size` | Sum | `By` | Disk space used by a table | — |
| `postgresql.table.vacuum.count` | Sum | `{vacuum}` | Number of times a table has been vacuumed | — |
| `postgresql.wal.age` | Gauge | `s` | Age of oldest WAL file | — |
| `postgresql.wal.lag` | Gauge | `s` | WAL replication lag time | `operation`, `replication_client` |

### Optional Metrics Not Used

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `postgresql.blks_hit` | Sum | `{blks_hit}` | Cache buffer hits | — |
| `postgresql.blks_read` | Sum | `{blks_read}` | Disk blocks read | — |
| `postgresql.database.locks` | Gauge | `{lock}` | Number of database locks | `relation`, `mode`, `lock_type` |
| `postgresql.deadlocks` | Sum | `{deadlock}` | Number of deadlocks | — |
| `postgresql.sequential_scans` | Sum | `{sequential_scan}` | Sequential scan count | — |
| `postgresql.temp.io` | Sum | `By` | Data written to temporary files | — |
| `postgresql.temp_files` | Sum | `{temp_file}` | Number of temp files | — |

## Related Resources

- [OpenTelemetry PostgreSQL Receiver Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/postgresqlreceiver)
- [Dashboard Compiler Documentation](../../index.md)
