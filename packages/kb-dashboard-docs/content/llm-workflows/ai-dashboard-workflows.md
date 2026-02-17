# AI Dashboard Iteration Workflows

This guide describes workflows for AI agents to effectively develop Kibana dashboards using kb-dashboard CLI tools combined with Playwright MCP for browser-based verification.

## Core Iteration Loop

The dashboard development workflow follows an iterative pattern:

```text
Edit YAML → Compile → Upload → Verify in Browser → Iterate
```

### Tool Separation

| Tool | Use For |
| ---- | ------- |
| **kb-dashboard CLI** | Compilation, upload, API operations (reliable, fast) |
| **Playwright MCP** | Visual verification, UI exploration (interactive) |

This separation ensures reliable compilation through CLI while enabling visual validation through the browser.

---

## Workflow 1: Dashboard Iteration

### Step 1: Edit YAML

Modify the dashboard YAML definition:

```yaml
dashboard:
  title: My Dashboard
  panels:
    - title: Request Rate
      type: xy
      esql: |
        TS metrics-*
        | STATS rate = SUM(RATE(http.requests))
          BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend)
```

### Step 2: Compile and Upload

Use the CLI to compile and upload:

```bash
# Compile to NDJSON
kb-dashboard compile --input-file dashboard.yaml --output-file dashboard.ndjson

# Upload to Kibana
kb-dashboard upload --input-file dashboard.ndjson
```

### Step 3: Verify in Browser

Using Playwright MCP, navigate to the dashboard and verify rendering:

1. Navigate to the dashboard URL
2. Wait for panels to load
3. Check for error states
4. Capture screenshot for review

### Step 4: Iterate

Based on verification results, return to Step 1 to make corrections.

---

## Workflow 2: Pattern Discovery

Explore existing dashboards to understand patterns before creating new ones.

### Navigate to Saved Objects

```text
1. Navigate to: {KIBANA_URL}/app/management/kibana/objects
2. Filter by type: "Dashboard"
3. Select a reference dashboard
```

### Inspect Dashboard Structure

Use Playwright's accessibility snapshot to understand panel layout:

1. Open target dashboard
2. Take accessibility snapshot
3. Identify panel types and configuration
4. Note layout patterns (grid positions, sizes)

### Inform YAML Authoring

Apply discovered patterns to your YAML definitions:

- Match panel sizing conventions
- Follow layout hierarchies
- Use consistent visualization types

---

## Verification Prompts

Reusable prompt patterns for common verification tasks.

### Verify Dashboard Loads

```text
Navigate to the dashboard at {DASHBOARD_URL}.
Wait for all panels to finish loading (look for loading spinners to disappear).
Check each panel for error states (red borders, error messages).
Report any panels that failed to load or show errors.
```

### Compare Dashboard Against YAML

```text
Navigate to the dashboard at {DASHBOARD_URL}.
Verify the following panels exist with correct titles:
- {PANEL_1_TITLE}
- {PANEL_2_TITLE}

For each panel, confirm:
1. The visualization type matches the YAML definition
2. Data is rendering (not "No data" state)
3. The panel title is correct
```

### Capture Dashboard Screenshot

```text
Navigate to the dashboard at {DASHBOARD_URL}.
Wait for the dashboard to fully load (all panels rendered, no loading spinners).
Set the time range to "Last 15 minutes" if data is expected.
Take a full-page screenshot for review.
```

### Explore Kibana UI

```text
Navigate to Kibana Saved Objects at {KIBANA_URL}/app/management/kibana/objects.
Filter to show only Dashboards.
List the available dashboards and their IDs.
For the dashboard named "{DASHBOARD_NAME}", open it and describe:
- Number of panels
- Panel types used
- Overall layout structure
```

---

## Troubleshooting

### Common Failure Patterns

| Symptom | Possible Cause | Diagnostic Steps |
| ------- | -------------- | ---------------- |
| Panel shows "No data" | Wrong index pattern, time range, or query | Check data view exists, verify time range, test query in Dev Tools |
| Visualization type mismatch | YAML panel type doesn't match expected output | Compare compiled JSON with source YAML |
| Time range issues | Dashboard time range excludes data | Set explicit time range, check data timestamps |
| Index pattern not found | Data view missing or misconfigured | Navigate to Data Views management, verify index exists |

### Playwright Diagnostic Workflow

For panels showing errors:

1. **Check browser console:** Open browser developer tools and look for JavaScript errors or failed network requests.

2. **Inspect panel loading state:** Take accessibility snapshot of the panel and look for error indicators in element tree.

3. **Verify data view exists:** Navigate to Stack Management → Data Views and confirm the required index pattern is configured.

### Fallback to CLI Tools

When Playwright-based diagnostics are insufficient, use CLI tools:

```bash
# Fetch existing dashboard configuration
kb-dashboard fetch --dashboard-id <id> --output-file fetched.yaml

# Disassemble for inspection
kb-dashboard disassemble --input-file dashboard.json --output-dir ./components
```

Compare fetched configuration with your source YAML to identify discrepancies.

---

## Best Practices

### Iteration Speed

- **Compile locally** before upload to catch YAML errors early
- **Use a dedicated test space** in Kibana for development
- **Set short time ranges** to reduce data loading time during verification

### Verification Completeness

- **Check all panels** after major changes
- **Verify interactivity** - test controls, filters, and drilldowns
- **Test different time ranges** to ensure queries work across periods

### Context Sharing

When working with AI agents:

- Provide the Kibana URL upfront
- Specify the target space if using Kibana spaces
- Share the dashboard ID or title for navigation
- Include expected panel names for verification

---

## Additional Resources

- [Playwright MCP Configuration](playwright-mcp.md) - Server setup and authentication
- [Dashboard Decompiling Guide](../dashboard-decompiling-guide.md) - Convert existing dashboards to YAML
- [CLI Reference](../CLI.md) - Complete CLI command documentation
- [ES|QL Language Reference](esql-language-reference.md) - Query syntax for ES|QL panels
