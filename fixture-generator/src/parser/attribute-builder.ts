/**
 * Lens Attribute Builder
 * Builds Lens visualization attributes from configuration objects
 */

import { buildXYChart, XYChartConfig } from '../visualizations/xy-chart';
import { buildMetricVisualization, MetricConfig } from '../visualizations/metric';
import { buildPieChart, PieConfig } from '../visualizations/pie';
import { buildDatatable, DatatableConfig } from '../visualizations/datatable';
import {
  buildGaugeVisualization,
  GaugeConfig,
} from '../visualizations/gauge';
import { buildHeatmap, HeatmapConfig } from '../visualizations/heatmap';
import { LensAttributes } from '../types/lens';

export class LensAttributeBuilder {
  buildVisualization(config: any): LensAttributes {
    switch (config.type) {
      case 'xy':
        return buildXYChart(config as XYChartConfig);
      case 'metric':
        return buildMetricVisualization(config as MetricConfig);
      case 'pie':
      case 'donut':
      case 'treemap':
      case 'waffle':
        return buildPieChart({ ...config, shape: config.type } as PieConfig);
      case 'datatable':
        return buildDatatable(config as DatatableConfig);
      case 'gauge':
        return buildGaugeVisualization(config as GaugeConfig);
      case 'heatmap':
        return buildHeatmap(config as HeatmapConfig);
      default:
        throw new Error(`Unknown visualization type: ${config.type}`);
    }
  }
}
