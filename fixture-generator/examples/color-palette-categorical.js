#!/usr/bin/env node
/**
 * Example: Generate a pie chart with categorical color mapping
 *
 * Demonstrates categorical color palette with custom assignments
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateColorPaletteCategorical() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: 'pie',
    title: 'Events by Level (Color Palette Test)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'
    },
    value: 'count',
    breakdown: 'log.level',
    palette: {
      type: 'palette',
      name: 'eui_amsterdam_color_blind'
    }
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'color-palette-categorical.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: color-palette-categorical.json');

  // Also output just the colorMapping for inspection
  if (lensAttributes.state && lensAttributes.state.visualization) {
    const layers = lensAttributes.state.visualization.layers;
    if (layers && layers.length > 0 && layers[0].colorMapping) {
      const colorMappingPath = path.join(outputDir, 'color-mapping-structure.json');
      fs.writeFileSync(colorMappingPath, JSON.stringify(layers[0].colorMapping, null, 2));
      console.log('✓ Generated: color-mapping-structure.json (for schema inspection)');
    }
  }
}

if (require.main === module) {
  generateColorPaletteCategorical()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateColorPaletteCategorical };
