#!/usr/bin/env node
/**
 * Example: Generate datatable matching user's test case
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableUserTest() {
  // Data View variant matching user's example
  const dataviewConfig = {
    chartType: 'table',
    title: 'Agent Status Table',
    dataset: {
      index: 'metrics-*'
    },
    breakdown: ['agent.version'],
    columns: [
      {
        columnId: 'agent_count',
        value: 'count(agent.name)'
      }
    ]
  };

  await generateDualFixture(
    'datatable-user-test',
    null, // No ESQL variant
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableUserTest, import.meta.url);
