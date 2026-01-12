#!/usr/bin/env node
/**
 * Example: Generate metric with secondary metric (both ES|QL and Data View)
 *
 * Demonstrates creating a metric with a secondary comparison value
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithSecondary(): Promise<void> {
  const sharedConfig: Partial<LensMetricConfig> = {
    label: 'Response Time'
  };

  const esqlConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Response Time with Secondary Metric',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_time = AVG(response_time), max_time = MAX(response_time)'
    },
    value: 'avg_time',
    querySecondaryMetric: 'max_time'
  };

  const dataviewConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Response Time with Secondary Metric (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    value: 'average(response_time)',
    querySecondaryMetric: 'max(response_time)'
  };

  await generateDualFixture(
    'metric-with-secondary',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithSecondary, import.meta.url);
