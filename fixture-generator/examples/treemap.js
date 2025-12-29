#!/usr/bin/env node
/**
 * Example: Generate treemap visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a hierarchical treemap showing nested breakdowns
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateTreemap() {
  // Shared configuration
  const sharedConfig = {
    chartType: 'treemap',
    legend: {
      show: true,
      position: 'right'
    }
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'Traffic by Source and Destination',
    dataset: {
      esql: 'FROM logs-* | STATS bytes = SUM(bytes) BY geo.src, geo.dest'
    },
    primaryGroup: 'geo.src',
    secondaryGroup: 'geo.dest',
    metric: 'bytes'
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'Traffic by Source and Destination (Data View)',
    dataset: {
      index: 'logs-*'
    },
    breakdown: ['geo.src', 'geo.dest'],
    primaryGroup: 'geo.src',
    secondaryGroup: 'geo.dest',
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
