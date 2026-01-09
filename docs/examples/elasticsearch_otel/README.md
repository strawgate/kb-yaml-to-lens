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

Then uncomment the API key section in `otel-collector-config.yaml`.

### Step 2: Run OpenTelemetry Collector

#### Using Docker

```bash
docker run -d \
  --name otel-collector \
  --env-file .env \
  -p 13133:13133 \
  -p 8888:8888 \
  -v $(pwd)/otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml \
  otel/opentelemetry-collector-contrib:latest
```

#### Using Binary

```bash
# Download and extract the collector
# https://github.com/open-telemetry/opentelemetry-collector-releases/releases

./otelcol-contrib --config=otel-collector-config.yaml
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
# Compile all dashboards at once
for file in *.yaml; do
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
- **Garbage Collection**: `jvm.gc.collections.count`, `jvm.gc.collections.elapsed` (by collector_name attribute)
- **Threads**: `jvm.threads.count`
- **Classes**: `jvm.classes.loaded`
- **Memory Pools**: `jvm.memory.pool.used`, `jvm.memory.pool.max` (by pool_name attribute)

#### Index Metrics

- **Size**: Index size, shard size, segment size
- **Segments**: Segment count, segment memory
- **Operations**: Index rate, search rate, merge rate, refresh rate, flush rate, query cache operations
- **Documents**: Total docs per index

#### Circuit Breaker Metrics

**Note:** Circuit breaker metrics use `elasticsearch.breaker.*` prefix (no `.node` in path)

- **Memory**: `elasticsearch.breaker.memory.estimated`, `elasticsearch.breaker.memory.limit`
- **Trips**: `elasticsearch.breaker.tripped` (breaker activation events)
- **Breakers**: Parent, request, fielddata, in-flight requests, accounting, model inference (by circuit_breaker_name attribute)

All metrics include dimensional attributes for filtering:

- `elasticsearch.cluster.name` - Cluster identifier
- `elasticsearch.node.name` - Node identifier
- `elasticsearch.index.name` - Index name
- `cache_name` - Cache type (fielddata, query, request)
- `thread_pool_name` - Thread pool type (search, write, get, etc.)
- `circuit_breaker_name` - Circuit breaker type
- `collector_name` - GC collector name
- `pool_name` - JVM memory pool name
- `operation` - Operation type (read, write, index, search, etc.)

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
