"""Compile Alerts Table panels into their Kibana representations."""

from dashboard_compiler.panels.alerts.config import AlertsPanel
from dashboard_compiler.panels.alerts.view import (
    KbnAlertsEmbeddableConfig,
    KbnAlertsFilterExpression,
    KbnAlertsQuery,
    KbnAlertsTableConfig,
)
from dashboard_compiler.shared.view import KbnReference


def compile_alerts_query(alerts_panel: AlertsPanel) -> KbnAlertsQuery:
    """Compile the alerts query configuration.

    Args:
        alerts_panel: The Alerts panel to compile.

    Returns:
        KbnAlertsQuery: The compiled alerts query.

    """
    filters = [
        KbnAlertsFilterExpression(
            field=f.field,
            values=f.values,
        )
        for f in alerts_panel.alerts.filters
    ]

    return KbnAlertsQuery(
        type='alertsFilters',
        filters=filters,
    )


def compile_alerts_table_config(alerts_panel: AlertsPanel) -> KbnAlertsTableConfig:
    """Compile the alerts table configuration.

    Args:
        alerts_panel: The Alerts panel to compile.

    Returns:
        KbnAlertsTableConfig: The compiled alerts table configuration.

    """
    return KbnAlertsTableConfig(
        solution=alerts_panel.alerts.solution,
        query=compile_alerts_query(alerts_panel),
    )


def compile_alerts_panel_config(alerts_panel: AlertsPanel) -> tuple[list[KbnReference], KbnAlertsEmbeddableConfig]:
    """Compile an AlertsPanel into its Kibana view model representation.

    Args:
        alerts_panel: The Alerts panel to compile.

    Returns:
        tuple: A tuple containing the references list (empty for alerts) and the embeddable config.

    """
    return [], KbnAlertsEmbeddableConfig(
        hidePanelTitles=alerts_panel.hide_title,
        enhancements={},
        description=None,
        tableConfig=compile_alerts_table_config(alerts_panel),
    )
