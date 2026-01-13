/**
 * Preview - Handles visual and JSON preview of compiled dashboards
 */

/**
 * Update preview with compiled NDJSON
 */
function updatePreview(ndjson) {
  try {
    // Parse NDJSON (one JSON object per line)
    const lines = ndjson.trim().split('\n');
    const dashboards = lines.map(line => JSON.parse(line));
    
    if (dashboards.length === 0) {
      showPreviewError('No dashboards found in output');
      return;
    }
    
    // Update visual preview
    updateVisualPreview(dashboards[0]);
    
    // Update JSON preview
    updateJsonPreview(ndjson);
    
  } catch (error) {
    showPreviewError('Failed to parse compiled output: ' + error.message);
  }
}

/**
 * Update visual preview with dashboard grid
 */
function updateVisualPreview(dashboard) {
  const container = document.getElementById('visual-preview');
  const infoDiv = document.getElementById('dashboard-info');
  const gridDiv = document.getElementById('grid-preview');
  
  // Update dashboard info
  const attrs = dashboard.attributes || {};
  infoDiv.innerHTML = `
    <h3>${attrs.title || 'Untitled Dashboard'}</h3>
    <p>${attrs.description || 'No description'}</p>
  `;
  
  // Parse panels
  let panels = [];
  try {
    panels = JSON.parse(attrs.panelsJSON || '[]');
  } catch (error) {
    console.error('Failed to parse panelsJSON:', error);
  }
  
  // Clear and rebuild grid
  gridDiv.innerHTML = '';
  
  if (panels.length === 0) {
    gridDiv.innerHTML = '<div style="padding: 16px; color: #999;">No panels defined</div>';
    return;
  }
  
  // Create grid container
  const gridContainer = document.createElement('div');
  gridContainer.className = 'grid-container';
  gridContainer.style.minHeight = calculateGridHeight(panels) + 'px';
  
  // Add each panel
  panels.forEach(panel => {
    const panelEl = createPanelElement(panel);
    gridContainer.appendChild(panelEl);
  });
  
  gridDiv.appendChild(gridContainer);
}

/**
 * Create a visual panel element
 */
function createPanelElement(panel) {
  const div = document.createElement('div');
  div.className = 'panel-preview';
  
  const grid = panel.gridData || {};
  const x = grid.x || 0;
  const y = grid.y || 0;
  const w = grid.w || 24;
  const h = grid.h || 15;
  
  // Calculate position (48 column grid, 20px per row height)
  const left = (x / 48) * 100;
  const top = y * 20;
  const width = (w / 48) * 100;
  const height = h * 20;
  
  div.style.cssText = `
    left: ${left}%;
    top: ${top}px;
    width: ${width}%;
    height: ${height}px;
  `;
  
  // Determine panel type and add color coding
  let typeColor = '#007acc';
  let typeLabel = panel.type || 'unknown';
  
  if (panel.type === 'markdown') {
    typeColor = '#16825d';
  } else if (panel.type === 'lens') {
    typeColor = '#cca700';
    const vizType = panel.embeddableConfig?.attributes?.visualizationType || '';
    if (vizType) {
      typeLabel = vizType.replace('lns', '').toLowerCase();
    }
  }
  
  div.style.borderColor = typeColor;
  
  div.innerHTML = `
    <div class="panel-title">${panel.title || 'Untitled Panel'}</div>
    <div class="panel-type" style="color: ${typeColor}">${typeLabel}</div>
  `;
  
  return div;
}

/**
 * Calculate required grid height based on panels
 */
function calculateGridHeight(panels) {
  let maxY = 0;
  panels.forEach(panel => {
    const grid = panel.gridData || {};
    const bottom = (grid.y || 0) + (grid.h || 15);
    maxY = Math.max(maxY, bottom);
  });
  return Math.max(400, maxY * 20 + 40); // 20px per row + padding
}

/**
 * Update JSON preview
 */
function updateJsonPreview(ndjson) {
  const jsonOutput = document.getElementById('json-output');
  
  try {
    // Pretty print each line
    const lines = ndjson.trim().split('\n');
    const formatted = lines.map(line => {
      const obj = JSON.parse(line);
      return JSON.stringify(obj, null, 2);
    }).join('\n\n---\n\n');
    
    jsonOutput.textContent = formatted;
  } catch (error) {
    jsonOutput.textContent = ndjson; // Fallback to raw
  }
}

/**
 * Show error in preview
 */
function showPreviewError(message) {
  const gridDiv = document.getElementById('grid-preview');
  gridDiv.innerHTML = `
    <div style="padding: 16px; color: #f14c4c;">
      ⚠️ ${message}
    </div>
  `;
}
