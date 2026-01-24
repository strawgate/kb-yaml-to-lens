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

- **Data stream dataset**: `memcachedreceiver.otel`
- **Data view**: `metrics-*`

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

## Usage

1. Configure the Memcached receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboard:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/memcached_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry Memcached Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/memcachedreceiver)
