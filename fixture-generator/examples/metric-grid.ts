#!/usr/bin/env node
/**
 * Example: Generate metric grid visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating multiple metrics in a grid layout
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.ts';

export async function generateMetricGrid(): Promise<void> {
  // Shared configuration
  const sharedConfig: Partial<LensMetricConfig> = {
    chartType: 'metric',
    maxCols: 3
  };

  // ES|QL variant
  const esqlConfig: LensMetricConfig = {
    ...sharedConfig,
    title: 'System Metrics Overview',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT(), avg_bytes = AVG(bytes)'
    },
    metrics: [
      { label: 'Total Events', value: 'count' },
      { label: 'Avg Bytes', value: 'avg_bytes' }
    ]
  };

  // Data View variant
  const dataviewConfig: LensMetricConfig = {
    ...sharedConfig,
    title: 'System Metrics Grid (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    metrics: [
      { label: 'Total Events', value: 'count()' },
      { label: 'Avg Bytes', value: 'average(bytes)' }
    ]
  };

  await generateDualFixture(
    'metric-grid',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricGrid, import.meta.url);
