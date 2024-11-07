"""Models for the lock platform."""

from __future__ import annotations

from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import TypedBaseModel


class LockState(TypedBaseModel):
    """Lock state model."""

    is_locked: bool
    available: bool


class LockEntityInfo(BasePlatformEntityInfo):
    """Lock entity model."""

    state: LockState
