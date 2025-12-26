#!/usr/bin/env node
/**
 * Example: Generate an XY chart with multiple layers (using data view)
 *
 * Demonstrates creating a chart with bar and line layers combined
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartMultiLayerDataview() {
  const config = {
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

  await generateFixture(
    'xy-chart-multi-layer-dataview.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartMultiLayerDataview, import.meta.url);
