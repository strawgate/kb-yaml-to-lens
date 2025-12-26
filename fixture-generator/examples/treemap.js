#!/usr/bin/env node
/**
 * Example: Generate a treemap visualization
 *
 * Demonstrates creating a hierarchical treemap showing nested breakdowns
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateTreemap() {
  const config = {
    chartType: 'treemap',
    title: 'Traffic by Source and Destination',
    dataset: {
      esql: 'FROM logs-* | STATS bytes = SUM(bytes) BY geo.src, geo.dest'
    },
    primaryGroup: 'geo.src',
    secondaryGroup: 'geo.dest',
    metric: 'bytes',
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'treemap.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateTreemap, import.meta.url);
