#!/usr/bin/env node
/**
 * Example: Generate a metric grid layout (using data view)
 *
 * Demonstrates creating multiple metrics in a grid layout using a data view
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricGridDataview() {
  const config = {
    chartType: 'metric',
    title: 'System Metrics Grid (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    metrics: [
      { label: 'Total Events', value: 'count()' },
      { label: 'Avg Bytes', value: 'average(bytes)' },
      { label: 'Max Price', value: 'max(price)' }
    ],
    maxCols: 3
  };

  await generateFixture(
    'metric-grid-dataview.json',
    config,
    { timeRange: { from: 'now-15m', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricGridDataview, import.meta.url);
