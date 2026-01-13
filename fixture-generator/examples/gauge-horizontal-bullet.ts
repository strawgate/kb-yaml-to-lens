#!/usr/bin/env node
/**
 * Example: Generate gauge chart with horizontal bullet shape (both ES|QL and Data View)
 *
 * Demonstrates creating a horizontal bullet gauge showing a metric value with goal/target
 */

import type { LensGaugeConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateGaugeHorizontalBullet(): Promise<void> {
  const sharedConfig: Partial<LensGaugeConfig> = {
    queryMinValue: '0',
    queryMaxValue: '100',
    queryGoalValue: '80',
    shape: 'horizontalBullet'
  };

  const esqlConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'Disk Usage (Horizontal Bullet)',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_disk = AVG(system.disk.used.pct) * 100'
    },
    value: 'avg_disk'
  };

  const dataviewConfig: LensGaugeConfig = {
    chartType: 'gauge',
    ...sharedConfig,
    title: 'Disk Usage (Horizontal Bullet, Data View)',
    dataset: {
      index: 'metrics-*'
    },
    value: 'average(system.disk.used.pct) * 100'
  };

  await generateDualFixture(
    'gauge-horizontal-bullet',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-15m', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateGaugeHorizontalBullet, import.meta.url);
