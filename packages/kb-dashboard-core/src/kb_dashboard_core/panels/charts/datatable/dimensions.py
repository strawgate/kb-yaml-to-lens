"""Datatable dimension types with nested appearance configuration."""

from kb_dashboard_core.panels.charts.datatable.appearance import DatatableColumnAppearanceMixin
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimension
from kb_dashboard_core.panels.charts.lens.dimensions.config import (
    LensDateHistogramDimension,
    LensFiltersDimension,
    LensIntervalsDimension,
    LensMultiTermsDimension,
    LensTermsDimension,
)


class DatatableLensTermsDimension(LensTermsDimension, DatatableColumnAppearanceMixin):
    """Datatable top-values dimension with appearance options."""


class DatatableLensMultiTermsDimension(LensMultiTermsDimension, DatatableColumnAppearanceMixin):
    """Datatable multi-terms dimension with appearance options."""


class DatatableLensDateHistogramDimension(LensDateHistogramDimension, DatatableColumnAppearanceMixin):
    """Datatable date-histogram dimension with appearance options."""


class DatatableLensFiltersDimension(LensFiltersDimension, DatatableColumnAppearanceMixin):
    """Datatable filters dimension with appearance options."""


class DatatableLensIntervalsDimension(LensIntervalsDimension, DatatableColumnAppearanceMixin):
    """Datatable intervals dimension with appearance options."""


class DatatableESQLDimension(ESQLDimension, DatatableColumnAppearanceMixin):
    """Datatable ES|QL dimension with appearance options."""


type LensDatatableDimensionTypes = (
    DatatableLensTermsDimension
    | DatatableLensMultiTermsDimension
    | DatatableLensDateHistogramDimension
    | DatatableLensFiltersDimension
    | DatatableLensIntervalsDimension
)

type ESQLDatatableDimensionTypes = DatatableESQLDimension
