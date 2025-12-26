#!/usr/bin/env node
/**
 * Generate all test fixtures
 *
 * Runs all example generator scripts and produces JSON fixtures
 */

import { fileURLToPath } from 'url';
import { generateMetricBasic } from './examples/metric-basic.js';
import { generateMetricWithBreakdown } from './examples/metric-with-breakdown.js';
import { generateXYChart } from './examples/xy-chart.js';
import { generatePieChart } from './examples/pie-chart.js';
import { generateHeatmap } from './examples/heatmap.js';

async function generateAll() {
  console.log('Generating all test fixtures...\n');

  const generators = [
    { name: 'Metric (Basic)', fn: generateMetricBasic },
    { name: 'Metric (Breakdown)', fn: generateMetricWithBreakdown },
    { name: 'XY Chart', fn: generateXYChart },
    { name: 'Pie Chart', fn: generatePieChart },
    { name: 'Heatmap', fn: generateHeatmap },
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
