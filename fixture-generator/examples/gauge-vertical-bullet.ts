#!/usr/bin/env node
/**
 * Example: Generate gauge chart with vertical bullet shape (both ES|QL and Data View)
 *
 * Demonstrates creating a vertical bullet gauge showing a metric value with goal/target
 */

import type { LensGaugeConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateGaugeVerticalBullet(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensGaugeConfig> = {
    queryMinValue: '0',
    queryMaxValue: '100',
    queryGoalValue: '95',
    shape: 'verticalBullet'
  };

  // ES|QL variant
  const esqlConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'Uptime Score (Vertical Bullet)',
    dataset: {
      esql: 'FROM metrics-* | STATS uptime = AVG(system.uptime.pct) * 100'
    },
    value: 'uptime'
  };

  // Data View variant
  const dataviewConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'Uptime Score (Vertical Bullet, Data View)',
    dataset: {
      index: 'metrics-*'
    },
    value: 'average(system.uptime.pct)'
  };

  await generateDualFixture(
    'gauge-vertical-bullet',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-15m', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateGaugeVerticalBullet, import.meta.url);
