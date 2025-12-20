/**
 * Metric visualization builder
 * Generates Kibana Lens metric chart attributes
 */

import { v4 as uuid } from 'uuid';
import { LensAttributes } from '../types/lens';

export interface MetricConfig {
  title: string;
  dataViewId: string;
  metric: {
    operation: 'count' | 'sum' | 'average' | 'min' | 'max' | 'unique_count';
    field?: string;
    label?: string;
  };
  secondaryMetric?: {
    operation: 'count' | 'sum' | 'average';
    field?: string;
  };
  breakdown?: {
    field: string;
    size?: number;
  };
  trendLine?: boolean;
  color?: string;
}

export function buildMetricVisualization(config: MetricConfig): LensAttributes {
  const layerId = uuid();
  const primaryMetricId = uuid();
  const secondaryMetricId = config.secondaryMetric ? uuid() : undefined;
  const breakdownId = config.breakdown ? uuid() : undefined;
  const trendDateId = config.trendLine ? uuid() : undefined;

  const columns: Record<string, unknown> = {
    [primaryMetricId]: {
      label: config.metric.label || `${config.metric.operation}`,
      dataType: 'number',
      operationType: config.metric.operation,
      sourceField: config.metric.field || '___records___',
      isBucketed: false,
      scale: 'ratio',
      params: { emptyAsNull: true },
    },
  };

  const columnOrder: string[] = [];

  if (breakdownId && config.breakdown) {
    columns[breakdownId] = {
      label: config.breakdown.field,
      dataType: 'string',
      operationType: 'terms',
      sourceField: config.breakdown.field,
      isBucketed: true,
      scale: 'ordinal',
      params: {
        size: config.breakdown.size || 5,
        orderBy: { type: 'column', columnId: primaryMetricId },
        orderDirection: 'desc',
      },
    };
    columnOrder.push(breakdownId);
  }

  if (secondaryMetricId && config.secondaryMetric) {
    columns[secondaryMetricId] = {
      label: `${config.secondaryMetric.operation}`,
      dataType: 'number',
      operationType: config.secondaryMetric.operation,
      sourceField: config.secondaryMetric.field || '___records___',
      isBucketed: false,
      scale: 'ratio',
    };
    columnOrder.push(secondaryMetricId);
  }

  if (trendDateId && config.trendLine) {
    columns[trendDateId] = {
      label: '@timestamp',
      dataType: 'date',
      operationType: 'date_histogram',
      sourceField: '@timestamp',
      isBucketed: true,
      scale: 'interval',
      params: { interval: 'auto' },
    };
    columnOrder.push(trendDateId);
  }

  columnOrder.push(primaryMetricId);

  return {
    title: config.title,
    visualizationType: 'lnsMetric',
    state: {
      visualization: {
        layerId,
        layerType: 'data',
        metricAccessor: primaryMetricId,
        secondaryMetricAccessor: secondaryMetricId,
        breakdownByAccessor: breakdownId,
        trendlineLayerId: config.trendLine ? layerId : undefined,
        trendlineMetricAccessor: config.trendLine ? primaryMetricId : undefined,
        trendlineTimeAccessor: trendDateId,
        color: config.color,
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: { columns, columnOrder, incompleteColumns: {} },
          },
        },
      },
    },
    references: [
      {
        type: 'index-pattern',
        id: config.dataViewId,
        name: `indexpattern-datasource-layer-${layerId}`,
      },
    ],
  };
}
