#!/usr/bin/env node
/**
 * Example: Generate advanced datatable visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a table with multiple rows, sorting, and formatting
 */

import type { LensTableConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.ts';

export async function generateDatatableAdvanced(): Promise<void> {
  // ES|QL variant
  const esqlConfig: LensTableConfig = {
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

  // Data View variant
  const dataviewConfig: LensTableConfig = {
    chartType: 'table',
    title: 'Top Agents by System Load (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    breakdown: ['agent.name', 'agent.id'],
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

  await generateDualFixture(
    'datatable-advanced',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableAdvanced, import.meta.url);
