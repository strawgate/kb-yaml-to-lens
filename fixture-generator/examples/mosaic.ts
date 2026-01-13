#!/usr/bin/env node
/**
 * Example: Generate mosaic chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a mosaic chart with various configurations including
 * legend positioning and custom formatting. Mosaic charts support only one
 * dimension and one metric.
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

export async function generateMosaicWithLegendPosition(): Promise<void> {
  // ES|QL variant - mosaic with bottom legend
  const esqlConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'Traffic by Source Country',
    dataset: {
      esql: 'FROM logs-* | STATS bytes = SUM(bytes) BY geo.src'
    },
    breakdown: ['geo.src'],
    value: 'bytes',
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  // Data View variant - mosaic with bottom legend
  const dataviewConfig: LensMosaicConfig = {
    chartType: 'mosaic',
    title: 'Traffic by Source Country (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    breakdown: ['geo.src'],
    value: 'sum(bytes)',
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  await generateDualFixture(
    'mosaic-legend-position',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(async () => {
  await generateMosaic();
  await generateMosaicWithLegendPosition();
}, import.meta.url);
