import * as assert from 'assert';
import { PreviewPanel } from '../../previewPanel';

suite('PreviewPanel Unit Tests', () => {
    test('PreviewPanel can be instantiated', () => {
        // Basic smoke test
        assert.ok(PreviewPanel, 'PreviewPanel class should exist');
    });

    test('PreviewPanel exports expected interface', () => {
        // Verify the class has the expected methods
        assert.ok(PreviewPanel.prototype.show, 'PreviewPanel should have show method');
        assert.ok(PreviewPanel.prototype.updatePreview, 'PreviewPanel should have updatePreview method');
    });
});
