# Kubernetes Cluster Receiver Dashboard

Comprehensive Kubernetes cluster monitoring dashboard using OpenTelemetry k8sclusterreceiver metrics.

## Overview

The **k8sclusterreceiver** is an OpenTelemetry Collector receiver that collects cluster-level metrics from the Kubernetes API server. It provides comprehensive visibility into cluster health, workload status, resource utilization, and autoscaling behavior.

### What Metrics Does It Collect?

The k8sclusterreceiver collects 50+ metrics across multiple categories:

- **Container metrics** - CPU/memory/storage requests and limits, readiness status, restart counts
- **Pod metrics** - Pod phase and status tracking
- **Workload controllers** - Deployments, StatefulSets, DaemonSets, ReplicaSets
- **Batch workloads** - Jobs and CronJobs
- **Autoscaling** - Horizontal Pod Autoscaler (HPA) metrics
- **Resource quotas** - Namespace-level resource limits and usage
- **Cluster resources** - Namespace and node information

### Deployment Model

**IMPORTANT:** The k8sclusterreceiver must be deployed as a **single instance per cluster**. Multiple instances will result in duplicate metrics and incorrect aggregations.

This single-instance architecture is required because:
- The receiver polls the Kubernetes API server for cluster-wide state
- Multiple instances would emit duplicate metric data points
- Cluster-level metrics cannot be safely distributed across multiple collectors

For high availability scenarios with multiple collector instances, configure leader election (advanced configuration not covered here).

## Prerequisites

Before deploying this dashboard, ensure you have:

- **Kubernetes cluster** (v1.24+)
- **OpenTelemetry Collector** (Contrib distribution required)
- **Kibana** (8.x or later)
- **Cluster admin permissions** (for RBAC configuration)

## RBAC Configuration

The k8sclusterreceiver requires cluster-level read permissions to query the Kubernetes API.

### ServiceAccount

Create a dedicated ServiceAccount for the OpenTelemetry Collector:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: otel-collector
  namespace: monitoring
```

### ClusterRole

Create a ClusterRole with the required permissions:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: otel-k8s-cluster-receiver
rules:
  # Core API resources
  - apiGroups: [""]
    resources:
      - events
      - namespaces
      - nodes
      - pods
      - replicationcontrollers
      - resourcequotas
      - services
    verbs: ["get", "list", "watch"]

  # Apps API resources
  - apiGroups: ["apps"]
    resources:
      - daemonsets
      - deployments
      - replicasets
      - statefulsets
    verbs: ["get", "list", "watch"]

  # Batch API resources
  - apiGroups: ["batch"]
    resources:
      - jobs
      - cronjobs
    verbs: ["get", "list", "watch"]

  # Autoscaling API resources
  - apiGroups: ["autoscaling"]
    resources:
      - horizontalpodautoscalers
    verbs: ["get", "list", "watch"]
```

### ClusterRoleBinding

Bind the ClusterRole to the ServiceAccount:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: otel-k8s-cluster-receiver
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: otel-k8s-cluster-receiver
subjects:
  - kind: ServiceAccount
    name: otel-collector
    namespace: monitoring
```

### Namespace-Scoped Alternative

For observing specific namespaces only, you can use namespace-scoped Roles and RoleBindings instead of ClusterRole. Note that cluster-scoped resources (nodes, namespaces, ClusterResourceQuotas) will not be accessible with this approach.

## OpenTelemetry Collector Configuration

### Receiver Configuration

Add the k8sclusterreceiver to your collector configuration:

```yaml
receivers:
  k8s_cluster:
    auth_type: serviceAccount
    collection_interval: 10s
    node_conditions_to_report: [Ready]
    distribution: kubernetes
    allocatable_types_to_report: [cpu, memory, ephemeral-storage, storage]
    metadata_collection_interval: 5m
```

**Important settings:**

- `auth_type: serviceAccount` - Use the ServiceAccount credentials for API authentication
- `collection_interval: 10s` - How often to collect metrics (default: 10s)
- `node_conditions_to_report` - Which node conditions to monitor (default: [Ready])
- `distribution: kubernetes` - Cluster distribution type (kubernetes, openshift)
- `allocatable_types_to_report` - Node resource types to report
- `metadata_collection_interval: 5m` - How often to collect entity metadata (default: 5m)

### Exporters Configuration

Configure exporters to send metrics to Elasticsearch:

```yaml
exporters:
  elasticsearch:
    endpoints: ["https://elasticsearch:9200"]
    auth:
      authenticator: basicauth
    logs_index: logs-generic-default
    metrics_index: metrics-generic-default
    traces_index: traces-generic-default
    mapping:
      mode: ecs
```

Alternatively, use the OTLP exporter if sending to Kibana's OTLP endpoint:

```yaml
exporters:
  otlp/elastic:
    endpoint: https://kibana:8220
    headers:
      Authorization: "Bearer ${ELASTIC_APM_SECRET_TOKEN}"
```

### Service Pipeline Configuration

Configure the pipeline to process and export metrics:

```yaml
service:
  pipelines:
    metrics:
      receivers: [k8s_cluster]
      processors: [batch, resourcedetection, resource]
      exporters: [elasticsearch]
```

### Complete Configuration Example

Here's a complete OpenTelemetry Collector configuration:

```yaml
receivers:
  k8s_cluster:
    auth_type: serviceAccount
    collection_interval: 10s
    node_conditions_to_report: [Ready]
    distribution: kubernetes

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

  resourcedetection:
    detectors: [env, system]

  resource:
    attributes:
      - key: deployment.environment
        value: production
        action: insert

exporters:
  elasticsearch:
    endpoints: ["https://elasticsearch:9200"]
    auth:
      authenticator: basicauth

service:
  pipelines:
    metrics:
      receivers: [k8s_cluster]
      processors: [batch, resourcedetection, resource]
      exporters: [elasticsearch]
```

## Deployment

Deploy the OpenTelemetry Collector as a single-replica Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-k8s-cluster-receiver
  namespace: monitoring
spec:
  replicas: 1  # MUST be 1 - see "Deployment Model" section
  selector:
    matchLabels:
      app: otel-k8s-cluster-receiver
  template:
    metadata:
      labels:
        app: otel-k8s-cluster-receiver
    spec:
      serviceAccountName: otel-collector
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:0.142.0
          args:
            - --config=/conf/config.yaml
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: config
              mountPath: /conf
      volumes:
        - name: config
          configMap:
            name: otel-collector-config
```

**Resource Recommendations:**

- **CPU Request:** 100m (can burst to 500m)
- **Memory Request:** 256Mi (limit: 512Mi)
- **Storage:** Not required (stateless)

**Why Single Replica?**

As mentioned earlier, the k8sclusterreceiver queries cluster-wide state from the Kubernetes API. Running multiple instances would:
- Generate duplicate metrics for every resource
- Increase API server load unnecessarily
- Produce incorrect aggregations in dashboards

**Advanced: Leader Election for Multi-Instance**

For high availability with multiple collector instances, configure leader election so only one instance actively collects metrics at a time. This is an advanced configuration requiring additional setup - consult the [OpenTelemetry Collector documentation](https://opentelemetry.io/docs/collector/) for details.

## Kibana Setup

### Create Data View

1. Navigate to **Stack Management > Data Views** in Kibana
2. Click **Create data view**
3. Configure:
   - **Name:** `Kubernetes Cluster Metrics`
   - **Index pattern:** `metrics-*`
   - **Timestamp field:** `@timestamp`
4. Click **Save data view to Kibana**

### Import Dashboard

The dashboard is defined in the `01-cluster-overview.yaml` file in this directory.

**Option 1: Compile and Upload**

```bash
# From the repository root
cd compiler

# Compile the dashboard to NDJSON
uv run dashboard_compiler compile ../docs/examples/k8s_cluster_otel/01-cluster-overview.yaml -o /tmp/k8s-cluster-dashboard.ndjson

# Upload to Kibana (replace with your Kibana URL and credentials)
uv run dashboard_compiler upload /tmp/k8s-cluster-dashboard.ndjson \
  --kibana-url https://your-kibana:5601 \
  --username elastic \
  --password your-password
```

**Option 2: Compile and Manually Import**

```bash
# Compile the dashboard
cd compiler
uv run dashboard_compiler compile ../docs/examples/k8s_cluster_otel/01-cluster-overview.yaml -o /tmp/k8s-cluster-dashboard.ndjson
```

Then import in Kibana:
1. Navigate to **Stack Management > Saved Objects**
2. Click **Import**
3. Select the generated `/tmp/k8s-cluster-dashboard.ndjson` file
4. Click **Import**

## Dashboard Overview

The dashboard provides comprehensive cluster monitoring across seven key sections:

### 1. Cluster Overview
High-level cluster health and resource statistics:
- Total nodes, pods, namespaces, deployments
- Pod distribution by phase (Pending, Running, Succeeded, Failed, Unknown)
- Workload controller types (Deployments, StatefulSets, DaemonSets, ReplicaSets)

### 2. Resource Utilization
Container resource requests and limits across the cluster:
- CPU requests vs limits over time
- Memory requests vs limits over time
- Storage requests vs limits over time
- Resource quota usage by resource type

### 3. Workload Health
Pod status distribution and container health metrics:
- Running, pending, and failed pod counts
- Container restart counts
- Pod status trends over time
- Container restart rate by namespace

### 4. Deployment Status
Deployment, StatefulSet, DaemonSet, and ReplicaSet health:
- Desired vs available replicas for each controller type
- Current vs ready pods for StatefulSets
- Desired vs ready nodes for DaemonSets
- Detailed status tables for deployments and StatefulSets

### 5. Job & CronJob Status
Batch workload execution and completion tracking:
- Active, successful, and failed job counts
- CronJob active jobs
- Job completion trends over time
- Detailed job status table

### 6. HPA Monitoring
Horizontal Pod Autoscaler scaling behavior and replica management:
- Total HPAs and replica counts
- Current vs desired replicas over time
- Min/current/max replica limits

### 7. Container Analysis
Container readiness, restarts, and resource allocation:
- Ready vs not ready container counts
- Container readiness trends over time
- Top containers by restart count
- CPU and memory resource allocation by namespace
- Container counts and resource summary by pod

### Interactive Controls

The dashboard includes four interactive controls for filtering:

- **Namespace** - Filter by Kubernetes namespace
- **Node** - Filter by node name
- **Deployment** - Filter by deployment name
- **Pod** - Filter by pod name

All panels automatically respond to control selections, enabling focused analysis of specific cluster components.

## Metrics Reference

For complete documentation of all metrics collected by the k8sclusterreceiver, see:

- [k8sclusterreceiver README](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8sclusterreceiver)
- [k8sclusterreceiver Metrics Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/receiver/k8sclusterreceiver/documentation.md)

### Metric Categories Summary

| Category | Example Metrics | Description |
|----------|----------------|-------------|
| **Containers** | `k8s.container.cpu_limit`, `k8s.container.memory_request`, `k8s.container.restarts` | Container resource allocation and health |
| **Pods** | `k8s.pod.phase` | Pod lifecycle status |
| **Deployments** | `k8s.deployment.desired`, `k8s.deployment.available` | Deployment replica status |
| **StatefulSets** | `k8s.statefulset.desired_pods`, `k8s.statefulset.ready_pods` | StatefulSet pod status |
| **DaemonSets** | `k8s.daemonset.desired_scheduled_nodes`, `k8s.daemonset.ready_nodes` | DaemonSet node coverage |
| **ReplicaSets** | `k8s.replicaset.desired`, `k8s.replicaset.available` | ReplicaSet replica status |
| **Jobs** | `k8s.job.active_pods`, `k8s.job.successful_pods`, `k8s.job.failed_pods` | Job execution status |
| **CronJobs** | `k8s.cronjob.active_jobs` | Scheduled job status |
| **HPAs** | `k8s.hpa.current_replicas`, `k8s.hpa.desired_replicas` | Autoscaling behavior |
| **Resource Quotas** | `k8s.resource_quota.hard_limit`, `k8s.resource_quota.used` | Namespace resource limits |
| **Namespaces** | `k8s.namespace.phase` | Namespace status |

### Pod Phase Values

The `k8s.pod.status.phase` attribute uses string values from the Kubernetes PodStatus.phase field:
- `Pending` - Pod has been accepted but is not yet running
- `Running` - Pod is actively running
- `Succeeded` - All containers terminated successfully
- `Failed` - At least one container terminated with failure
- `Unknown` - Pod status cannot be determined

Note: The dashboard uses numeric filter values (`'1'`, `'2'`, etc.) which may need to be updated to match your data stream's encoding. If your k8sclusterreceiver outputs string phase values, update the dashboard filters accordingly.

### Namespace Phase Values

The `k8s.namespace.phase` attribute uses string values:
- `Active` - Namespace is active and available
- `Terminating` - Namespace is being deleted

Note: The dashboard uses numeric filter values (`'1'` for Active, `'0'` for Terminating) which may need to be updated to match your data stream's encoding.

### Container Ready Values

The `k8s.container.ready` attribute uses string boolean values:
- `true` - Container is ready to serve requests
- `false` - Container is not ready

Note: The dashboard uses numeric filter values (`'1'` for ready, `'0'` for not ready) which may need to be updated to match your data stream's encoding.

## Troubleshooting

### Common Issues

#### No Data Appearing in Kibana

1. **Verify collector is running:**
   ```bash
   kubectl get pods -n monitoring -l app=otel-k8s-cluster-receiver
   kubectl logs -n monitoring -l app=otel-k8s-cluster-receiver
   ```

2. **Check collector configuration:**
   ```bash
   kubectl get configmap -n monitoring otel-collector-config -o yaml
   ```

3. **Verify metrics are being exported:**
   ```bash
   # Check collector logs for export errors
   kubectl logs -n monitoring -l app=otel-k8s-cluster-receiver | grep -i error
   ```

4. **Verify data view exists:**
   - Navigate to **Stack Management > Data Views**
   - Confirm `metrics-*` data view exists
   - Check that `@timestamp` is set as the time field

#### RBAC Permission Errors

If you see permission errors in the collector logs:

```
Error: ... is forbidden: User "system:serviceaccount:monitoring:otel-collector" cannot list resource ...
```

**Solution:**

1. Verify the ServiceAccount exists:
   ```bash
   kubectl get serviceaccount -n monitoring otel-collector
   ```

2. Verify the ClusterRole exists and has correct permissions:
   ```bash
   kubectl get clusterrole otel-k8s-cluster-receiver -o yaml
   ```

3. Verify the ClusterRoleBinding exists and links the ServiceAccount to the ClusterRole:
   ```bash
   kubectl get clusterrolebinding otel-k8s-cluster-receiver -o yaml
   ```

4. Ensure the deployment is using the correct ServiceAccount:
   ```bash
   kubectl get deployment -n monitoring otel-k8s-cluster-receiver -o yaml | grep serviceAccountName
   ```

#### Duplicate Metrics

If you're seeing duplicate or multiplied metric values:

**Cause:** Multiple collector instances are running simultaneously.

**Solution:**

1. Verify replica count:
   ```bash
   kubectl get deployment -n monitoring otel-k8s-cluster-receiver
   ```

2. Scale down to exactly 1 replica:
   ```bash
   kubectl scale deployment -n monitoring otel-k8s-cluster-receiver --replicas=1
   ```

3. Update the deployment YAML to set `replicas: 1`

#### Metrics Delayed or Missing

If metrics appear delayed or some are missing:

**Potential causes:**

1. **Collection interval too high** - Reduce `collection_interval` in receiver config (default: 10s)
2. **API server throttling** - Check for rate limiting in collector logs
3. **Network issues** - Verify connectivity between collector and Kubernetes API
4. **Resource constraints** - Check collector CPU/memory usage and increase if needed

### How to Verify Data Collection

#### Check Elasticsearch Indices

Verify metrics are being written to Elasticsearch:

```bash
# List metrics indices
curl -X GET "https://elasticsearch:9200/_cat/indices/metrics-*?v"

# Query recent k8s cluster metrics
curl -X GET "https://elasticsearch:9200/metrics-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "data_stream.dataset": "kubernetesclusterreceiver.otel" } },
        { "range": { "@timestamp": { "gte": "now-5m" } } }
      ]
    }
  },
  "size": 10,
  "sort": [{ "@timestamp": "desc" }]
}
'
```

#### Check Kibana Discover

1. Navigate to **Analytics > Discover** in Kibana
2. Select the `metrics-*` data view
3. Add filter: `data_stream.dataset: kubernetesclusterreceiver.otel`
4. Verify recent documents appear

#### Check Specific Metrics

Search for specific metrics to verify they're being collected:

1. In Kibana Discover, add additional filters:
   - `exists: k8s.pod.name` - Verify pod metrics
   - `exists: k8s.deployment.name` - Verify deployment metrics
   - `exists: k8s.node.name` - Verify node metrics

## Additional Resources

- [OpenTelemetry Collector Documentation](https://opentelemetry.io/docs/collector/)
- [OpenTelemetry Collector Contrib Repository](https://github.com/open-telemetry/opentelemetry-collector-contrib)
- [k8sclusterreceiver Source Code](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8sclusterreceiver)
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Elastic Common Schema (ECS)](https://www.elastic.co/guide/en/ecs/current/index.html)
