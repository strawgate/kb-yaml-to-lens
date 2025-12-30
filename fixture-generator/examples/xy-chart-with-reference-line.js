#!/usr/bin/env node
/**
 * Example: Generate XY chart with reference line (multi-layer)
 *
 * Demonstrates creating a line chart with a reference line threshold
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartWithReferenceLine() {
  // ES|QL variant
  const esqlConfig = {
    chartType: 'xy',
    title: 'Response Time with SLA Threshold',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_response = AVG(response_time) BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Average Response Time',
            value: 'avg_response'
          }
        ]
      },
      {
        type: 'referenceLine',
        yAxis: [
          {
            value: 500.0,
            label: 'SLA Threshold',
            color: '#FF0000',
            lineStyle: 'dashed',
            lineWidth: 2
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
    title: 'Response Time with SLA Threshold (Data View)',
    dataset: {
      index: 'metrics-*',
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
            label: 'Average Response Time',
            value: 'average(response_time)'
          }
        ]
      },
      {
        type: 'referenceLine',
        yAxis: [
          {
            value: 500.0,
            label: 'SLA Threshold',
            color: '#FF0000',
            lineStyle: 'dashed',
            lineWidth: 2
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
    'xy-chart-with-reference-line',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartWithReferenceLine, import.meta.url);
