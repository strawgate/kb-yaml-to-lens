"""Configuration system for dashboard linting."""

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from dashboard_lint.registry import default_registry
from dashboard_lint.types import Severity

logger = logging.getLogger(__name__)


class RuleConfig(BaseModel):
    """Configuration for a single rule."""

    model_config: ConfigDict = ConfigDict(
        strict=True,
        extra='forbid',
        frozen=True,
        validate_default=True,
    )

    enabled: bool = Field(default=True)
    """Whether the rule is enabled."""

    severity: Severity | None = Field(default=None)
    """Override the default severity. If None, uses rule's default."""

    options: dict[str, Any] = Field(default_factory=dict)
    """Rule-specific options."""


class LintConfig(BaseModel):
    """Configuration for the linting system."""

    model_config: ConfigDict = ConfigDict(
        strict=True,
        extra='forbid',
        frozen=True,
        validate_default=True,
    )

    extends: str | None = Field(default=None)
    """Base configuration preset to extend ('default', 'strict', 'minimal')."""

    rules: dict[str, RuleConfig] = Field(default_factory=dict)
    """Per-rule configuration overrides."""


# Built-in presets
PRESETS: dict[str, dict[str, RuleConfig]] = {
    'default': {},  # All rules at their default severity
    'strict': {
        # Elevate all rules to warning or higher
        'markdown-header-height': RuleConfig(severity=Severity.ERROR),
        'metric-redundant-label': RuleConfig(severity=Severity.ERROR),
        'dashboard-dataset-filter': RuleConfig(severity=Severity.ERROR),
        'esql-where-clause': RuleConfig(severity=Severity.WARNING),
        'dimension-missing-label': RuleConfig(severity=Severity.WARNING),
    },
    'minimal': {
        # Only error-level rules
        'markdown-header-height': RuleConfig(severity=Severity.OFF),
        'metric-redundant-label': RuleConfig(severity=Severity.OFF),
        'dashboard-dataset-filter': RuleConfig(severity=Severity.OFF),
        'esql-where-clause': RuleConfig(severity=Severity.OFF),
        'dimension-missing-label': RuleConfig(severity=Severity.OFF),
    },
}


def get_effective_config(
    rule_id: str,
    config: LintConfig,
    default_severity: Severity,
) -> tuple[bool, Severity, dict[str, Any]]:
    """Get the effective configuration for a rule, merging preset defaults with user overrides."""
    # Start with defaults
    enabled = True
    severity = default_severity
    options: dict[str, Any] = {}

    # Apply preset if specified
    if config.extends is not None:
        if config.extends not in PRESETS:
            logger.warning('Unknown preset: %s, using defaults', config.extends)
        else:
            preset = PRESETS[config.extends]
            if rule_id in preset:
                preset_config = preset[rule_id]
                if preset_config.severity is not None:
                    severity = preset_config.severity
                if severity == Severity.OFF:
                    enabled = False
                options = dict(preset_config.options)

    # Apply user overrides
    if rule_id in config.rules:
        user_config = config.rules[rule_id]
        enabled = user_config.enabled
        if user_config.severity is not None:
            severity = user_config.severity
        if severity == Severity.OFF:
            enabled = False
        # Merge options (user overrides preset)
        options = {**options, **user_config.options}

    return enabled, severity, options


def _find_config_file(start_path: Path | None = None) -> Path | None:
    """Search for `.dashboard-lint.yaml` in the start path and parent directories."""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    while True:
        config_path = current / '.dashboard-lint.yaml'
        if config_path.is_file():
            return config_path

        parent = current.parent
        if parent == current:
            # Reached filesystem root
            break
        current = parent

    return None


def load_config(path: Path | None = None) -> LintConfig:
    """Load lint configuration from a file.

    If no path is provided, searches for `.dashboard-lint.yaml` in the
    current directory and parent directories.

    Args:
        path: Explicit path to config file. If None, searches automatically.

    Returns:
        The loaded configuration, or default configuration if no file found.

    """
    if path is None:
        path = _find_config_file()

    if path is None:
        # No config file found, return defaults
        return LintConfig()

    if not path.is_file():
        logger.warning('Config file not found: %s', path)
        return LintConfig()

    try:
        with path.open(encoding='utf-8') as f:
            data = yaml.safe_load(f)  # pyright: ignore[reportAny]

        if data is None:
            return LintConfig()

        # Validate rule IDs against registry
        if isinstance(data, dict) and 'rules' in data:
            for rule_id in data['rules']:  # pyright: ignore[reportUnknownVariableType]
                if rule_id not in default_registry:
                    logger.warning('Unknown rule ID in config: %s', rule_id)  # pyright: ignore[reportUnknownArgumentType]

        return LintConfig.model_validate(data)

    except yaml.YAMLError as e:
        logger.warning('Failed to parse config file %s: %s', path, e)
        return LintConfig()
    except ValidationError as e:
        logger.warning('Failed to validate config file %s: %s', path, e)
        return LintConfig()
    except OSError as e:
        logger.warning('Failed to load config file %s: %s', path, e)
        return LintConfig()
