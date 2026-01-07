#!/usr/bin/env node
/**
 * Example: Generate metric with trend visualization (Data View only)
 *
 * Demonstrates creating a metric showing trend arrow/change
 * Note: Trendlines require time-series data and are not supported with ES|QL
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithTrend(): Promise<void> {
  // Data View configuration with trendline
  const config: LensMetricConfig = {
    chartType: 'metric',
    title: 'Event Count with Trend',
    label: 'Total Events',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    value: 'count()',
    trendLine: true
  };

  await generateFixture(
    'metric-with-trend.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithTrend, import.meta.url);
