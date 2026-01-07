#!/usr/bin/env node
/**
 * Test fixture: Curve type options for line charts
 *
 * Tests: LINEAR, CURVE_MONOTONE_X, CURVE_STEP_AFTER, etc.
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateLineCurveTypes(): Promise<void> {
  // ES|QL variant - testing CURVE_MONOTONE_X
  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Line Chart - Monotone X Curve',
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
    curveType: 'CURVE_MONOTONE_X'
  };

  // Data View variant - testing LINEAR
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Line Chart - Linear Curve (Data View)',
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
    curveType: 'LINEAR'
  };

  await generateDualFixture(
    'xy-line-curve-types',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateLineCurveTypes, import.meta.url);
