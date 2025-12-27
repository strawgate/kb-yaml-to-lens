#!/usr/bin/env node
/**
 * Example: Generate dual-axis XY chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a chart with both left and right Y-axes
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartDualAxis() {
  // ES|QL variant
  const esqlConfig = {
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

  // Data View variant
  const dataviewConfig = {
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

  await generateDualFixture(
    'xy-chart-dual-axis',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartDualAxis, import.meta.url);
