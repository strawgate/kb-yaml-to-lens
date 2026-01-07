#!/usr/bin/env node
/**
 * Example: Generate treemap visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a hierarchical treemap showing nested breakdowns
 */

import type { LensTreeMapConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateTreemap(): Promise<void> {
  // ES|QL variant
  const esqlConfig: LensTreeMapConfig = {
    chartType: 'treemap',
    title: 'Traffic by Source and Destination',
    dataset: {
      esql: 'FROM logs-* | STATS bytes = SUM(bytes) BY geo.src, geo.dest'
    },
    breakdown: ['geo.src', 'geo.dest'],
    value: 'bytes'
  };

  // Data View variant
  const dataviewConfig: LensTreeMapConfig = {
    chartType: 'treemap',
    title: 'Traffic by Source and Destination (Data View)',
    dataset: {
      index: 'logs-*'
    },
    breakdown: ['geo.src', 'geo.dest'],
    value: 'sum(bytes)'
  };

  await generateDualFixture(
    'treemap',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateTreemap, import.meta.url);
