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
import { generateXYChartAdvancedLegend } from './examples/xy-chart-advanced-legend.js';
import { generateXYChartCustomColors } from './examples/xy-chart-custom-colors.js';
import { generatePieChartAdvancedColors } from './examples/pie-chart-advanced-colors.js';

async function generateAll() {
  console.log('Generating all test fixtures...\n');

  const generators = [
    // Metric visualizations (ES|QL only)
    { name: 'Metric (Basic)', fn: generateMetricBasic },
    { name: 'Metric (Breakdown)', fn: generateMetricWithBreakdown },

    // Metric visualizations (dual: ES|QL + Data View)
    { name: 'Metric (Trend)', fn: generateMetricWithTrend, dual: true },
    { name: 'Metric (Grid)', fn: generateMetricGrid, dual: true },

    // XY Charts (ES|QL only)
    { name: 'XY Chart (Line)', fn: generateXYChart },

    // XY Charts (dual: ES|QL + Data View)
    { name: 'XY Chart (Stacked Bar)', fn: generateXYChartStackedBar, dual: true },
    { name: 'XY Chart (Dual Axis)', fn: generateXYChartDualAxis, dual: true },
    { name: 'XY Chart (Multi-Layer)', fn: generateXYChartMultiLayer, dual: true },
    { name: 'XY Chart (Advanced Legend)', fn: generateXYChartAdvancedLegend, dual: true },
    { name: 'XY Chart (Custom Colors)', fn: generateXYChartCustomColors, dual: true },

    // Pie Charts (ES|QL only)
    { name: 'Pie Chart', fn: generatePieChart },

    // Pie Charts (dual: ES|QL + Data View)
    { name: 'Pie Chart (Donut)', fn: generatePieChartDonut, dual: true },
    { name: 'Pie Chart (Advanced Colors)', fn: generatePieChartAdvancedColors, dual: true },

    // Other chart types (ES|QL only)
    { name: 'Heatmap', fn: generateHeatmap },

    // Other chart types (dual: ES|QL + Data View)
    { name: 'Datatable (Advanced)', fn: generateDatatableAdvanced, dual: true },
    { name: 'Gauge', fn: generateGauge, dual: true },
    { name: 'Treemap', fn: generateTreemap, dual: true },
    { name: 'Waffle', fn: generateWaffle, dual: true },
  ];

  for (const { name, fn, dual } of generators) {
    try {
      await fn();
      if (dual) {
        console.log(`  (generated both ES|QL and Data View variants)`);
      }
    } catch (err) {
      console.error(`✗ Failed to generate ${name}:`, err.message);
      process.exit(1);
    }
  }

  const kibanaVersion = process.env.KIBANA_VERSION || 'v9.2.0';
  console.log('\n✓ All fixtures generated successfully');
  console.log(`  Output directory: ./output/${kibanaVersion}/`);
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateAll()
    .catch((err) => {
      console.error('Fatal error:', err);
      process.exit(1);
    });
}

export { generateAll };
