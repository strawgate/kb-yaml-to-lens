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

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Overview (mysql-overview-esql.yaml)"

    ```yaml
    --8<-- "examples/mysql_otel/mysql-overview-esql.yaml"
    ```

??? example "Extended (mysql-extended-esql.yaml)"

    ```yaml
    --8<-- "examples/mysql_otel/mysql-extended-esql.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Prerequisites

- **MySQL**: MySQL 5.7+ or 8.x database server
- **OpenTelemetry Collector**: Collector Contrib with MySQL receiver configured
- **Kibana**: Version 9.2 or later (dashboards use ES|QL TS command)

## Data Requirements

- **Data stream dataset**: `mysqlreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

```yaml
receivers:
  mysql:
    endpoint: localhost:3306
    username: ${env:MYSQL_USERNAME}
    password: ${env:MYSQL_PASSWORD}
    collection_interval: 10s

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [mysql]
      exporters: [elasticsearch]
```

## Metrics Reference

### Default Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `mysql.buffer_pool.data_pages` | Sum | `1` | Number of data pages in the InnoDB buffer pool | `status` |
| `mysql.buffer_pool.limit` | Sum | `By` | Configured size of the InnoDB buffer pool | — |
| `mysql.buffer_pool.operations` | Sum | `1` | Number of operations on the InnoDB buffer pool | `operation` |
| `mysql.buffer_pool.page_flushes` | Sum | `1` | Number of requests to flush pages from buffer pool | — |
| `mysql.buffer_pool.pages` | Sum | `1` | Number of pages in the InnoDB buffer pool | `kind` |
| `mysql.buffer_pool.usage` | Sum | `By` | Bytes in the InnoDB buffer pool | `status` |
| `mysql.double_writes` | Sum | `1` | Writes to the InnoDB doublewrite buffer | `kind` |
| `mysql.handlers` | Sum | `1` | Requests to various MySQL handlers | `kind` |
| `mysql.index.io.wait.count` | Sum | `1` | Total I/O wait count for an index | `operation`, `table`, `schema`, `index` |
| `mysql.index.io.wait.time` | Sum | `ns` | Total I/O wait time for an index | `operation`, `table`, `schema`, `index` |
| `mysql.locks` | Sum | `1` | Number of MySQL locks | `kind` |
| `mysql.log_operations` | Sum | `1` | Number of InnoDB log operations | `operation` |
| `mysql.mysqlx_connections` | Sum | `1` | Document Store connections | `status` |
| `mysql.opened_resources` | Sum | `1` | Number of opened resources | `kind` |
| `mysql.operations` | Sum | `1` | Number of InnoDB operations | `operation` |
| `mysql.page_operations` | Sum | `1` | Number of InnoDB page operations | `operation` |
| `mysql.prepared_statements` | Sum | `1` | Prepared statement commands issued | `command` |
| `mysql.row_locks` | Sum | `1` | Number of InnoDB row locks | `kind` |
| `mysql.row_operations` | Sum | `1` | Number of InnoDB row operations | `operation` |
| `mysql.sorts` | Sum | `1` | Number of MySQL sorts | `kind` |
| `mysql.table.io.wait.count` | Sum | `1` | Total I/O wait count for a table | `operation`, `table`, `schema` |
| `mysql.table.io.wait.time` | Sum | `ns` | Total I/O wait time for a table | `operation`, `table`, `schema` |
| `mysql.threads` | Sum | `1` | State of MySQL threads | `kind` |
| `mysql.tmp_resources` | Sum | `1` | Number of created temporary resources | `resource` |
| `mysql.uptime` | Sum | `s` | Seconds the server has been up | — |

### Optional Metrics (disabled by default)

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `mysql.client.network.io` | Sum | `By` | Bytes transmitted between server and clients | `kind` |
| `mysql.commands` | Sum | `1` | Number of times each command has been executed | `command` |
| `mysql.connection.count` | Sum | `1` | Connection attempts to the MySQL server | — |
| `mysql.connection.errors` | Sum | `1` | Errors during client connection process | `error` |
| `mysql.joins` | Sum | `1` | Joins that perform table scans | `kind` |
| `mysql.query.slow.count` | Sum | `1` | Number of slow queries | — |
| `mysql.table.rows` | Sum | `1` | Number of rows for a given table | `table`, `schema` |
| `mysql.table.size` | Sum | `By` | Table size in bytes | `table`, `schema`, `kind` |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `status` | `dirty`, `clean` | Buffer pool status |
| `kind` (pages) | `data`, `free`, `misc`, `total` | Page type |
| `kind` (handlers) | `commit`, `delete`, `update`, `write`, `read_first`, `read_key`, `read_next`, `read_prev`, `read_rnd`, `read_rnd_next` | Handler type |
| `kind` (locks) | `immediate`, `waited` | Lock type |
| `kind` (double_writes) | `pages_written`, `writes` | Double write type |
| `kind` (row_locks) | `waits`, `time` | Row lock type |
| `kind` (sorts) | `merge_passes`, `range`, `rows`, `scan` | Sort type |
| `kind` (threads) | `cached`, `connected`, `created`, `running` | Thread state |
| `operation` (log) | `waits`, `write_requests`, `writes`, `fsyncs` | Log operation type |
| `operation` (InnoDB) | `fsyncs`, `reads`, `writes` | InnoDB operation type |
| `operation` (page) | `created`, `read`, `written` | Page operation type |
| `operation` (row) | `deleted`, `inserted`, `read`, `updated` | Row operation type |
| `resource` | `disk_tables`, `files`, `tables` | Temporary resource type |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `host.name` | MySQL host name |
| `service.instance.id` | MySQL instance identifier |

## Metrics Not Used in Dashboards

The following default metrics are available from the MySQL receiver but are not currently visualized in the dashboards:

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `mysql.buffer_pool.data_pages` | Sum | `1` | Number of data pages in the InnoDB buffer pool | `status` |
| `mysql.buffer_pool.limit` | Sum | `By` | Configured size of the InnoDB buffer pool | — |
| `mysql.index.io.wait.time` | Sum | `ns` | Total I/O wait time for an index | `operation`, `table`, `schema`, `index` |
| `mysql.table.io.wait.time` | Sum | `ns` | Total I/O wait time for a table | `operation`, `table`, `schema` |

All optional metrics listed above are used in the Extended dashboard.

## Related Resources

- [OpenTelemetry MySQL Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/mysqlreceiver)
