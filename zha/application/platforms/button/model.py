"""Models for the button platform."""

from __future__ import annotations

from typing import Any

from zha.application.platforms.model import (
    BaseEntityInfo,
    BasePlatformEntityInfo,
    EntityState,
)


class ButtonEntityInfo(
    BasePlatformEntityInfo
):  # TODO split into two models CommandButton and WriteAttributeButton
    """Button model."""

    command: str | None = None
    attribute_name: str | None = None
    attribute_value: Any | None = None
    state: EntityState


class CommandButtonEntityInfo(BaseEntityInfo):
    """Command button entity info."""

    command: str
    args: list[Any]
    kwargs: dict[str, Any]


class WriteAttributeButtonEntityInfo(BaseEntityInfo):
    """Write attribute button entity info."""

    attribute_name: str
    attribute_value: Any
