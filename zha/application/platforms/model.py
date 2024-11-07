"""Models for the ZHA platforms module."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypeVar

from zigpy.types.named import EUI64

from zha.application.discovery import Platform
from zha.event import EventBase
from zha.model import BaseModel, TypedBaseModel
from zha.zigbee.cluster_handlers.model import ClusterHandlerInfo


class BaseEntityInfo(TypedBaseModel):
    """Information about a base entity."""

    platform: Platform
    unique_id: str
    class_name: str
    translation_key: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    entity_category: str | None = None
    entity_registry_enabled_default: bool
    enabled: bool = True
    fallback_name: str | None = None
    state: dict[str, Any]

    # For platform entities
    cluster_handlers: list[ClusterHandlerInfo]
    device_ieee: EUI64 | None = None
    endpoint_id: int | None = None
    available: bool | None = None

    # For group entities
    group_id: int | None = None


T = TypeVar("T", bound=BaseEntityInfo)


class BaseIdentifiers(BaseModel):
    """Identifiers for the base entity."""

    unique_id: str
    platform: Platform


class PlatformEntityIdentifiers(BaseIdentifiers):
    """Identifiers for the platform entity."""

    device_ieee: EUI64
    endpoint_id: int


class GroupEntityIdentifiers(BaseIdentifiers):
    """Identifiers for the group entity."""

    group_id: int


class EntityState(TypedBaseModel):
    """Default state model."""

    available: bool | None = None
    state: str | bool | int | float | datetime | None = None


class BasePlatformEntityInfo(EventBase, BaseEntityInfo):
    """Base platform entity model."""
