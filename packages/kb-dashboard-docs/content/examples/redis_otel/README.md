# Redis OpenTelemetry Dashboards

Redis database monitoring dashboards using OpenTelemetry Redis receiver metrics.

## Overview

These dashboards provide comprehensive monitoring for Redis instances, including client connections, memory usage, command throughput, keyspace statistics, and replication metrics.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `overview.yaml` | Multi-instance monitoring with key metrics across all Redis instances |
| **Instance Details** | `instance-details.yaml` | Detailed single-instance analysis including memory, connections, keyspace, and replication metrics |
| **Database Metrics** | `database-metrics.yaml` | Per-database keyspace metrics including keys, TTL, and expiration statistics |

All dashboards include navigation links for easy switching between views.

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Overview (overview.yaml)"

    ```yaml
    --8<-- "examples/redis_otel/overview.yaml"
    ```

??? example "Instance Details (instance-details.yaml)"

    ```yaml
    --8<-- "examples/redis_otel/instance-details.yaml"
    ```

??? example "Database Metrics (database-metrics.yaml)"

    ```yaml
    --8<-- "examples/redis_otel/database-metrics.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Prerequisites

- **Redis**: Redis server instances (6.x or later recommended)
- **OpenTelemetry Collector**: Collector Contrib with Redis receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `redisreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

```yaml
receivers:
  redis:
    endpoint: localhost:6379
    collection_interval: 10s

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [redis]
      exporters: [elasticsearch]
```

## Metrics Reference

### Default Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `redis.clients.blocked` | Sum | `{client}` | Clients pending on a blocking call | — |
| `redis.clients.connected` | Sum | `{client}` | Client connections (excluding replicas) | — |
| `redis.clients.max_input_buffer` | Gauge | `By` | Largest input buffer among connections | — |
| `redis.clients.max_output_buffer` | Gauge | `By` | Longest output list among connections | — |
| `redis.commands` | Gauge | `{ops}/s` | Processed commands per second | — |
| `redis.commands.processed` | Sum | `{command}` | Total server commands executed | — |
| `redis.connections.received` | Sum | `{connection}` | Total accepted connections | — |
| `redis.connections.rejected` | Sum | `{connection}` | Connections denied due to maxclients | — |
| `redis.cpu.time` | Sum | `s` | CPU consumed since server start | `state` |
| `redis.db.avg_ttl` | Gauge | `ms` | Average keyspace keys TTL | `db` |
| `redis.db.expires` | Gauge | `{key}` | Keys with expiration in keyspace | `db` |
| `redis.db.keys` | Gauge | `{key}` | Total keyspace keys | `db` |
| `redis.keys.evicted` | Sum | `{key}` | Keys removed due to maxmemory limit | — |
| `redis.keys.expired` | Sum | `{event}` | Total key expiration events | — |
| `redis.keyspace.hits` | Sum | `{hit}` | Successful key lookups | — |
| `redis.keyspace.misses` | Sum | `{miss}` | Failed key lookups | — |
| `redis.latest_fork` | Gauge | `us` | Duration of most recent fork operation | — |
| `redis.memory.fragmentation_ratio` | Gauge | `1` | Ratio between RSS and used memory | — |
| `redis.memory.lua` | Gauge | `By` | Memory used by Lua engine | — |
| `redis.memory.peak` | Gauge | `By` | Peak memory consumption | — |
| `redis.memory.rss` | Gauge | `By` | Memory allocated as viewed by OS | — |
| `redis.memory.used` | Gauge | `By` | Bytes allocated by Redis allocator | — |
| `redis.net.input` | Sum | `By` | Total network bytes read | — |
| `redis.net.output` | Sum | `By` | Total network bytes written | — |
| `redis.rdb.changes_since_last_save` | Sum | `{change}` | Modifications since last dump | — |
| `redis.replication.backlog_first_byte_offset` | Gauge | `By` | Master offset of replication backlog | — |
| `redis.replication.offset` | Gauge | `By` | Server's current replication offset | — |
| `redis.slaves.connected` | Sum | `{replica}` | Number of connected replicas | — |
| `redis.uptime` | Sum | `s` | Seconds since server start | — |

### Optional Metrics (disabled by default)

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `redis.cmd.calls` | Sum | `{call}` | Command execution call count | `cmd` |
| `redis.cmd.latency` | Gauge | `s` | Command execution latency | `cmd`, `percentile` |
| `redis.cmd.usec` | Sum | `us` | Total command execution time | `cmd` |
| `redis.maxmemory` | Gauge | `By` | Configured maximum memory limit | — |
| `redis.role` | Sum | `{role}` | Node's operational role | `role` |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `state` | `sys`, `sys_children`, `sys_main_thread`, `user`, `user_children`, `user_main_thread` | CPU state |
| `db` | `db0`, `db1`, etc. | Database index |
| `cmd` | Command name | Redis command |
| `percentile` | `p50`, `p99`, `p99.9` | Latency percentile |
| `role` | `replica`, `primary` | Node role |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `redis.version` | Server version identifier |
| `server.address` | Server address (optional) |
| `server.port` | Server port (optional) |

## Metrics Not Used in Dashboards

All optional metrics listed in the [Optional Metrics](#optional-metrics-disabled-by-default) section above are not currently visualized in the dashboards. These metrics are disabled by default and must be explicitly enabled in the OpenTelemetry Collector configuration.

## Related Resources

- [OpenTelemetry Redis Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/redisreceiver)
- [Redis Documentation](https://redis.io/docs/)
