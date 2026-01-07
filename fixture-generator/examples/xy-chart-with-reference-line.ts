#!/usr/bin/env node
/**
 * Example: Generate XY chart with reference line (Data View only)
 *
 * Demonstrates creating a line chart with a reference line threshold.
 * Note: Reference lines are not supported with ES|QL queries.
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartWithReferenceLine(): Promise<void> {
  // Data View variant only - reference lines are not supported with ES|QL queries
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Response Time with SLA Threshold',
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
        type: 'reference',
        yAxis: [
          {
            value: '500',
            label: 'SLA Threshold',
            color: '#FF0000'
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
    'xy-chart-with-reference-line.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartWithReferenceLine, import.meta.url);
