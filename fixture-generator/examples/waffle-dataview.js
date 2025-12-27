#!/usr/bin/env node
/**
 * Example: Generate a waffle chart visualization (using data view)
 *
 * Demonstrates creating a waffle/mosaic chart showing proportional data
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateWaffleDataview() {
  const config = {
    chartType: 'mosaic',
    title: 'HTTP Methods Distribution (Data View)',
    dataset: {
      index: 'logs-*'
    },
    breakdown: ['request.method'],
    value: 'count()',
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'waffle-dataview.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateWaffleDataview, import.meta.url);
