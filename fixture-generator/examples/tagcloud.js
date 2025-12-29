#!/usr/bin/env node
/**
 * Example: Generate a tagcloud visualization
 *
 * Demonstrates creating a tagcloud with tags sized by a metric value
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateTagcloud() {
  // ES|QL configuration
  const esqlConfig = {
    chartType: 'tagcloud',
    title: 'Top Log Levels',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 20'
    },
    metric: 'count',
    breakdown: ['log.level']
  };

  // Data View configuration
  const dataviewConfig = {
    chartType: 'tagcloud',
    title: 'Top Log Levels',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    metric: [{
      type: 'count',
      label: 'Count'
    }],
    breakdown: [{
      type: 'terms',
      field: 'log.level',
      params: {
        size: 20,
        orderBy: { type: 'column', columnId: 'metric-column' },
        orderDirection: 'desc'
      }
    }]
  };

  await generateDualFixture(
    'tagcloud',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateTagcloud, import.meta.url);
