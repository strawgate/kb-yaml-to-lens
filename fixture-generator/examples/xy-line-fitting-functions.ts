#!/usr/bin/env node
/**
 * Test fixture: Line chart fitting functions (Linear and Average)
 *
 * Tests: Linear (ES|QL), Average (Data View)
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateLineFittingFunctions(): Promise<void> {
  // ES|QL variant - testing Linear fitting
  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Line Chart - Linear Fitting',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Count',
            value: 'count'
          }
        ]
      }
    ],
    fittingFunction: 'Linear',
    emphasizeFitting: true
  };

  // Data View variant - testing Average fitting
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Line Chart - Average Fitting (Data View)',
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
            label: 'Count',
            value: 'count()'
          }
        ]
      }
    ],
    fittingFunction: 'Average',
    emphasizeFitting: true
  };

  await generateDualFixture(
    'xy-line-fitting-functions',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateLineFittingFunctions, import.meta.url);
