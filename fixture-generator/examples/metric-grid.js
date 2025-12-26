#!/usr/bin/env node
/**
 * Example: Generate multiple metrics in a grid layout
 *
 * Demonstrates creating a metric visualization with multiple values
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricGrid() {
  const config = {
    chartType: 'metric',
    title: 'System Metrics Overview',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT(), avg_bytes = AVG(bytes), max_bytes = MAX(bytes)'
    },
    primaryMetric: 'count',
    secondaryMetric: 'avg_bytes',
    maxCols: 3
  };

  await generateFixture(
    'metric-grid.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricGrid, import.meta.url);
