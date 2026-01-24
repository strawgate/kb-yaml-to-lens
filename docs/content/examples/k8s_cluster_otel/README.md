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

## Metrics Reference

For complete documentation, see [k8sclusterreceiver Metrics Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/receiver/k8sclusterreceiver/documentation.md).

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

### Phase Value Encoding

The `k8s.pod.phase` attribute uses numeric filter values:

- `'1'` - Pending
- `'2'` - Running
- `'3'` - Succeeded
- `'4'` - Failed
- `'5'` - Unknown

**Note:** If your k8sclusterreceiver outputs string values (`Pending`, `Running`, etc.), update the dashboard filters accordingly.

## Usage

1. Configure RBAC permissions for the OpenTelemetry Collector ServiceAccount
2. Configure the k8sclusterreceiver in your OpenTelemetry Collector
3. Ensure metrics are being sent to Elasticsearch
4. Compile and upload the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/k8s_cluster_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry k8sclusterreceiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/k8sclusterreceiver)
- [k8sclusterreceiver Metrics Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/receiver/k8sclusterreceiver/documentation.md)
