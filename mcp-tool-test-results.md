# MCP Tool Access Test Results

**Test Date:** 2025-12-20
**Issue:** #26 - Identify issues with Claude and tools

## Summary

✅ **2 out of 3 MCP servers are working**
- ✅ `repository-summary` - WORKING
- ✅ `code-search` - WORKING
- ❌ `github-research` - NOT AVAILABLE

## Detailed Results

### 1. Repository Summary MCP Server ✅

**Tool Name:** `mcp__repository-summary__generate_agents_md`

**Test:** Successfully called the tool to get project summary

**Result:** Tool returned comprehensive project overview including:
- Architecture overview
- Code style & conventions
- Key directories & entry points
- Quick recipes for common commands
- Dependencies & compatibility
- Unique workflows
- API surface map
- Onboarding steps

**Conclusion:** This MCP server is properly configured and functioning correctly.

### 2. Code Search MCP Server ✅

**Tool Name:** `mcp__code-search__search_code`

**Test:** Searched for the pattern `def compile_dashboard` in the repository

**Result:** Tool successfully returned search results showing:
- `dashboard_compiler/dashboard/compile.py` - 3 matches
- `dashboard_compiler/panels/compile.py` - 2 matches
- `dashboard_compiler/panels/links/compile.py` - 1 match

**Conclusion:** This MCP server is properly configured and functioning correctly.

### 3. GitHub Research MCP Server ❌

**Tool Name:** Expected `mcp__github-research` or related tools

**Test:** Checked available tools list

**Result:** No github-research related tools are available in the current session

**Expected Tools** (based on typical github-research-mcp functionality):
- Search issues
- Search pull requests
- Get issue/PR details
- Search discussions

**Conclusion:** This MCP server did not load successfully. This is a stdio-based MCP server that uses `uvx github-research-mcp`, which may have failed to initialize.

## Tool Naming Convention Discovery

The previous analysis was partially incorrect about tool naming. The actual pattern is:

- **Server-level access:** `mcp__<server-name>` allows access to the server
- **Individual tools:** `mcp__<server-name>__<tool-name>` for specific tools

**Examples from working servers:**
- `mcp__repository-summary__generate_agents_md`
- `mcp__code-search__search_code`

The custom instructions in the workflow files reference short names like `generate_agents_md` and `search_code`, which is actually **incorrect** - the full prefixed names are required.

## Recommendations

### 1. Update Custom Instructions (High Priority)

The workflow custom instructions at:
- `.github/workflows/claude-on-mention.yml:47-49`
- `.github/workflows/claude-on-open-label.yml:50-54`

Should be updated to use the correct tool names:

**Current (Incorrect):**
```
1. Call the generate_agents_md tool to get a high-level summary...
3. Don't forget about your MCP tools to call search_code, get_files, etc...
```

**Should be:**
```
1. Call the mcp__repository-summary__generate_agents_md tool to get a high-level summary...
3. Don't forget about your MCP tools like mcp__code-search__search_code to search the repository...
```

### 2. Investigate github-research Server Failure (Medium Priority)

The github-research MCP server (stdio-based) is not loading. Possible issues:
- The `uvx github-research-mcp` command may be failing in the GitHub Actions environment
- Missing dependencies for the stdio server
- Authentication or environment variable issues
- The server may need additional setup time

**Troubleshooting steps:**
1. Add debug logging to the workflow to show MCP server initialization
2. Test `uvx github-research-mcp` independently in the workflow
3. Check if the server requires additional dependencies
4. Review Claude Code Action logs for MCP server errors

### 3. Test After Updates (Required)

After updating the custom instructions, test that:
1. The corrected tool names work properly
2. Claude can successfully use the tools when following the custom instructions
3. The github-research server loads (after fixing it)

## Conclusion

The MCP tool configuration is **partially working**. Two of three servers are functioning correctly, but:

1. **Custom instructions use incorrect tool names** - they reference short names instead of the full `mcp__<server>__<tool>` format
2. **The github-research stdio server is not loading** - requires investigation
3. **The allowed-tools configuration is correct** - the issue is with how the tools are referenced in the custom instructions

The good news is that the HTTP-based MCP servers (repository-summary and code-search) are working perfectly, demonstrating that the core MCP integration is functional.
