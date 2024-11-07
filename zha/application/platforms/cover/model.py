"""Models for the device tracker platform."""

from __future__ import annotations

from zha.application.platforms.cover.const import CoverEntityFeature
from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import TypedBaseModel


class CoverState(TypedBaseModel):
    """Cover state model."""

    current_position: int | None = None
    current_tilt_position: int | None = None
    target_lift_position: int | None = None
    target_tilt_position: int | None = None
    state: str | None = None
    is_opening: bool
    is_closing: bool
    is_closed: bool | None = None
    available: bool


class ShadeState(TypedBaseModel):
    """Cover state model."""

    current_position: int | None = (
        None  # TODO: how should we represent this when it is None?
    )
    is_closed: bool | None = None
    state: str | None = None
    available: bool


class CoverEntityInfo(BasePlatformEntityInfo):
    """Cover entity model."""

    supported_features: CoverEntityFeature
    state: CoverState


class ShadeEntityInfo(BasePlatformEntityInfo):
    """Shade entity model."""

    supported_features: CoverEntityFeature
    state: ShadeState
