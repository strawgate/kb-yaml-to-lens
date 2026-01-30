import { expect } from 'chai';
import { escapeHtml, getLoadingContent, getErrorContent } from '../../webviewUtils';

suite('Webview Utils Test Suite', () => {
	suite('escapeHtml', () => {
		test('escapes HTML special characters', () => {
			expect(escapeHtml('<div class="test">')).to.equal('&lt;div class=&quot;test&quot;&gt;');
			expect(escapeHtml("Tom & Jerry's")).to.equal('Tom &amp; Jerry&#039;s');
		});

		test('leaves normal text unchanged', () => {
			expect(escapeHtml('Hello World')).to.equal('Hello World');
		});

		test('handles empty string', () => {
			expect(escapeHtml('')).to.equal('');
		});

		test('handles string with only special characters', () => {
			expect(escapeHtml('<>&"\'')).to.equal('&lt;&gt;&amp;&quot;&#039;');
		});

		test('handles repeated special characters', () => {
			expect(escapeHtml('<<<>>>')).to.equal('&lt;&lt;&lt;&gt;&gt;&gt;');
		});
	});

	suite('getLoadingContent', () => {
		test('generates valid HTML with DOCTYPE', () => {
			const html = getLoadingContent();
			expect(html).to.include('<!DOCTYPE html>');
		});

		test('includes default loading message', () => {
			const html = getLoadingContent();
			expect(html).to.include('Loading...');
		});

		test('uses custom loading message when provided', () => {
			const html = getLoadingContent('Compiling dashboard...');
			expect(html).to.include('Compiling dashboard...');
		});

		test('escapes HTML in custom message to prevent XSS', () => {
			const html = getLoadingContent('<script>alert("xss")</script>');
			expect(html).to.not.include('<script>alert');
			expect(html).to.match(/<h2>&lt;script&gt;alert\(&quot;xss&quot;\)&lt;\/script&gt;<\/h2>/);
		});

		test('includes CSS styling', () => {
			const html = getLoadingContent();
			expect(html).to.include('<style>');
			expect(html).to.match(/<div class="loading">/);
			expect(html).to.match(/<style>[\s\S]*\.loading\s*\{/);
		});
	});

	suite('getErrorContent', () => {
		test('generates valid HTML with DOCTYPE', () => {
			const html = getErrorContent(new Error('Test error'));
			expect(html).to.include('<!DOCTYPE html>');
		});

		test('displays error message from Error object', () => {
			const html = getErrorContent(new Error('Something went wrong'));
			expect(html).to.match(/<pre>Something went wrong<\/pre>/);
		});

		test('displays error from string', () => {
			const html = getErrorContent('String error message');
			expect(html).to.match(/<pre>String error message<\/pre>/);
		});

		test('uses default title when not provided', () => {
			const html = getErrorContent(new Error('Test'));
			expect(html).to.match(/<h2>Error<\/h2>/);
		});

		test('uses custom title when provided', () => {
			const html = getErrorContent(new Error('Test'), 'Compilation Failed');
			expect(html).to.match(/<h2>Compilation Failed<\/h2>/);
		});

		test('escapes HTML in error message to prevent XSS', () => {
			const html = getErrorContent(new Error('<script>alert("xss")</script>'));
			expect(html).to.not.include('<script>alert');
			expect(html).to.match(/<pre>&lt;script&gt;alert\(&quot;xss&quot;\)&lt;\/script&gt;<\/pre>/);
		});

		test('escapes HTML in custom title to prevent XSS', () => {
			const html = getErrorContent(new Error('Test'), '<img src=x onerror=alert(1)>');
			expect(html).to.not.include('<img src=x');
			expect(html).to.match(/<h2>&lt;img src=x onerror=alert\(1\)&gt;<\/h2>/);
		});

		test('includes error styling', () => {
			const html = getErrorContent(new Error('Test'));
			expect(html).to.include('<style>');
			expect(html).to.match(/<style>[\s\S]*pre\s*\{/);
		});
	});
});
