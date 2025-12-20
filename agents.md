# Claude Code Triage Agent

This document describes the Claude Code triage agent configured for the kb-yaml-to-lens repository.

## Overview

The kb-yaml-to-lens repository uses a custom Claude Code agent for issue triage. This agent helps investigate issues, locate related code and documentation, and provide actionable recommendations without making direct changes to the codebase.

## Agent Capabilities

### Core Functionality

The triage agent is designed to:

1. **Investigate Issues**: Analyze issue descriptions and gather relevant context
2. **Locate Related Items**: Find related issues, pull requests, and files in the repository
3. **Provide Recommendations**: Offer clear, actionable guidance based on deep code analysis
4. **Document Findings**: Create detailed reports with evidence-based conclusions

### Available MCP Tools

The agent has access to the following Model Context Protocol (MCP) tools:

- **repository-summary**: Generate high-level project summaries
- **code-search**: Search code across the repository and dependencies
- **github-research**: Search issues and pull requests for context

### Additional Capabilities

- **Code Analysis**: Read and analyze Python code, YAML configurations, and documentation
- **Makefile Operations**: Run build, lint, and test commands via `make`
- **Git Operations**: Inspect repository history and changes via git commands
- **Dependency Analysis**: Search external package code (e.g., elasticsearch-py) for API references

## Agent Limitations

The triage agent is intentionally restricted to investigation and recommendation:

- **No Branch Creation**: The agent does not create branches or pull requests
- **No Code Changes**: The agent does not modify code directly
- **Investigation Only**: Focus is on analysis and providing actionable guidance

## Response Format

The agent provides structured responses with the following sections:

### 1. Problems Encountered
Documents any issues encountered during the investigation (missing tools, permissions, etc.)

### 2. Recommendation
A single, high-quality recommendation based on findings, or explicit statement if no recommendation can be made

### 3. Findings
Detailed evidence from code analysis supporting the recommendation

### 4. Detailed Action Plan
Step-by-step implementation guide that a junior developer could follow

### 5. Related Items
Tables documenting related issues, pull requests, files, and web resources

## Usage Guidelines

### When the Agent is Most Effective

- **Bug Reports**: Investigating root causes and identifying affected code
- **Feature Requests**: Analyzing feasibility and suggesting implementation approaches
- **Questions**: Providing context-aware answers with code references
- **Architecture Decisions**: Evaluating trade-offs based on existing patterns

### Working with the Agent

1. **Be Specific**: Provide clear issue descriptions with relevant context
2. **Reference Code**: Mention specific files, functions, or error messages when applicable
3. **Ask Questions**: The agent can clarify requirements or investigate multiple approaches
4. **Review Findings**: The agent provides evidence-based recommendations, not speculation

## Agent Principles

The triage agent follows these core principles:

1. **Thoroughness**: Goes the extra mile to find relevant information
2. **Evidence-Based**: Only asserts facts traceable to code, issues, or documentation
3. **No Speculation**: Avoids guessing when information is unclear
4. **Concise Communication**: Prioritizes clarity and actionability over verbosity
5. **Accuracy First**: "I don't know" is better than a wrong answer

## Example Workflow

1. Agent receives issue notification
2. Analyzes issue description and context
3. Uses code-search to find relevant files and functions
4. Uses github-research to find related issues/PRs
5. Reads relevant code files for detailed analysis
6. Formulates evidence-based recommendation
7. Provides structured response with findings and action plan

## Project Context

kb-yaml-to-lens is a Python project that compiles Kibana dashboards from simplified YAML format to Lens JSON format. The agent has specific knowledge of:

- **Architecture**: Layered design with YAML parsing, Pydantic models, and JSON compilation
- **Key Components**: `models.py`, `compiler.py`, test suite
- **Dependencies**: PyYAML, Pydantic, Kibana/Lens specifications
- **Testing**: Make-based build system with lint and typecheck support

## Reference

For more information about the project architecture, see:
- [architecture.md](architecture.md) - System design and data flow
- [README.md](README.md) - Project overview
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
