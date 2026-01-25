# Testing and Library Research

This document provides research findings and recommendations for improving the VS Code extension's test infrastructure and reducing custom implementations via well-tested libraries.

## Current State

### Testing Infrastructure

| Component | Current | Status |
| --------- | ------- | ------ |
| Test Framework | Mocha 11.7.5 (TDD style) | ✅ Well-suited for VS Code |
| Assertion Library | Node.js `assert` | ⚠️ Basic, consider upgrading |
| Mocking Library | Manual (Map + casting) | ⚠️ Fragile, consider upgrading |
| VS Code Testing | @vscode/test-electron | ✅ Official, required |
| Coverage | 31 tests, ~10% of code | ❌ Needs improvement |

### Implementation Patterns

The extension contains ~3,760 lines across 10 modules with several areas of custom implementation:

- **Subprocess handling**: Custom Promise wrappers around `child_process.spawn()` (~80 lines duplicated)
- **Platform detection**: Manual if/else chains for OS/arch detection (~50 lines)
- **HTML generation**: Template string concatenation with manual escaping (~200 lines)
- **YAML AST traversal**: Custom recursive tree walking (~100 lines)
- **Error handling**: Repeated `error instanceof Error ? error.message : String(error)` pattern (20+ occurrences)

## Evaluation of CodeRabbit's Recommendations

### 1. Sinon.js for Mocking

**Recommendation**: ✅ **Adopt**

**Rationale**:

- Current manual mocking with `as unknown as Type` casting is error-prone
- Sinon provides spies, stubs, and mocks designed for testing
- Industry standard when paired with Mocha
- Good TypeScript support via `@types/sinon`

**Example improvement**:

```typescript
// Current: Manual mock with type casting
const secretsStore = new Map<string, string>();
const mockContext = {
    secrets: {
        store: async (key: string, value: string) => secretsStore.set(key, value),
        get: async (key: string) => secretsStore.get(key),
    }
} as unknown as vscode.ExtensionContext;

// With Sinon: Type-safe stubs
import sinon from 'sinon';
const secretsStub = {
    store: sinon.stub().resolves(),
    get: sinon.stub().resolves('test-value'),
};
// Plus: sinon.assert.calledWith(secretsStub.store, 'key', 'value')
```

### 2. Chai for Assertions

**Recommendation**: ⚠️ **Optional**

**Rationale**:

- Chai provides more expressive assertions (`expect(x).to.equal(y)`)
- However, Node.js `assert` is sufficient for most cases
- Adding Chai increases bundle size and dependencies
- sinon-chai integration is useful if using Sinon

**Alternative**: Consider `@sinonjs/referee` if using Sinon heavily, or stick with `assert` module for simplicity.

### 3. sinon-chai Integration

**Recommendation**: ⚠️ **Adopt if using Chai**

**Rationale**:

- Only valuable if both Sinon and Chai are adopted
- Provides `expect(spy).to.have.been.calledWith(args)` syntax
- Not essential if using Sinon's built-in assertions

## Additional Testing Library Recommendations

### 1. proxyquire or esmock (Module Mocking)

**Recommendation**: ✅ **Consider for LSP client testing**

**Rationale**:

- compiler.ts imports `vscode-languageclient` which is hard to mock
- proxyquire allows replacing module dependencies at test time
- Enables testing without actual LSP server

```typescript
import proxyquire from 'proxyquire';

const MockLanguageClient = class {
    sendRequest = sinon.stub();
    start = sinon.stub().resolves();
};

const { DashboardCompilerLSP } = proxyquire('../compiler', {
    'vscode-languageclient/node': { LanguageClient: MockLanguageClient }
});
```

### 2. Vitest (Alternative Framework)

**Recommendation**: ❌ **Not recommended for this project**

**Rationale**:

- VS Code's official testing tools (`@vscode/test-electron`, `@vscode/test-cli`) are built around Mocha
- Vitest would require significant migration effort
- Benefits (faster execution) don't outweigh integration costs for VS Code extensions

## Implementation Library Recommendations

### High Priority

#### 1. execa - Subprocess Management

**Recommendation**: ✅ **Strongly recommended**

**Current problem**: Custom Promise wrapper around `child_process.spawn()` duplicated in `previewPanel.ts` (lines 155-229) and `gridEditorPanel.ts` (lines 109-184).

**Benefits**:

- Promise-based API with proper timeout support
- Better error handling and stream management
- Cross-platform compatibility
- ~80-100 lines of custom code eliminated

**Example**:

```typescript
// Current (80+ lines across files)
const child = spawn(resolved.executable, fullArgs, { cwd: resolved.cwd });
let stdout = '';
let stderr = '';
let settled = false;
const timeoutHandle = setTimeout(() => { child.kill(); settled = true; reject(new Error('timeout')); }, 30000);
child.on('error', (err) => { if (!settled) { settled = true; clearTimeout(timeoutHandle); reject(err); } });
child.stdout.on('data', (data) => { stdout += data.toString(); });
// ... more boilerplate

// With execa (5 lines)
import { execa } from 'execa';
const { stdout, stderr } = await execa(resolved.executable, fullArgs, {
    cwd: resolved.cwd,
    timeout: 30000,
});
```

**Install**: `npm install execa`

#### 2. zod - Runtime Validation

**Recommendation**: ✅ **Recommended for LSP response validation**

**Current problem**: Heavy use of `as any` casting for LSP responses (e.g., line 262 in previewPanel.ts: `const dashboardData = dashboard as any`).

**Benefits**:

- TypeScript-first with automatic type inference
- Zero dependencies
- Validates LSP responses at runtime
- Eliminates unsafe casts

**Example**:

```typescript
// Current: Unsafe casting
const response = await this.client.sendRequest('dashboard/compile', params);
const dashboard = (response as any).dashboard;  // No validation

// With zod: Type-safe validation
import { z } from 'zod';

const CompileResponseSchema = z.object({
    success: z.boolean(),
    dashboard: z.record(z.unknown()).optional(),
    error: z.string().optional(),
});

const response = await this.client.sendRequest('dashboard/compile', params);
const parsed = CompileResponseSchema.parse(response);
// parsed.dashboard is now properly typed
```

**Install**: `npm install zod`

### Medium Priority

#### 3. DOMPurify or xss - HTML Sanitization

**Recommendation**: ⚠️ **Consider for webview security**

**Current implementation**: Custom `escapeHtml()` function in `webviewUtils.ts`.

**Rationale**:

- Current implementation handles basic XSS prevention
- DOMPurify is more comprehensive but requires DOM environment
- `xss` library works in Node.js and handles more edge cases

**Decision**: Current implementation is acceptable but could be enhanced with a tested library for complex HTML content.

#### 4. p-timeout - Promise Timeouts

**Recommendation**: ⚠️ **Consider if not adopting execa**

**Current problem**: Manual setTimeout/clearTimeout patterns for subprocess timeouts.

**Benefits**:

- Clean Promise-based timeout wrapper
- Proper cleanup on resolution
- Typed error handling

**Note**: If adopting execa, this becomes unnecessary as execa includes timeout support.

### Lower Priority / Not Recommended

#### lodash-es

**Recommendation**: ❌ **Not recommended**

**Rationale**:

- Only a few utility patterns exist (batch processing, truncation)
- Modern JavaScript has `Array.prototype.flatMap`, `Promise.all`, etc.
- Adds unnecessary bundle size for minimal benefit

#### xstate (State Management)

**Recommendation**: ❌ **Not recommended for now**

**Rationale**:

- WebView panel lifecycle is manageable with current approach
- xstate adds significant learning curve
- Would require major refactoring
- Benefits don't justify complexity

## Summary of Recommendations

### Testing Libraries

| Library | Recommendation | Priority | Impact |
| ------- | -------------- | -------- | ------ |
| sinon | ✅ Adopt | High | Better mocking, less fragile tests |
| @types/sinon | ✅ Adopt | High | TypeScript support for Sinon |
| chai | ⚠️ Optional | Low | More expressive assertions |
| proxyquire | ⚠️ Consider | Medium | Module mocking for LSP client |

### Implementation Libraries

| Library | Recommendation | Priority | Lines Saved |
| ------- | -------------- | -------- | ----------- |
| execa | ✅ Adopt | High | 80-100 |
| zod | ✅ Adopt | High | Variable (type safety) |
| xss or DOMPurify | ⚠️ Consider | Medium | ~20 |
| p-timeout | ⚠️ Conditional | Low | 20-30 |

### Install Commands

```bash
# Recommended testing additions
npm install -D sinon @types/sinon

# Recommended implementation additions
npm install execa zod

# Optional (if more expressive assertions desired)
npm install -D chai @types/chai sinon-chai @types/sinon-chai
```

## Next Steps

1. **Phase 1**: Add Sinon for mocking in existing tests
2. **Phase 2**: Add execa and refactor subprocess handling
3. **Phase 3**: Add zod for LSP response validation
4. **Phase 4**: Implement comprehensive test coverage per CodeRabbit's plan

## References

- [VS Code Extension Testing Documentation](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
- [Sinon.JS](https://sinonjs.org/)
- [execa](https://github.com/sindresorhus/execa)
- [zod](https://zod.dev/)
- [Joi vs Zod Comparison](https://betterstack.com/community/guides/scaling-nodejs/joi-vs-zod/)
- [JavaScript Testing Frameworks Comparison](https://blog.seancoughlin.me/comparing-modern-javascript-testing-frameworks-jest-mocha-and-vitest)
