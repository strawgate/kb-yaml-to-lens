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

## Prerequisites

- **Redis**: Redis server instances (6.x or later recommended)
- **OpenTelemetry Collector**: Collector Contrib with Redis receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

Dashboards expect metrics from the OpenTelemetry Redis receiver:

- **Data stream dataset**: `redisreceiver.otel`
- **Data view**: `metrics-*`

### Key Metrics

| Metric | Description |
|--------|-------------|
| `redis.clients.connected` | Number of connected clients |
| `redis.commands` | Commands processed per second |
| `redis.memory.used` | Memory used by Redis |
| `redis.keyspace.*` | Per-database key statistics |
| `redis.replication.*` | Replication metrics |

### Key Attributes

- `resource.attributes.service.instance.id` - Redis instance identifier

## Configuration Example

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

## Usage

1. Configure the Redis receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/redis_otel/
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/redis_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry Redis Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/redisreceiver)
- [Redis Documentation](https://redis.io/docs/)
