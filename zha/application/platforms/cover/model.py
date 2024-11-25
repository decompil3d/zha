"""Models for the device tracker platform."""

from __future__ import annotations

from typing import Literal

from zha.application.platforms.cover.const import CoverEntityFeature
from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import BaseModel


class CoverState(BaseModel):
    """Cover state model."""

    class_name: Literal["Cover"] = "Cover"
    current_position: int | None = None
    current_tilt_position: int | None = None
    target_lift_position: int | None = None
    target_tilt_position: int | None = None
    state: str | None = None
    is_opening: bool
    is_closing: bool
    is_closed: bool | None = None
    available: bool


class ShadeState(BaseModel):
    """Cover state model."""

    class_name: Literal["Shade", "KeenVent"]
    current_position: int | None = (
        None  # TODO: how should we represent this when it is None?
    )
    is_closed: bool | None = None
    state: str | None = None
    available: bool


class CoverEntityInfo(BasePlatformEntityInfo):
    """Cover entity model."""

    class_name: Literal["Cover"]
    supported_features: CoverEntityFeature
    state: CoverState


class ShadeEntityInfo(BasePlatformEntityInfo):
    """Shade entity model."""

    class_name: Literal["Shade", "KeenVent"]
    supported_features: CoverEntityFeature
    state: ShadeState
