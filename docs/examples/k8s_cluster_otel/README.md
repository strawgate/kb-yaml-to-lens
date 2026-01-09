# Kubernetes Cluster Receiver Dashboards

Comprehensive Kubernetes cluster monitoring dashboards using OpenTelemetry k8sclusterreceiver metrics, designed for SRE and DevOps workflows.

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

### Receiver Configuration Options

| YAML Key | Type | Description | Default | Required |
|----------|------|-------------|---------|----------|
| `auth_type` | string | Kubernetes API authentication method (`serviceAccount`, `kubeConfig`) | `serviceAccount` | No |
| `collection_interval` | duration | Metric collection frequency | `10s` | No |
| `node_conditions_to_report` | list | Node conditions to monitor | `[Ready]` | No |
| `distribution` | string | Cluster type (`kubernetes`, `openshift`) | `kubernetes` | No |
| `allocatable_types_to_report` | list | Node resource types to report | `[cpu, memory, ephemeral-storage, storage]` | No |
| `metadata_collection_interval` | duration | Entity metadata collection frequency | `5m` | No |
| `namespaces` | list | Limit observation to specific namespaces | (cluster-wide) | No |
| `k8s_leader_elector` | string | K8s leader elector extension for HA mode | (disabled) | No |

For additional metric and attribute filtering options, consult the [official k8sclusterreceiver documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8sclusterreceiver).

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

### Minimal Configuration Example

For a quick start with default settings:

```yaml
receivers:
  k8s_cluster:

exporters:
  elasticsearch:
    endpoints: ["https://elasticsearch:9200"]

service:
  pipelines:
    metrics:
      receivers: [k8s_cluster]
      exporters: [elasticsearch]
```

### Complete Configuration Example

Here's a complete OpenTelemetry Collector configuration with all recommended options:

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
          image: otel/opentelemetry-collector-contrib:0.143.1
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

### Import Dashboards

This example includes 5 focused dashboards designed for SRE/DevOps workflows:

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `01-cluster-overview.yaml` | Entry point for cluster health triage |
| **Workloads** | `02-workload-health.yaml` | Deployment and container health |
| **Resources** | `03-resource-allocation.yaml` | Capacity planning and quota analysis |
| **Batch Jobs** | `04-batch-jobs.yaml` | Job and CronJob monitoring |
| **Autoscaling** | `05-autoscaling.yaml` | HPA scaling behavior |

**Option 1: Compile and Upload All Dashboards**

```bash
# From the repository root
cd compiler

# Compile and upload all dashboards
uv run kb-dashboard compile \
  --input-dir ../docs/examples/k8s_cluster_otel/ \
  --upload \
  --kibana-url https://your-kibana:5601 \
  --kibana-username elastic \
  --kibana-password your-password
```

**Option 2: Compile and Manually Import**

```bash
# Compile all dashboards
cd compiler
uv run kb-dashboard compile \
  --input-dir ../docs/examples/k8s_cluster_otel/ \
  --output-dir /tmp/k8s-dashboards/
```

Then import in Kibana:
1. Navigate to **Stack Management > Saved Objects**
2. Click **Import**
3. Select the generated `/tmp/k8s-dashboards/compiled_dashboards.ndjson` file
4. Click **Import**

## Dashboard Overview

This example provides comprehensive cluster monitoring across 5 focused dashboards, each designed for specific SRE/DevOps workflows. All dashboards include consistent navigation links at the top for easy switching between views.

### 1. Cluster Overview (`01-cluster-overview.yaml`)

**Purpose:** Entry point for incident triage - "Is my cluster healthy? Where should I look?"

**Key Panels:**
- **Cluster Health:** Running pods (green), pending pods (yellow), failed pods (red), container restarts
- **Pod Health Distribution:** Donut chart showing pod phase breakdown
- **Pod Health Over Time:** Stacked area chart of pod phases
- **Workload Health Preview:** Deployments desired vs available, restarts by namespace
- **Unhealthy Deployments:** Table showing deployments with missing replicas

**Controls:** Namespace filter for broad filtering

**SRE Workflow:** Start here during incidents. Red/yellow metrics indicate where to drill down to other dashboards.

---

### 2. Workload Health (`02-workload-health.yaml`)

**Purpose:** Application health monitoring - "Are my deployments healthy? What's crashing?"

**Key Panels:**
- **Container Health:** Ready vs not ready containers, restarts, and restarting containers
- **Deployment Health:** Desired vs available replicas for Deployments, StatefulSets, DaemonSets, ReplicaSets
- **Container Analysis:** Readiness over time, top restarting containers
- **Workload Details:** Detailed status tables for Deployments and StatefulSets

**Controls:** Namespace and Deployment filters for app-specific analysis

**SRE Workflow:** Use when investigating deployment rollout issues, scaling problems, container crashes, or readiness probe failures.

---

### 3. Resource Allocation (`03-resource-allocation.yaml`)

**Purpose:** Capacity planning and resource analysis - "Am I running out of resources?"

**Key Panels:**
- **Cluster Capacity:** CPU, memory, and storage requests vs limits over time
- **Resource Quotas:** Quota usage by resource type (used vs available)
- **Namespace Allocation:** CPU and memory allocation by namespace
- **Pod Details:** Comprehensive resource summary table

**Controls:** Namespace and Node filters for capacity segmentation

**SRE Workflow:** Use when investigating OOMKilled pods, analyzing resource quotas, or identifying over/under-provisioned workloads.

---

### 4. Batch Jobs (`04-batch-jobs.yaml`)

**Purpose:** Job and CronJob monitoring - "Are my jobs completing? What's failing?"

**Key Panels:**
- **Job Summary:** Active, successful, and failed job counts; CronJob activity
- **Completion Trends:** Job success/failure patterns over time
- **Job Details:** Detailed status table with per-job metrics

**Controls:** Namespace and Job filters for job-specific analysis

**SRE Workflow:** Use for monitoring batch processing, data pipelines, scheduled maintenance tasks, and investigating job failures.

---

### 5. Autoscaling (`05-autoscaling.yaml`)

**Purpose:** HPA behavior analysis - "Is autoscaling working? Am I hitting limits?"

**Key Panels:**
- **HPA Summary:** Total HPAs, current/desired replicas, max limits
- **Scaling Trends:** Replica scaling behavior and capacity over time
- **HPA Details:** Per-HPA configuration and status table

**Controls:** Namespace and HPA filters for autoscaler-specific analysis

**SRE Workflow:** Use during traffic spikes, capacity planning, and investigating why workloads aren't scaling properly.

---

### Navigation

All dashboards include a navigation panel at the top with links to:
- **Overview** - Cluster health triage
- **Workloads** - Application health
- **Resources** - Capacity planning
- **Batch Jobs** - Job monitoring
- **Autoscaling** - HPA behavior

This allows seamless navigation between dashboards during incident investigation.

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

The `k8s.pod.phase` attribute in the dashboard uses numeric filter values that may need to be updated to match your data stream's encoding:
- `'1'` - Pending (Pod has been accepted but is not yet running)
- `'2'` - Running (Pod is actively running)
- `'3'` - Succeeded (All containers terminated successfully)
- `'4'` - Failed (At least one container terminated with failure)
- `'5'` - Unknown (Pod status cannot be determined)

**Note:** The OpenTelemetry k8sclusterreceiver semantic conventions use `k8s.pod.status.phase` with string values (`Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`). If your collector outputs string values, you'll need to update the dashboard filters from numeric (`'1'`, `'2'`, etc.) to string values (`'Pending'`, `'Running'`, etc.).

### Namespace Phase Values

The `k8s.namespace.phase` attribute in the dashboard uses numeric filter values:
- `'1'` - Active (Namespace is active and available)
- `'0'` - Terminating (Namespace is being deleted)

**Note:** If your k8sclusterreceiver outputs string values (`Active`, `Terminating`), update the dashboard filters accordingly.

### Container Ready Values

The `k8s.container.ready` attribute in the dashboard uses numeric filter values:
- `'1'` - Ready (Container is ready to serve requests)
- `'0'` - Not ready (Container is not ready)

**Note:** If your k8sclusterreceiver outputs string boolean values (`true`, `false`), update the dashboard filters accordingly.

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
2. **Throttling from API server** - Check for rate-limiting in collector logs
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
