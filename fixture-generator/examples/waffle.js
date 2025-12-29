#!/usr/bin/env node
/**
 * Example: Generate waffle/mosaic chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a waffle/mosaic chart showing proportional data
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateWaffle() {
  // Shared configuration
  const sharedConfig = {
    chartType: 'mosaic',
    breakdown: ['request.method'],
    legend: {
      show: true,
      position: 'right'
    }
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'HTTP Methods Distribution',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY request.method'
    },
    value: 'count'
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'HTTP Methods Distribution (Data View)',
    dataset: {
      index: 'logs-*'
    },
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
