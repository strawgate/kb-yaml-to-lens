import assert from 'assert';
import { escapeHtml } from '../../webviewUtils';

suite('Webview Utils Test Suite', () => {
	test('escapeHtml escapes special characters', () => {
		assert.strictEqual(escapeHtml('<div class="test">'), '&lt;div class=&quot;test&quot;&gt;');
		assert.strictEqual(escapeHtml("Tom & Jerry's"), 'Tom &amp; Jerry&#039;s');
	});

	test('escapeHtml leaves normal text alone', () => {
		assert.strictEqual(escapeHtml('Hello World'), 'Hello World');
	});
});
