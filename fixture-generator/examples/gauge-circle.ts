#!/usr/bin/env node
/**
 * Example: Generate gauge chart with circle shape (both ES|QL and Data View)
 *
 * Demonstrates creating a circular gauge showing a single metric value with min/max ranges
 */

import type { LensGaugeConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateGaugeCircle(): Promise<void> {
  const sharedConfig: Partial<LensGaugeConfig> = {
    queryMinValue: '0',
    queryMaxValue: '1',
    queryGoalValue: '0.8',
    shape: 'circle'
  };

  const esqlConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'Memory Usage Gauge (Circle)',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_mem = AVG(system.memory.used.pct)'
    },
    value: 'avg_mem'
  };

  const dataviewConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'Memory Usage Gauge (Circle, Data View)',
    dataset: {
      index: 'metrics-*'
    },
    value: 'average(system.memory.used.pct)'
  };

  await generateDualFixture(
    'gauge-circle',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-15m', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateGaugeCircle, import.meta.url);
