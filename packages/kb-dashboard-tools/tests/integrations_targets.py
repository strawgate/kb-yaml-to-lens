"""Pinned integrations fixture targets for decompile snapshot tests."""

INTEGRATIONS_PINNED_SHA = 'ddf1422f1a10d2794520ce01000d808dda6d7f13'

INTEGRATIONS_DASHBOARD_TARGETS: tuple[str, ...] = (
    'packages/apache/kibana/dashboard/apache-Logs-Apache-Dashboard.json',
    'packages/nginx/kibana/dashboard/nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129.json',
    'packages/mysql/kibana/dashboard/mysql-Logs-MySQL-Dashboard.json',
    'packages/system/kibana/dashboard/system-Metrics-system-overview.json',
    'packages/system/kibana/dashboard/system-Logs-syslog-dashboard.json',
    'packages/kubernetes/kibana/dashboard/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013.json',
)
