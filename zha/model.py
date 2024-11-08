"""Shared models for ZHA."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
import logging
from typing import Annotated, Any, Literal, Optional, Union, get_args

from pydantic import (
    BaseModel as PydanticBaseModel,
    ConfigDict,
    Discriminator,
    Field,
    Tag,
    computed_field,
    field_serializer,
    field_validator,
)
from zigpy.types.named import EUI64, NWK

from zha.event import EventBase

_LOGGER = logging.getLogger(__name__)


def convert_ieee(ieee: Optional[Union[str, EUI64]]) -> Optional[EUI64]:
    """Convert ieee to EUI64."""
    if ieee is None:
        return None
    if isinstance(ieee, str):
        return EUI64.convert(ieee)
    return ieee


def convert_nwk(nwk: Optional[Union[int, str, NWK]]) -> Optional[NWK]:
    """Convert int to NWK."""
    if isinstance(nwk, int) and not isinstance(nwk, NWK):
        return NWK(nwk)
    if isinstance(nwk, str):
        return NWK(int(nwk, base=16))
    return nwk


def convert_enum(enum_type: Enum) -> Callable[[str | Enum], Enum]:
    """Convert enum name to enum instance."""

    def _convert_enum(enum_name_or_instance: str | Enum) -> Enum:
        """Convert extended_pan_id to ExtendedPanId."""
        if isinstance(enum_name_or_instance, str):
            return enum_type[enum_name_or_instance]  # type: ignore
        return enum_name_or_instance

    return _convert_enum


def convert_int(zigpy_type: type) -> Any:
    """Convert int to zigpy type."""

    def _convert_int(value: int) -> Any:
        """Convert int to zigpy type."""
        return zigpy_type(value)

    return _convert_int


class BaseModel(PydanticBaseModel):
    """Base model for ZHA models."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    _convert_ieee = field_validator(
        "ieee", "device_ieee", mode="before", check_fields=False
    )(convert_ieee)

    _convert_nwk = field_validator(
        "nwk", "dest_nwk", "next_hop", mode="before", check_fields=False
    )(convert_nwk)

    @field_serializer("ieee", "device_ieee", check_fields=False)
    def serialize_ieee(self, ieee: EUI64):
        """Customize how ieee is serialized."""
        if ieee is not None:
            return str(ieee)
        return ieee

    @field_serializer(
        "nwk", "dest_nwk", "next_hop", when_used="json", check_fields=False
    )
    def serialize_nwk(self, nwk: NWK):
        """Serialize nwk as hex string."""
        if nwk is not None:
            return repr(nwk)
        return nwk


class TypedBaseModel(BaseModel):
    """Typed base model for use in discriminated unions."""

    @computed_field  # type: ignore
    @property
    def model_class_name(self) -> str:
        """Property to create type field from class name when serializing."""
        return self.__class__.__name__

    @classmethod
    def _tag(cls):
        """Create a pydantic `Tag` for this class to include it in tagged unions."""
        return Annotated[cls, Tag(cls.__name__)]

    @staticmethod
    def _discriminator():
        """Create a pydantic `Discriminator` for a tagged union of `TypedBaseModel`."""
        return Field(discriminator=Discriminator(TypedBaseModel._get_model_class_name))

    @staticmethod
    def _get_model_class_name(x: Any) -> str | None:
        """Get the model_class_name from an instance or serialized `dict` of `TypedBaseModel`.

        This is a callable for pydantic Discriminator to discriminate between types in a
        tagged union of `TypedBaseModel` child classes.

        If given an instance of `TypedBaseModel` then this method is being called to
        serialize an instance. The model_class_name field of the entry for this instance should be
        its class name.

        If given a dictionary, then an instance is being deserialized. The name of the
        class to be instantiated is given by the model_class_name field, and the remaining fields
        should be passed as fields to the class.

        In any other case, return `None` to cause a pydantic validation error.

        Args:
            x: `TypedBaseModel` instance or serialized `dict` of a `TypedBaseModel`

        """
        match x:
            case TypedBaseModel():
                return x.__class__.__name__
            case dict() as serialized:
                return serialized.pop("model_class_name", None)
            case _:
                return None


def as_tagged_union(union):
    """Create a tagged union from a `Union` of `TypedBaseModel`.

    Members will be tagged with their class name to be discriminated by pydantic.

    Args:
        union: `Union` of `TypedBaseModel` to convert to a tagged union

    """
    union_members = get_args(union)

    return Annotated[
        Union[tuple(cls._tag() for cls in union_members)],
        TypedBaseModel._discriminator(),
    ]


class BaseEvent(TypedBaseModel):
    """Base model for ZHA events."""

    message_type: Literal["event"] = "event"
    event_type: str
    event: str


class BaseEventedModel(EventBase, BaseModel):
    """Base evented model."""
