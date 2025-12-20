/**
 * Gauge visualization builder
 */

import { v4 as uuid } from 'uuid';
import { LensAttributes } from '../types/lens';

export interface GaugeConfig {
  title: string;
  dataViewId: string;
  metric: {
    operation: 'count' | 'sum' | 'average' | 'min' | 'max';
    field?: string;
    label?: string;
  };
  shape:
    | 'horizontalBullet'
    | 'verticalBullet'
    | 'semiCircle'
    | 'arc'
    | 'circle';
  min?: number;
  max?: number;
  goal?: number;
  colorMode?: 'none' | 'palette';
}

export function buildGaugeVisualization(config: GaugeConfig): LensAttributes {
  const layerId = uuid();
  const metricId = uuid();
  const minId = config.min !== undefined ? uuid() : undefined;
  const maxId = config.max !== undefined ? uuid() : undefined;
  const goalId = config.goal !== undefined ? uuid() : undefined;

  const columns: Record<string, unknown> = {
    [metricId]: {
      label: config.metric.label || config.metric.operation,
      dataType: 'number',
      operationType: config.metric.operation,
      sourceField: config.metric.field || '___records___',
      isBucketed: false,
      scale: 'ratio',
    },
  };

  const columnOrder = [metricId];

  if (minId !== undefined) {
    columns[minId] = {
      label: 'Min',
      dataType: 'number',
      operationType: 'static_value',
      isBucketed: false,
      scale: 'ratio',
      params: { value: config.min?.toString() },
      references: [],
    };
    columnOrder.push(minId);
  }

  if (maxId !== undefined) {
    columns[maxId] = {
      label: 'Max',
      dataType: 'number',
      operationType: 'static_value',
      isBucketed: false,
      scale: 'ratio',
      params: { value: config.max?.toString() },
      references: [],
    };
    columnOrder.push(maxId);
  }

  if (goalId !== undefined) {
    columns[goalId] = {
      label: 'Goal',
      dataType: 'number',
      operationType: 'static_value',
      isBucketed: false,
      scale: 'ratio',
      params: { value: config.goal?.toString() },
      references: [],
    };
    columnOrder.push(goalId);
  }

  return {
    title: config.title,
    visualizationType: 'lnsGauge',
    state: {
      visualization: {
        layerId,
        layerType: 'data',
        shape: config.shape,
        metricAccessor: metricId,
        minAccessor: minId,
        maxAccessor: maxId,
        goalAccessor: goalId,
        colorMode: config.colorMode || 'none',
        ticksPosition: 'auto',
        labelMajorMode: 'auto',
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
