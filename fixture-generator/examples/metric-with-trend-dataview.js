#!/usr/bin/env node
/**
 * Example: Generate a metric with trend indicator (using data view)
 *
 * Demonstrates creating a metric showing trend arrow/change using a data view
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithTrendDataview() {
  const config = {
    chartType: 'metric',
    title: 'Event Count with Trend (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    label: 'Total Events',
    trendline: true,
    progressDirection: 'vertical'
  };

  await generateFixture(
    'metric-with-trend-dataview.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithTrendDataview, import.meta.url);
