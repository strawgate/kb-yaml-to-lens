#!/usr/bin/env node
/**
 * Example: Generate a metric with trend indicator
 *
 * Demonstrates creating a metric showing trend arrow/change
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithTrend() {
  const config = {
    chartType: 'metric',
    title: 'Event Count with Trend',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count',
    label: 'Total Events',
    trendline: true,
    progressDirection: 'vertical'
  };

  await generateFixture(
    'metric-with-trend.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithTrend, import.meta.url);
