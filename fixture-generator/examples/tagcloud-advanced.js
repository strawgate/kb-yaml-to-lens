#!/usr/bin/env node
/**
 * Example: Generate tagcloud visualizations with various settings
 *
 * This creates multiple tagcloud fixtures to test different configurations:
 * - Basic tagcloud
 * - Custom font sizes
 * - Different orientations
 * - Label visibility
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

/**
 * Generate basic tagcloud (ES|QL)
 */
async function generateBasicTagcloud() {
  const config = {
    chartType: 'tagcloud',
    title: 'Basic Tag Cloud',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 20'
    },
    metric: 'count',
    breakdown: ['log.level']
  };

  await generateFixture(
    'tagcloud-basic.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

/**
 * Generate tagcloud with custom font sizes (ES|QL)
 */
async function generateTagcloudCustomFontSize() {
  const config = {
    chartType: 'tagcloud',
    title: 'Tag Cloud - Custom Font Size',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY host.name | SORT count DESC | LIMIT 15'
    },
    metric: 'count',
    breakdown: ['host.name'],
    // Custom appearance settings
    minFontSize: 24,
    maxFontSize: 96
  };

  await generateFixture(
    'tagcloud-custom-font-size.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

/**
 * Generate tagcloud with right-angled orientation (ES|QL)
 */
async function generateTagcloudRightAngled() {
  const config = {
    chartType: 'tagcloud',
    title: 'Tag Cloud - Right Angled',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY service.name | SORT count DESC | LIMIT 25'
    },
    metric: 'count',
    breakdown: ['service.name'],
    orientation: 'right angled'
  };

  await generateFixture(
    'tagcloud-right-angled.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

/**
 * Generate tagcloud with multiple orientations (ES|QL)
 */
async function generateTagcloudMultipleOrientations() {
  const config = {
    chartType: 'tagcloud',
    title: 'Tag Cloud - Multiple Orientations',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY error.type | SORT count DESC | LIMIT 30'
    },
    metric: 'count',
    breakdown: ['error.type'],
    orientation: 'multiple'
  };

  await generateFixture(
    'tagcloud-multiple-orientations.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

/**
 * Generate tagcloud without labels (ES|QL)
 */
async function generateTagcloudNoLabels() {
  const config = {
    chartType: 'tagcloud',
    title: 'Tag Cloud - No Labels',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY url.path | SORT count DESC | LIMIT 20'
    },
    metric: 'count',
    breakdown: ['url.path'],
    showLabel: false
  };

  await generateFixture(
    'tagcloud-no-labels.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

/**
 * Generate tagcloud with all custom settings (ES|QL)
 */
async function generateTagcloudAllSettings() {
  const config = {
    chartType: 'tagcloud',
    title: 'Tag Cloud - All Custom Settings',
    dataset: {
      esql: 'FROM logs-* | STATS total = COUNT() BY user.name | SORT total DESC | LIMIT 50'
    },
    metric: 'total',
    breakdown: ['user.name'],
    minFontSize: 18,
    maxFontSize: 120,
    orientation: 'right angled',
    showLabel: true
  };

  await generateFixture(
    'tagcloud-all-settings.json',
    config,
    { timeRange: { from: 'now-30d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

/**
 * Generate Data View variant with custom settings
 */
async function generateTagcloudDataView() {
  const config = {
    chartType: 'tagcloud',
    title: 'Tag Cloud - Data View',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    metric: [{
      type: 'count',
      label: 'Document Count'
    }],
    breakdown: [{
      type: 'terms',
      field: 'log.level',
      params: {
        size: 20,
        orderBy: { type: 'column', columnId: 'metric-column' },
        orderDirection: 'desc'
      }
    }],
    minFontSize: 16,
    maxFontSize: 80,
    orientation: 'single',
    showLabel: true
  };

  await generateFixture(
    'tagcloud-dataview.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

/**
 * Run all tagcloud generators
 */
async function generateAllTagclouds() {
  await generateBasicTagcloud();
  await generateTagcloudCustomFontSize();
  await generateTagcloudRightAngled();
  await generateTagcloudMultipleOrientations();
  await generateTagcloudNoLabels();
  await generateTagcloudAllSettings();
  await generateTagcloudDataView();
}

runIfMain(generateAllTagclouds, import.meta.url);

// Export for auto-discovery by generate-all.js
export { generateAllTagclouds };
