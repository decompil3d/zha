"""Models for the switch platform."""

from __future__ import annotations

from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import TypedBaseModel


class SwitchState(TypedBaseModel):
    """Switch state model."""

    state: bool
    available: bool
    inverted: bool | None = None


class SwitchEntityInfo(BasePlatformEntityInfo):
    """Switch entity model."""

    state: SwitchState


class ConfigurableAttributeSwitchEntityInfo(BasePlatformEntityInfo):
    """Switch configuration entity info."""

    attribute_name: str
    invert_attribute_name: str | None = None
    force_inverted: bool
    off_value: int
    on_value: int
    state: SwitchState
