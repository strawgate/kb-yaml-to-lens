#!/usr/bin/env node
/**
 * Example: Generate XY chart testing metric format options
 *
 * Note: This fixture tests Data View format support only.
 * ES|QL datasources do not support format configuration via LensConfigBuilder.
 *
 * LensConfigBuilder limitations for ES|QL:
 * - ❌ format on yAxis items (ignored)
 * - ❌ color on yAxis items (use palette instead)
 * - ❌ axisMode on yAxis items (not supported)
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartESQLMetricAppearance(): Promise<void> {
  // ES|QL variant - demonstrates that format/color/axisMode are NOT supported
  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'ES|QL Multi-Metric Chart',
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
            value: 'event_count'
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
            value: 'total_bytes'
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
            value: 'avg_bytes'
          }
        ]
      }
    ],
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  // Data View variant - DOES support format configuration
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Data View Multi-Metric with Formats',
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
