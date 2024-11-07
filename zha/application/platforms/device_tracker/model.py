"""Models for the device tracker platform."""

from __future__ import annotations

from zha.application.platforms.device_tracker.const import SourceType
from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import TypedBaseModel


class DeviceTrackerState(TypedBaseModel):
    """Device tracker state model."""

    connected: bool
    battery_level: float | None = None
    source_type: SourceType
    available: bool


class DeviceTrackerEntityInfo(BasePlatformEntityInfo):
    """Device tracker entity model."""

    state: DeviceTrackerState
