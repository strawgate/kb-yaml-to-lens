import assert from 'assert';
import { escapeHtml, getLoadingContent, getErrorContent } from '../../webviewUtils';

suite('Webview Utils Test Suite', () => {
	suite('escapeHtml', () => {
		test('escapes HTML special characters', () => {
			assert.strictEqual(escapeHtml('<div class="test">'), '&lt;div class=&quot;test&quot;&gt;');
			assert.strictEqual(escapeHtml("Tom & Jerry's"), 'Tom &amp; Jerry&#039;s');
		});

		test('leaves normal text unchanged', () => {
			assert.strictEqual(escapeHtml('Hello World'), 'Hello World');
		});

		test('handles empty string', () => {
			assert.strictEqual(escapeHtml(''), '');
		});

		test('handles string with only special characters', () => {
			assert.strictEqual(escapeHtml('<>&"\''), '&lt;&gt;&amp;&quot;&#039;');
		});

		test('handles repeated special characters', () => {
			assert.strictEqual(escapeHtml('<<<>>>'), '&lt;&lt;&lt;&gt;&gt;&gt;');
		});
	});

	suite('getLoadingContent', () => {
		test('generates valid HTML with DOCTYPE', () => {
			const html = getLoadingContent();
			assert.ok(html.includes('<!DOCTYPE html>'), 'Should have DOCTYPE declaration');
		});

		test('includes default loading message', () => {
			const html = getLoadingContent();
			assert.ok(html.includes('Loading...'), 'Should contain default loading message');
		});

		test('uses custom loading message when provided', () => {
			const html = getLoadingContent('Compiling dashboard...');
			assert.ok(html.includes('Compiling dashboard...'), 'Should contain custom message');
			assert.ok(!html.includes('Loading...') || html.includes('Compiling dashboard...'), 'Should use custom message');
		});

		test('escapes HTML in custom message to prevent XSS', () => {
			const html = getLoadingContent('<script>alert("xss")</script>');
			assert.ok(!html.includes('<script>alert'), 'Should not contain unescaped script tag');
			assert.ok(html.includes('&lt;script&gt;'), 'Should contain escaped script tag');
		});

		test('includes CSS styling', () => {
			const html = getLoadingContent();
			assert.ok(html.includes('<style>'), 'Should contain style tag');
			assert.ok(html.includes('loading'), 'Should have loading class styling');
		});
	});

	suite('getErrorContent', () => {
		test('generates valid HTML with DOCTYPE', () => {
			const html = getErrorContent(new Error('Test error'));
			assert.ok(html.includes('<!DOCTYPE html>'), 'Should have DOCTYPE declaration');
		});

		test('displays error message from Error object', () => {
			const html = getErrorContent(new Error('Something went wrong'));
			assert.ok(html.includes('Something went wrong'), 'Should contain error message');
		});

		test('displays error from string', () => {
			const html = getErrorContent('String error message');
			assert.ok(html.includes('String error message'), 'Should contain string error');
		});

		test('uses default title when not provided', () => {
			const html = getErrorContent(new Error('Test'));
			assert.ok(html.includes('Error'), 'Should contain default Error title');
		});

		test('uses custom title when provided', () => {
			const html = getErrorContent(new Error('Test'), 'Compilation Failed');
			assert.ok(html.includes('Compilation Failed'), 'Should contain custom title');
		});

		test('escapes HTML in error message to prevent XSS', () => {
			const html = getErrorContent(new Error('<script>alert("xss")</script>'));
			assert.ok(!html.includes('<script>alert'), 'Should not contain unescaped script tag');
			assert.ok(html.includes('&lt;script&gt;'), 'Should contain escaped script tag');
		});

		test('escapes HTML in custom title to prevent XSS', () => {
			const html = getErrorContent(new Error('Test'), '<img src=x onerror=alert(1)>');
			assert.ok(!html.includes('<img src=x'), 'Should not contain unescaped img tag');
			assert.ok(html.includes('&lt;img'), 'Should contain escaped img tag');
		});

		test('includes error styling', () => {
			const html = getErrorContent(new Error('Test'));
			assert.ok(html.includes('<style>'), 'Should contain style tag');
			assert.ok(html.includes('pre'), 'Should style pre element for error display');
		});
	});
});
