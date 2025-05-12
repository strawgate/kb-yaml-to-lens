from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from pydantic import RootModel as PydanticRootModel


class BaseRootCfgModel(PydanticRootModel):
    """Base configuration model for the dashboard compiler."""

    model_config = ConfigDict(
        strict=True,  # Do not coerce types
        validate_default=True,  # Whether to validate default values during validation.
        use_enum_values=True,  # Use enum values instead of enum instances when serializing.
        frozen=True,  # Make the model immutable after creation.
        use_attribute_docstrings=True,  # Use attribute docstrings for field descriptions.
        serialize_by_alias=True,  # Whether to serialize fields by their alias names.
    )


class BaseModel(PydanticBaseModel):
    """Base configuration model for the dashboard compiler."""

    model_config = ConfigDict(
        strict=True,  # Do not coerce types
        validate_default=True,  # Whether to validate default values during validation.
        extra='forbid',  # Forbid extra fields that are not defined in the model.
        use_enum_values=True,  # Use enum values instead of enum instances when serializing.
        frozen=True,  # Make the model immutable after creation.
        use_attribute_docstrings=True,  # Use attribute docstrings for field descriptions.
        serialize_by_alias=True,  # Whether to serialize fields by their alias names.
    )
