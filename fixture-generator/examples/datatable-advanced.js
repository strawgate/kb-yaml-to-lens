#!/usr/bin/env node
/**
 * Example: Generate an advanced datatable visualization
 *
 * Demonstrates creating a table with multiple rows, sorting, and formatting
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableAdvanced() {
  const config = {
    chartType: 'table',
    title: 'Top Agents by System Load',
    dataset: {
      esql: 'FROM metrics-* | STATS median_load = MEDIAN(beat.stats.system.load.1) BY agent.name, agent.id | LIMIT 100'
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
        width: 120
      }
    ],
    sortingColumnId: 'median_load',
    sortingDirection: 'desc'
  };

  await generateFixture(
    'datatable-advanced.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableAdvanced, import.meta.url);
