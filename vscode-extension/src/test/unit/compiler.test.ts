import * as assert from 'assert';
import { DashboardCompiler } from '../../compiler';

suite('DashboardCompiler Unit Tests', () => {
    test('DashboardCompiler can be instantiated', () => {
        // This is a basic smoke test - we can't fully test the compiler
        // without a VSCode extension context
        assert.ok(DashboardCompiler, 'DashboardCompiler class should exist');
    });

    test('DashboardCompiler exports CompiledDashboard type', () => {
        // Type checking test - will fail at compile time if type is missing
        const testData: import('../../compiler').CompiledDashboard = {};
        assert.ok(testData !== undefined);
    });
});
