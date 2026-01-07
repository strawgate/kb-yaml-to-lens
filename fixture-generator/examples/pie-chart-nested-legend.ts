#!/usr/bin/env node
/**
 * Example: Generate pie chart with nested legend (both ES|QL and Data View)
 *
 * Demonstrates nested legend display for multi-level pie charts
 */

import type { LensPieConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils';

export async function generatePieChartNestedLegend(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensPieConfig> = {
    chartType: 'pie',
    legend: {
      show: true,
      position: 'right',
      nestedLegend: true
    }
  };

  // ES|QL variant
  const esqlConfig: LensPieConfig = {
    ...sharedConfig,
    title: 'Events by Status and Level (Nested Legend)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level, host.name | SORT count DESC | LIMIT 20'
    },
    value: 'count',
    breakdown: ['log.level', 'host.name']
  };

  // Data View variant
  const dataviewConfig: LensPieConfig = {
    ...sharedConfig,
    title: 'Events by Status and Level (Nested Legend - Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: ['log.level', 'host.name']
  };

  await generateDualFixture(
    'pie-chart-nested-legend',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generatePieChartNestedLegend, import.meta.url);
