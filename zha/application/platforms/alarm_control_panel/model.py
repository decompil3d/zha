"""Models for the alarm control panel platform."""

from __future__ import annotations

from zha.application.platforms.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
    CodeFormat,
)
from zha.application.platforms.model import BasePlatformEntityInfo, EntityState


class AlarmControlPanelEntityInfo(BasePlatformEntityInfo):
    """Alarm control panel model."""

    code_format: CodeFormat
    supported_features: AlarmControlPanelEntityFeature
    code_arm_required: bool
    max_invalid_tries: int
    state: EntityState
