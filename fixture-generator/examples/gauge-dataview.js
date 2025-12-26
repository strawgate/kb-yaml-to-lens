#!/usr/bin/env node
/**
 * Example: Generate a gauge chart visualization (using data view)
 *
 * Demonstrates creating a gauge showing a single metric value with min/max ranges
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateGaugeDataview() {
  const config = {
    chartType: 'gauge',
    title: 'CPU Usage Gauge (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    metric: 'average(system.cpu.total.pct)',
    min: 0,
    max: 1,
    goal: 0.8,
    shape: 'arc',
    colorMode: 'palette'
  };

  await generateFixture(
    'gauge-dataview.json',
    config,
    { timeRange: { from: 'now-15m', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateGaugeDataview, import.meta.url);
