"""Events for ZHA platforms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from zigpy.types.named import EUI64

from zha.application import Platform
from zha.application.platforms.climate.model import ThermostatState
from zha.application.platforms.cover.model import CoverState, ShadeState
from zha.application.platforms.device_tracker.model import DeviceTrackerState
from zha.application.platforms.fan.model import FanState
from zha.application.platforms.light.model import LightState
from zha.application.platforms.lock.model import LockState
from zha.application.platforms.model import EntityState
from zha.application.platforms.sensor.model import (
    BatteryState,
    DeviceCounterSensorState,
    ElectricalMeasurementState,
    SmartEnergyMeteringState,
    TimestampState,
)
from zha.application.platforms.switch.model import SwitchState
from zha.application.platforms.update.model import FirmwareUpdateState
from zha.model import BaseEvent, as_tagged_union

EntityStateUnion = (
    DeviceTrackerState
    | CoverState
    | ShadeState
    | FanState
    | LockState
    | BatteryState
    | ElectricalMeasurementState
    | LightState
    | SwitchState
    | SmartEnergyMeteringState
    | EntityState
    | ThermostatState
    | FirmwareUpdateState
    | DeviceCounterSensorState
    | TimestampState
)

if not TYPE_CHECKING:
    EntityStateUnion = as_tagged_union(EntityStateUnion)


class EntityStateChangedEvent(BaseEvent):
    """Event for when an entity state changes."""

    event_type: Literal["entity"] = "entity"
    event: Literal["state_changed"] = "state_changed"
    platform: Platform
    unique_id: str
    device_ieee: EUI64 | None = None
    endpoint_id: int | None = None
    group_id: int | None = None
    state: EntityStateUnion | None
