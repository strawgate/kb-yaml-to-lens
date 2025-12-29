#!/usr/bin/env node
/**
 * Example: Generate multi-layer XY chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a chart with bar and line layers combined
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartMultiLayer() {
  // ES|QL variant
  const esqlConfig = {
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

  // Data View variant
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Events with Avg Bytes Overlay (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
        xAxis: {
          type: 'dateHistogram',
          field: '@timestamp'
        },
        yAxis: [
          {
            label: 'Total Events',
            value: 'count()'
          }
        ]
      },
      {
        type: 'series',
        seriesType: 'line',
        xAxis: {
          type: 'dateHistogram',
          field: '@timestamp'
        },
        yAxis: [
          {
            label: 'Avg Bytes',
            value: 'average(bytes)'
          }
        ]
      }
    ],
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateDualFixture(
    'xy-chart-multi-layer',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartMultiLayer, import.meta.url);
