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
		});

		test('escapes HTML in custom message to prevent XSS', () => {
			const html = getLoadingContent('<script>alert("xss")</script>');
			assert.ok(!html.includes('<script>alert'), 'Should not contain unescaped script tag');
			assert.match(
				html,
				/<h2>&lt;script&gt;alert\(&quot;xss&quot;\)&lt;\/script&gt;<\/h2>/,
				'Should render escaped script tag inside the heading'
			);
		});

		test('includes CSS styling', () => {
			const html = getLoadingContent();
			assert.ok(html.includes('<style>'), 'Should contain style tag');
			assert.match(html, /<div class="loading">/, 'Should render loading container');
			assert.match(html, /<style>[\s\S]*\.loading\s*\{/, 'Should include .loading CSS rule');
		});
	});

	suite('getErrorContent', () => {
		test('generates valid HTML with DOCTYPE', () => {
			const html = getErrorContent(new Error('Test error'));
			assert.ok(html.includes('<!DOCTYPE html>'), 'Should have DOCTYPE declaration');
		});

		test('displays error message from Error object', () => {
			const html = getErrorContent(new Error('Something went wrong'));
			assert.match(html, /<pre>Something went wrong<\/pre>/, 'Should contain error message in pre element');
		});

		test('displays error from string', () => {
			const html = getErrorContent('String error message');
			assert.match(html, /<pre>String error message<\/pre>/, 'Should contain string error in pre element');
		});

		test('uses default title when not provided', () => {
			const html = getErrorContent(new Error('Test'));
			assert.match(html, /<h2>Error<\/h2>/, 'Should contain default Error title in h2');
		});

		test('uses custom title when provided', () => {
			const html = getErrorContent(new Error('Test'), 'Compilation Failed');
			assert.match(html, /<h2>Compilation Failed<\/h2>/, 'Should contain custom title in h2');
		});

		test('escapes HTML in error message to prevent XSS', () => {
			const html = getErrorContent(new Error('<script>alert("xss")</script>'));
			assert.ok(!html.includes('<script>alert'), 'Should not contain unescaped script tag');
			assert.match(
				html,
				/<pre>&lt;script&gt;alert\(&quot;xss&quot;\)&lt;\/script&gt;<\/pre>/,
				'Should render escaped script tag inside the pre element'
			);
		});

		test('escapes HTML in custom title to prevent XSS', () => {
			const html = getErrorContent(new Error('Test'), '<img src=x onerror=alert(1)>');
			assert.ok(!html.includes('<img src=x'), 'Should not contain unescaped img tag');
			assert.match(
				html,
				/<h2>&lt;img src=x onerror=alert\(1\)&gt;<\/h2>/,
				'Should render escaped img tag inside the h2 element'
			);
		});

		test('includes error styling', () => {
			const html = getErrorContent(new Error('Test'));
			assert.ok(html.includes('<style>'), 'Should contain style tag');
			assert.match(html, /<style>[\s\S]*pre\s*\{/, 'Should include pre CSS rule for error display');
		});
	});
});
