#!/usr/bin/env node
/**
 * Example: Generate datatable with splitBy (both ES|QL and Data View)
 *
 * Demonstrates creating a datatable with splitBy for row grouping
 */

import type { LensTableConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableWithSplit(): Promise<void> {
  const esqlConfig: LensTableConfig = {
    chartType: 'table',
    title: 'Agent Performance by Version',
    dataset: {
      esql: 'FROM metrics-* | STATS count = COUNT() BY agent.version, agent.name | SORT count DESC'
    },
    splitBy: ['agent.version'],
    breakdown: ['agent.name'],
    value: 'count'
  };

  const dataviewConfig: LensTableConfig = {
    chartType: 'table',
    title: 'Agent Performance by Version (Data View)',
    dataset: {
      index: 'metrics-*',
      timeFieldName: '@timestamp'
    },
    splitBy: ['agent.version'],
    breakdown: ['agent.name'],
    value: 'count()'
  };

  await generateDualFixture(
    'datatable-with-split',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableWithSplit, import.meta.url);
