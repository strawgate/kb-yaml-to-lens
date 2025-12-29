"""Shared view module for the dashboard compiler, defining data structures used in Kibana JSON."""

from dataclasses import dataclass
from typing import TypeVar

from pydantic import Field, RootModel, model_serializer

from dashboard_compiler.shared.model import BaseModel

T = TypeVar('T')


@dataclass
class OmitIfNone:
    pass


class BaseVwModel(BaseModel):
    """Base view model for the dashboard compiler."""

    @model_serializer
    def _serialize(self):
        model_class = self.__class__

        omit_if_none_fields: set[str] = {
            k
            for k, v in model_class.model_fields.items()
            if any(isinstance(m, OmitIfNone) for m in v.metadata)  # pyright: ignore[reportAny]
        }

        serialization_aliases: dict[str, str] = {
            k: v.serialization_alias for k, v in model_class.model_fields.items() if v.serialization_alias is not None
        }

        return {serialization_aliases.get(k, k): v for k, v in self if k not in omit_if_none_fields or v is not None}  # pyright: ignore[reportAny]


class KbnReference(BaseVwModel):
    """Represents a reference object in the Kibana JSON structure."""

    type: str = Field()
    """The type of the referenced object, e.g., 'index-pattern', 'visualization', 'dashboard'."""
    id: str = Field()
    """The unique or friendly identifier of the referenced object, e.x. `metrics-*` or id of the dashboard."""
    name: str = Field()
    """A sometimes namespaced identifier for the reference."""


class RootDict(RootModel[dict[str, T]]):
    """A root model that contains a dictionary with string keys and values of type T."""

    root: dict[str, T] = Field(
        default_factory=dict,
        description='A dictionary mapping string keys to values of type T.',
    )

    def add(self, key: str, value: T) -> None:
        """Add an item to the root dictionary."""
        self.root[key] = value
