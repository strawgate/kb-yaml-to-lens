# Elasticsearch OpenTelemetry Receiver Dashboards

A comprehensive set of Kibana dashboards for monitoring Elasticsearch clusters using OpenTelemetry's Elasticsearch receiver. These dashboards provide detailed visibility into cluster health, node performance, JVM metrics, index statistics, and circuit breaker behavior.

## Overview

This example demonstrates how to monitor Elasticsearch using OpenTelemetry and visualize the metrics in Kibana using auto-generated Lens dashboards. The dashboards cover all aspects of Elasticsearch cluster monitoring, from high-level cluster health to detailed JVM and thread pool metrics.

### Dashboard Suite

The suite includes 7 interconnected dashboards:

1. **Cluster Overview** (`01-cluster-overview.yaml`) - High-level cluster health, node counts, shard distribution, and pending tasks
2. **Node Overview** (`02-node-overview.yaml`) - Node-level summary with CPU, memory, disk, and operations
3. **Node Metrics** (`03-node-metrics.yaml`) - Detailed node performance metrics including cache and thread pools
4. **Index Metrics** (`04-index-metrics.yaml`) - Index-level statistics, shard sizes, segments, and operations
5. **JVM Health** (`05-jvm-health.yaml`) - JVM memory (heap/non-heap), garbage collection, threads, and memory pools
6. **Circuit Breakers** (`06-circuit-breakers.yaml`) - Circuit breaker memory usage, limits, and trip events
7. **Cluster Metadata** (`07-cluster-metadata.yaml`) - Cluster configuration and metadata exploration

All dashboards include navigation links for easy switching between views.

## Quick Start

### Prerequisites

- **Elasticsearch**: Version 7.x or 8.x
  - Requires a user with `monitor` or `manage` cluster privileges
  - For self-monitoring, ensure cluster health is green or yellow

- **OpenTelemetry Collector**: Collector Contrib distribution (includes Elasticsearch receiver)
  - Download from: <https://github.com/open-telemetry/opentelemetry-collector-releases/releases>
  - Or use Docker: `otel/opentelemetry-collector-contrib:latest`

- **Kibana**: Version compatible with your Elasticsearch cluster
  - For dashboard import: `kb-yaml-to-lens` CLI tool

### Step 1: Set Environment Variables

Create a `.env` file or export these variables:

```bash
# Elasticsearch cluster being monitored
export ELASTICSEARCH_ENDPOINT="http://localhost:9200"
export ELASTICSEARCH_USERNAME="elastic"
export ELASTICSEARCH_PASSWORD="your-password"

# Elasticsearch cluster for metric storage (can be the same cluster)
export ELASTICSEARCH_EXPORT_ENDPOINT="http://localhost:9200"
export ELASTICSEARCH_EXPORT_USERNAME="elastic"
export ELASTICSEARCH_EXPORT_PASSWORD="your-password"

# Optional: Collector hostname for identification
export HOSTNAME="otel-collector-01"
```

#### Alternative: API Key Authentication

For better security, use API keys instead of username/password:

```bash
# Create an API key in Kibana:
# Stack Management → Security → API Keys → Create API Key
# Grant "monitor" cluster privilege

export ELASTICSEARCH_API_KEY="your-base64-encoded-api-key"
```

Then uncomment the API key section in the collector configuration below.

### Step 2: Run OpenTelemetry Collector

First, save the [Complete Collector Configuration](#complete-collector-configuration) below to a file named `collector-config.yaml`.

#### Using Docker

```bash
docker run -d \
  --name otel-collector \
  --env-file .env \
  -p 13133:13133 \
  -p 8888:8888 \
  -v $(pwd)/collector-config.yaml:/etc/otelcol-contrib/config.yaml \
  otel/opentelemetry-collector-contrib:latest
```

#### Using Binary

```bash
# Download and extract the collector
# https://github.com/open-telemetry/opentelemetry-collector-releases/releases

./otelcol-contrib --config=collector-config.yaml
```

#### Verify Collector is Running

Check health endpoint:

```bash
curl http://localhost:13133/health
```

Check collector metrics:

```bash
curl http://localhost:8888/metrics
```

### Step 3: Verify Data Collection

After 10-30 seconds, verify metrics are being collected:

```bash
# Check if data stream exists
curl -u elastic:password "http://localhost:9200/_data_stream/metrics-elasticsearchreceiver.otel-*"

# Query sample metrics
curl -u elastic:password "http://localhost:9200/metrics-elasticsearchreceiver.otel-*/_search?size=1&pretty"
```

You should see documents with fields like:

- `elasticsearch.cluster.name` - Cluster identifier
- `elasticsearch.node.name` - Node identifier
- `elasticsearch.cluster.nodes` - Node count metric
- `elasticsearch.process.cpu.usage` - CPU usage metric
- `jvm.memory.heap.used` - JVM heap memory metric
- `data_stream.dataset: "elasticsearchreceiver.otel"` - Data stream identifier

**Important:** Note the metric naming conventions:

- JVM metrics use `jvm.*` prefix (no elasticsearch prefix)
- Elasticsearch-specific metrics use `elasticsearch.*` prefix
- Process metrics use `elasticsearch.process.*` prefix
- OS metrics use `elasticsearch.os.*` prefix

### Step 4: Import Dashboards to Kibana

#### Option A: Using kb-yaml-to-lens CLI

```bash
# Install kb-yaml-to-lens
pip install kb-yaml-to-lens

# Compile all dashboards
kb-yaml-to-lens compile \
  --input-file 01-cluster-overview.yaml \
  --input-file 02-node-overview.yaml \
  --input-file 03-node-metrics.yaml \
  --input-file 04-index-metrics.yaml \
  --input-file 05-jvm-health.yaml \
  --input-file 06-circuit-breakers.yaml \
  --input-file 07-cluster-metadata.yaml \
  --output-dir ./compiled

# Import to Kibana
kb-yaml-to-lens import \
  --compiled-json ./compiled/*.json \
  --kibana-url http://localhost:5601 \
  --username elastic \
  --password your-password
```

#### Option B: Batch Compilation

```bash
# Compile all dashboards at once (excluding collector config)
for file in [0-9]*.yaml; do
  kb-yaml-to-lens compile --input-file "$file" --output-dir ./compiled
done

# Import all at once
kb-yaml-to-lens import \
  --compiled-json ./compiled/ \
  --kibana-url http://localhost:5601 \
  --username elastic \
  --password your-password
```

### Step 5: View Dashboards

1. Open Kibana: `http://localhost:5601`
2. Navigate to **Analytics → Dashboards**
3. Search for "Elasticsearch OTel"
4. Click on "[Elasticsearch OTel] Cluster Overview" to start

Use the navigation links at the top of each dashboard to switch between views.

## Configuration Deep Dive

### Metrics Collected

The Elasticsearch receiver collects 100+ metrics across these categories.

**Critical Naming Convention:** The receiver uses two distinct metric naming patterns:

1. **JVM Metrics** - Use `jvm.*` prefix (NO `elasticsearch.` prefix):
   - `jvm.memory.heap.used`, `jvm.memory.heap.max`, `jvm.gc.collections.count`, etc.
   - These are standard JVM metrics shared across all JVM-based applications

2. **Elasticsearch Metrics** - Use `elasticsearch.*` prefix:
   - Cluster: `elasticsearch.cluster.*`
   - Node: `elasticsearch.node.*`
   - Index: `elasticsearch.index.*`
   - Process: `elasticsearch.process.*`
   - OS: `elasticsearch.os.*`
   - Breaker: `elasticsearch.breaker.*` (note: NOT `elasticsearch.node.breaker.*`)

This dual naming convention reflects the different sources of the metrics and enables consistent monitoring across OpenTelemetry-instrumented applications.

#### Cluster Metrics

- **Health**: `elasticsearch.cluster.health` (status: green/yellow/red)
- **Nodes**: Total nodes, data nodes
- **Shards**: Active, primary, initializing, relocating, unassigned
- **Indices**: Total index count
- **Operations**: Pending tasks, in-flight fetches, state queue

#### Node Metrics

- **System**: CPU percent, available disk, memory usage
- **Documents**: Total document count per node
- **Operations**: Open files, HTTP connections
- **I/O**: Disk reads/writes, network traffic
- **Cache**: Query cache, fielddata cache, request cache usage
- **Thread Pools**: Queue counts, thread counts (by pool: search, write, get, etc.)

#### JVM Metrics

**Note:** JVM metrics use `jvm.*` prefix (no `elasticsearch.` prefix)

- **Memory**: `jvm.memory.heap.used`, `jvm.memory.heap.committed`, `jvm.memory.heap.max`, `jvm.memory.nonheap.used`
- **Garbage Collection**: `jvm.gc.collections.count`, `jvm.gc.collections.elapsed` (by `name` attribute)
- **Threads**: `jvm.threads.count`
- **Classes**: `jvm.classes.loaded`
- **Memory Pools**: `jvm.memory.pool.used`, `jvm.memory.pool.max` (by `name` attribute)

#### Index Metrics

- **Size**: Index size, shard size, segment size
- **Segments**: Segment count, segment memory
- **Operations**: Index rate, search rate, merge rate, refresh rate, flush rate, query cache operations
- **Documents**: Total docs per index

#### Circuit Breaker Metrics

**Note:** Circuit breaker metrics use `elasticsearch.breaker.*` prefix (no `.node` in path)

- **Memory**: `elasticsearch.breaker.memory.estimated`, `elasticsearch.breaker.memory.limit`
- **Trips**: `elasticsearch.breaker.tripped` (breaker activation events)
- **Breakers**: Parent, request, fielddata, in-flight requests, accounting, model inference (by `name` attribute)

All metrics include dimensional attributes for filtering:

- `elasticsearch.cluster.name` - Cluster identifier
- `elasticsearch.node.name` - Node identifier
- `elasticsearch.index.name` - Index name
- `cache_name` - Cache type (fielddata, query, request)
- `thread_pool_name` - Thread pool type (search, write, get, etc.)
- `name` - Used for circuit breaker type, GC collector name, and JVM memory pool name
- `operation` - Operation type (read, write, index, search, etc.)
- `direction` - Direction for I/O metrics (receive, transmit)
- `memory_state` - Memory state (used, free)
- `state` - Thread state, shard state, or health status
- `aggregation` - Aggregation type for shards (total, primary, replica)
- `fs_direction` - Filesystem direction (read, write)

### Complete Field Reference

The following tables document all metrics and attributes available from the OpenTelemetry Elasticsearch receiver.

#### Elasticsearch Metrics

| Metric | Type | Unit | Description |
| ------ | ---- | ---- | ----------- |
| `elasticsearch.breaker.memory.estimated` | Gauge | By | Estimated memory used by circuit breaker |
| `elasticsearch.breaker.memory.limit` | Gauge | By | Maximum memory for circuit breaker |
| `elasticsearch.breaker.tripped` | Counter | 1 | Total circuit breaker trips |
| `elasticsearch.cluster.data_nodes` | Gauge | 1 | Number of data nodes in cluster |
| `elasticsearch.cluster.health` | Gauge | 1 | Cluster health status |
| `elasticsearch.cluster.in_flight_fetch` | Gauge | 1 | Number of in-flight fetch operations |
| `elasticsearch.cluster.nodes` | Gauge | 1 | Total number of nodes in cluster |
| `elasticsearch.cluster.pending_tasks` | Gauge | 1 | Number of pending cluster tasks |
| `elasticsearch.cluster.published_states.differences` | Counter | 1 | Published cluster state differences |
| `elasticsearch.cluster.published_states.full` | Counter | 1 | Published full cluster states |
| `elasticsearch.cluster.shards` | Gauge | 1 | Number of shards (by aggregation, state) |
| `elasticsearch.cluster.state_queue` | Gauge | 1 | Cluster state queue size |
| `elasticsearch.cluster.state_update.count` | Counter | 1 | Cluster state update count |
| `elasticsearch.cluster.state_update.time` | Counter | ms | Cluster state update time |
| `elasticsearch.index.cache.evictions` | Counter | 1 | Index cache evictions |
| `elasticsearch.index.cache.memory.usage` | Gauge | By | Index cache memory usage |
| `elasticsearch.index.documents` | Gauge | 1 | Number of documents in index |
| `elasticsearch.index.operations.completed` | Counter | 1 | Completed index operations (by operation) |
| `elasticsearch.index.operations.merge.docs_count` | Counter | 1 | Merged document count |
| `elasticsearch.index.operations.merge.size` | Counter | By | Merged size in bytes |
| `elasticsearch.index.operations.time` | Counter | ms | Time spent on operations (by operation) |
| `elasticsearch.index.segments.count` | Gauge | 1 | Number of segments in index |
| `elasticsearch.index.segments.memory` | Gauge | By | Memory used by segments |
| `elasticsearch.index.segments.size` | Gauge | By | Size of segments |
| `elasticsearch.index.shards.size` | Gauge | By | Size of index shards |
| `elasticsearch.index.translog.operations` | Counter | 1 | Translog operations |
| `elasticsearch.index.translog.size` | Gauge | By | Translog size |
| `elasticsearch.indexing_pressure.memory.limit` | Gauge | By | Indexing pressure memory limit |
| `elasticsearch.indexing_pressure.memory.total.primary_rejections` | Counter | 1 | Primary rejection count |
| `elasticsearch.indexing_pressure.memory.total.replica_rejections` | Counter | 1 | Replica rejection count |
| `elasticsearch.memory.indexing_pressure` | Gauge | By | Indexing pressure memory |
| `elasticsearch.node.cache.count` | Gauge | 1 | Node cache count |
| `elasticsearch.node.cache.evictions` | Counter | 1 | Node cache evictions (by cache_name) |
| `elasticsearch.node.cache.hit_count` | Counter | 1 | Cache hit count |
| `elasticsearch.node.cache.memory.usage` | Gauge | By | Cache memory usage (by cache_name) |
| `elasticsearch.node.cache.miss_count` | Counter | 1 | Cache miss count |
| `elasticsearch.node.cache.size` | Gauge | 1 | Cache size |
| `elasticsearch.node.cluster.connections` | Gauge | 1 | Cluster connections |
| `elasticsearch.node.cluster.io` | Counter | By | Cluster I/O (by direction) |
| `elasticsearch.node.disk.io.read` | Counter | 1 | Disk read operations |
| `elasticsearch.node.disk.io.write` | Counter | 1 | Disk write operations |
| `elasticsearch.node.documents` | Gauge | 1 | Documents on node |
| `elasticsearch.node.fs.disk.available` | Gauge | By | Available disk space |
| `elasticsearch.node.fs.disk.free` | Gauge | By | Free disk space |
| `elasticsearch.node.fs.disk.total` | Gauge | By | Total disk space |
| `elasticsearch.node.http.connections` | Gauge | 1 | HTTP connections |
| `elasticsearch.node.ingest.documents` | Counter | 1 | Ingested documents |
| `elasticsearch.node.ingest.documents.current` | Gauge | 1 | Currently ingesting documents |
| `elasticsearch.node.ingest.operations.failed` | Counter | 1 | Failed ingest operations |
| `elasticsearch.node.open_files` | Gauge | 1 | Open file descriptors |
| `elasticsearch.node.operations.completed` | Counter | 1 | Completed node operations |
| `elasticsearch.node.operations.current` | Gauge | 1 | Current operations |
| `elasticsearch.node.operations.get.completed` | Counter | 1 | Completed get operations |
| `elasticsearch.node.operations.get.time` | Counter | ms | Get operation time |
| `elasticsearch.node.operations.time` | Counter | ms | Operation time |
| `elasticsearch.node.pipeline.ingest.documents.current` | Gauge | 1 | Pipeline documents currently ingesting |
| `elasticsearch.node.pipeline.ingest.documents.preprocessed` | Counter | 1 | Preprocessed pipeline documents |
| `elasticsearch.node.pipeline.ingest.operations.failed` | Counter | 1 | Failed pipeline operations |
| `elasticsearch.node.script.cache_evictions` | Counter | 1 | Script cache evictions |
| `elasticsearch.node.script.compilation_limit_triggered` | Counter | 1 | Compilation limit triggered |
| `elasticsearch.node.script.compilations` | Counter | 1 | Script compilations |
| `elasticsearch.node.segments.memory` | Gauge | By | Segment memory on node |
| `elasticsearch.node.shards.data_set.size` | Gauge | By | Shard data set size |
| `elasticsearch.node.shards.reserved.size` | Gauge | By | Reserved shard size |
| `elasticsearch.node.shards.size` | Gauge | By | Shard size |
| `elasticsearch.node.thread_pool.tasks.completed` | Counter | 1 | Completed thread pool tasks |
| `elasticsearch.node.thread_pool.tasks.finished` | Counter | 1 | Finished thread pool tasks (by state) |
| `elasticsearch.node.thread_pool.tasks.queued` | Gauge | 1 | Queued thread pool tasks |
| `elasticsearch.node.thread_pool.threads` | Gauge | 1 | Thread pool threads (by state) |
| `elasticsearch.node.translog.operations` | Counter | 1 | Translog operations on node |
| `elasticsearch.node.translog.size` | Gauge | By | Translog size on node |
| `elasticsearch.node.translog.uncommitted_size` | Gauge | By | Uncommitted translog size |
| `elasticsearch.os.cpu.load_avg.15m` | Gauge | 1 | 15-minute CPU load average |
| `elasticsearch.os.cpu.load_avg.1m` | Gauge | 1 | 1-minute CPU load average |
| `elasticsearch.os.cpu.load_avg.5m` | Gauge | 1 | 5-minute CPU load average |
| `elasticsearch.os.cpu.usage` | Gauge | 1 | OS CPU usage |
| `elasticsearch.os.memory` | Gauge | By | OS memory (by memory_state) |
| `elasticsearch.process.cpu.time` | Counter | ms | Process CPU time |
| `elasticsearch.process.cpu.usage` | Gauge | 1 | Process CPU usage (0-1) |
| `elasticsearch.process.memory.virtual` | Gauge | By | Virtual memory size |

#### JVM Metrics

| Metric | Type | Unit | Description |
| ------ | ---- | ---- | ----------- |
| `jvm.classes.loaded` | Gauge | 1 | Loaded classes |
| `jvm.gc.collections.count` | Counter | 1 | GC collection count (by name) |
| `jvm.gc.collections.elapsed` | Counter | ms | GC collection time (by name) |
| `jvm.memory.heap.committed` | Gauge | By | Committed heap memory |
| `jvm.memory.heap.max` | Gauge | By | Maximum heap memory |
| `jvm.memory.heap.used` | Gauge | By | Used heap memory |
| `jvm.memory.nonheap.committed` | Gauge | By | Committed non-heap memory |
| `jvm.memory.nonheap.used` | Gauge | By | Used non-heap memory |
| `jvm.memory.pool.max` | Gauge | By | Memory pool maximum (by name) |
| `jvm.memory.pool.used` | Gauge | By | Memory pool used (by name) |
| `jvm.threads.count` | Gauge | 1 | JVM thread count |

#### Attributes

| Attribute | Description | Used By |
| --------- | ----------- | ------- |
| `elasticsearch.cluster.name` | Cluster identifier | All metrics |
| `elasticsearch.node.name` | Node identifier | Node metrics |
| `elasticsearch.index.name` | Index name | Index metrics |
| `aggregation` | Shard aggregation type (total, primary, replica) | `elasticsearch.cluster.shards` |
| `cache_name` | Cache type (fielddata, query) | Node cache metrics |
| `direction` | I/O direction (receive, transmit) | `elasticsearch.node.cluster.io` |
| `fs_direction` | Filesystem direction (read, write) | Disk I/O metrics |
| `health` | Health status (green, yellow, red) | `elasticsearch.cluster.health` |
| `memory_state` | Memory state (used, free) | `elasticsearch.os.memory` |
| `name` | Circuit breaker, GC collector, or memory pool name | Breaker, GC, memory pool metrics |
| `operation` | Operation type (index, search, merge, etc.) | Operation metrics |
| `shard_state` | Shard state (active, initializing, relocating, unassigned) | `elasticsearch.cluster.shards` |
| `state` | Thread state (active, idle) or task state | Thread pool metrics |
| `status` | Cluster health status | Health metrics |
| `thread_pool_name` | Thread pool name (search, write, get, etc.) | Thread pool metrics |

### Collection Interval Tuning

The `collection_interval` setting controls how often metrics are scraped:

- **10s** (default): Good for most clusters, provides detailed time-series data
- **30s**: Recommended for large clusters (100+ nodes) to reduce API load
- **60s+**: For large-scale clusters or when detailed granularity isn't needed

Consider cluster size and API load when tuning:

```yaml
elasticsearch:
  collection_interval: 30s  # Adjust based on cluster size
```

### Node and Index Filtering

#### Collect from Specific Nodes

```yaml
elasticsearch:
  # Option 1: Collect only from local node
  nodes: ["_local"]

  # Option 2: Collect from specific nodes
  nodes: ["node-1", "node-2", "node-3"]

  # Option 3: Collect from all nodes (default, recommended)
  nodes: ["_all"]
```

#### Collect from Specific Indices

For clusters with thousands of indices, collecting all index metrics can be expensive:

```yaml
elasticsearch:
  # Option 1: Collect from all indices
  indices: ["_all"]

  # Option 2: Collect from specific indices
  indices: ["logs-production", "metrics-production"]

  # Option 3: Collect using patterns
  indices: ["logs-*", "metrics-*"]

  # Option 4: Skip index metrics entirely (only cluster/node metrics)
  indices: []
```

### Self-Monitoring vs. Remote Monitoring

#### Self-Monitoring (Monitor the Same Cluster)

Use the same cluster for both collection and storage:

```bash
# Environment variables
ELASTICSEARCH_ENDPOINT="http://localhost:9200"
ELASTICSEARCH_EXPORT_ENDPOINT="http://localhost:9200"  # Same cluster
```

**Pros**: Simple setup, single cluster to manage
**Cons**: Monitoring overhead on production cluster, monitoring data lost if cluster fails

#### Remote Monitoring (Separate Monitoring Cluster)

Use a dedicated monitoring cluster:

```bash
# Environment variables
ELASTICSEARCH_ENDPOINT="http://production-cluster:9200"       # Production
ELASTICSEARCH_EXPORT_ENDPOINT="http://monitoring-cluster:9200" # Monitoring
```

**Pros**: Monitoring data preserved during production issues, no overhead on production
**Cons**: Requires second cluster, more complex setup

Recommended: Remote monitoring for production, self-monitoring for dev/test.

### Security Configuration

#### TLS/SSL for Monitoring Connection

```yaml
elasticsearch:
  endpoint: https://localhost:9200
  tls:
    ca_file: /etc/ssl/certs/ca.crt
    cert_file: /etc/ssl/certs/client.crt
    key_file: /etc/ssl/private/client.key
    insecure_skip_verify: false
```

#### API Key Authentication

More secure than username/password:

```yaml
elasticsearch:
  endpoint: ${env:ELASTICSEARCH_ENDPOINT}
  headers:
    Authorization: ApiKey ${env:ELASTICSEARCH_API_KEY}
```

Create API key in Kibana (Stack Management → Security → API Keys) with `monitor` privilege.

### Processing Pipeline Optimization

The configuration includes three key processors:

#### 1. Memory Limiter (First in Pipeline)

Protects collector from OOM:

```yaml
memory_limiter:
  limit_mib: 512        # Hard limit
  spike_limit_mib: 128  # Short-term spike allowance
  check_interval: 1s
```

Adjust based on your environment:

- Small deployments: 256 MiB limit
- Medium deployments: 512 MiB limit (default)
- Large deployments: 1024+ MiB limit

#### 2. Resource Processor (Second in Pipeline)

Adds metadata about collector instance:

```yaml
resource:
  attributes:
    - key: otel.collector.name
      value: ${env:HOSTNAME}
      action: insert
```

Useful for multi-collector deployments to identify which collector generated metrics.

#### 3. Batch Processor (Last in Pipeline)

Groups metrics before export:

```yaml
batch:
  timeout: 10s              # Max wait time
  send_batch_size: 1000     # Target batch size
  send_batch_max_size: 2000 # Hard limit
```

Benefits:

- Reduces network overhead (fewer HTTP requests)
- Improves Elasticsearch indexing efficiency (bulk API)
- Lower resource usage on both collector and Elasticsearch

### Exporter Configuration

#### Data Stream Naming

**CRITICAL**: Dashboard filters expect this exact data stream configuration:

```yaml
elasticsearch:
  dataset: elasticsearchreceiver.otel  # Must match dashboard filter
  namespace: default
```

This creates data streams like: `metrics-elasticsearchreceiver.otel-default`

The dashboards filter on: `data_stream.dataset == "elasticsearchreceiver.otel"`

**Do not change** these values unless you also update all dashboard YAML files.

**Note**: Do not set the `index` field as it overrides dynamic data stream routing.

#### Retry and Queue Configuration

For reliable data delivery:

```yaml
elasticsearch:
  retry:
    enabled: true
    initial_interval: 5s
    max_interval: 30s
    max_elapsed_time: 300s  # 5 minutes total retry time

  sending_queue:
    enabled: true
    num_consumers: 10   # Parallel workers
    queue_size: 1000    # Buffer size
```

Increase `queue_size` and `num_consumers` for high-throughput environments.

## Troubleshooting

### No Data Appearing in Dashboards

1. **Verify collector is running**:

   ```bash
   curl http://localhost:13133/health
   ```

2. **Check collector logs**:

   ```bash
   docker logs otel-collector
   # Or check logs if running as binary
   ```

3. **Verify data stream exists**:

   ```bash
   curl -u elastic:password "http://localhost:9200/_data_stream/metrics-elasticsearchreceiver.otel-*"
   ```

4. **Query for metrics**:

   ```bash
   curl -u elastic:password "http://localhost:9200/metrics-elasticsearchreceiver.otel-*/_search?pretty" \
     -H 'Content-Type: application/json' \
     -d '{"size": 1, "query": {"match_all": {}}}'
   ```

5. **Check data_stream.dataset field**:

   ```bash
   curl -u elastic:password "http://localhost:9200/metrics-elasticsearchreceiver.otel-*/_search?pretty" \
     -H 'Content-Type: application/json' \
     -d '{
       "size": 0,
       "aggs": {
         "datasets": {
           "terms": {"field": "data_stream.dataset"}
         }
       }
     }'
   ```

   Should return: `"key": "elasticsearchreceiver.otel"`

### Authentication Failures

**Error**: `401 Unauthorized` or `403 Forbidden`

**Solution**: Verify credentials and permissions:

```bash
# Test credentials
curl -u elastic:password "http://localhost:9200/_cluster/health"

# Check user privileges (should include "monitor" or "manage")
curl -u elastic:password "http://localhost:9200/_security/user/elastic"
```

Create a dedicated monitoring user:

```bash
curl -X POST -u elastic:password "http://localhost:9200/_security/user/otel_monitor" \
  -H 'Content-Type: application/json' \
  -d '{
    "password": "your-secure-password",
    "roles": ["monitoring_user"]
  }'
```

### Missing Metrics

**Problem**: Some metrics are missing from dashboards

**Check**:

1. **Elasticsearch version**: Some metrics require specific ES versions
2. **Node configuration**: Some metrics only available on certain node types
3. **Index configuration**: Index metrics require indices to exist

**Debug**:

```bash
# List all collected metric names
curl -u elastic:password "http://localhost:9200/metrics-elasticsearchreceiver.otel-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "metrics": {
        "terms": {"field": "name", "size": 200}
      }
    }
  }'
```

### High Collector Memory Usage

**Problem**: Collector using too much memory

**Solutions**:

1. **Increase collection interval**:

   ```yaml
   collection_interval: 30s  # Was 10s
   ```

2. **Reduce memory limiter**:

   ```yaml
   memory_limiter:
     limit_mib: 256  # Was 512
   ```

3. **Optimize batch size**:

   ```yaml
   batch:
     send_batch_size: 500   # Was 1000
     send_batch_max_size: 1000  # Was 2000
   ```

4. **Limit indices collected**:

   ```yaml
   indices: ["important-index-*"]  # Was ["_all"]
   ```

### High Elasticsearch API Load

**Problem**: Collector causing high load on Elasticsearch

**Solutions**:

1. **Increase collection interval**:

   ```yaml
   collection_interval: 60s  # Reduce API calls
   ```

2. **Collect from fewer nodes**:

   ```yaml
   nodes: ["_local"]  # Instead of ["_all"]
   ```

3. **Skip cluster metrics**:

   ```yaml
   skip_cluster_metrics: true  # Node metrics only
   ```

4. **Limit index collection**:

   ```yaml
   indices: []  # Skip index metrics
   ```

### Dashboard Time Range Issues

**Problem**: Dashboards show "No data"

**Solution**:

1. Check time picker in Kibana (top-right)
2. Ensure time range covers when collector was running
3. Verify `@timestamp` field exists:

   ```bash
   curl -u elastic:password "http://localhost:9200/metrics-elasticsearchreceiver.otel-*/_search?size=1&sort=@timestamp:desc&pretty"
   ```

## Production Deployment Considerations

### High Availability

Deploy multiple collectors with load balancing:

```yaml skip
# Collector 1
resource:
  attributes:
    - key: otel.collector.name
      value: collector-01

# Collector 2
resource:
  attributes:
    - key: otel.collector.name
      value: collector-02
```

Each collector should:

- Use `nodes: ["_all"]` to collect from all nodes
- Export to the same monitoring cluster
- Have identical configuration except collector name

### Resource Allocation

Recommended resources per collector:

| Cluster Size | CPU | Memory | Collection Interval |
| ------------ | --- | ------ | ------------------- |
| < 10 nodes | 0.5 | 256 MB | 10s |
| 10-50 nodes | 1.0 | 512 MB | 30s |
| 50-100 nodes | 2.0 | 1 GB | 30s |
| 100+ nodes | 4.0 | 2 GB | 60s |

### Retention and Rollover

Configure Index Lifecycle Management (ILM) for metric retention:

```bash
# Create ILM policy for metrics
curl -X PUT -u elastic:password "http://localhost:9200/_ilm/policy/metrics-elasticsearch-otel" \
  -H 'Content-Type: application/json' \
  -d '{
    "policy": {
      "phases": {
        "hot": {
          "actions": {
            "rollover": {
              "max_age": "7d",
              "max_size": "50gb"
            }
          }
        },
        "warm": {
          "min_age": "7d",
          "actions": {
            "shrink": {"number_of_shards": 1},
            "forcemerge": {"max_num_segments": 1}
          }
        },
        "delete": {
          "min_age": "30d",
          "actions": {"delete": {}}
        }
      }
    }
  }'
```

Apply to data stream template:

```bash
curl -X PUT -u elastic:password "http://localhost:9200/_index_template/metrics-elasticsearchreceiver.otel" \
  -H 'Content-Type: application/json' \
  -d '{
    "index_patterns": ["metrics-elasticsearchreceiver.otel-*"],
    "data_stream": {},
    "priority": 200,
    "template": {
      "settings": {
        "index.lifecycle.name": "metrics-elasticsearch-otel"
      }
    }
  }'
```

### Monitoring the Collector

Monitor collector health using:

1. **Health check endpoint**: `http://localhost:13133/health`
2. **Metrics endpoint**: `http://localhost:8888/metrics`
3. **Logs**: Set `level: debug` for troubleshooting

Key collector metrics to monitor:

- `otelcol_receiver_accepted_metric_points` - Metrics received
- `otelcol_exporter_sent_metric_points` - Metrics exported
- `otelcol_processor_batch_batch_send_size` - Batch sizes
- `otelcol_exporter_send_failed_metric_points` - Export failures

## Advanced Topics

### Custom Attributes and Filtering

Add environment labels to all metrics:

```yaml
resource:
  attributes:
    - key: deployment.environment
      value: production
      action: insert
    - key: datacenter
      value: us-east-1
      action: insert
    - key: cluster.tier
      value: hot
      action: insert
```

Then filter dashboards by these attributes in Kibana.

### Multiple Elasticsearch Clusters

Monitor multiple clusters with one collector:

```yaml
receivers:
  elasticsearch/prod:
    endpoint: http://prod-cluster:9200
    username: ${env:PROD_ES_USER}
    password: ${env:PROD_ES_PASS}

  elasticsearch/staging:
    endpoint: http://staging-cluster:9200
    username: ${env:STAGING_ES_USER}
    password: ${env:STAGING_ES_PASS}

service:
  pipelines:
    metrics/prod:
      receivers: [elasticsearch/prod]
      processors: [batch]
      exporters: [elasticsearch]

    metrics/staging:
      receivers: [elasticsearch/staging]
      processors: [batch]
      exporters: [elasticsearch]
```

### Integration with Other Signals

Correlate metrics with logs and traces:

```yaml
receivers:
  elasticsearch:
    # ... metrics config ...

  filelog:
    include: [/var/log/elasticsearch/*.log]
    # Parse Elasticsearch logs

  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
    # Receive traces from applications

exporters:
  elasticsearch:
    # Export all signals to Elasticsearch
    logs_dynamic_index:
      enabled: true
    metrics_dynamic_index:
      enabled: true
    traces_dynamic_index:
      enabled: true

service:
  pipelines:
    metrics:
      receivers: [elasticsearch]
      processors: [batch]
      exporters: [elasticsearch]

    logs:
      receivers: [filelog]
      processors: [batch]
      exporters: [elasticsearch]

    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [elasticsearch]
```

## Complete Collector Configuration

The following is a complete, production-ready OpenTelemetry Collector configuration for monitoring Elasticsearch. Save this to a file named `collector-config.yaml`:

```yaml
#
# OpenTelemetry Collector Configuration for Elasticsearch Receiver
#
# This configuration demonstrates how to collect metrics from Elasticsearch using the
# OpenTelemetry Elasticsearch receiver and export them back to Elasticsearch for
# visualization with the companion Kibana dashboards.
#
# Documentation:
# - Elasticsearch Receiver: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/elasticsearchreceiver
# - Elasticsearch Exporter: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/elasticsearchexporter
#
# ==============================================================================
# RECEIVERS
# ==============================================================================
receivers:
  # Elasticsearch receiver collects metrics from Elasticsearch cluster APIs
  # Requires 'monitor' or 'manage' cluster privileges
  elasticsearch:
    # Elasticsearch cluster endpoint (can be any node in the cluster)
    endpoint: ${env:ELASTICSEARCH_ENDPOINT}

    # Authentication credentials
    # OPTION 1: Username/password authentication
    username: ${env:ELASTICSEARCH_USERNAME}
    password: ${env:ELASTICSEARCH_PASSWORD}

    # OPTION 2: API key authentication (uncomment to use)
    # headers:
    #   Authorization: ApiKey ${env:ELASTICSEARCH_API_KEY}

    # Collection interval - how often to scrape metrics
    # Default: 10s
    # Recommendation: 10-30s for most deployments, 60s+ for very large clusters
    collection_interval: 10s

    # Initial delay before first collection (useful for startup coordination)
    initial_delay: 1s

    # Nodes to collect metrics from
    # Options:
    #   ["_all"]   - Collect from all nodes (recommended for complete visibility)
    #   ["_local"] - Collect only from the node specified in endpoint
    #   ["node1", "node2"] - Collect from specific named nodes
    nodes:
      - _all

    # Whether to skip cluster-level metrics collection
    # Set to true if you only need node-level metrics
    skip_cluster_metrics: false

    # Indices to collect metrics from
    # Options:
    #   ["_all"] - Collect from all indices (can be expensive for many indices)
    #   ["index1", "index2"] - Collect from specific indices
    #   ["prefix-*"] - Collect from indices matching pattern
    indices:
      - _all

    # TLS/SSL configuration (uncomment if using HTTPS with custom CA)
    # tls:
    #   ca_file: /path/to/ca.crt
    #   cert_file: /path/to/client.crt
    #   key_file: /path/to/client.key
    #   insecure_skip_verify: false

    # Timeout for API requests
    # timeout: 10s
# ==============================================================================
# PROCESSORS
# ==============================================================================
processors:
  # Batch processor groups metrics before export for improved efficiency
  # This reduces network overhead and API calls to the backend
  batch:
    # Maximum time to wait before sending a batch
    timeout: 10s

    # Maximum number of items in a batch
    send_batch_size: 1000

    # Maximum number of items to keep in memory
    send_batch_max_size: 2000

  # Memory limiter prevents OOM by forcing garbage collection and refusing data
  # Recommended for production deployments
  memory_limiter:
    # Maximum memory allocated to the collector
    limit_mib: 512

    # Memory spike limit (short-term peak usage)
    spike_limit_mib: 128

    # Check interval for memory usage
    check_interval: 1s

  # Resource processor adds metadata about the collector itself
  # Useful for identifying which collector instance generated the metrics
  resource:
    attributes:
      # Add collector identification
      - key: otel.collector.name
        value: ${env:HOSTNAME}
        action: insert

      # Add deployment environment (optional)
      # - key: deployment.environment
      #   value: production
      #   action: insert

  # Attributes processor can transform metric attributes
  # Example: Rename or add labels to metrics
  # attributes:
  #   actions:
  #     - key: environment
  #       value: production
  #       action: insert
# ==============================================================================
# EXPORTERS
# ==============================================================================
exporters:
  # Elasticsearch exporter sends metrics back to Elasticsearch
  # The dashboards expect data in the 'metrics-elasticsearchreceiver.otel' data stream
  elasticsearch:
    # Elasticsearch endpoints for data export
    # Can be the same cluster being monitored (self-monitoring) or a separate cluster
    endpoints:
      - ${env:ELASTICSEARCH_EXPORT_ENDPOINT}

    # Authentication for export
    auth:
      authenticator: basicauth

    # Data stream configuration
    # IMPORTANT: This must match the dashboard filters
    # Dashboards filter on: data_stream.dataset == "elasticsearchreceiver.otel"
    logs_dynamic_index:
      enabled: false
    metrics_dynamic_index:
      enabled: true
    traces_dynamic_index:
      enabled: false

    # Index/data stream naming
    # The default pattern creates: metrics-{dataset}-{namespace}
    # With dataset and namespace below, creates: metrics-elasticsearchreceiver.otel-default
    # Note: Do not set 'index' field here as it overrides dynamic data stream routing

    # Data stream dataset identifier
    # This value appears in the data_stream.dataset field used by dashboard filters
    dataset: elasticsearchreceiver.otel

    # Data stream namespace (defaults to "default")
    namespace: default

    # Retry configuration for failed exports
    retry:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s

    # Queue configuration for buffering before export
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 1000

    # TLS configuration (if exporting to HTTPS endpoint)
    # tls:
    #   insecure_skip_verify: false

    # Timeout for export requests
    # timeout: 90s

    # Bulk indexing configuration
    # flush:
    #   bytes: 5242880  # 5MB
    #   interval: 30s

  # Debug exporter for troubleshooting (optional)
  # Uncomment to log metrics to console
  # logging:
  #   verbosity: detailed
  #   sampling_initial: 5
  #   sampling_thereafter: 200
# ==============================================================================
# EXTENSIONS
# ==============================================================================
extensions:
  # Health check endpoint for monitoring collector health
  health_check:
    endpoint: :13133
    path: /health

  # Performance profiler for debugging (optional)
  pprof:
    endpoint: :1777

  # Zpages for in-process diagnostics (optional)
  zpages:
    endpoint: :55679

  # Basic auth extension for Elasticsearch export authentication
  basicauth:
    client_auth:
      username: ${env:ELASTICSEARCH_EXPORT_USERNAME}
      password: ${env:ELASTICSEARCH_EXPORT_PASSWORD}
# ==============================================================================
# SERVICE CONFIGURATION
# ==============================================================================
service:
  # Enable configured extensions
  extensions:
    - health_check
    - basicauth
    # - pprof  # Uncomment for performance profiling
    # - zpages  # Uncomment for in-process diagnostics

  # Configure telemetry for the collector itself
  telemetry:
    logs:
      level: info
      # Set to "debug" for troubleshooting
      # level: debug
    metrics:
      # Expose collector's own metrics on this address
      address: :8888

  # Define data pipelines
  pipelines:
    # Metrics pipeline: receive → process → export
    metrics:
      receivers:
        - elasticsearch
      processors:
        - memory_limiter  # First: protect collector from OOM
        - resource  # Second: add metadata
        - batch  # Last: batch for efficiency
      exporters:
        - elasticsearch
        # - logging  # Uncomment for debugging
```

## Related Resources

- **OpenTelemetry Documentation**: <https://opentelemetry.io/docs/>
- **Elasticsearch Receiver**: <https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/elasticsearchreceiver>
- **Elasticsearch Exporter**: <https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/elasticsearchexporter>
- **kb-yaml-to-lens**: <https://github.com/strawgate/kb-yaml-to-lens>
- **Elasticsearch Monitoring Guide**: <https://www.elastic.co/guide/en/elasticsearch/reference/current/monitor-elasticsearch-cluster.html>

## Support and Contributing

Found an issue or have a suggestion?

1. **Issues**: Open an issue at <https://github.com/strawgate/kb-yaml-to-lens/issues>
2. **Contributing**: See CONTRIBUTING.md for contribution guidelines

## License

This example is part of the kb-yaml-to-lens project and follows the same license.
