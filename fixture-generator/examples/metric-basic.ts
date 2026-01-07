#!/usr/bin/env node
/**
 * Example: Generate a basic metric visualization (both ES|QL and Data View)
 *
 * Demonstrates creating a simple count metric
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricBasic(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensMetricConfig> = {
    label: 'Total Events'
  };

  // ES|QL variant
  const esqlConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Basic Count Metric',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count'
  };

  // Data View variant
  const dataviewConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Basic Count Metric (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()'
  };

  await generateDualFixture(
    'metric-basic',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricBasic, import.meta.url);
