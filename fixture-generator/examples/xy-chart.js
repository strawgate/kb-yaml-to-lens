#!/usr/bin/env node
/**
 * Example: Generate XY (line) chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a time series line chart
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChart() {
  // Shared configuration between both variants
  const sharedConfig = {
    chartType: 'xy',
    legend: {
      show: true,
      position: 'right'
    }
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'Events Over Time',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Count',
            value: 'count'
          }
        ]
      }
    ]
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'Events Over Time (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Count',
            value: 'count()'
          }
        ]
      }
    ]
  };

  await generateDualFixture(
    'xy-chart',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChart, import.meta.url);
