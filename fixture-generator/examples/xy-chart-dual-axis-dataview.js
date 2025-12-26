#!/usr/bin/env node
/**
 * Example: Generate an XY chart with dual Y-axes (using data view)
 *
 * Demonstrates creating a chart with both left and right Y-axes
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartDualAxisDataview() {
  const config = {
    chartType: 'xy',
    title: 'Event Count and Response Time (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: {
          type: 'dateHistogram',
          field: '@timestamp'
        },
        yAxis: [
          {
            label: 'Event Count',
            value: 'count()',
            axisMode: 'left'
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
            value: 'average(bytes)',
            axisMode: 'right'
          }
        ]
      }
    ],
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  await generateFixture(
    'xy-chart-dual-axis-dataview.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartDualAxisDataview, import.meta.url);
