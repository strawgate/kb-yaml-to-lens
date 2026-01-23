/**
 * Layout Editor - Drag and Drop Panel Management
 * 
 * This script handles interactive panel positioning and resizing in the dashboard preview.
 * It reads configuration from a <script id="layout-config"> element in the page.
 * 
 * Expected config format:
 * {
 *   "cellSize": 12,
 *   "gridColumns": 48,
 *   "panels": [...],
 *   "showStaleWarning": true|false
 * }
 */

(function () {
    'use strict';

    // Read configuration from the page
    const configElement = document.getElementById('layout-config');
    let config = {
        cellSize: 12,
        gridColumns: 48,
        panels: [],
        showStaleWarning: false
    };

    if (configElement) {
        try {
            config = { ...config, ...JSON.parse(configElement.textContent || '{}') };
        } catch (e) {
            console.error('Failed to parse layout config:', e);
        }
    }

    const CELL_SIZE = config.cellSize;
    const GRID_COLUMNS = config.gridColumns;
    let panels = config.panels || [];
    const showStaleWarning = config.showStaleWarning;

    // Acquire VS Code API for messaging
    const vscode = typeof acquireVsCodeApi === 'function' ? acquireVsCodeApi() : null;

    // State for drag/resize operations
    let draggedPanel = null;
    let dragStartX = 0;
    let dragStartY = 0;
    let dragStartGridX = 0;
    let dragStartGridY = 0;
    let isResizing = false;
    let resizeStartW = 0;
    let resizeStartH = 0;

    // DOM elements
    const gridElement = document.getElementById('layoutGrid');
    const showGridCheckbox = document.getElementById('showGrid');

    /**
     * Calculate the required grid height based on panel positions
     */
    function calculateGridHeight() {
        let maxY = 20;
        panels.forEach(panel => {
            const panelBottom = panel.grid.y + panel.grid.h;
            if (panelBottom > maxY) {
                maxY = panelBottom;
            }
        });
        return maxY + 10;
    }

    /**
     * Update the grid container height based on current panel positions
     */
    function updateGridHeight() {
        if (!gridElement) {
            return;
        }
        const gridHeight = calculateGridHeight();
        const heightPx = (gridHeight * CELL_SIZE) + 'px';
        gridElement.style.height = heightPx;
        const container = gridElement.parentElement;
        if (container) {
            container.style.height = heightPx;
        }
    }

    /**
     * Handle mouse down on a panel (start dragging)
     */
    function handlePanelMouseDown(e) {
        if (e.target.classList.contains('resize-handle')) {
            return;
        }
        e.preventDefault();
        draggedPanel = e.target.closest('.layout-panel');
        if (!draggedPanel) return;

        const index = parseInt(draggedPanel.dataset.index, 10);
        if (isNaN(index) || !panels[index]) return;

        dragStartX = e.clientX;
        dragStartY = e.clientY;
        dragStartGridX = panels[index].grid.x;
        dragStartGridY = panels[index].grid.y;
        isResizing = false;

        draggedPanel.classList.add('dragging');

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }

    /**
     * Handle mouse down on resize handle (start resizing)
     */
    function handleResizeMouseDown(e) {
        e.preventDefault();
        e.stopPropagation();

        isResizing = true;
        draggedPanel = e.target.closest('.layout-panel');
        if (!draggedPanel) return;

        const index = parseInt(draggedPanel.dataset.index, 10);
        if (isNaN(index) || !panels[index]) return;

        dragStartX = e.clientX;
        dragStartY = e.clientY;
        resizeStartW = panels[index].grid.w;
        resizeStartH = panels[index].grid.h;

        draggedPanel.classList.add('resizing');

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }

    /**
     * Handle mouse movement during drag/resize
     */
    function handleMouseMove(e) {
        if (!draggedPanel) return;

        const index = parseInt(draggedPanel.dataset.index, 10);
        if (isNaN(index) || !panels[index]) return;
        const panel = panels[index];

        if (isResizing) {
            const deltaX = e.clientX - dragStartX;
            const deltaY = e.clientY - dragStartY;

            let newW = resizeStartW + Math.round(deltaX / CELL_SIZE);
            let newH = resizeStartH + Math.round(deltaY / CELL_SIZE);

            // Enforce minimum size
            newW = Math.max(4, newW);
            newH = Math.max(4, newH);
            // Don't exceed grid bounds
            newW = Math.min(newW, GRID_COLUMNS - panel.grid.x);

            panel.grid.w = newW;
            panel.grid.h = newH;

            draggedPanel.style.width = (newW * CELL_SIZE) + 'px';
            draggedPanel.style.height = (newH * CELL_SIZE) + 'px';

            const coordsElement = draggedPanel.querySelector('.panel-coords');
            if (coordsElement) {
                coordsElement.textContent = 'x:' + panel.grid.x + ' y:' + panel.grid.y + ' w:' + panel.grid.w + ' h:' + panel.grid.h;
            }
            updateGridHeight();
        } else {
            const deltaX = e.clientX - dragStartX;
            const deltaY = e.clientY - dragStartY;

            let newX = dragStartGridX + Math.round(deltaX / CELL_SIZE);
            let newY = dragStartGridY + Math.round(deltaY / CELL_SIZE);

            // Clamp to grid bounds
            newX = Math.max(0, Math.min(newX, GRID_COLUMNS - panel.grid.w));
            newY = Math.max(0, newY);

            panel.grid.x = newX;
            panel.grid.y = newY;

            draggedPanel.style.left = (newX * CELL_SIZE) + 'px';
            draggedPanel.style.top = (newY * CELL_SIZE) + 'px';

            const coordsElement = draggedPanel.querySelector('.panel-coords');
            if (coordsElement) {
                coordsElement.textContent = 'x:' + panel.grid.x + ' y:' + panel.grid.y + ' w:' + panel.grid.w + ' h:' + panel.grid.h;
            }
            updateGridHeight();
        }
    }

    /**
     * Handle mouse up (end drag/resize and save changes)
     */
    function handleMouseUp() {
        if (!draggedPanel) return;

        const index = parseInt(draggedPanel.dataset.index, 10);
        if (isNaN(index) || !panels[index]) {
            draggedPanel.classList.remove('dragging', 'resizing');
            draggedPanel = null;
            isResizing = false;
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            return;
        }
        const panel = panels[index];

        // Send update to VS Code extension
        if (vscode) {
            vscode.postMessage({
                command: 'updateGrid',
                panelId: panel.id,
                grid: panel.grid
            });
        }

        // Show stale warning if configured (full preview mode)
        if (showStaleWarning) {
            const staleWarningEl = document.getElementById('staleWarning');
            if (staleWarningEl) {
                staleWarningEl.classList.add('show');
            }
        }

        draggedPanel.classList.remove('dragging', 'resizing');
        draggedPanel = null;
        isResizing = false;

        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    }

    // Expose handlers globally for inline event attributes
    window.handlePanelMouseDown = handlePanelMouseDown;
    window.handleResizeMouseDown = handleResizeMouseDown;

    // Initialize grid height
    if (gridElement && panels.length > 0) {
        updateGridHeight();
    }

    // Set up grid visibility toggle
    if (showGridCheckbox) {
        showGridCheckbox.addEventListener('change', function (e) {
            if (gridElement) {
                if (e.target.checked) {
                    gridElement.classList.remove('hide-grid');
                } else {
                    gridElement.classList.add('hide-grid');
                }
            }
        });
    }
})();
