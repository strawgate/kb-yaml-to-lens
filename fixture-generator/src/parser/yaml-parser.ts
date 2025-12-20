/**
 * YAML Dashboard Parser
 * Parses YAML configuration files and builds dashboard JSON
 */

import * as yaml from 'js-yaml';
import * as fs from 'fs';
import { DashboardBuilder } from '../dashboard/builder';
import { LensAttributeBuilder } from './attribute-builder';
import { PanelLayout } from '../dashboard/grid';

interface YamlConfig {
  version: string;
  settings: {
    dataView: string;
    timeFrom?: string;
    timeTo?: string;
  };
  dashboard: {
    title: string;
    description?: string;
  };
  panels: Array<{
    type: string;
    title: string;
    layout: string | { type: string; width?: number; height?: number };
    config: Record<string, unknown>;
  }>;
}

export class YamlDashboardParser {
  private builder: LensAttributeBuilder;

  constructor() {
    this.builder = new LensAttributeBuilder();
  }

  parse(yamlPath: string): string {
    const content = fs.readFileSync(yamlPath, 'utf-8');
    const config = yaml.load(content) as YamlConfig;

    return this.buildDashboard(config);
  }

  parseString(yamlContent: string): string {
    const config = yaml.load(yamlContent) as YamlConfig;
    return this.buildDashboard(config);
  }

  private buildDashboard(config: YamlConfig): string {
    const panels = config.panels.map((panel) => {
      // Merge default data view into panel config
      const vizConfig = {
        ...panel.config,
        title: panel.title,
        dataViewId:
          (panel.config as any).dataView || config.settings.dataView,
      };

      // Build visualization attributes
      const visualization = this.builder.buildVisualization({
        type: panel.type,
        ...vizConfig,
      });

      // Parse layout
      const layout = this.parseLayout(panel.layout);

      return {
        visualization,
        layout,
        title: panel.title,
      };
    });

    const dashboardBuilder = new DashboardBuilder({
      title: config.dashboard.title,
      description: config.dashboard.description,
      timeFrom: config.settings.timeFrom,
      timeTo: config.settings.timeTo,
      panels,
    });

    return dashboardBuilder.toJSON();
  }

  private parseLayout(
    layout: string | { type: string; width?: number; height?: number }
  ): PanelLayout {
    if (typeof layout === 'string') {
      return {
        type: layout as 'full' | 'half' | 'third' | 'quarter',
      };
    }
    return {
      type: layout.type as 'full' | 'half' | 'third' | 'quarter' | 'custom',
      customWidth: layout.width,
      height: layout.height,
    };
  }
}
