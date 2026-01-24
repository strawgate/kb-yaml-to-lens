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

## OpenTelemetry Collector Configuration

```yaml
receivers:
  elasticsearch:
    endpoint: http://localhost:9200
    username: ${env:ELASTICSEARCH_USERNAME}
    password: ${env:ELASTICSEARCH_PASSWORD}
    collection_interval: 10s
    metrics:
      elasticsearch.cluster.health:
        enabled: true
      elasticsearch.cluster.nodes:
        enabled: true
      elasticsearch.cluster.data_nodes:
        enabled: true
      elasticsearch.cluster.shards:
        enabled: true
      elasticsearch.cluster.pending_tasks:
        enabled: true
      elasticsearch.node.documents:
        enabled: true
      elasticsearch.node.fs.disk.available:
        enabled: true
      elasticsearch.node.cache.memory.usage:
        enabled: true
      elasticsearch.process.cpu.usage:
        enabled: true
      jvm.memory.heap.used:
        enabled: true
      jvm.memory.heap.max:
        enabled: true
      jvm.gc.collections.count:
        enabled: true

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [elasticsearch]
      exporters: [elasticsearch]
```

## Metrics Reference

**Critical Naming Convention:** The receiver uses two distinct metric naming patterns:

1. **JVM Metrics** - Use `jvm.*` prefix (NO `elasticsearch.` prefix)
2. **Elasticsearch Metrics** - Use `elasticsearch.*` prefix

### Cluster Metrics (default enabled)

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `elasticsearch.cluster.health` | Sum | `{status}` | Cluster health (green/yellow/red) | `status` |
| `elasticsearch.cluster.nodes` | Sum | `{nodes}` | Total node count | — |
| `elasticsearch.cluster.data_nodes` | Sum | `{nodes}` | Data node count | — |
| `elasticsearch.cluster.shards` | Sum | `{shards}` | Shard count by state | `state` |
| `elasticsearch.cluster.pending_tasks` | Sum | `{tasks}` | Pending cluster tasks | — |
| `elasticsearch.cluster.in_flight_fetch` | Sum | `{fetches}` | Unfinished fetches | — |
| `elasticsearch.cluster.published_states.full` | Sum | `1` | Published cluster states | — |
| `elasticsearch.cluster.published_states.differences` | Sum | `1` | Differences between states | `state` |
| `elasticsearch.cluster.state_queue` | Sum | `1` | Cluster states in queue | `state` |
| `elasticsearch.cluster.state_update.count` | Sum | `1` | State update attempts | `state` |
| `elasticsearch.cluster.state_update.time` | Sum | `ms` | Time updating cluster state | `state`, `type` |

### Node Metrics (default enabled)

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `elasticsearch.node.documents` | Sum | `{documents}` | Documents on node | `state` |
| `elasticsearch.node.fs.disk.available` | Sum | `By` | Available disk space | — |
| `elasticsearch.node.fs.disk.free` | Sum | `By` | Unallocated disk space | — |
| `elasticsearch.node.fs.disk.total` | Sum | `By` | Total disk space | — |
| `elasticsearch.node.http.connections` | Sum | `{connections}` | HTTP connections to node | — |
| `elasticsearch.node.cache.memory.usage` | Sum | `By` | Cache size on node | `cache_name` |
| `elasticsearch.node.cache.count` | Sum | `{count}` | Query cache hits/misses | `type` |
| `elasticsearch.node.cache.evictions` | Sum | `{evictions}` | Cache evictions | `cache_name` |
| `elasticsearch.node.cluster.connections` | Sum | `{connections}` | Cluster TCP connections | — |
| `elasticsearch.node.cluster.io` | Sum | `By` | Cluster network bytes | `direction` |
| `elasticsearch.node.disk.io.read` | Sum | `KiBy` | Disk bytes read (Linux) | — |
| `elasticsearch.node.disk.io.write` | Sum | `KiBy` | Disk bytes written (Linux) | — |
| `elasticsearch.node.ingest.documents` | Sum | `{documents}` | Documents ingested lifetime | — |
| `elasticsearch.node.ingest.documents.current` | Sum | `{documents}` | Documents currently ingesting | — |
| `elasticsearch.node.ingest.operations.failed` | Sum | `{operation}` | Failed ingest operations | — |
| `elasticsearch.node.open_files` | Sum | `{files}` | Open file descriptors | — |
| `elasticsearch.node.operations.completed` | Sum | `{operations}` | Operations completed | `operation` |
| `elasticsearch.node.operations.time` | Sum | `ms` | Operation time | `operation` |
| `elasticsearch.node.pipeline.ingest.documents.current` | Sum | `{documents}` | Documents in pipeline | `name` |
| `elasticsearch.node.pipeline.ingest.documents.preprocessed` | Sum | `{documents}` | Documents preprocessed | `name` |
| `elasticsearch.node.pipeline.ingest.operations.failed` | Sum | `{operation}` | Failed pipeline ops | `name` |
| `elasticsearch.node.script.compilations` | Sum | `{compilations}` | Script compilations | — |
| `elasticsearch.node.script.cache_evictions` | Sum | `1` | Script cache evictions | — |
| `elasticsearch.node.script.compilation_limit_triggered` | Sum | `1` | Circuit breaker triggers | — |
| `elasticsearch.node.shards.size` | Sum | `By` | Shard storage size | — |
| `elasticsearch.node.shards.data_set.size` | Sum | `By` | Dataset size of shards | — |
| `elasticsearch.node.shards.reserved.size` | Sum | `By` | Reserved shard size | — |
| `elasticsearch.node.thread_pool.tasks.queued` | Sum | `{tasks}` | Queued tasks | `thread_pool_name` |
| `elasticsearch.node.thread_pool.tasks.finished` | Sum | `{tasks}` | Finished tasks | `thread_pool_name`, `state` |
| `elasticsearch.node.thread_pool.threads` | Sum | `{threads}` | Thread count | `thread_pool_name`, `state` |
| `elasticsearch.node.translog.operations` | Sum | `{operations}` | Transaction log ops | — |
| `elasticsearch.node.translog.size` | Sum | `By` | Transaction log size | — |
| `elasticsearch.node.translog.uncommitted.size` | Sum | `By` | Uncommitted translog size | — |
| `elasticsearch.os.cpu.usage` | Gauge | `%` | System CPU usage | — |
| `elasticsearch.os.cpu.load_avg.1m` | Gauge | `1` | 1-minute load average | — |
| `elasticsearch.os.cpu.load_avg.5m` | Gauge | `1` | 5-minute load average | — |
| `elasticsearch.os.cpu.load_avg.15m` | Gauge | `1` | 15-minute load average | — |
| `elasticsearch.os.memory` | Gauge | `By` | Physical memory | `state` |
| `elasticsearch.process.cpu.usage` | Gauge | `1` | Process CPU usage (0-1) | — |

### JVM Metrics (default enabled)

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `jvm.memory.heap.used` | Gauge | `By` | Used heap memory | — |
| `jvm.memory.heap.max` | Gauge | `By` | Maximum heap memory | — |
| `jvm.memory.heap.committed` | Gauge | `By` | Committed heap memory | — |
| `jvm.memory.nonheap.used` | Gauge | `By` | Used non-heap memory | — |
| `jvm.memory.nonheap.committed` | Gauge | `By` | Committed non-heap | — |
| `jvm.memory.pool.used` | Gauge | `By` | Memory pool usage | `name` |
| `jvm.memory.pool.max` | Gauge | `By` | Memory pool maximum | `name` |
| `jvm.gc.collections.count` | Sum | `1` | GC collection count | `name` |
| `jvm.gc.collections.elapsed` | Sum | `ms` | GC elapsed time | `name` |
| `jvm.classes.loaded` | Gauge | `1` | Loaded classes | — |
| `jvm.threads.count` | Gauge | `1` | JVM thread count | — |

### Index Metrics (default enabled)

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `elasticsearch.index.documents` | Sum | `{documents}` | Documents in index | `state`, `aggregation` |
| `elasticsearch.index.shards.size` | Sum | `By` | Index shard size | `aggregation` |
| `elasticsearch.index.segments.count` | Sum | `{segments}` | Segments in index | `aggregation` |
| `elasticsearch.index.operations.completed` | Sum | `{operations}` | Completed operations | `operation`, `aggregation` |
| `elasticsearch.index.operations.time` | Sum | `ms` | Operation time | `operation`, `aggregation` |
| `elasticsearch.index.operations.merge.current` | Gauge | `{merges}` | Active segment merges | `aggregation` |

### Circuit Breaker Metrics (default enabled)

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `elasticsearch.breaker.memory.estimated` | Gauge | `By` | Estimated memory used | `name` |
| `elasticsearch.breaker.memory.limit` | Sum | `By` | Memory limit | `name` |
| `elasticsearch.breaker.tripped` | Sum | `1` | Circuit breaker trips | `name` |

### Indexing Pressure Metrics (default enabled)

| Metric | Type | Unit | Description | Attributes |
| ------ | ---- | ---- | ----------- | ---------- |
| `elasticsearch.indexing_pressure.memory.limit` | Gauge | `By` | Indexing memory limit | — |
| `elasticsearch.indexing_pressure.memory.total.primary_rejections` | Sum | `1` | Primary rejections | — |
| `elasticsearch.indexing_pressure.memory.total.replica_rejections` | Sum | `1` | Replica rejections | — |
| `elasticsearch.memory.indexing_pressure` | Sum | `By` | Indexing memory | `stage` |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `status` | `green`, `yellow`, `red` | Cluster health status |
| `state` (shards) | `active`, `active_primary`, `initializing`, `relocating`, `unassigned`, `unassigned_delayed` | Shard state |
| `state` (documents) | `active`, `deleted` | Document state |
| `state` (queue) | `pending`, `committed` | Queue state |
| `state` (memory) | `free`, `used` | Memory state |
| `state` (threads) | `active`, `idle` | Thread state |
| `type` (update) | `computation_time`, `context_construction_time`, `notification_time`, `publication_time` | State update type |
| `cache_name` | `fielddata`, `query`, `request` | Cache type |
| `thread_pool_name` | `analyze`, `fetch_shard_store`, `get`, `listener`, `search`, `write` | Thread pool |
| `operation` | `index`, `delete`, `get`, `query`, `fetch`, `scroll`, `suggest`, `merge`, `refresh`, `flush`, `warmer` | Operation type |
| `aggregation` | `total`, `primaries`, `replicas` | Shard aggregation |
| `direction` | `sent`, `received` | Network direction |
| `name` | Various | Circuit breaker, GC, or memory pool name |
| `stage` | `coordinating`, `primary`, `replica` | Indexing pressure stage |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `elasticsearch.cluster.name` | Cluster identifier |
| `elasticsearch.node.name` | Node identifier |
| `elasticsearch.node.version` | Node version |
| `elasticsearch.index.name` | Index name |

## Related Resources

- [OpenTelemetry Elasticsearch Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/elasticsearchreceiver)
- [Elasticsearch Monitoring Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/monitor-elasticsearch-cluster.html)
