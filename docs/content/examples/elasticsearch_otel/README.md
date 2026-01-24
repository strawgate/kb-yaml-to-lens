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

## Metrics Reference

**Critical Naming Convention:** The receiver uses two distinct metric naming patterns:

1. **JVM Metrics** - Use `jvm.*` prefix (NO `elasticsearch.` prefix)
2. **Elasticsearch Metrics** - Use `elasticsearch.*` prefix

### Cluster Metrics

| Metric | Type | Description |
| ------ | ---- | ----------- |
| `elasticsearch.cluster.health` | Gauge | Cluster health status (green/yellow/red) |
| `elasticsearch.cluster.nodes` | Gauge | Total number of nodes in cluster |
| `elasticsearch.cluster.data_nodes` | Gauge | Number of data nodes in cluster |
| `elasticsearch.cluster.shards` | Gauge | Number of shards (by aggregation, state) |
| `elasticsearch.cluster.pending_tasks` | Gauge | Number of pending cluster tasks |

### Node Metrics

| Metric | Type | Description |
| ------ | ---- | ----------- |
| `elasticsearch.node.documents` | Gauge | Documents on node |
| `elasticsearch.node.fs.disk.available` | Gauge | Available disk space |
| `elasticsearch.node.http.connections` | Gauge | HTTP connections |
| `elasticsearch.node.cache.memory.usage` | Gauge | Cache memory usage (by cache_name) |
| `elasticsearch.node.thread_pool.tasks.queued` | Gauge | Queued thread pool tasks |
| `elasticsearch.process.cpu.usage` | Gauge | Process CPU usage (0-1) |

### JVM Metrics

| Metric | Type | Description |
| ------ | ---- | ----------- |
| `jvm.memory.heap.used` | Gauge | Used heap memory |
| `jvm.memory.heap.max` | Gauge | Maximum heap memory |
| `jvm.gc.collections.count` | Counter | GC collection count (by name) |
| `jvm.gc.collections.elapsed` | Counter | GC collection time (by name) |
| `jvm.threads.count` | Gauge | JVM thread count |

### Index Metrics

| Metric | Type | Description |
| ------ | ---- | ----------- |
| `elasticsearch.index.documents` | Gauge | Number of documents in index |
| `elasticsearch.index.shards.size` | Gauge | Size of index shards |
| `elasticsearch.index.segments.count` | Gauge | Number of segments in index |
| `elasticsearch.index.operations.completed` | Counter | Completed index operations (by operation) |

### Circuit Breaker Metrics

| Metric | Type | Description |
| ------ | ---- | ----------- |
| `elasticsearch.breaker.memory.estimated` | Gauge | Estimated memory used by circuit breaker |
| `elasticsearch.breaker.memory.limit` | Gauge | Maximum memory for circuit breaker |
| `elasticsearch.breaker.tripped` | Counter | Total circuit breaker trips |

### Attributes

| Attribute | Description |
| --------- | ----------- |
| `elasticsearch.cluster.name` | Cluster identifier |
| `elasticsearch.node.name` | Node identifier |
| `elasticsearch.index.name` | Index name |
| `cache_name` | Cache type (fielddata, query, request) |
| `thread_pool_name` | Thread pool type (search, write, get, etc.) |
| `name` | Circuit breaker type, GC collector name, or JVM memory pool name |
| `operation` | Operation type (read, write, index, search, etc.) |
| `aggregation` | Shard aggregation type (total, primary, replica) |
| `state` | Thread state, shard state, or health status |

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
