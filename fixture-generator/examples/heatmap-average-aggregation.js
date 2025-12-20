#!/usr/bin/env node
/**
 * Example: Generate a heatmap with average aggregation
 *
 * Demonstrates using different aggregation types (average instead of sum/count)
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmapAverageAggregation() {
  const builder = new LensConfigBuilder();

  // Heatmap using average aggregation
  const config = {
    chartType: 'heatmap',
    title: 'Average Response Time by Country and OS',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS avg_bytes = AVG(bytes) BY geo.dest, machine.os.keyword'
    },
    breakdown: 'geo.dest',      // Y-axis: destination country
    xAxis: 'machine.os.keyword', // X-axis: operating system
    value: 'avg_bytes',          // Metric: average bytes (demonstrates non-count aggregation)
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

  const outputPath = path.join(outputDir, 'heatmap-average-aggregation.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: heatmap-average-aggregation.json');
}

if (require.main === module) {
  generateHeatmapAverageAggregation()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateHeatmapAverageAggregation };
