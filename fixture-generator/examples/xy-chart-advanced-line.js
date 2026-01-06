#!/usr/bin/env node
/**
 * Example: Generate line chart with advanced options (fitting functions, time markers, curve types)
 *
 * Demonstrates the new advanced line chart features added in PR #542:
 * - Fitting functions (Linear, Average, Carry, etc.)
 * - End value handling
 * - Curve types
 * - Time markers
 * - Hide endzones
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartAdvancedLine() {
  // ES|QL variant
  const esqlConfig = {
    chartType: 'xy',
    title: 'Advanced Line Chart with Fitting Functions',
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
        ],
        seriesOptions: {
          fittingFunction: 'Average',
          emphasizeFitting: true,
          endValue: 'Zero',
          curveType: 'CURVE_MONOTONE_X'
        }
      }
    ],
    legend: {
      show: true,
      position: 'right'
    },
    hideEndzones: true,
    showCurrentTimeMarker: true
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Advanced Line Chart (Data View)',
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
        ],
        seriesOptions: {
          fittingFunction: 'Average',
          emphasizeFitting: true,
          endValue: 'Zero',
          curveType: 'CURVE_MONOTONE_X'
        }
      }
    ],
    legend: {
      show: true,
      position: 'right'
    },
    hideEndzones: true,
    showCurrentTimeMarker: true
  };

  await generateDualFixture(
    'xy-chart-advanced-line',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartAdvancedLine, import.meta.url);
