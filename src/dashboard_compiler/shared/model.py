from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from pydantic import RootModel as PydanticRootModel


class BaseRootCfgModel(PydanticRootModel[Any]):
    """Base configuration model for the dashboard compiler."""

    model_config: ConfigDict = ConfigDict(
        strict=True,
        validate_default=True,
        use_enum_values=True,
        frozen=True,
        use_attribute_docstrings=True,
        serialize_by_alias=True,
    )


class BaseModel(PydanticBaseModel):
    """Base configuration model for the dashboard compiler."""

    model_config: ConfigDict = ConfigDict(
        strict=True,
        validate_default=True,
        extra='forbid',
        use_enum_values=True,
        frozen=True,
        use_attribute_docstrings=True,
        serialize_by_alias=True,
    )
