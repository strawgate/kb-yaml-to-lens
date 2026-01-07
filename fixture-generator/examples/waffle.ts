#!/usr/bin/env node
/**
 * Example: Generate waffle/mosaic chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a waffle/mosaic chart showing proportional data
 */

import type { LensMosaicConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateWaffle(): Promise<void> {
  // ES|QL variant
  const esqlConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'HTTP Methods Distribution',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY request.method'
    },
    breakdown: ['request.method'],
    value: 'count'
  };

  // Data View variant
  const dataviewConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'HTTP Methods Distribution (Data View)',
    dataset: {
      index: 'logs-*'
    },
    breakdown: ['request.method'],
    value: 'count()'
  };

  await generateDualFixture(
    'waffle',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateWaffle, import.meta.url);
