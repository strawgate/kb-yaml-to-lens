# CrowdStrike Modern Dashboards

Workflow-centric security operations dashboards designed for modern SOC workflows.

## Overview

Unlike the dataset-centric [CrowdStrike dashboards](../crowdstrike/README.md), these modern dashboards are organized by security workflow rather than data source, making them ideal for daily SOC operations.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **SOC Dashboard** | `soc.yaml` | Real-time security event monitoring, alert triage, and incident response coordination |
| **Threat Investigation** | `threat-investigation.yaml` | Deep-dive threat analysis with MITRE ATT&CK mapping and IOC tracking |
| **Asset & Vulnerability** | `asset-vulnerability.yaml` | Asset inventory and vulnerability tracking for risk assessment and patch prioritization |
| **Compliance & Audit** | `compliance-audit.yaml` | Compliance monitoring and audit trail analysis for regulatory reporting |

All dashboards include consistent navigation for seamless workflow transitions.

## Prerequisites

- **CrowdStrike Falcon**: EDR solution with data streaming enabled
- **Elastic Agent**: With CrowdStrike integration configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data view**: `logs-*`
- **Data stream datasets**: `crowdstrike.alert`, `crowdstrike.falcon`, `crowdstrike.fdr`

## Related

See also: [CrowdStrike Dashboards](../crowdstrike/README.md) for dataset-centric dashboards organized by data source.
