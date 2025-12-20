#!/usr/bin/env node
/**
 * Example: Generate a basic 2D heatmap visualization
 *
 * Demonstrates a simple heatmap with X and Y axes showing geographic traffic patterns
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmapBasic() {
  const builder = new LensConfigBuilder();

  // Basic 2D heatmap configuration
  // Shows traffic volume between source and destination countries
  const config = {
    chartType: 'heatmap',
    title: 'Traffic Heatmap by Geographic Location',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src'
    },
    breakdown: 'geo.dest',  // Y-axis: destination country
    xAxis: 'geo.src',       // X-axis: source country
    value: 'bytes',         // Metric: total bytes transferred
    legend: {
      show: true,
      position: 'right'
    }
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'heatmap-basic.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: heatmap-basic.json');
}

if (require.main === module) {
  generateHeatmapBasic()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateHeatmapBasic };
