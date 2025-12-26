#!/usr/bin/env node
/**
 * Example: Generate an XY chart with dual Y-axes
 *
 * Demonstrates creating a chart with both left and right Y-axes
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartDualAxis() {
  const config = {
    chartType: 'xy',
    title: 'Event Count and Response Time',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT(), avg_bytes = AVG(bytes) BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Event Count',
            value: 'count',
            axisMode: 'left'
          }
        ]
      },
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Avg Bytes',
            value: 'avg_bytes',
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
    'xy-chart-dual-axis.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartDualAxis, import.meta.url);
