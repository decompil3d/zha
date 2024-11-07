"""Models for the number platform."""

from __future__ import annotations

from zha.application.platforms.model import BasePlatformEntityInfo, EntityState
from zha.application.platforms.number.const import NumberMode


class NumberEntityInfo(BasePlatformEntityInfo):
    """Number entity model."""

    engineering_units: int | None = (
        None  # TODO: how should we represent this when it is None?
    )
    application_type: int | None = (
        None  # TODO: how should we represent this when it is None?
    )
    step: float | None = None  # TODO: how should we represent this when it is None?
    min_value: float
    max_value: float
    mode: NumberMode = NumberMode.AUTO
    unit: str | None = None
    description: str | None = None
    icon: str | None = None
    state: EntityState


class NumberConfigurationEntityInfo(BasePlatformEntityInfo):
    """Number configuration entity info."""

    step: float | None
    min_value: float | None
    max_value: float | None
    mode: NumberMode = NumberMode.AUTO
    unit: str | None = None
    multiplier: float | None
    device_class: str | None
    description: str | None = None
    icon: str | None = None
    state: EntityState
