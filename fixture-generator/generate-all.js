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
import { generateMetricGrid } from './examples/metric-grid.js';
import { generateXYChart } from './examples/xy-chart.js';
import { generateXYChartStackedBar } from './examples/xy-chart-stacked-bar.js';
import { generateXYChartDualAxis } from './examples/xy-chart-dual-axis.js';
import { generateXYChartMultiLayer } from './examples/xy-chart-multi-layer.js';
import { generatePieChart } from './examples/pie-chart.js';
import { generatePieChartDonut } from './examples/pie-chart-donut.js';
import { generateHeatmap } from './examples/heatmap.js';
import { generateDatatableAdvanced } from './examples/datatable-advanced.js';
import { generateGauge } from './examples/gauge.js';
import { generateTreemap } from './examples/treemap.js';
import { generateWaffle } from './examples/waffle.js';

async function generateAll() {
  console.log('Generating all test fixtures...\n');

  const generators = [
    // Metric visualizations
    { name: 'Metric (Basic)', fn: generateMetricBasic },
    { name: 'Metric (Breakdown)', fn: generateMetricWithBreakdown },
    { name: 'Metric (Trend)', fn: generateMetricWithTrend },
    { name: 'Metric (Grid)', fn: generateMetricGrid },

    // XY Charts
    { name: 'XY Chart (Line)', fn: generateXYChart },
    { name: 'XY Chart (Stacked Bar)', fn: generateXYChartStackedBar },
    { name: 'XY Chart (Dual Axis)', fn: generateXYChartDualAxis },
    { name: 'XY Chart (Multi-Layer)', fn: generateXYChartMultiLayer },

    // Pie Charts
    { name: 'Pie Chart', fn: generatePieChart },
    { name: 'Pie Chart (Donut)', fn: generatePieChartDonut },

    // Other chart types
    { name: 'Heatmap', fn: generateHeatmap },
    { name: 'Datatable (Advanced)', fn: generateDatatableAdvanced },
    { name: 'Gauge', fn: generateGauge },
    { name: 'Treemap', fn: generateTreemap },
    { name: 'Waffle', fn: generateWaffle },
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
