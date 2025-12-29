#!/usr/bin/env node
/**
 * Example: Generate an XY chart with dual Y-axes
 *
 * Demonstrates creating a line chart with metrics on different Y-axes (left/right)
 * to test per-series Y-axis configuration
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateDualAxisChart() {
  // ES|QL variant
  const esqlConfig = {
    chartType: 'xy',
    title: 'Dual Y-Axis Chart',
    dataset: {
      esql: `FROM logs-*
        | STATS
          count = COUNT(),
          avg_bytes = AVG(bytes)
        BY @timestamp`
    },
    layers: [{
      seriesType: 'line',
      xAxis: '@timestamp',
      breakdown: null,
      yAxis: [
        {
          value: 'count',
          label: 'Event Count',
          color: '#2196F3',
          axisMode: 'left'
        },
        {
          value: 'avg_bytes',
          label: 'Avg Bytes',
          color: '#FF5252',
          axisMode: 'right'
        }
      ]
    }],
    legend: {
      show: true,
      position: 'right'
    }
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Dual Y-Axis Chart (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [{
      seriesType: 'line',
      xAxis: {
        type: 'dateHistogram',
        field: '@timestamp'
      },
      breakdown: null,
      yAxis: [
        {
          value: 'count()',
          label: 'Event Count',
          color: '#2196F3',
          axisMode: 'left'
        },
        {
          value: 'average(bytes)',
          label: 'Avg Bytes',
          color: '#FF5252',
          axisMode: 'right'
        }
      ]
    }],
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateDualFixture(
    'xy-dual-axis',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDualAxisChart, import.meta.url);
