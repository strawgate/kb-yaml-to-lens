#!/usr/bin/env node
/**
 * Example: Generate a waffle chart visualization
 *
 * Demonstrates creating a waffle/mosaic chart showing proportional data
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateWaffle() {
  const config = {
    chartType: 'mosaic',
    title: 'HTTP Methods Distribution',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY request.method'
    },
    breakdown: ['request.method'],
    value: 'count',
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'waffle.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateWaffle, import.meta.url);
