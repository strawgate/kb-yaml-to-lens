# Fixture Generator Known Issues

## Issue: Cannot Load @kbn Packages

**Status:** Unresolved
**Date Discovered:** 2025-12-20
**Severity:** High - blocks fixture generation

### Problem

The fixture generator cannot load Kibana packages because they are TypeScript source files, not compiled JavaScript.

**Error:**
```
Error: Cannot find module '@kbn/lens-embeddable-utils/config_builder'
```

### Root Cause

1. `yarn kbn bootstrap` creates symlinks to packages in `node_modules/@kbn/`
2. These packages contain TypeScript source files (`.ts`), not compiled JavaScript
3. Node.js cannot directly `require()` TypeScript files
4. The packages don't have proper `package.json` exports configured

### Attempted Solutions

1. **Using tsx (TypeScript executor)**
   - Installed tsx to execute TypeScript directly
   - Failed: Kibana uses `.peggy` files (PEG grammar) which tsx cannot parse
   - Error: `SyntaxError: Unexpected token ':'` in `grammar.peggy`

2. **Using ts-node**
   - Not attempted yet, but likely would face similar issues with `.peggy` files

### Possible Solutions

1. **Build Kibana packages before use**
   - Run Kibana's build process to compile TypeScript to JavaScript
   - May require significant additional build time and disk space

2. **Use Kibana's own TypeScript configuration**
   - Set up tsconfig to match Kibana's configuration
   - Use custom loaders for `.peggy` files
   - Complex setup, may be fragile

3. **Alternative: Use Kibana REST API**
   - Start Kibana server in Docker
   - Use API to create visualizations
   - Export via Kibana's export API
   - More reliable but slower and more resource-intensive

4. **Alternative: Manual fixture creation**
   - Create fixtures manually based on Kibana documentation
   - Less reliable but works for basic scenarios
   - Requires manual updates when Kibana changes

### Recommendation

For now, fixtures should be created manually or by:
1. Running a local Kibana instance
2. Creating visualizations via UI
3. Exporting via Kibana's export API
4. Copying the JSON to test scenarios

A proper solution would require fixing the Docker setup to either:
- Pre-compile Kibana packages during build
- Use Kibana's server API for fixture generation

### Impact

- Cannot automatically generate test fixtures from JavaScript/TypeScript code
- Manual fixture creation required
- Test scenarios may drift from actual Kibana output
