# PostgreSQL OpenTelemetry Receiver Dashboards

Comprehensive dashboards for monitoring PostgreSQL databases using OpenTelemetry's PostgreSQL receiver.

## Overview

This dashboard provides visibility into PostgreSQL database performance, connections, transactions, and I/O metrics collected via the [OpenTelemetry PostgreSQL Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/postgresqlreceiver).

## Dashboard

### 02-overview-esql.yaml

ES|QL-based overview dashboard using the `TS` (time series) command for optimized time series analysis:

- **KPI Metrics**: Total databases, active connections, max connections, database count
- **Performance Summary Table**: Database-level metrics including:
  - Active connections per database
  - Database sizes
  - Cumulative commit and rollback counts
  - Block I/O totals
- **Time Series Charts**:
  - Active connections over time by database
  - Transaction rates (commits and rollbacks)
  - Block I/O by source (heap_hit, heap_read, idx_hit, idx_read)
  - Database operations by type (ins, upd, del, hot_upd)
- **Distribution Charts**:
  - Database sizes (pie chart)
  - Connection states (pie chart)
- **Metadata Table**: List of monitored databases and hosts

**Data Source**: `metrics-*` index pattern
**Filter**: `data_stream.dataset == "postgresqlreceiver.otel"`

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

- `resource.attributes.postgresql.database.name` - Database name
- `resource.attributes.host.name` - Host name
- `attributes.source` - Block I/O source (heap_hit, heap_read, idx_hit, idx_read)
- `attributes.operation` - Operation type (ins, upd, del, hot_upd)
- `attributes.state` - Connection state

## Setup

### Prerequisites

1. **OpenTelemetry Collector** with PostgreSQL receiver configured
2. **Elastic Stack** with metrics ingested from OTel Collector
3. **Data Stream**: `metrics-postgresqlreceiver-*` or similar

### PostgreSQL Receiver Configuration Example

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

## Usage

### Filters

The dashboard includes controls for filtering by:

- **Database Name**: Filter to specific database(s)
- **Host Name**: Filter to specific PostgreSQL host(s)

## Customization

### Adjusting Time Ranges

All time series charts respect the dashboard time picker. Common time ranges:

- Last 15 minutes (real-time monitoring)
- Last 1 hour (recent activity)
- Last 24 hours (daily trends)
- Last 7 days (weekly patterns)

### Modifying Aggregations

For ES|QL panels, modify the query:

```sql
-- Example: Use dynamic bucket sizing (recommended for all queries)
STATS commits = SUM(RATE(postgresql.commits)) BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend)

-- Adjust bucket count (20-50) based on desired granularity
STATS commits = MAX(postgresql.commits) BY time_bucket = BUCKET(@timestamp, 50, ?_tstart, ?_tend)
```

### Adding Alerts

This dashboard can be used as a foundation for creating alerts on:

- High connection count (approaching max_connections)
- Elevated rollback rates (possible application issues)
- Slow query performance
- Disk I/O saturation
- Database size growth

## Related Resources

- [OpenTelemetry PostgreSQL Receiver Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/postgresqlreceiver)
- [Elastic Observability](https://www.elastic.co/observability)
- [Dashboard Compiler Documentation](../../index.md)
- [ES|QL Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html)
