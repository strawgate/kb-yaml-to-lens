#!/usr/bin/env node
/**
 * Example: Generate donut chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a pie chart in donut mode with various label configurations
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChartDonut() {
  // Shared configuration
  const sharedConfig = {
    chartType: 'pie',
    shape: 'donut',
    labels: {
      show: true,
      position: 'inside',
      percentDecimals: 1
    },
    legend: {
      show: true,
      position: 'right'
    }
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'Response Codes Distribution (Donut)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY response.keyword'
    },
    value: 'count',
    breakdown: ['response.keyword']
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'Response Codes Distribution (Donut - Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: ['response.keyword']
  };

  await generateDualFixture(
    'pie-chart-donut',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generatePieChartDonut, import.meta.url);
