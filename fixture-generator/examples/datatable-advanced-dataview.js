#!/usr/bin/env node
/**
 * Example: Generate an advanced datatable visualization (using data view)
 *
 * Demonstrates creating a table with multiple rows, sorting, and formatting
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableAdvancedDataview() {
  const config = {
    chartType: 'datatable',
    title: 'Top Agents by System Load (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    columns: [
      {
        columnId: 'agent.name',
        width: 200
      },
      {
        columnId: 'agent.id',
        width: 150
      },
      {
        columnId: 'median_load',
        width: 120,
        value: 'median(beat.stats.system.load.1)'
      }
    ],
    sortingColumnId: 'median_load',
    sortingDirection: 'desc'
  };

  await generateFixture(
    'datatable-advanced-dataview.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableAdvancedDataview, import.meta.url);
