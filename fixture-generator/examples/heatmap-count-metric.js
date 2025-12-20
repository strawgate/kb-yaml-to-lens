#!/usr/bin/env node
/**
 * Example: Generate a heatmap with count aggregation
 *
 * Demonstrates using COUNT() aggregation for simple event counting
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmapCountMetric() {
  const builder = new LensConfigBuilder();

  // Heatmap using count aggregation
  const config = {
    chartType: 'heatmap',
    title: 'Event Count by Response Code and Extension',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS event_count = COUNT() BY response.keyword, extension.keyword'
    },
    breakdown: 'response.keyword',   // Y-axis: HTTP response code
    xAxis: 'extension.keyword',      // X-axis: file extension
    value: 'event_count',            // Metric: count of events
    legend: {
      show: true,
      position: 'top'
    }
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'heatmap-count-metric.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: heatmap-count-metric.json');
}

if (require.main === module) {
  generateHeatmapCountMetric()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateHeatmapCountMetric };
