"""Models for the ZHA application module."""

from enum import Enum
from typing import Any, Literal

from zigpy.types.named import EUI64, NWK

from zha.const import EventTypes
from zha.model import BaseEvent, BaseModel
from zha.websocket.const import ControllerEvents, DeviceEvents
from zha.zigbee.model import DeviceInfo, ExtendedDeviceInfo, GroupInfo


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
