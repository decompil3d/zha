"""Models for the select platform."""

from __future__ import annotations

from zha.application.platforms.model import BasePlatformEntityInfo, EntityState


class SelectEntityInfo(BasePlatformEntityInfo):
    """Select entity model."""

    enum: str
    options: list[str]
    state: EntityState


class EnumSelectEntityInfo(BasePlatformEntityInfo):
    """Enum select entity info."""

    enum: str
    options: list[str]
    state: EntityState
