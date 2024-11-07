"""Models for the siren platform."""

from __future__ import annotations

from zha.application.platforms.model import BasePlatformEntityInfo, EntityState
from zha.application.platforms.siren.const import SirenEntityFeature


class SirenEntityInfo(BasePlatformEntityInfo):
    """Siren entity model."""

    available_tones: dict[int, str]
    supported_features: SirenEntityFeature
    state: EntityState
