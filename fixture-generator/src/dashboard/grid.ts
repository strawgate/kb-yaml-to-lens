/**
 * Grid layout calculator for Kibana dashboard panels
 * Kibana uses a 48-column grid system
 */

export interface GridPosition {
  x: number; // 0-47
  y: number; // Row position
  w: number; // Width (max 48)
  h: number; // Height in row units
}

export interface PanelLayout {
  type: 'full' | 'half' | 'third' | 'quarter' | 'custom';
  height?: number;
  customWidth?: number;
}

export class GridLayoutCalculator {
  private currentY = 0;
  private currentX = 0;
  private rowHeight = 15;

  // Width mappings for standard layouts
  private widths = {
    full: 48,
    half: 24,
    third: 16,
    quarter: 12,
  };

  calculatePosition(layout: PanelLayout): GridPosition {
    const width =
      layout.type === 'custom'
        ? layout.customWidth || 24
        : this.widths[layout.type];
    const height = layout.height || this.rowHeight;

    // Check if panel fits in current row
    if (this.currentX + width > 48) {
      this.currentX = 0;
      this.currentY += this.rowHeight;
    }

    const position: GridPosition = {
      x: this.currentX,
      y: this.currentY,
      w: width,
      h: height,
    };

    this.currentX += width;

    // If we've filled a row, move to next
    if (this.currentX >= 48) {
      this.currentX = 0;
      this.currentY += height;
    }

    return position;
  }

  newRow(height?: number) {
    if (this.currentX > 0) {
      this.currentY += this.rowHeight;
      this.currentX = 0;
    }
    if (height) {
      this.rowHeight = height;
    }
  }

  reset() {
    this.currentX = 0;
    this.currentY = 0;
    this.rowHeight = 15;
  }
}
