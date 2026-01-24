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

## Usage

1. Configure the Memcached receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboard:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/memcached_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry Memcached Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/memcachedreceiver)
