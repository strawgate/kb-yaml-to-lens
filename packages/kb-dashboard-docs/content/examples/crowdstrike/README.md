# CrowdStrike Security Dashboards

Security monitoring dashboards for CrowdStrike EDR data streams.

## Overview

These dashboards provide visibility into CrowdStrike Falcon EDR alerts, incidents, vulnerabilities, and host data. Each dashboard focuses on a specific data stream or security domain.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/crowdstrike) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `overview.yaml` | High-level entry point with navigation to all CrowdStrike dashboards |
| **Alert** | `alert.yaml` | Comprehensive alert monitoring with status, severity, IOCs, and network context |
| **Falcon Overview** | `falcon-overview.yaml` | Falcon incidents with MITRE ATT&CK technique and tactic mapping |
| **FDR Overview** | `fdr-overview.yaml` | Falcon Data Replicator events and alerts monitoring |
| **Host** | `host.yaml` | Host device monitoring with OS platform distribution and activity tracking |
| **Vulnerability** | `vulnerability.yaml` | Vulnerability tracking with severity, status, and confidence breakdowns |

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Overview (overview.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/overview.yaml"
    ```

??? example "Alert (alert.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/alert.yaml"
    ```

??? example "Falcon Overview (falcon-overview.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/falcon-overview.yaml"
    ```

??? example "FDR Overview (fdr-overview.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/fdr-overview.yaml"
    ```

??? example "Host (host.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/host.yaml"
    ```

??? example "Vulnerability (vulnerability.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/vulnerability.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Prerequisites

- **CrowdStrike Falcon**: EDR solution with data streaming enabled
- **Elastic Agent**: With CrowdStrike integration configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data view**: `logs-*`
- **Data stream datasets**: `crowdstrike.fdr`, `crowdstrike.falcon`, `crowdstrike.alert`, `crowdstrike.host`, `crowdstrike.vulnerability`

## Related

See also: [CrowdStrike Modern Dashboards](../crowdstrike-modern/README.md) for workflow-centric SOC dashboards.
