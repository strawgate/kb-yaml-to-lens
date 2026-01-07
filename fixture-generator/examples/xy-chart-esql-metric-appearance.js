#!/usr/bin/env node
/**
 * Example: Generate XY chart with ES|QL metric appearance options
 *
 * Demonstrates:
 * - Custom format types (bytes, number, percent)
 * - Custom colors for individual metrics
 * - Dual-axis assignment (left/right)
 * - Multiple metrics with different appearance configurations
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartESQLMetricAppearance() {
  // ES|QL variant - bar chart with multiple metrics showing different formats and appearances
  const esqlConfig = {
    chartType: 'xy',
    title: 'ES|QL Metrics with Appearance Options',
    dataset: {
      esql: 'FROM logs-* | STATS event_count = COUNT(), total_bytes = SUM(bytes), avg_bytes = AVG(bytes) BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Event Count',
            value: 'event_count',
            axisMode: 'left',
            color: '#68BC00',
            format: {
              id: 'number',
              params: {
                pattern: '0,0'
              }
            }
          }
        ]
      },
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Total Bytes',
            value: 'total_bytes',
            axisMode: 'right',
            color: '#009CE0',
            format: {
              id: 'bytes',
              params: {
                pattern: '0,0.0 b'
              }
            }
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
            axisMode: 'right',
            color: '#F04E98',
            format: {
              id: 'bytes',
              params: {
                pattern: '0.00 b'
              }
            }
          }
        ]
      }
    ],
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  // Data View variant - same chart using data view aggregations
  const dataviewConfig = {
    chartType: 'xy',
    title: 'ES|QL Metrics with Appearance Options (Data View)',
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
            label: 'Event Count',
            value: 'count()',
            axisMode: 'left',
            color: '#68BC00',
            format: {
              id: 'number',
              params: {
                pattern: '0,0'
              }
            }
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
            label: 'Total Bytes',
            value: 'sum(bytes)',
            axisMode: 'right',
            color: '#009CE0',
            format: {
              id: 'bytes',
              params: {
                pattern: '0,0.0 b'
              }
            }
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
            axisMode: 'right',
            color: '#F04E98',
            format: {
              id: 'bytes',
              params: {
                pattern: '0.00 b'
              }
            }
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
    'xy-chart-esql-metric-appearance',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartESQLMetricAppearance, import.meta.url);
