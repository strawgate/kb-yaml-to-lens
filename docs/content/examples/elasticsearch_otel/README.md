# Elasticsearch OpenTelemetry Receiver Dashboards

Kibana dashboards for monitoring Elasticsearch clusters using OpenTelemetry's Elasticsearch receiver.

## Overview

These dashboards provide detailed visibility into cluster health, node performance, JVM metrics, index statistics, and circuit breaker behavior.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Cluster Overview** | `01-cluster-overview.yaml` | High-level cluster health, node counts, shard distribution, and pending tasks |
| **Node Overview** | `02-node-overview.yaml` | Node-level summary with CPU, memory, disk, and operations |
| **Node Metrics** | `03-node-metrics.yaml` | Detailed node performance metrics including cache and thread pools |
| **Index Metrics** | `04-index-metrics.yaml` | Index-level statistics, shard sizes, segments, and operations |
| **JVM Health** | `05-jvm-health.yaml` | JVM memory (heap/non-heap), garbage collection, threads, and memory pools |
| **Circuit Breakers** | `06-circuit-breakers.yaml` | Circuit breaker memory usage, limits, and trip events |
| **Cluster Metadata** | `07-cluster-metadata.yaml` | Cluster configuration and metadata exploration |

All dashboards include navigation links for easy switching between views.

## Prerequisites

- **Elasticsearch**: Version 7.x or 8.x with `monitor` or `manage` cluster privileges
- **OpenTelemetry Collector**: Collector Contrib distribution with Elasticsearch receiver
- **Kibana**: Version compatible with your Elasticsearch cluster

## Data Requirements

- **Data stream dataset**: `elasticsearchreceiver.otel`
- **Data view**: `metrics-*`

## Usage

1. Configure the Elasticsearch receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/elasticsearch_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry Elasticsearch Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/elasticsearchreceiver)
- [Elasticsearch Monitoring Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/monitor-elasticsearch-cluster.html)
