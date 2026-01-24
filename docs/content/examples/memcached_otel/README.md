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

| Metric | Description |
|--------|-------------|
| `memcached.current_items` | Current number of items in cache |
| `memcached.bytes` | Storage bytes used |
| `memcached.current_connections` | Active client connections |
| `memcached.commands` | Command counts (get, set, etc.) |
| `memcached.operation_hit_ratio` | Cache hit/miss ratio |

### Attributes

| Attribute | Description |
| --------- | ----------- |
| `resource.attributes.host.name` | Memcached host name |

## Related Resources

- [OpenTelemetry Memcached Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/memcachedreceiver)
