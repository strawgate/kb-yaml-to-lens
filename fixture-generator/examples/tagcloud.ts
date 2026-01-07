#!/usr/bin/env node
/**
 * Example: Generate a tagcloud visualization
 *
 * Demonstrates creating a tagcloud with tags sized by a metric value
 */

import type { LensTagCloudConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateTagcloud(): Promise<void> {
  // ES|QL configuration
  const esqlConfig: LensTagCloudConfig = {
    chartType: 'tagcloud',
    title: 'Top Log Levels',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 20'
    },
    value: 'count',
    breakdown: 'log.level'
  };

  // Data View configuration
  const dataviewConfig: LensTagCloudConfig = {
    chartType: 'tagcloud',
    title: 'Top Log Levels',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    value: 'count()',
    breakdown: 'log.level'
  };

  await generateDualFixture(
    'tagcloud',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateTagcloud, import.meta.url);
