"""Models for the ZHA application module."""

from __future__ import annotations

import collections
import dataclasses
import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from aiohttp import ClientSession
from pydantic import Field
from zigpy.types.named import EUI64, NWK

from zha.application import Platform
from zha.application.const import (
    CONF_DEFAULT_CONSIDER_UNAVAILABLE_BATTERY,
    CONF_DEFAULT_CONSIDER_UNAVAILABLE_MAINS,
)
from zha.const import ControllerEvents, DeviceEvents, EventTypes
from zha.model import BaseEvent, BaseModel
from zha.zigbee.model import DeviceInfo, ExtendedDeviceInfo, GroupInfo

if TYPE_CHECKING:
    from zha.application.gateway import Gateway


class DevicePairingStatus(Enum):
    """Status of a device."""

    PAIRED = 1
    INTERVIEW_COMPLETE = 2
    CONFIGURED = 3
    INITIALIZED = 4


class DeviceInfoWithPairingStatus(DeviceInfo):
    """Information about a device with pairing status."""

    pairing_status: DevicePairingStatus


class ExtendedDeviceInfoWithPairingStatus(ExtendedDeviceInfo):
    """Information about a device with pairing status."""

    pairing_status: DevicePairingStatus


class DeviceJoinedDeviceInfo(BaseModel):
    """Information about a device."""

    ieee: EUI64
    nwk: NWK
    pairing_status: DevicePairingStatus


class ConnectionLostEvent(BaseEvent):
    """Event to signal that the connection to the radio has been lost."""

    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.CONNECTION_LOST] = ControllerEvents.CONNECTION_LOST
    exception: Exception | None = None


class DeviceJoinedEvent(BaseEvent):
    """Event to signal that a device has joined the network."""

    device_info: DeviceJoinedDeviceInfo
    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.DEVICE_JOINED] = ControllerEvents.DEVICE_JOINED


class DeviceLeftEvent(BaseEvent):
    """Event to signal that a device has left the network."""

    ieee: EUI64
    nwk: NWK
    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.DEVICE_LEFT] = ControllerEvents.DEVICE_LEFT


class RawDeviceInitializedDeviceInfo(DeviceJoinedDeviceInfo):
    """Information about a device that has been initialized without quirks loaded."""

    model: str
    manufacturer: str
    signature: dict[str, Any]


class RawDeviceInitializedEvent(BaseEvent):
    """Event to signal that a device has been initialized without quirks loaded."""

    device_info: RawDeviceInitializedDeviceInfo
    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.RAW_DEVICE_INITIALIZED] = (
        ControllerEvents.RAW_DEVICE_INITIALIZED
    )


class DeviceFullyInitializedEvent(BaseEvent):
    """Event to signal that a device has been fully initialized."""

    device_info: ExtendedDeviceInfoWithPairingStatus
    new_join: bool = False
    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.DEVICE_FULLY_INITIALIZED] = (
        ControllerEvents.DEVICE_FULLY_INITIALIZED
    )


class GroupRemovedEvent(BaseEvent):
    """Group removed event."""

    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.GROUP_REMOVED] = ControllerEvents.GROUP_REMOVED
    group_info: GroupInfo


class GroupAddedEvent(BaseEvent):
    """Group added event."""

    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.GROUP_ADDED] = ControllerEvents.GROUP_ADDED
    group_info: GroupInfo


class GroupMemberAddedEvent(BaseEvent):
    """Group member added event."""

    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.GROUP_MEMBER_ADDED] = (
        ControllerEvents.GROUP_MEMBER_ADDED
    )
    group_info: GroupInfo


class GroupMemberRemovedEvent(BaseEvent):
    """Group member removed event."""

    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.GROUP_MEMBER_REMOVED] = (
        ControllerEvents.GROUP_MEMBER_REMOVED
    )
    group_info: GroupInfo


class DeviceRemovedEvent(BaseEvent):
    """Event to signal that a device has been removed."""

    device_info: ExtendedDeviceInfo
    event_type: Literal[EventTypes.CONTROLLER_EVENT] = EventTypes.CONTROLLER_EVENT
    event: Literal[ControllerEvents.DEVICE_REMOVED] = ControllerEvents.DEVICE_REMOVED


class DeviceOfflineEvent(BaseEvent):
    """Device offline event."""

    event: Literal[DeviceEvents.DEVICE_OFFLINE] = DeviceEvents.DEVICE_OFFLINE
    event_type: Literal[EventTypes.DEVICE_EVENT] = EventTypes.DEVICE_EVENT
    device_info: ExtendedDeviceInfo


class DeviceOnlineEvent(BaseEvent):
    """Device online event."""

    event: Literal[DeviceEvents.DEVICE_ONLINE] = DeviceEvents.DEVICE_ONLINE
    event_type: Literal[EventTypes.DEVICE_EVENT] = EventTypes.DEVICE_EVENT
    device_info: ExtendedDeviceInfo


class LightOptions(BaseModel):
    """ZHA light options."""

    default_light_transition: float = Field(default=0)
    enable_enhanced_light_transition: bool = Field(default=False)
    enable_light_transitioning_flag: bool = Field(default=True)
    always_prefer_xy_color_mode: bool = Field(default=True)
    group_members_assume_state: bool = Field(default=True)


class DeviceOptions(BaseModel):
    """ZHA device options."""

    enable_identify_on_join: bool = Field(default=True)
    consider_unavailable_mains: int = Field(
        default=CONF_DEFAULT_CONSIDER_UNAVAILABLE_MAINS
    )
    consider_unavailable_battery: int = Field(
        default=CONF_DEFAULT_CONSIDER_UNAVAILABLE_BATTERY
    )
    enable_mains_startup_polling: bool = Field(default=True)


class AlarmControlPanelOptions(BaseModel):
    """ZHA alarm control panel options."""

    master_code: str = Field(default="1234")
    failed_tries: int = Field(default=3)
    arm_requires_code: bool = Field(default=False)


class CoordinatorConfiguration(BaseModel):
    """ZHA coordinator configuration."""

    path: str
    baudrate: int = Field(default=115200)
    flow_control: str = Field(default="hardware")
    radio_type: str = Field(default="ezsp")


class QuirksConfiguration(BaseModel):
    """ZHA quirks configuration."""

    enabled: bool = Field(default=True)
    custom_quirks_path: str | None = Field(default=None)


class DeviceOverridesConfiguration(BaseModel):
    """ZHA device overrides configuration."""

    type: Platform


class WebsocketServerConfiguration(BaseModel):
    """Websocket Server configuration for zha."""

    host: str = "0.0.0.0"
    port: int = 8001
    network_auto_start: bool = False


class WebsocketClientConfiguration(BaseModel):
    """Websocket client configuration for zha."""

    host: str = "0.0.0.0"
    port: int = 8001
    aiohttp_session: ClientSession | None = None


class ZHAConfiguration(BaseModel):
    """ZHA configuration."""

    coordinator_configuration: CoordinatorConfiguration = Field(
        default_factory=CoordinatorConfiguration
    )
    quirks_configuration: QuirksConfiguration = Field(
        default_factory=QuirksConfiguration
    )
    device_overrides: dict[str, DeviceOverridesConfiguration] = Field(
        default_factory=dict
    )
    light_options: LightOptions = Field(default_factory=LightOptions)
    device_options: DeviceOptions = Field(default_factory=DeviceOptions)
    alarm_control_panel_options: AlarmControlPanelOptions = Field(
        default_factory=AlarmControlPanelOptions
    )


@dataclasses.dataclass(kw_only=True, slots=True)
class ZHAData:
    """ZHA data stored in `gateway.data`."""

    config: ZHAConfiguration
    ws_server_config: WebsocketServerConfiguration | None = None
    ws_client_config: WebsocketClientConfiguration | None = None
    zigpy_config: dict[str, Any] = dataclasses.field(default_factory=dict)
    platforms: collections.defaultdict[Platform, list] = dataclasses.field(
        default_factory=lambda: collections.defaultdict(list)
    )
    gateway: Gateway | None = dataclasses.field(default=None)
    device_trigger_cache: dict[str, tuple[str, dict]] = dataclasses.field(
        default_factory=dict
    )
    allow_polling: bool = dataclasses.field(default=False)
    local_timezone: datetime.tzinfo = dataclasses.field(default=datetime.UTC)
