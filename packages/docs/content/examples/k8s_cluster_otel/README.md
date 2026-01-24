# Kubernetes Cluster Receiver Dashboards

Kubernetes cluster monitoring dashboards using OpenTelemetry k8sclusterreceiver metrics, designed for SRE and DevOps workflows.

## Overview

The **k8sclusterreceiver** is an OpenTelemetry Collector receiver that collects cluster-level metrics from the Kubernetes API server. It provides visibility into cluster health, workload status, resource utilization, and autoscaling behavior.

**Important:** The k8sclusterreceiver must be deployed as a **single instance per cluster** to avoid duplicate metrics.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Cluster Overview** | `01-cluster-overview.yaml` | Entry point for cluster health triage |
| **Workload Health** | `02-workload-health.yaml` | Deployment and container health |
| **Resource Allocation** | `03-resource-allocation.yaml` | Capacity planning and quota analysis |
| **Batch Jobs** | `04-batch-jobs.yaml` | Job and CronJob monitoring |
| **Autoscaling** | `05-autoscaling.yaml` | HPA scaling behavior |

All dashboards include navigation links for easy switching between views.

## Prerequisites

- **Kubernetes cluster**: v1.24+
- **OpenTelemetry Collector**: Contrib distribution with k8sclusterreceiver
- **Kibana**: Version 8.x or later
- **Cluster admin permissions**: For RBAC configuration

## Data Requirements

- **Data stream dataset**: `kubernetesclusterreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

### Receiver Configuration

```yaml
receivers:
  k8s_cluster:
    auth_type: serviceAccount
    collection_interval: 10s
    node_conditions_to_report: [Ready]
    distribution: kubernetes
    allocatable_types_to_report: [cpu, memory, ephemeral-storage, storage]
    metadata_collection_interval: 5m

exporters:
  elasticsearch:
    endpoints: ["https://elasticsearch:9200"]
    auth:
      authenticator: basicauth
    mapping:
      mode: ecs

service:
  pipelines:
    metrics:
      receivers: [k8s_cluster]
      processors: [batch, resourcedetection, resource]
      exporters: [elasticsearch]
```

### Receiver Configuration Options

| YAML Key | Type | Description | Default |
|----------|------|-------------|---------|
| `auth_type` | string | Kubernetes API authentication method (`serviceAccount`, `kubeConfig`) | `serviceAccount` |
| `collection_interval` | duration | Metric collection frequency | `10s` |
| `node_conditions_to_report` | list | Node conditions to monitor | `[Ready]` |
| `distribution` | string | Cluster type (`kubernetes`, `openshift`) | `kubernetes` |
| `allocatable_types_to_report` | list | Node resource types to report | `[cpu, memory, ephemeral-storage, storage]` |
| `metadata_collection_interval` | duration | Entity metadata collection frequency | `5m` |

## Metrics Reference

All metrics below are enabled by default.

### Container Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.container.cpu_limit` | Gauge | `{cpu}` | Maximum CPU resource limit for container |
| `k8s.container.cpu_request` | Gauge | `{cpu}` | CPU resources requested for container |
| `k8s.container.memory_limit` | Gauge | `By` | Maximum memory resource limit |
| `k8s.container.memory_request` | Gauge | `By` | Memory resources requested |
| `k8s.container.storage_limit` | Gauge | `By` | Maximum storage resource limit |
| `k8s.container.storage_request` | Gauge | `By` | Storage resources requested |
| `k8s.container.ephemeralstorage_limit` | Gauge | `By` | Maximum ephemeral storage limit |
| `k8s.container.ephemeralstorage_request` | Gauge | `By` | Ephemeral storage requested |
| `k8s.container.ready` | Gauge | — | Whether container passed readiness probe (0/1) |
| `k8s.container.restarts` | Gauge | `{restart}` | Container restart count |

### Pod Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.pod.phase` | Gauge | — | Current pod phase (numeric encoding, see below) |

### Deployment Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.deployment.desired` | Gauge | `{pod}` | Desired pod count in deployment |
| `k8s.deployment.available` | Gauge | `{pod}` | Available pods (ready for minReadySeconds) |

### StatefulSet Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.statefulset.desired_pods` | Gauge | `{pod}` | Desired pods (spec.replicas) |
| `k8s.statefulset.ready_pods` | Gauge | `{pod}` | Pods with Ready condition |
| `k8s.statefulset.current_pods` | Gauge | `{pod}` | Pods created from StatefulSet version |
| `k8s.statefulset.updated_pods` | Gauge | `{pod}` | Pods created from current version |

### DaemonSet Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.daemonset.desired_scheduled_nodes` | Gauge | `{node}` | Nodes that should run daemon pods |
| `k8s.daemonset.current_scheduled_nodes` | Gauge | `{node}` | Nodes running daemon pods as intended |
| `k8s.daemonset.ready_nodes` | Gauge | `{node}` | Nodes with ready daemon pods |
| `k8s.daemonset.misscheduled_nodes` | Gauge | `{node}` | Nodes running daemon pods incorrectly |

### ReplicaSet Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.replicaset.desired` | Gauge | `{pod}` | Desired pod count in replicaset |
| `k8s.replicaset.available` | Gauge | `{pod}` | Available pods targeted by replicaset |

### Job Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.job.active_pods` | Gauge | `{pod}` | Actively running job pods |
| `k8s.job.desired_successful_pods` | Gauge | `{pod}` | Desired successful pod count |
| `k8s.job.successful_pods` | Gauge | `{pod}` | Pods in Succeeded phase |
| `k8s.job.failed_pods` | Gauge | `{pod}` | Pods in Failed phase |
| `k8s.job.max_parallel_pods` | Gauge | `{pod}` | Maximum concurrent pods |

### CronJob Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.cronjob.active_jobs` | Gauge | `{job}` | Count of actively running jobs |

### HPA Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.hpa.current_replicas` | Gauge | `{pod}` | Current pod replicas managed by autoscaler |
| `k8s.hpa.desired_replicas` | Gauge | `{pod}` | Desired pod replicas for autoscaler |
| `k8s.hpa.min_replicas` | Gauge | `{pod}` | Minimum autoscaler replica count |
| `k8s.hpa.max_replicas` | Gauge | `{pod}` | Maximum autoscaler replica count |

### Resource Quota Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `k8s.resource_quota.hard_limit` | Gauge | `{resource}` | Upper resource limit in namespace quota | `resource` |
| `k8s.resource_quota.used` | Gauge | `{resource}` | Resource usage against quota | `resource` |

### Namespace Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `k8s.namespace.phase` | Gauge | — | Current phase (1=active, 0=terminating) |

### Optional Metrics (disabled by default)

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `k8s.container.status.reason` | Sum | `{container}` | Container count by status reason | `k8s.container.status.reason` |
| `k8s.container.status.state` | Sum | `{container}` | Container count by state | `k8s.container.status.state` |
| `k8s.node.condition` | Gauge | `{condition}` | Node condition status | `condition` |
| `k8s.pod.status_reason` | Gauge | — | Pod status reason (numeric encoding) | — |

### Phase Value Encoding

The `k8s.pod.phase` metric uses numeric values:

| Value | Phase |
|-------|-------|
| `1` | Pending |
| `2` | Running |
| `3` | Succeeded |
| `4` | Failed |
| `5` | Unknown |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `resource` | `cpu`, `memory`, `pods`, `requests.cpu`, `requests.memory`, `limits.cpu`, `limits.memory` | Resource quota type |
| `k8s.container.status.reason` | `ContainerCreating`, `CrashLoopBackOff`, `CreateContainerConfigError`, `ErrImagePull`, `ImagePullBackOff`, `OOMKilled`, `Completed`, `Error`, `ContainerCannotRun` | Container status reason |
| `k8s.container.status.state` | `terminated`, `running`, `waiting` | Container state |
| `condition` | `Ready`, `MemoryPressure`, `PIDPressure`, `DiskPressure` | Node condition |

## Related Resources

- [OpenTelemetry k8sclusterreceiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8sclusterreceiver)
- [k8sclusterreceiver Metrics Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/receiver/k8sclusterreceiver/documentation.md)
