#!/usr/bin/env node
/**
 * Example: Generate datatable with ALL possible configuration options
 *
 * Tests sorting, paging, column width, alignment, summary rows, row height, density
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableWithAllFeatures() {
  // ES|QL variant with all features
  const esqlConfig = {
    chartType: 'table',
    title: 'Datatable with All Features (ESQL)',
    dataset: {
      esql: 'FROM metrics-* | STATS count = COUNT(*), avg_load = AVG(beat.stats.system.load.1) BY agent.name | SORT count DESC | LIMIT 100'
    },
    columns: [
      {
        columnId: 'agent.name',
        width: 200,
        alignment: 'left',
        hidden: false
      },
      {
        columnId: 'count',
        width: 120,
        alignment: 'right',
        colorMode: 'cell',
        summaryRow: 'sum',
        summaryLabel: 'Total Count'
      },
      {
        columnId: 'avg_load',
        width: 150,
        alignment: 'right',
        summaryRow: 'avg'
      }
    ],
    sortingColumnId: 'count',
    sortingDirection: 'desc',
    pagingEnabled: true,
    pagingSize: 25,
    rowHeight: 'single',
    headerRowHeight: 'auto',
    rowHeightLines: undefined,
    headerRowHeightLines: undefined,
    density: 'compact'
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'table',
    title: 'Datatable with All Features (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    breakdown: ['agent.name'],
    columns: [
      {
        columnId: 'agent.name',
        width: 200,
        alignment: 'left'
      },
      {
        columnId: 'count',
        width: 120,
        alignment: 'right',
        value: 'count()',
        colorMode: 'cell',
        summaryRow: 'sum',
        summaryLabel: 'Total Count'
      },
      {
        columnId: 'avg_load',
        width: 150,
        alignment: 'right',
        value: 'average(beat.stats.system.load.1)',
        summaryRow: 'avg'
      }
    ],
    sortingColumnId: 'count',
    sortingDirection: 'desc',
    pagingEnabled: true,
    pagingSize: 25,
    rowHeight: 'single',
    headerRowHeight: 'auto',
    density: 'compact'
  };

  await generateDualFixture(
    'datatable-all-features',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableWithAllFeatures, import.meta.url);
