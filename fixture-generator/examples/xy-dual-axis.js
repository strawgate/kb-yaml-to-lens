#!/usr/bin/env node
/**
 * Example: Generate an XY chart with dual Y-axes
 *
 * Demonstrates creating a line chart with metrics on different Y-axes (left/right)
 * to test per-series Y-axis configuration
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateDualAxisChart() {
  const builder = new LensConfigBuilder();

  // Try to configure dual Y-axis with per-series configuration
  const config = {
    chartType: 'xy',
    title: 'Dual Y-Axis Chart',
    dataset: {
      esql: `FROM logs-* 
        | STATS 
          count = COUNT(), 
          avg_bytes = AVG(bytes) 
        BY @timestamp`
    },
    layers: [{
      seriesType: 'line',
      xAxis: '@timestamp',
      breakdown: null,
      metrics: [
        {
          value: 'count',
          label: 'Event Count',
          color: '#2196F3',
          axisMode: 'left'
        },
        {
          value: 'avg_bytes',
          label: 'Avg Bytes',
          color: '#FF5252',
          axisMode: 'right'
        }
      ]
    }],
    legend: {
      show: true,
      position: 'right'
    }
  };

  try {
    const lensAttributes = await builder.build(config, {
      timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
    });

    const outputDir = path.join(__dirname, '..', 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const outputPath = path.join(outputDir, 'xy-dual-axis.json');
    fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

    console.log('✓ Generated: xy-dual-axis.json');
  } catch (error) {
    console.error('Error generating dual-axis chart:', error.message);
    console.error('Note: This API might not support all dual-axis configuration yet');
    throw error;
  }
}

if (require.main === module) {
  generateDualAxisChart()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateDualAxisChart };
