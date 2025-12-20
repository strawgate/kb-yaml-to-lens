/**
 * Heatmap visualization builder
 */

import { v4 as uuid } from 'uuid';
import { LensAttributes } from '../types/lens';

export interface HeatmapConfig {
  title: string;
  dataViewId: string;
  xAxis: {
    field: string;
    type: 'date_histogram' | 'terms';
    interval?: string;
    size?: number;
  };
  yAxis: {
    field: string;
    size?: number;
  };
  value: {
    operation: 'count' | 'sum' | 'average' | 'min' | 'max';
    field?: string;
  };
  legend?: {
    isVisible: boolean;
    position: 'top' | 'bottom' | 'left' | 'right';
  };
}

export function buildHeatmap(config: HeatmapConfig): LensAttributes {
  const layerId = uuid();
  const xId = uuid();
  const yId = uuid();
  const valueId = uuid();

  const columns: Record<string, unknown> = {
    [xId]:
      config.xAxis.type === 'date_histogram'
        ? {
            label: config.xAxis.field,
            dataType: 'date',
            operationType: 'date_histogram',
            sourceField: config.xAxis.field,
            isBucketed: true,
            scale: 'interval',
            params: { interval: config.xAxis.interval || 'auto' },
          }
        : {
            label: config.xAxis.field,
            dataType: 'string',
            operationType: 'terms',
            sourceField: config.xAxis.field,
            isBucketed: true,
            scale: 'ordinal',
            params: { size: config.xAxis.size || 10, orderDirection: 'desc' },
          },
    [yId]: {
      label: config.yAxis.field,
      dataType: 'string',
      operationType: 'terms',
      sourceField: config.yAxis.field,
      isBucketed: true,
      scale: 'ordinal',
      params: { size: config.yAxis.size || 10, orderDirection: 'desc' },
    },
    [valueId]: {
      label:
        config.value.operation === 'count'
          ? 'Count'
          : `${config.value.operation}(${config.value.field})`,
      dataType: 'number',
      operationType: config.value.operation,
      sourceField: config.value.field || '___records___',
      isBucketed: false,
      scale: 'ratio',
    },
  };

  return {
    title: config.title,
    visualizationType: 'lnsHeatmap',
    state: {
      visualization: {
        layerId,
        layerType: 'data',
        shape: 'heatmap',
        xAccessor: xId,
        yAccessor: yId,
        valueAccessor: valueId,
        legend: {
          isVisible: config.legend?.isVisible ?? true,
          position: config.legend?.position || 'right',
          type: 'gradient',
        },
        gridConfig: {
          strokeWidth: 1,
          isCellLabelVisible: false,
          isYAxisLabelVisible: true,
          isXAxisLabelVisible: true,
        },
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns,
              columnOrder: [yId, xId, valueId],
              incompleteColumns: {},
            },
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
