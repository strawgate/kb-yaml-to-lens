#!/usr/bin/env node
/**
 * Generate all test fixtures
 *
 * Runs all example generator scripts and produces JSON fixtures
 */

const { generateMetricBasic } = require('./examples/metric-basic');
const { generateMetricWithBreakdown } = require('./examples/metric-with-breakdown');
const { generateXYChart } = require('./examples/xy-chart');
const { generatePieChart } = require('./examples/pie-chart');
const { generateHeatmap } = require('./examples/heatmap');
const { generateHeatmapBasic } = require('./examples/heatmap-basic');
const { generateHeatmapWithPalette } = require('./examples/heatmap-with-palette');
const { generateHeatmapAverageAggregation } = require('./examples/heatmap-average-aggregation');
const { generateHeatmapCountMetric } = require('./examples/heatmap-count-metric');
const { generateHeatmapNoLegend } = require('./examples/heatmap-no-legend');

async function generateAll() {
  console.log('Generating all test fixtures...\n');

  const generators = [
    { name: 'Metric (Basic)', fn: generateMetricBasic },
    { name: 'Metric (Breakdown)', fn: generateMetricWithBreakdown },
    { name: 'XY Chart', fn: generateXYChart },
    { name: 'Pie Chart', fn: generatePieChart },
    { name: 'Heatmap', fn: generateHeatmap },
    { name: 'Heatmap (Basic)', fn: generateHeatmapBasic },
    { name: 'Heatmap (With Palette)', fn: generateHeatmapWithPalette },
    { name: 'Heatmap (Average Aggregation)', fn: generateHeatmapAverageAggregation },
    { name: 'Heatmap (Count Metric)', fn: generateHeatmapCountMetric },
    { name: 'Heatmap (No Legend)', fn: generateHeatmapNoLegend },
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

if (require.main === module) {
  generateAll()
    .catch((err) => {
      console.error('Fatal error:', err);
      process.exit(1);
    });
}

module.exports = { generateAll };
