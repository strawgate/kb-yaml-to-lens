#!/usr/bin/env node
/**
 * Example: Generate XY chart with annotation layer (Data View only)
 *
 * Demonstrates creating a line chart with an annotation layer for events.
 * Note: Annotation layers are not supported with ES|QL queries.
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartWithAnnotations(): Promise<void> {
  // Data View variant only - annotation layers are not supported with ES|QL queries
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Response Time with Event Annotations',
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
        type: 'annotation',
        yAxis: [],
        events: [
          {
            name: 'Deployment',
            // Note: Using absolute timestamp for fixture reproducibility.
            // In production, you might use relative times or query-based annotations.
            datetime: '2024-01-15T12:00:00.000Z',
            color: '#0077CC',
            icon: 'tag'
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
    'xy-chart-with-annotations.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartWithAnnotations, import.meta.url);
