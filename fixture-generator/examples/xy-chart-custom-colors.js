#!/usr/bin/env node
/**
 * Example: Generate XY chart with custom color palette (both ES|QL and Data View)
 *
 * Demonstrates custom color configurations and palette options
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartCustomColors() {
  // Shared custom palette configuration
  const customPalette = {
    type: 'palette',
    name: 'custom',
    params: {
      colors: ['#68BC00', '#009CE0', '#F04E98', '#FEC514', '#FF6600'],
      gradient: false,
      stops: [],
      rangeType: 'number',
      rangeMin: 0,
      rangeMax: null,
      continuity: 'above',
      reverse: false
    }
  };

  // ES|QL variant
  const esqlConfig = {
    chartType: 'xy',
    title: 'Traffic by Log Level (Custom Colors)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp, log.level'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'area',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Count',
            value: 'count'
          }
        ],
        breakdown: 'log.level',
        seriesOptions: {
          stacked: 'normal'
        }
      }
    ],
    palette: customPalette,
    legend: {
      show: true,
      position: 'right'
    }
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Traffic by Log Level (Custom Colors - Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'area',
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
        breakdown: 'log.level',
        seriesOptions: {
          stacked: 'normal'
        }
      }
    ],
    palette: customPalette,
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateDualFixture(
    'xy-chart-custom-colors',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartCustomColors, import.meta.url);
