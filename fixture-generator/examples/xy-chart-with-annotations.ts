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
        annotations: [
          {
            type: 'manual',
            label: 'Deployment',
            // Note: 'now-1h' is intentionally relative for demo purposes.
            // For deterministic fixtures, use an absolute ISO timestamp instead.
            key: {
              type: 'point_in_time',
              timestamp: 'now-1h'
            },
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
