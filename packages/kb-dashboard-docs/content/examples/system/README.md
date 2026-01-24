# System Integration Dashboards (Classic)

Comprehensive monitoring dashboards for the Elastic System integration.

## Overview

These dashboards provide monitoring for Linux/Unix systems, Windows systems, and Windows security events using the Elastic Agent System integration.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/system) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

### Metrics Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Metrics Overview** | `01-metrics-overview.yaml` | Overview of system metrics across all monitored hosts |
| **Host Details** | `02-host-details.yaml` | Detailed metrics for individual hosts |

### Log Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Syslog** | `03-syslog.yaml` | System log analysis and monitoring |
| **Sudo Commands** | `04-sudo-commands.yaml` | Privileged command execution tracking |
| **SSH Logins** | `05-ssh-logins.yaml` | SSH authentication monitoring |
| **Users & Groups** | `06-users-groups.yaml` | User and group management events |

### Windows Security Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Windows Overview** | `07-windows-overview.yaml` | Windows security event overview |
| **Windows Logons** | `08-windows-logons.yaml` | Windows authentication events |
| **Windows Failed & Blocked** | `09-windows-failed-blocked.yaml` | Failed and blocked access attempts |
| **Windows User Management** | `10-windows-user-management.yaml` | User account management events |
| **Windows Group Management** | `11-windows-group-management.yaml` | Group management events |
| **Windows Directory Monitoring** | `12-windows-directory-monitoring.yaml` | Active Directory monitoring |
| **Windows System Process** | `13-windows-system-process.yaml` | System process events |
| **Windows Policy Object** | `14-windows-policy-object.yaml` | Group Policy object changes |

## Prerequisites

- **Elastic Agent**: With System integration configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data view**: `metrics-*` (for metrics), `logs-*` (for logs)
- **Data stream datasets**: `system.cpu`, `system.memory`, `system.network`, `system.filesystem`, `system.process`, `system.load`, `system.fsstat`, `system.syslog`, `system.auth`

## Related

See also: [System Modern Dashboards](../system_modern/README.md) for dashboards with modern UX patterns.
