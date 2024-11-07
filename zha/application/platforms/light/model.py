"""Models for the light platform."""

from __future__ import annotations

from zha.application.platforms.light.const import ColorMode, LightEntityFeature
from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import TypedBaseModel


class LightState(TypedBaseModel):
    """Light state model."""

    on: bool
    brightness: int | None = None
    xy_color: tuple[float, float] | None = None
    color_temp: int | None = None
    effect: str
    off_brightness: int | None = None
    color_mode: ColorMode | None = None
    off_with_transition: bool = False
    available: bool


class LightEntityInfo(BasePlatformEntityInfo):
    """Light model."""

    supported_features: LightEntityFeature
    min_mireds: int
    max_mireds: int
    effect_list: list[str] | None = None
    supported_color_modes: set[ColorMode]
    state: LightState
