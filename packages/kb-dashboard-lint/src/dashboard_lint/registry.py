"""Rule registry for managing and discovering lint rules."""

from dashboard_lint.types import Rule


class RuleRegistry:
    """Registry for lint rules.

    The registry stores rules by their unique ID and provides methods
    for registration and retrieval. Rules self-register when their
    modules are imported.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._rules: dict[str, Rule] = {}

    def register(self, rule: Rule) -> None:
        """Register a rule in the registry.

        Args:
            rule: The rule to register.

        Raises:
            ValueError: If a rule with the same ID is already registered.

        """
        if rule.id in self._rules:
            msg = f"Rule '{rule.id}' is already registered"
            raise ValueError(msg)
        self._rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> Rule | None:
        """Get a rule by its ID.

        Args:
            rule_id: The unique identifier of the rule.

        Returns:
            The rule if found, None otherwise.

        """
        return self._rules.get(rule_id)

    def get_all_rules(self) -> list[Rule]:
        """Get all registered rules.

        Returns:
            List of all registered rules, sorted by ID.

        """
        return sorted(self._rules.values(), key=lambda r: r.id)

    def get_rule_ids(self) -> list[str]:
        """Get all registered rule IDs.

        Returns:
            List of all registered rule IDs, sorted alphabetically.

        """
        return sorted(self._rules.keys())

    def __len__(self) -> int:
        """Return the number of registered rules."""
        return len(self._rules)

    def __contains__(self, rule_id: str) -> bool:
        """Check if a rule ID is registered."""
        return rule_id in self._rules


# Module-level default registry instance
default_registry = RuleRegistry()


def register_rule(rule: Rule) -> Rule:
    """Register a rule instance with the default registry.

    This function expects a Rule instance, not a class. It does not instantiate
    classes. For class decorator usage, use the specialized decorators in
    dashboard_lint/rules/core/decorators.py (e.g., @panel_rule, @chart_rule,
    @dashboard_rule) which handle instantiation before calling register_rule.

    Args:
        rule: The rule instance to register.

    Returns:
        The rule instance (unchanged).

    Example:
        # Register an existing instance
        register_rule(MyRule())

    """
    default_registry.register(rule)
    return rule
