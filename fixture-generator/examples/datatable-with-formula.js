#!/usr/bin/env node
/**
 * Example: Generate datatable with formula metrics (Data View only)
 *
 * Demonstrates creating a table with formula-based metrics and dimensions.
 * This fixture validates the behavior when formula columns cannot be used
 * for aggregation ordering (must use alphabetical ordering instead).
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableWithFormula() {
  const dataviewConfig = {
    chartType: 'table',
    title: 'Host Performance Summary',
    dataset: {
      index: 'metrics-*'
    },
    breakdown: ['host.name'],
    columns: [
      {
        columnId: 'host.name',
        width: 200
      },
      {
        columnId: 'cpu_util',
        width: 120,
        value: '1 - average(system.cpu.idle.pct)'
      },
      {
        columnId: 'mem_util',
        width: 120,
        value: 'average(system.memory.used.pct)'
      }
    ]
  };

  await generateFixture(
    'datatable-with-formula-dataview',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableWithFormula, import.meta.url);
