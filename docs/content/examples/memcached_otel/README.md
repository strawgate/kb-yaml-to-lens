# Memcached OpenTelemetry Dashboard

Memcached monitoring dashboard using OpenTelemetry Memcached receiver metrics.

## Overview

This dashboard provides comprehensive monitoring for Memcached instances, displaying metrics collected via the `stats` command by the OpenTelemetry Collector's Memcached receiver.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `01-memcached-overview.yaml` | Memcached monitoring with items, storage, connections, and hit/miss rates |

## Prerequisites

- **Memcached**: Memcached server instances
- **OpenTelemetry Collector**: Collector Contrib with Memcached receiver configured
- **Kibana**: Version 9.2 or later (dashboards use ES|QL TS command)

## Data Requirements

- **Data stream dataset**: `memcachedreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

```yaml
receivers:
  memcached:
    endpoint: localhost:11211
    collection_interval: 10s

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [memcached]
      exporters: [elasticsearch]
```

## Metrics Reference

All metrics are enabled by default.

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `memcached.bytes` | Gauge | `By` | Current bytes used to store items | — |
| `memcached.commands` | Sum | `{commands}` | Orders processed | `command` |
| `memcached.connections.current` | Sum | `{connections}` | Active open connections | — |
| `memcached.connections.total` | Sum | `{connections}` | Total connections opened since server start | — |
| `memcached.cpu.usage` | Sum | `s` | Accumulated processing time | `state` |
| `memcached.current_items` | Sum | `{items}` | Items currently stored in the cache | — |
| `memcached.evictions` | Sum | `{evictions}` | Cache item evictions | — |
| `memcached.network` | Sum | `By` | Data transferred across network | `direction` |
| `memcached.operation_hit_ratio` | Gauge | `%` | Hit ratio (0.0 to 100.0) for operations | `operation` |
| `memcached.operations` | Sum | `{operations}` | Request outcomes | `type`, `operation` |
| `memcached.threads` | Sum | `{threads}` | Threads used by the memcached instance | — |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `command` | `get`, `set`, `flush`, `touch` | Command type |
| `state` | `system`, `user` | CPU usage state |
| `direction` | `sent`, `received` | Network direction |
| `operation` | `increment`, `decrement`, `get` | Operation type |
| `type` | `hit`, `miss` | Request outcome type |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `host.name` | Memcached host name |

## Related Resources

- [OpenTelemetry Memcached Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/memcachedreceiver)
