#!/usr/bin/env node
/**
 * Example: Generate metric with max value/progress bar (both ES|QL and Data View)
 *
 * Demonstrates creating a metric showing a progress bar toward a max value
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithMaxValue(): Promise<void> {
  const sharedConfig: Partial<LensMetricConfig> = {
    label: 'Storage Used'
  };

  const esqlConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Storage Usage (Progress)',
    dataset: {
      esql: 'FROM metrics-* | STATS used = AVG(storage.used.bytes), total = AVG(storage.total.bytes)'
    },
    value: 'used',
    queryMaxValue: 'total',
    format: 'bytes'
  };

  const dataviewConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Storage Usage (Progress, Data View)',
    dataset: {
      index: 'metrics-*'
    },
    value: 'average(storage.used.bytes)',
    queryMaxValue: 'average(storage.total.bytes)',
    format: 'bytes'
  };

  await generateDualFixture(
    'metric-with-max-value',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithMaxValue, import.meta.url);
