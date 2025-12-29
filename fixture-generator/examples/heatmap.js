#!/usr/bin/env node
/**
 * Example: Generate heatmap visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a heatmap showing geographic traffic patterns
 * with data aggregated by source and destination countries.
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateHeatmap() {
  // Shared configuration between both variants
  const sharedConfig = {
    chartType: 'heatmap',
    legend: {
      show: true,
      position: 'right'
    }
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'Traffic Heatmap by Geographic Location',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src'
    },
    breakdown: 'geo.dest',  // Y-axis: destination country
    xAxis: 'geo.src',       // X-axis: source country
    value: 'bytes'          // Metric: total bytes transferred
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'Traffic Heatmap by Geographic Location (Data View)',
    dataset: {
      index: 'kibana_sample_data_logs'
    },
    breakdown: 'geo.dest',
    xAxis: 'geo.src',
    value: 'sum(bytes)'
  };

  await generateDualFixture(
    'heatmap',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateHeatmap, import.meta.url);
