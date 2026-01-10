#!/usr/bin/env node
/**
 * Example: Generate fixtures with complex Lens formulas
 *
 * Demonstrates various formula types:
 * - Simple aggregations: count(), unique_count(), sum()
 * - Math operations: sum(field) / count()
 * - fullReference operations: counter_rate(max(field)), cumulative_sum(count())
 * - Nested formulas: moving_average(average(field))
 *
 * These fixtures are used to validate the formula parser generates correct
 * helper columns (X0, X1, etc.) and tinymath AST structures.
 */

import type { LensXYConfig, LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, generateFixture, runIfMain } from '../generator-utils.js';

export async function generateFormulaComplex(): Promise<void> {
  // ========================================
  // 1. Simple formula with single aggregation
  // ========================================
  const simpleMetric: LensMetricConfig = {
    chartType: 'metric',
    title: 'Simple Formula - unique_count',
    dataset: {
      index: 'postgresql-*'
    },
    value: 'unique_count(resource.attributes.postgresql.database.name)'
  };

  await generateFixture(
    'formula-simple-unique-count.json',
    simpleMetric,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 2. Math formula with division
  // ========================================
  const mathDivision: LensMetricConfig = {
    chartType: 'metric',
    title: 'Math Formula - Division',
    dataset: {
      index: 'metrics-*'
    },
    value: 'sum(bytes) / count()'
  };

  await generateFixture(
    'formula-math-division.json',
    mathDivision,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 3. counter_rate with max (fullReference operation)
  // ========================================
  const counterRateMetric: LensMetricConfig = {
    chartType: 'metric',
    title: 'Counter Rate with Max',
    dataset: {
      index: 'postgresql-*'
    },
    value: 'counter_rate(max(postgresql.operations))'
  };

  await generateFixture(
    'formula-counter-rate-max.json',
    counterRateMetric,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 4. cumulative_sum with count
  // ========================================
  const cumulativeSumMetric: LensMetricConfig = {
    chartType: 'metric',
    title: 'Cumulative Sum of Count',
    dataset: {
      index: 'logs-*'
    },
    value: 'cumulative_sum(count())'
  };

  await generateFixture(
    'formula-cumulative-sum-count.json',
    cumulativeSumMetric,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 5. differences with sum
  // ========================================
  const differencesMetric: LensMetricConfig = {
    chartType: 'metric',
    title: 'Differences of Sum',
    dataset: {
      index: 'metrics-*'
    },
    value: 'differences(sum(bytes))'
  };

  await generateFixture(
    'formula-differences-sum.json',
    differencesMetric,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 6. moving_average with average
  // ========================================
  const movingAverageMetric: LensMetricConfig = {
    chartType: 'metric',
    title: 'Moving Average of Average',
    dataset: {
      index: 'metrics-*'
    },
    value: 'moving_average(average(cpu.usage))'
  };

  await generateFixture(
    'formula-moving-average.json',
    movingAverageMetric,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 7. Complex formula with multiple operations
  // ========================================
  const complexFormula: LensMetricConfig = {
    chartType: 'metric',
    title: 'Complex Formula - Multiple Counter Rates',
    dataset: {
      index: 'postgresql-*'
    },
    // Formula: (counter_rate(max(field1)) + counter_rate(max(field2))) / 2
    value: '(counter_rate(max(postgresql.rows_fetched)) + counter_rate(max(postgresql.rows_returned))) / 2'
  };

  await generateFixture(
    'formula-complex-counter-rates.json',
    complexFormula,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 8. Formula with KQL filter
  // ========================================
  const formulaWithFilter: LensMetricConfig = {
    chartType: 'metric',
    title: 'Formula with KQL Filter',
    dataset: {
      index: 'logs-*'
    },
    value: "count(kql='log.level: error')"
  };

  await generateFixture(
    'formula-with-kql-filter.json',
    formulaWithFilter,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 9. XY chart with counter_rate formula over time
  // ========================================
  const counterRateXY: LensXYConfig = {
    chartType: 'xy',
    title: 'Counter Rate Over Time',
    dataset: {
      index: 'postgresql-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: {
          type: 'dateHistogram',
          field: '@timestamp'
        },
        yAxis: [
          {
            label: 'Operations Rate',
            value: 'counter_rate(max(postgresql.operations))'
          }
        ]
      }
    ],
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'formula-xy-counter-rate.json',
    counterRateXY,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );

  // ========================================
  // 10. percentile formula
  // ========================================
  const percentileMetric: LensMetricConfig = {
    chartType: 'metric',
    title: 'Percentile 95',
    dataset: {
      index: 'apm-*'
    },
    value: 'percentile(transaction.duration.us, percentile=95)'
  };

  await generateFixture(
    'formula-percentile.json',
    percentileMetric,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );

  console.log('✓ All formula fixtures generated successfully');
}

runIfMain(generateFormulaComplex, import.meta.url);
