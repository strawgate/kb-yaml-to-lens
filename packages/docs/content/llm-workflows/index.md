# LLM-Driven Workflows

This section provides comprehensive guides for using Large Language Models (LLMs) to work with Kibana dashboards and the kb-yaml-to-lens compiler.

## Overview

LLMs can assist with dashboard creation and conversion in several ways:

- **Converting existing dashboards** from Kibana JSON to YAML format
- **Generating new dashboards** from natural language descriptions
- **Following best practices** for dashboard design and layout
- **Accessing complete documentation** via llms.txt and llms-full.txt

## Workflows

### [Dashboard Decompiling Guide](../dashboard-decompiling-guide.md)

Convert existing Kibana dashboard JSON files into YAML format. This guide provides step-by-step instructions for using the `kb-dashboard disassemble` command and converting components to YAML.

**Key topics:**

- Disassembling dashboard JSON into components
- Component-by-component conversion strategies
- Common patterns and mappings
- Validation and testing

### [Dashboard Style Guide](../dashboard-style-guide.md)

Best practices for designing effective Kibana dashboards, based on analysis of 49 production dashboards across 37 Elastic integration packages.

**Key topics:**

- Standard layout hierarchy and grid system
- Panel sizing and positioning conventions
- Visualization type selection
- Navigation and organization patterns
- Color and formatting standards

### [ES|QL Language Reference](esql-language-reference.md)

Complete ES|QL syntax reference for creating dashboards with ES|QL queries. Helps avoid common mistakes like using SQL syntax instead of ES|QL.

**Key topics:**

- ES|QL vs SQL differences and common mistakes
- Source commands (FROM, ROW, SHOW, TS)
- Processing commands (WHERE, STATS, EVAL, KEEP, etc.)
- Aggregation and time series functions
- Dashboard query patterns for different chart types

### [Creating Dashboards from OTel Receivers](otel-dashboard-guide.md)

Systematic guide for building Kibana dashboards from OpenTelemetry Collector receiver data. Based on lessons learned from extensive dashboard development and review.

**Key topics:**

- Locating and understanding receiver documentation
- Field path patterns for OTel data (metrics, attributes, resources)
- ES|QL and Lens formula patterns for counter vs gauge metrics
- Validation checklist for metric names, attributes, and queries
- Common pitfalls and how to avoid them

## LLM Resources

### llms.txt

Curated navigation file with links to key documentation sections. Perfect for LLMs to understand the project structure and available resources.

**Access:** [llms.txt](../llms.txt)

### llms-full.txt

Complete concatenation of all project documentation in navigation order. Provides comprehensive context for LLM-based dashboard creation and conversion.

**Access:** [llms-full.txt](../llms-full.txt)

**Note:** Both files are auto-generated during documentation builds via the `generate_llms_txt.py` MkDocs hook.

## Additional Resources

- [Complete Examples](../examples/index.md) - Real-world YAML dashboard examples
- [CLI Reference](../CLI.md) - Full command-line documentation including `disassemble` command
- [Panel Types Documentation](../panels/base.md) - Detailed panel configuration reference
