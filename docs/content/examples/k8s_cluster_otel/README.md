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
