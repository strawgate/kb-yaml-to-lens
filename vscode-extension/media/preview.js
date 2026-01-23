/**
 * Preview Panel - Full Preview Functionality
 * 
 * This script handles clipboard operations, file downloads, and collapsible sections
 * for the full dashboard preview mode.
 * 
 * Expected page elements:
 * - <script id="ndjson-data" type="application/json"> containing the NDJSON content
 * - <script id="preview-config" type="application/json"> containing { "downloadFilename": "..." }
 */

(function () {
    'use strict';

    // Read NDJSON data from the page
    let ndjsonData = '';
    const ndjsonElement = document.getElementById('ndjson-data');
    if (ndjsonElement) {
        try {
            ndjsonData = ndjsonElement.textContent || '';
        } catch (e) {
            console.error('Failed to read ndjson data:', e);
        }
    }

    // Read preview config
    let previewConfig = { downloadFilename: 'dashboard.ndjson' };
    const configElement = document.getElementById('preview-config');
    if (configElement) {
        try {
            previewConfig = { ...previewConfig, ...JSON.parse(configElement.textContent || '{}') };
        } catch (e) {
            console.error('Failed to parse preview config:', e);
        }
    }

    /**
     * Escape HTML special characters (client-side)
     */
    function escapeHtmlClient(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Toggle collapsible section visibility
     */
    function toggleCollapsible(id) {
        const content = document.getElementById(id);
        const arrow = document.getElementById(id + '-arrow');
        if (content && arrow) {
            content.classList.toggle('expanded');
            arrow.classList.toggle('expanded');
        }
    }

    /**
     * Copy NDJSON to clipboard
     */
    function copyToClipboard() {
        navigator.clipboard.writeText(ndjsonData).then(function () {
            const message = document.getElementById('successMessage');
            if (message) {
                message.classList.add('show');
                setTimeout(function () {
                    message.classList.remove('show');
                }, 3000);
            }
        }).catch(function (err) {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard: ' + err.message);
        });
    }

    /**
     * Download NDJSON as a file
     */
    function downloadNDJSON() {
        const blob = new Blob([ndjsonData], { type: 'application/x-ndjson' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = previewConfig.downloadFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Expose functions globally for inline onclick handlers
    window.escapeHtmlClient = escapeHtmlClient;
    window.toggleCollapsible = toggleCollapsible;
    window.copyToClipboard = copyToClipboard;
    window.downloadNDJSON = downloadNDJSON;
})();
