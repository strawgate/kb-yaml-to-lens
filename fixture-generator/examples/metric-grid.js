#!/usr/bin/env node
/**
 * Example: Generate metric grid visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating multiple metrics in a grid layout
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricGrid() {
  // Shared configuration
  const sharedConfig = {
    chartType: 'metric',
    maxCols: 3
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'System Metrics Overview',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT(), avg_bytes = AVG(bytes)'
    },
    metrics: [
      { label: 'Total Events', value: 'count' },
      { label: 'Avg Bytes', value: 'avg_bytes' }
    ]
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'System Metrics Grid (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    metrics: [
      { label: 'Total Events', value: 'count()' },
      { label: 'Avg Bytes', value: 'average(bytes)' }
    ]
  };

  await generateDualFixture(
    'metric-grid',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricGrid, import.meta.url);
