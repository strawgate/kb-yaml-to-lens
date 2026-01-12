#!/usr/bin/env node
/**
 * Example: Generate datatable with multiple columns (both ES|QL and Data View)
 *
 * Demonstrates creating a datatable with multiple breakdown columns and metrics
 */

import type { LensTableConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableMultiColumn(): Promise<void> {
  const esqlConfig: LensTableConfig = {
    chartType: 'table',
    title: 'Log Events by Source and Level',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level, source.ip | SORT count DESC | LIMIT 100'
    },
    breakdown: ['log.level', 'source.ip'],
    value: 'count'
  };

  const dataviewConfig: LensTableConfig = {
    chartType: 'table',
    title: 'Log Events by Source and Level (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    breakdown: ['log.level', 'source.ip'],
    value: 'count()'
  };

  await generateDualFixture(
    'datatable-multi-column',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableMultiColumn, import.meta.url);
