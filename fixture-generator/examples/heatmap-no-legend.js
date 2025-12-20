#!/usr/bin/env node
/**
 * Example: Generate a heatmap without legend
 *
 * Demonstrates minimal heatmap configuration without legend display
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmapNoLegend() {
  const builder = new LensConfigBuilder();

  // Minimal heatmap without legend
  const config = {
    chartType: 'heatmap',
    title: 'Traffic Volume (No Legend)',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS total_bytes = SUM(bytes) BY host.keyword, geo.src'
    },
    breakdown: 'host.keyword',  // Y-axis: hostname
    xAxis: 'geo.src',           // X-axis: source country
    value: 'total_bytes',       // Metric: total bytes
    legend: {
      show: false  // Hide legend for cleaner visualization
    }
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'heatmap-no-legend.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: heatmap-no-legend.json');
}

if (require.main === module) {
  generateHeatmapNoLegend()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateHeatmapNoLegend };
