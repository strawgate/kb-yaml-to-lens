# Code Style: VS Code Extension

This document describes TypeScript code style conventions that are **atypical** but **mandatory** in this project.

## TypeScript Strict Mode

This project uses strict TypeScript configuration. All code must pass strict type checking.

### Avoid `any`

Never use `any` type. Use:

- `unknown` for truly unknown types (then narrow with type guards)
- Specific types or generics where possible
- Type assertions only when absolutely necessary (document why)

```typescript
// Correct
function processData(data: unknown): string {
    if (typeof data === 'string') {
        return data.toUpperCase();
    }
    throw new Error('Expected string');
}

// Incorrect - do not use
function processData(data: any): string {
    return data.toUpperCase();  // No type safety
}
```

## Async/Await Error Handling

Handle errors explicitly with try/catch. Don't let promises fail silently.

```typescript
// Correct
async function compile(): Promise<Result> {
    try {
        const result = await runCompiler();
        return result;
    } catch (error) {
        logger.error('Compilation failed', error);
        throw error;
    }
}

// Incorrect - silent failure
async function compile(): Promise<Result | undefined> {
    const result = await runCompiler().catch(() => undefined);
    return result;
}
```

## Configuration

| Setting | Value | Enforced By |
| ------- | ----- | ----------- |
| TypeScript strict | `true` | tsconfig.json |
| ESLint | Enabled | CI |
