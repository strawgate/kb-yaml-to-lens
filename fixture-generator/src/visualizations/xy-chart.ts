/**
 * XY Chart visualization builder
 * Generates Kibana Lens XY chart attributes (line, bar, area, stacked variants)
 */

import { v4 as uuid } from 'uuid';
import { LensAttributes } from '../types/lens';

export interface XYChartConfig {
  title: string;
  dataViewId: string;
  seriesType: 'line' | 'bar' | 'area' | 'bar_stacked' | 'area_stacked' | 'bar_horizontal';
  xAxis: {
    field: string;
    type: 'date_histogram' | 'terms';
    interval?: string;
    size?: number;
  };
  yAxis: {
    operation: 'count' | 'sum' | 'average' | 'min' | 'max';
    field?: string;
    label?: string;
  };
  breakdown?: {
    field: string;
    size?: number;
  };
  legend?: {
    isVisible: boolean;
    position: 'top' | 'bottom' | 'left' | 'right';
  };
}

export function buildXYChart(config: XYChartConfig): LensAttributes {
  const layerId = uuid();
  const xColumnId = uuid();
  const yColumnId = uuid();
  const breakdownColumnId = config.breakdown ? uuid() : undefined;

  const columns: Record<string, unknown> = {
    [xColumnId]: buildXAxisColumn(config.xAxis, xColumnId, yColumnId),
    [yColumnId]: buildYAxisColumn(config.yAxis, yColumnId),
  };

  const columnOrder = [xColumnId];
  const accessors = [yColumnId];

  if (breakdownColumnId && config.breakdown) {
    columns[breakdownColumnId] = {
      label: `Top ${config.breakdown.size || 5} ${config.breakdown.field}`,
      dataType: 'string',
      operationType: 'terms',
      sourceField: config.breakdown.field,
      isBucketed: true,
      scale: 'ordinal',
      params: {
        size: config.breakdown.size || 5,
        orderBy: { type: 'column', columnId: yColumnId },
        orderDirection: 'desc',
        otherBucket: true,
        missingBucket: false,
      },
    };
    columnOrder.unshift(breakdownColumnId);
  }

  columnOrder.push(yColumnId);

  return {
    title: config.title,
    visualizationType: 'lnsXY',
    state: {
      visualization: {
        legend: config.legend || { isVisible: true, position: 'right' },
        valueLabels: 'hide',
        fittingFunction: 'None',
        preferredSeriesType: config.seriesType,
        layers: [
          {
            layerId,
            layerType: 'data',
            seriesType: config.seriesType,
            xAccessor: xColumnId,
            accessors,
            splitAccessor: breakdownColumnId,
          },
        ],
        axisTitlesVisibilitySettings: { x: true, yLeft: true, yRight: true },
        tickLabelsVisibilitySettings: { x: true, yLeft: true, yRight: true },
        gridlinesVisibilitySettings: { x: true, yLeft: true, yRight: true },
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns,
              columnOrder,
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

function buildXAxisColumn(
  xAxis: XYChartConfig['xAxis'],
  columnId: string,
  metricColumnId: string
) {
  if (xAxis.type === 'date_histogram') {
    return {
      label: xAxis.field,
      dataType: 'date',
      operationType: 'date_histogram',
      sourceField: xAxis.field,
      isBucketed: true,
      scale: 'interval',
      params: {
        interval: xAxis.interval || 'auto',
        includeEmptyRows: true,
        dropPartials: false,
      },
    };
  }
  return {
    label: `Top ${xAxis.size || 10} ${xAxis.field}`,
    dataType: 'string',
    operationType: 'terms',
    sourceField: xAxis.field,
    isBucketed: true,
    scale: 'ordinal',
    params: {
      size: xAxis.size || 10,
      orderBy: { type: 'column', columnId: metricColumnId },
      orderDirection: 'desc',
    },
  };
}

function buildYAxisColumn(yAxis: XYChartConfig['yAxis'], columnId: string) {
  const base = {
    label:
      yAxis.label ||
      (yAxis.operation === 'count'
        ? 'Count'
        : `${yAxis.operation}(${yAxis.field})`),
    dataType: 'number',
    operationType: yAxis.operation,
    isBucketed: false,
    scale: 'ratio',
  };

  if (yAxis.operation === 'count') {
    return { ...base, sourceField: '___records___' };
  }
  return { ...base, sourceField: yAxis.field };
}
