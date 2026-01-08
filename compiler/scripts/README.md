# Compiler Scripts

Utility scripts for the dashboard compiler.

## validate_snippets.py

Validates ES|QL snippets from the VS Code extension against the Pydantic schema models.

### Purpose

This script ensures that the snippets provided in `vscode-extension/snippets/dashboards.json`
are valid according to the compiler's Pydantic schemas. This catches issues early before
users encounter them when using the snippets.

### Usage

```bash
cd compiler
uv run python scripts/validate_snippets.py
```

### What It Does

1. Reads the snippets JSON file from the VS Code extension
2. Extracts all ES|QL-related snippets (panels and controls)
3. Converts each snippet body to a YAML dashboard structure
4. Validates using the Dashboard Pydantic models
5. Reports validation errors with specific details
6. Provides a detailed analysis of common issues

### Validated Snippets

**Panel Snippets:**
- ESQL Metric Panel (`panel-esql-metric`)
- ESQL Line Chart (`panel-esql-line`)
- ESQL Bar Chart (`panel-esql-bar`)
- ESQL Datatable (`panel-esql-datatable`)
- ESQL Tagcloud Panel (`panel-esql-tagcloud`)
- ESQL Heatmap Panel (`panel-esql-heatmap`)
- ESQL XY Chart with Appearance (`panel-esql-xy-advanced`)

**Control Snippets:**
- Control - ESQL Static Values (`control-esql-static`)
- Control - ESQL Query (`control-esql-query`)

### Output

The script outputs:
- Per-snippet validation results
- YAML preview for failing snippets
- Summary statistics
- Detailed issue analysis grouped by type

Exit codes:
- `0`: All snippets valid
- `1`: Some snippets have validation errors

### Example Output

```
================================================================================
ES|QL Snippet Validation Report
================================================================================

Validating Panel Snippets:
--------------------------------------------------------------------------------

✗ ESQL Metric Panel:
  Validation error:
  • dashboards -> 0 -> panels -> 0 -> esql -> esql -> metric -> query: Input should be a valid string
    Input: {'esql': 'FROM logs-*\n| STATS count()\n...'}
  • dashboards -> 0 -> panels -> 0 -> esql -> esql -> metric -> primary: Field required

  Panel YAML (first 15 lines):
     1: - title: ESQL Metric
     2:   description: Metric calculated using ESQL query
     ...

✓ ESQL Tagcloud Panel:
  ✓ Valid

...

================================================================================
Summary:
================================================================================
Panels: 2/7 valid
Controls: 2/2 valid

✗ Some ES|QL snippets have validation errors.

================================================================================
Detailed Issue Analysis:
================================================================================

Issue #1: INCORRECT QUERY STRUCTURE
--------------------------------------------------------------------------------
Affected snippets:
  - ESQL Metric Panel
  ...
```

### Common Issues Detected

1. **Incorrect Query Structure**: Snippets using nested `query: { esql: | ... }` instead of flat `query: |`
2. **Missing Required Fields**: Chart types missing required configuration (e.g., `primary`, `metrics`)
3. **Extra/Invalid Fields**: Fields that are not permitted in the configuration

### When to Run

- Before committing changes to snippet files
- When updating Pydantic schemas that affect ES|QL panels
- As part of CI/CD validation (future enhancement)
