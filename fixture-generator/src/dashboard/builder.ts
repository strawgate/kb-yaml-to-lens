/**
 * Dashboard builder
 * Assembles Lens visualizations into a complete Kibana dashboard
 */

import { v4 as uuid } from 'uuid';
import { GridLayoutCalculator, PanelLayout } from './grid';
import { DashboardSavedObject, LensAttributes } from '../types/lens';

export interface DashboardConfig {
  title: string;
  description?: string;
  timeFrom?: string;
  timeTo?: string;
  panels: Array<{
    visualization: LensAttributes;
    layout: PanelLayout;
    title?: string;
  }>;
}

export class DashboardBuilder {
  private dashboardId: string;
  private grid: GridLayoutCalculator;
  private panels: any[] = [];
  private references: any[] = [];

  constructor(private config: DashboardConfig) {
    this.dashboardId = uuid();
    this.grid = new GridLayoutCalculator();
  }

  build(): { dashboard: DashboardSavedObject; visualizations: any[] } {
    const visualizations: any[] = [];

    this.config.panels.forEach((panel, index) => {
      const panelId = uuid();
      const vizId = uuid();
      const position = this.grid.calculatePosition(panel.layout);

      // Create by-value panel (embedded visualization)
      const panelConfig = {
        type: 'lens',
        gridData: {
          x: position.x,
          y: position.y,
          w: position.w,
          h: position.h,
          i: panelId,
        },
        panelIndex: panelId,
        embeddableConfig: {
          attributes: {
            ...panel.visualization,
            title: panel.title || panel.visualization.title,
          },
          enhancements: {},
        },
      };

      this.panels.push(panelConfig);

      // Collect references from visualization
      panel.visualization.references.forEach((ref: any) => {
        this.references.push({
          ...ref,
          name: `${panelId}:${ref.name}`,
        });
      });
    });

    const dashboard: DashboardSavedObject = {
      type: 'dashboard',
      id: this.dashboardId,
      attributes: {
        title: this.config.title,
        description: this.config.description || '',
        version: 1,
        timeRestore: !!(this.config.timeFrom || this.config.timeTo),
        timeFrom: this.config.timeFrom,
        timeTo: this.config.timeTo,
        kibanaSavedObjectMeta: {
          searchSourceJSON: JSON.stringify({
            query: { query: '', language: 'kuery' },
            filter: [],
          }),
        },
        optionsJSON: JSON.stringify({
          useMargins: true,
          syncColors: false,
          syncCursor: true,
          syncTooltips: false,
          hidePanelTitles: false,
        }),
        panelsJSON: JSON.stringify(this.panels),
      },
      references: this.references,
    };

    return { dashboard, visualizations };
  }

  toNDJSON(): string {
    const { dashboard } = this.build();
    return JSON.stringify(dashboard);
  }

  toJSON(): string {
    const { dashboard } = this.build();
    return JSON.stringify(dashboard, null, 2);
  }
}
