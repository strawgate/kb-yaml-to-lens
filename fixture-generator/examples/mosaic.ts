#!/usr/bin/env node
/**
 * Example: Generate mosaic chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a mosaic chart with various configurations including
 * legend positioning, multi-dimensional grouping, and custom formatting.
 */

import type { LensMosaicConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMosaic(): Promise<void> {
  // ES|QL variant - basic mosaic
  const esqlConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'HTTP Methods Distribution',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY request.method'
    },
    breakdown: ['request.method'],
    value: 'count',
    legend: {
      show: true,
      position: 'right'
    }
  };

  // Data View variant - basic mosaic
  const dataviewConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'HTTP Methods Distribution (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    breakdown: ['request.method'],
    value: 'count()',
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateDualFixture(
    'mosaic',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

export async function generateMosaicMultiDimensional(): Promise<void> {
  // ES|QL variant - multi-dimensional mosaic
  const esqlConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'Traffic by Source and Destination',
    dataset: {
      esql: 'FROM logs-* | STATS bytes = SUM(bytes) BY geo.src, geo.dest'
    },
    breakdown: ['geo.src', 'geo.dest'],
    value: 'bytes',
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  // Data View variant - multi-dimensional mosaic
  const dataviewConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'Traffic by Source and Destination (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    breakdown: ['geo.src', 'geo.dest'],
    value: 'sum(bytes)',
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  await generateDualFixture(
    'mosaic-multi-dimensional',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(async () => {
  await generateMosaic();
  await generateMosaicMultiDimensional();
}, import.meta.url);
