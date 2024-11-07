"""Models for the binary sensor platform."""

from __future__ import annotations

from zha.application.platforms.model import BasePlatformEntityInfo, EntityState


class BinarySensorEntityInfo(BasePlatformEntityInfo):
    """Binary sensor model."""

    attribute_name: str | None = None
    state: EntityState
