"""Datatable breakdown types with nested appearance configuration and collapse support."""

from kb_dashboard_core.panels.charts.datatable.appearance import DatatableColumnAppearanceMixin
from kb_dashboard_core.panels.charts.datatable.dimensions import ESQLDatatableDimensionTypes
from kb_dashboard_core.panels.charts.lens.breakdowns.config import (
    LensDateHistogramBreakdown,
    LensFiltersBreakdown,
    LensIntervalsBreakdown,
    LensMultiTermsBreakdown,
    LensTermsBreakdown,
)


class DatatableLensTermsBreakdown(LensTermsBreakdown, DatatableColumnAppearanceMixin):
    """Datatable top-values breakdown with appearance options and collapse support."""


class DatatableLensMultiTermsBreakdown(LensMultiTermsBreakdown, DatatableColumnAppearanceMixin):
    """Datatable multi-terms breakdown with appearance options and collapse support."""


class DatatableLensDateHistogramBreakdown(LensDateHistogramBreakdown, DatatableColumnAppearanceMixin):
    """Datatable date-histogram breakdown with appearance options and collapse support."""


class DatatableLensFiltersBreakdown(LensFiltersBreakdown, DatatableColumnAppearanceMixin):
    """Datatable filters breakdown with appearance options and collapse support."""


class DatatableLensIntervalsBreakdown(LensIntervalsBreakdown, DatatableColumnAppearanceMixin):
    """Datatable intervals breakdown with appearance options and collapse support."""


type LensDatatableBreakdownTypes = (
    DatatableLensTermsBreakdown
    | DatatableLensMultiTermsBreakdown
    | DatatableLensDateHistogramBreakdown
    | DatatableLensFiltersBreakdown
    | DatatableLensIntervalsBreakdown
)

type ESQLDatatableBreakdownTypes = ESQLDatatableDimensionTypes
