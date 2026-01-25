"""Rule: ES|QL queries with SORT DESC should have explicit LIMIT."""

import re
from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.panels.charts.config import (
    ESQLAreaPanelConfig,
    ESQLBarPanelConfig,
    ESQLDatatablePanelConfig,
    ESQLGaugePanelConfig,
    ESQLHeatmapPanelConfig,
    ESQLLinePanelConfig,
    ESQLMetricPanelConfig,
    ESQLMosaicPanelConfig,
    ESQLPanel,
    ESQLPiePanelConfig,
    ESQLTagcloudPanelConfig,
    LensPanel,
)
from dashboard_lint.esql_helpers import get_query_string
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

type ESQLConfig = (
    ESQLMetricPanelConfig
    | ESQLGaugePanelConfig
    | ESQLHeatmapPanelConfig
    | ESQLPiePanelConfig
    | ESQLLinePanelConfig
    | ESQLBarPanelConfig
    | ESQLAreaPanelConfig
    | ESQLTagcloudPanelConfig
    | ESQLDatatablePanelConfig
    | ESQLMosaicPanelConfig
)

# Pattern to detect SORT with DESC
SORT_DESC_PATTERN = re.compile(r'\bSORT\b[^|]*\bDESC\b', re.IGNORECASE)

# Pattern to detect LIMIT clause
LIMIT_PATTERN = re.compile(r'\bLIMIT\b', re.IGNORECASE)


class ESQLMissingLimitOptions(BaseModel):
    """Options for the esql-missing-limit rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    suggested_limit: int = Field(
        default=10,
        ge=1,
        description='Suggested LIMIT value to include in the message',
    )


@chart_rule
@dataclass(frozen=True)
class ESQLMissingLimitRule(ChartRule[ESQLConfig, ESQLMissingLimitOptions]):
    """Rule: ES|QL queries with SORT DESC should have explicit LIMIT.

    Top-N queries (SORT ... DESC) typically want only the top results.
    Without an explicit LIMIT, ES|QL returns up to 1000 rows by default.
    Adding LIMIT makes the intent clear and can improve performance.

    Example fix:
        Before: FROM logs-* | STATS count = COUNT(*) BY host.name | SORT count DESC
        After:  FROM logs-* | STATS count = COUNT(*) BY host.name | SORT count DESC | LIMIT 10

    Options:
        suggested_limit (int): Suggested LIMIT value to include in message. Default: 10.
    """

    id: str = 'esql-missing-limit'
    description: str = 'ES|QL queries with SORT DESC should have explicit LIMIT for top-N results'
    default_severity: Severity = Severity.INFO
    options_model: type[ESQLMissingLimitOptions] = ESQLMissingLimitOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: ESQLMissingLimitOptions,
    ) -> ViolationResult:
        """Check if ES|QL query with SORT DESC has explicit LIMIT.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if SORT DESC without LIMIT is found, None otherwise.

        """
        query_str = get_query_string(config.query)

        # Only check if query has SORT DESC
        if not SORT_DESC_PATTERN.search(query_str):
            return None

        # Check if LIMIT is present
        if LIMIT_PATTERN.search(query_str):
            return None

        return Violation(
            rule_id=self.id,
            message=f'ES|QL query has SORT DESC but no LIMIT; consider adding LIMIT {options.suggested_limit} for top-N results',
            severity=self.default_severity,
            dashboard_name=context.dashboard_name,
            panel_title=context.panel_title,
            location=context.location('query'),
        )
