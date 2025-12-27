#!/usr/bin/env node
/**
 * Example: Generate a treemap visualization (using data view)
 *
 * Demonstrates creating a hierarchical treemap showing nested breakdowns
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateTreemapDataview() {
  const config = {
    chartType: 'treemap',
    title: 'Traffic by Source and Destination (Data View)',
    dataset: {
      index: 'logs-*'
    },
    breakdown: ['geo.src', 'geo.dest'],
    primaryGroup: 'geo.src',
    secondaryGroup: 'geo.dest',
    value: 'sum(bytes)',
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'treemap-dataview.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateTreemapDataview, import.meta.url);
