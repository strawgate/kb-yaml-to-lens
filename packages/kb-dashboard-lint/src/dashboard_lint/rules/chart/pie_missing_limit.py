"""Rule: Pie charts should limit the number of slices shown."""

import re
from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPiePanelConfig,
    LensPanel,
    LensPiePanelConfig,
)
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    BaseLensTermsDimension,
)
from dashboard_lint.esql_helpers import get_query_string
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

type PieConfig = LensPiePanelConfig | ESQLPiePanelConfig

# Pattern to detect LIMIT clause in ES|QL
# Note: This pattern may match LIMIT in string literals or comments.
# This is a known limitation of regex-based linting and is acceptable for this use case.
LIMIT_PATTERN = re.compile(r'\bLIMIT\s+(\d+)', re.IGNORECASE)


class PieMissingLimitOptions(BaseModel):
    """Options for the pie-missing-limit rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    recommended_max: int = Field(
        default=10,
        ge=1,
        description='Recommended maximum number of slices for readability',
    )


@chart_rule
@dataclass(frozen=True)
class PieMissingLimitRule(ChartRule[PieConfig, PieMissingLimitOptions]):
    """Rule: Pie charts should limit the number of slices shown.

    Pie charts with too many slices become hard to read. The style guide
    recommends showing only the top 5-10 categories. This rule checks:

    - Lens pie charts: dimensions should have `size` set (default is often high)
    - ESQL pie charts: queries should include LIMIT clause

    Options:
        recommended_max (int): Recommended maximum slices. Default: 10.
    """

    id: str = 'pie-missing-limit'
    description: str = 'Pie charts should limit slices shown (recommend 5-10 categories)'
    default_severity: Severity = Severity.INFO
    options_model: type[PieMissingLimitOptions] = PieMissingLimitOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,
        config: PieConfig,
        context: ChartContext,
        options: PieMissingLimitOptions,
    ) -> ViolationResult:
        """Check if pie chart has appropriate slice limiting.

        Args:
            panel: The pie chart panel to check.
            config: The panel's pie chart configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if no limit is applied, None otherwise.

        """
        if isinstance(panel, LensPanel):
            return self._check_lens_pie(config, context, options)
        return self._check_esql_pie(config, context, options)

    def _check_lens_pie(
        self,
        config: PieConfig,
        context: ChartContext,
        options: PieMissingLimitOptions,
    ) -> ViolationResult:
        """Check Lens pie chart for size limits on dimensions."""
        if not isinstance(config, LensPiePanelConfig):
            return None

        for dim in config.dimensions:
            # Only terms dimensions have a size parameter
            if isinstance(dim, BaseLensTermsDimension):
                # size=None means Kibana default (often 5, but can be higher)
                # We want explicit sizing for clarity
                if dim.size is None:
                    return Violation(
                        rule_id=self.id,
                        message=f'Pie chart dimension lacks explicit size; consider setting size to {options.recommended_max} or less',
                        severity=self.default_severity,
                        dashboard_name=context.dashboard_name,
                        panel_title=context.panel_title,
                        location=context.location('dimensions'),
                    )
                if dim.size > options.recommended_max:
                    return Violation(
                        rule_id=self.id,
                        message=f'Pie chart dimension shows {dim.size} values; consider {options.recommended_max} or fewer for readability',
                        severity=self.default_severity,
                        dashboard_name=context.dashboard_name,
                        panel_title=context.panel_title,
                        location=context.location('dimensions'),
                    )

        return None

    def _check_esql_pie(
        self,
        config: PieConfig,
        context: ChartContext,
        options: PieMissingLimitOptions,
    ) -> ViolationResult:
        """Check ESQL pie chart for LIMIT clause."""
        if not isinstance(config, ESQLPiePanelConfig):
            return None

        query_str = get_query_string(config.query)
        limit_match = LIMIT_PATTERN.search(query_str)

        if limit_match is None:
            return Violation(
                rule_id=self.id,
                message=f'ES|QL pie chart has no LIMIT; consider adding LIMIT {options.recommended_max} for readability',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        limit_value = int(limit_match.group(1))
        if limit_value > options.recommended_max:
            return Violation(
                rule_id=self.id,
                message=f'ES|QL pie chart LIMIT {limit_value} may show too many slices; consider {options.recommended_max} or fewer',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        return None
