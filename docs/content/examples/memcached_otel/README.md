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
- **Kibana**: Version 8.x or later

## Data Requirements

Dashboard expects metrics from the OpenTelemetry Memcached receiver:

- **Data stream dataset**: `memcachedreceiver.otel`
- **Data view**: `metrics-*`

### Key Metrics

| Metric | Description |
|--------|-------------|
| `memcached.current_items` | Current number of items in cache |
| `memcached.bytes` | Storage bytes used |
| `memcached.current_connections` | Active client connections |
| `memcached.commands` | Command counts (get, set, etc.) |
| `memcached.operation_hit_ratio` | Cache hit/miss ratio |

### Key Attributes

- `resource.attributes.host.name` - Memcached host name

## Configuration Example

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

## Usage

1. Configure the Memcached receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile the dashboard:

   ```bash
   kb-dashboard compile --input-file docs/content/examples/memcached_otel/01-memcached-overview.yaml
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-file docs/content/examples/memcached_otel/01-memcached-overview.yaml --upload
   ```

## Dashboard Controls

The dashboard includes interactive controls for filtering:

- **Host Name**: Filter by Memcached host
