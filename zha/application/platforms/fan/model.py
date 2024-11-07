"""Models for the fan platform."""

from __future__ import annotations

from zha.application.platforms.fan.const import FanEntityFeature
from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import TypedBaseModel


class FanState(TypedBaseModel):
    """Fan state model."""

    preset_mode: str | None = (
        None  # TODO: how should we represent these when they are None?
    )
    percentage: int | None = (
        None  # TODO: how should we represent these when they are None?
    )
    is_on: bool
    speed: str | None = None
    available: bool


class FanEntityInfo(BasePlatformEntityInfo):
    """Fan model."""

    preset_modes: list[str]
    supported_features: FanEntityFeature
    default_on_percentage: int
    speed_count: int
    speed_list: list[str]
    percentage_step: float
    state: FanState
