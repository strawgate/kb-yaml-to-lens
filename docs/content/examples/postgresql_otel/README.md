# PostgreSQL OpenTelemetry Receiver Dashboards

Comprehensive dashboards for monitoring PostgreSQL databases using OpenTelemetry's PostgreSQL receiver.

## Overview

These dashboards provide visibility into PostgreSQL database performance, connections, transactions, and I/O metrics collected via the [OpenTelemetry PostgreSQL Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/postgresqlreceiver).

## Dashboards

### 01-overview-lens.yaml

#### Lens-based Overview Dashboard

Provides a comprehensive view of PostgreSQL performance using Lens visualizations:

- **Navigation Links**: Quick access to all PostgreSQL dashboards
- **KPI Metrics**: Total databases, active connections, max connections, database count
- **Performance Summary Table**: Database-level metrics including:
  - Active connections per database
  - Database sizes
  - Commit and rollback rates
  - Block I/O operations
- **Time Series Charts**:
  - Active connections over time by database
  - Transaction rates (commits and rollbacks)
  - Block I/O by source (heap_hit, heap_read, idx_hit, idx_read)
  - Database operations by type (ins, upd, del, hot_upd)
- **Distribution Charts**:
  - Database sizes (pie chart)
  - Connection states (pie chart)

**Data Source**: `metrics-*` index pattern
**Filter**: `data_stream.dataset == "postgresqlreceiver.otel"`

### 02-overview-esql.yaml

#### ES|QL-based Overview Dashboard

Similar visualizations to the Lens dashboard but using ES|QL queries for data aggregation:

- Uses ES|QL `FROM metrics-*` syntax for KPI and aggregation queries
- Uses ES|QL `TS metrics-*` syntax for time-series visualizations with `RATE()` and `TBUCKET()`
- ES|QL metric panels for KPI metrics
- ES|QL datatable for performance summary
- ES|QL pie charts for distributions
- 100% ES|QL-based (no Lens dependencies)

**Note**: This dashboard uses ES|QL's `TS` (time series) command for time-series visualizations, which provides native rate calculations via `RATE()` and efficient time bucketing via `TBUCKET()`. KPI metrics and aggregation panels use `FROM metrics-*` syntax.

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
- `resource.attributes.postgresql.version` - PostgreSQL version
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

### Compiling Dashboards

```bash
# From the compiler directory
cd compiler

# Compile Lens dashboard
make compile INPUTS=../docs/examples/postgresql_otel/01-overview-lens.yaml

# Compile ES|QL dashboard
make compile INPUTS=../docs/examples/postgresql_otel/02-overview-esql.yaml
```

## Usage

### Filters

Both dashboards include controls for filtering by:

- **Database Name**: Filter to specific database(s)
- **Host Name**: Filter to specific PostgreSQL host(s)

### Navigation

The navigation panel provides quick access between dashboards:

- **Overview (Lens)**: Lens-based visualizations
- **Overview (ES|QL)**: ES|QL-based visualizations

## Customization

### Adjusting Time Ranges

All time series charts respect the dashboard time picker. Common time ranges:

- Last 15 minutes (real-time monitoring)
- Last 1 hour (recent activity)
- Last 24 hours (daily trends)
- Last 7 days (weekly patterns)

### Modifying Aggregations

For Lens panels, formulas can be adjusted:

```yaml
# Example: Change from sum to average
formula: average(postgresql.backends)  # instead of sum()

# Example: Add rate calculation
formula: counter_rate(max(postgresql.commits))
```

For ES|QL panels, modify the query:

```sql
-- Example: Change aggregation interval (for FROM queries)
STATS commits = MAX(postgresql.commits) BY time_bucket = BUCKET(@timestamp, 5 minutes)

-- Example: For TS (time series) queries, use TBUCKET instead
STATS commits = SUM(RATE(postgresql.commits)) BY time_bucket = TBUCKET(5 minutes)
```

### Adding Alerts

These dashboards can be used as a foundation for creating alerts on:

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

## Contributing

To add new dashboards or enhance existing ones:

1. Follow the existing naming convention: `##-name-type.yaml`
2. Test compilation with `make check`
3. Verify against actual PostgreSQL metrics data
4. Update this README with new dashboard descriptions
5. Submit a pull request

## License

These dashboard examples are part of the kb-yaml-to-lens project and follow the same license.
