#!/usr/bin/env node
/**
 * Example: Generate a stacked bar chart
 *
 * Demonstrates creating a vertical stacked bar chart with multiple series
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartStackedBar() {
  const config = {
    chartType: 'xy',
    title: 'Stacked Events by Response Code',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp, response.keyword'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Count',
            value: 'count'
          }
        ],
        breakdown: 'response.keyword',
        seriesOptions: {
          stacked: 'normal'
        }
      }
    ],
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'xy-chart-stacked-bar.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartStackedBar, import.meta.url);
