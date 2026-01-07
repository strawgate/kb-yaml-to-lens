#!/usr/bin/env node
/**
 * Example: Generate gauge chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a gauge showing a single metric value with min/max ranges
 */

import type { LensGaugeConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateGauge(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensGaugeConfig> = {
    queryMinValue: '0',
    queryMaxValue: '1',
    queryGoalValue: '0.8',
    shape: 'arc'
  };

  // ES|QL variant
  const esqlConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'CPU Usage Gauge',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)'
    },
    value: 'avg_cpu'
  };

  // Data View variant
  const dataviewConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'CPU Usage Gauge (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    value: 'average(system.cpu.total.pct)'
  };

  await generateDualFixture(
    'gauge',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-15m', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateGauge, import.meta.url);
