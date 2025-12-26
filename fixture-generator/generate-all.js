#!/usr/bin/env node
/**
 * Generate all test fixtures
 *
 * Runs all example generator scripts and produces JSON fixtures
 */

import { fileURLToPath } from 'url';
import { generateMetricBasic } from './examples/metric-basic.js';
import { generateMetricWithBreakdown } from './examples/metric-with-breakdown.js';
import { generateMetricWithTrend } from './examples/metric-with-trend.js';
import { generateMetricWithTrendDataview } from './examples/metric-with-trend-dataview.js';
import { generateMetricGrid } from './examples/metric-grid.js';
import { generateMetricGridDataview } from './examples/metric-grid-dataview.js';
import { generateXYChart } from './examples/xy-chart.js';
import { generateXYChartStackedBar } from './examples/xy-chart-stacked-bar.js';
import { generateXYChartStackedBarDataview } from './examples/xy-chart-stacked-bar-dataview.js';
import { generateXYChartDualAxis } from './examples/xy-chart-dual-axis.js';
import { generateXYChartDualAxisDataview } from './examples/xy-chart-dual-axis-dataview.js';
import { generateXYChartMultiLayer } from './examples/xy-chart-multi-layer.js';
import { generateXYChartMultiLayerDataview } from './examples/xy-chart-multi-layer-dataview.js';
import { generatePieChart } from './examples/pie-chart.js';
import { generatePieChartDonut } from './examples/pie-chart-donut.js';
import { generatePieChartDonutDataview } from './examples/pie-chart-donut-dataview.js';
import { generateHeatmap } from './examples/heatmap.js';
import { generateDatatableAdvanced } from './examples/datatable-advanced.js';
import { generateDatatableAdvancedDataview } from './examples/datatable-advanced-dataview.js';
import { generateGauge } from './examples/gauge.js';
import { generateGaugeDataview } from './examples/gauge-dataview.js';
import { generateTreemap } from './examples/treemap.js';
import { generateTreemapDataview } from './examples/treemap-dataview.js';
import { generateWaffle } from './examples/waffle.js';
import { generateWaffleDataview } from './examples/waffle-dataview.js';

async function generateAll() {
  console.log('Generating all test fixtures...\n');

  const generators = [
    // Metric visualizations (ES|QL)
    { name: 'Metric (Basic)', fn: generateMetricBasic },
    { name: 'Metric (Breakdown)', fn: generateMetricWithBreakdown },
    { name: 'Metric (Trend)', fn: generateMetricWithTrend },
    { name: 'Metric (Grid)', fn: generateMetricGrid },

    // Metric visualizations (Data View)
    { name: 'Metric (Trend - Data View)', fn: generateMetricWithTrendDataview },
    { name: 'Metric (Grid - Data View)', fn: generateMetricGridDataview },

    // XY Charts (ES|QL)
    { name: 'XY Chart (Line)', fn: generateXYChart },
    { name: 'XY Chart (Stacked Bar)', fn: generateXYChartStackedBar },
    { name: 'XY Chart (Dual Axis)', fn: generateXYChartDualAxis },
    { name: 'XY Chart (Multi-Layer)', fn: generateXYChartMultiLayer },

    // XY Charts (Data View)
    { name: 'XY Chart (Stacked Bar - Data View)', fn: generateXYChartStackedBarDataview },
    { name: 'XY Chart (Dual Axis - Data View)', fn: generateXYChartDualAxisDataview },
    { name: 'XY Chart (Multi-Layer - Data View)', fn: generateXYChartMultiLayerDataview },

    // Pie Charts (ES|QL)
    { name: 'Pie Chart', fn: generatePieChart },
    { name: 'Pie Chart (Donut)', fn: generatePieChartDonut },

    // Pie Charts (Data View)
    { name: 'Pie Chart (Donut - Data View)', fn: generatePieChartDonutDataview },

    // Other chart types (ES|QL)
    { name: 'Heatmap', fn: generateHeatmap },
    { name: 'Datatable (Advanced)', fn: generateDatatableAdvanced },
    { name: 'Gauge', fn: generateGauge },
    { name: 'Treemap', fn: generateTreemap },
    { name: 'Waffle', fn: generateWaffle },

    // Other chart types (Data View)
    { name: 'Datatable (Advanced - Data View)', fn: generateDatatableAdvancedDataview },
    { name: 'Gauge (Data View)', fn: generateGaugeDataview },
    { name: 'Treemap (Data View)', fn: generateTreemapDataview },
    { name: 'Waffle (Data View)', fn: generateWaffleDataview },
  ];

  for (const { name, fn } of generators) {
    try {
      await fn();
    } catch (err) {
      console.error(`✗ Failed to generate ${name}:`, err.message);
      process.exit(1);
    }
  }

  console.log('\n✓ All fixtures generated successfully');
  console.log('  Output directory: ./output/');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateAll()
    .catch((err) => {
      console.error('Fatal error:', err);
      process.exit(1);
    });
}

export { generateAll };
