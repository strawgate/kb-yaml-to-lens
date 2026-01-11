#!/usr/bin/env node
/**
 * Formula API Mock
 *
 * Creates a FormulaPublicApi instance using Kibana's actual formula parser.
 * This is needed for generating fixtures with formulas (index-based datasets),
 * as the formula parser generates helper columns (X0, X1, etc.) and tinymathAST.
 *
 * ES|QL datasets don't need this since they don't use formula parsing.
 */

// Set up browser environment BEFORE importing any Kibana code
require('./browser-env.js');

/**
 * Creates a FormulaPublicApi using Kibana's actual implementation
 *
 * This imports createFormulaPublicApi from the lens plugin and returns
 * a real formula parser that can parse formulas and generate helper columns.
 *
 * @returns {import('@kbn/lens-plugin/public').FormulaPublicApi}
 */
export function createFormulaApiMock() {
  try {
    // Try to import the actual Kibana formula API
    const {
      createFormulaPublicApi,
    } = require('/kibana/x-pack/platform/plugins/shared/lens/public/datasources/form_based/operations/definitions/formula/formula_public_api');
    return createFormulaPublicApi();
  } catch (error) {
    console.warn('Warning: Could not load Kibana FormulaPublicApi:', error.message);
    console.warn('Formulas with index-based datasets will not work correctly.');
    return undefined;
  }
}
