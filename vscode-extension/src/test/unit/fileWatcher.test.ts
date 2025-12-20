import * as assert from 'assert';
import { setupFileWatcher } from '../../fileWatcher';

suite('FileWatcher Unit Tests', () => {
    test('setupFileWatcher function exists', () => {
        assert.ok(setupFileWatcher, 'setupFileWatcher function should exist');
        assert.strictEqual(typeof setupFileWatcher, 'function', 'setupFileWatcher should be a function');
    });
});
