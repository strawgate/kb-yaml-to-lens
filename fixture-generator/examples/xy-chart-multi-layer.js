#!/usr/bin/env node
/**
 * Example: Generate an XY chart with multiple layers
 *
 * Demonstrates creating a chart with bar and line layers combined
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartMultiLayer() {
  const config = {
    chartType: 'xy',
    title: 'Events with Success Rate Overlay',
    dataset: {
      esql: 'FROM logs-* | STATS total = COUNT(), successes = COUNT(CASE WHEN response.keyword == "200" THEN 1 END) BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Total Events',
            value: 'total'
          }
        ]
      },
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Successful Events',
            value: 'successes'
          }
        ]
      }
    ],
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'xy-chart-multi-layer.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartMultiLayer, import.meta.url);
