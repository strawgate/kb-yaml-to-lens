#!/usr/bin/env node
/**
 * Example: Generate a gauge chart visualization
 *
 * Demonstrates creating a gauge showing a single metric value with min/max ranges
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateGauge() {
  const config = {
    chartType: 'gauge',
    title: 'CPU Usage Gauge',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)'
    },
    metric: 'avg_cpu',
    min: 0,
    max: 1,
    goal: 0.8,
    shape: 'arc',
    colorMode: 'palette'
  };

  await generateFixture(
    'gauge.json',
    config,
    { timeRange: { from: 'now-15m', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateGauge, import.meta.url);
