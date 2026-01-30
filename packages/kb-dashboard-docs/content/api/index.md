# API Reference

This section contains the complete API documentation for the Dashboard Compiler.

## Overview

The Dashboard Compiler provides a Python API for creating Kibana dashboards programmatically. For a high-level guide on programmatic usage, see the **[Programmatic Usage Guide](../programmatic-usage.md)**.

## Core Modules

- **[Dashboard](dashboard.md)** – Dashboard configuration and compilation
- **[Panels](panels.md)** – Panel types and compilation logic (includes Python examples)
- **[Controls](controls.md)** – Control group configuration
- **[Filters](filters.md)** – Filter compilation
- **[Queries](queries.md)** – Query compilation

## Core Functions

The Dashboard Compiler provides these core functions for working with dashboards:

::: kb_dashboard_core.dashboard_compiler
    options:
      show_source: true
      members:
        - load
        - render
        - dump
