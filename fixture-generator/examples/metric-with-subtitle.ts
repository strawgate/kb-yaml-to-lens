#!/usr/bin/env node
/**
 * Example: Generate metric with subtitle (both ES|QL and Data View)
 *
 * Demonstrates creating a metric showing a subtitle under the primary value
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithSubtitle(): Promise<void> {
  const sharedConfig: Partial<LensMetricConfig> = {
    label: 'Total Events',
    subtitle: 'Last 24 hours'
  };

  const esqlConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Event Count with Subtitle',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count'
  };

  const dataviewConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Event Count with Subtitle (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()'
  };

  await generateDualFixture(
    'metric-with-subtitle',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithSubtitle, import.meta.url);
