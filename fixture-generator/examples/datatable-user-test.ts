#!/usr/bin/env node
/**
 * Example: Generate datatable matching user's test case
 */

import type { LensTableConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateDatatableUserTest(): Promise<void> {
  // Data View variant matching user's example
  const dataviewConfig: LensTableConfig = {
    chartType: 'table',
    title: 'Agent Status Table',
    dataset: {
      index: 'metrics-*'
    },
    breakdown: ['agent.version'],
    value: 'count(agent.name)'
  };

  await generateFixture(
    'datatable-user-test.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateDatatableUserTest, import.meta.url);
