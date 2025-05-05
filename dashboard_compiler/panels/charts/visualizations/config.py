from dashboard_compiler.panels.charts.visualizations.metric.config import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.visualizations.pie.config import ESQLPieChart, LensPieChart

type AllChartTypes = LensChartTypes | ESQLChartTypes

type LensChartTypes = LensMetricChart | LensPieChart
type ESQLChartTypes = ESQLMetricChart | ESQLPieChart
