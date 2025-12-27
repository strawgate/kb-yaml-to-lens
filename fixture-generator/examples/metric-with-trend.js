#!/usr/bin/env node
/**
 * Example: Generate metric with trend visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a metric showing trend arrow/change
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithTrend() {
  // Shared configuration
  const sharedConfig = {
    chartType: 'metric',
    label: 'Total Events',
    trendline: true,
    progressDirection: 'vertical'
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'Event Count with Trend',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count'
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'Event Count with Trend (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()'
  };

  await generateDualFixture(
    'metric-with-trend',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithTrend, import.meta.url);
