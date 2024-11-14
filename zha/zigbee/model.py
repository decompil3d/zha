"""Models for the ZHA zigbee module."""

from __future__ import annotations

from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Any, Literal, Union

from pydantic import field_serializer, field_validator
from zigpy.types import uint1_t, uint8_t
from zigpy.types.named import EUI64, NWK, ExtendedPanId
from zigpy.zdo.types import RouteStatus, _NeighborEnums

from zha.application import Platform
from zha.application.platforms.alarm_control_panel.model import (
    AlarmControlPanelEntityInfo,
)
from zha.application.platforms.binary_sensor.model import BinarySensorEntityInfo
from zha.application.platforms.button.model import (
    ButtonEntityInfo,
    CommandButtonEntityInfo,
    WriteAttributeButtonEntityInfo,
)
from zha.application.platforms.climate.model import ThermostatEntityInfo
from zha.application.platforms.cover.model import CoverEntityInfo, ShadeEntityInfo
from zha.application.platforms.device_tracker.model import DeviceTrackerEntityInfo
from zha.application.platforms.fan.model import FanEntityInfo
from zha.application.platforms.light.model import LightEntityInfo
from zha.application.platforms.lock.model import LockEntityInfo
from zha.application.platforms.number.model import (
    NumberConfigurationEntityInfo,
    NumberEntityInfo,
)
from zha.application.platforms.select.model import (
    EnumSelectEntityInfo,
    SelectEntityInfo,
)
from zha.application.platforms.sensor.model import (
    BatteryEntityInfo,
    DeviceCounterSensorEntityInfo,
    ElectricalMeasurementEntityInfo,
    SensorEntityInfo,
    SetpointChangeSourceTimestampSensorEntityInfo,
    SmartEnergyMeteringEntityInfo,
)
from zha.application.platforms.siren.model import SirenEntityInfo
from zha.application.platforms.switch.model import (
    ConfigurableAttributeSwitchEntityInfo,
    SwitchEntityInfo,
)
from zha.application.platforms.update.model import FirmwareUpdateEntityInfo
from zha.const import DeviceEvents, EventTypes
from zha.model import BaseEvent, BaseModel, as_tagged_union, convert_enum, convert_int


class DeviceStatus(StrEnum):
    """Status of a device."""

    CREATED = "created"
    INITIALIZED = "initialized"


class ZHAEvent(BaseEvent):
    """Event generated when a device wishes to send an arbitrary event."""

    device_ieee: EUI64
    unique_id: str
    data: dict[str, Any]
    event_type: Literal[EventTypes.DEVICE_EVENT] = EventTypes.DEVICE_EVENT
    event: Literal[DeviceEvents.ZHA_EVENT] = DeviceEvents.ZHA_EVENT


class ClusterHandlerConfigurationComplete(BaseEvent):
    """Event generated when all cluster handlers are configured."""

    device_ieee: EUI64
    unique_id: str
    event_type: Literal["zha_channel_message"] = "zha_channel_message"
    event: Literal["zha_channel_cfg_done"] = "zha_channel_cfg_done"


class ClusterBinding(BaseModel):
    """Describes a cluster binding."""

    name: str
    type: str
    id: int
    endpoint_id: int


class DeviceInfo(BaseModel):
    """Describes a device."""

    ieee: EUI64
    nwk: NWK
    manufacturer: str
    model: str
    name: str
    quirk_applied: bool
    quirk_class: str
    quirk_id: str | None
    manufacturer_code: int | None
    power_source: str
    lqi: int | None
    rssi: int | None
    last_seen: float | None = None
    last_seen_time: str | None = None
    available: bool
    on_network: bool
    is_groupable: bool
    device_type: str
    signature: dict[str, Any]
    sw_version: int | None = None

    @field_serializer("signature", check_fields=False)
    def serialize_signature(self, signature: dict[str, Any]):
        """Serialize signature."""
        if "node_descriptor" in signature and not isinstance(
            signature["node_descriptor"], dict
        ):
            signature["node_descriptor"] = signature["node_descriptor"].as_dict()
        return signature


class NeighborInfo(BaseModel):
    """Describes a neighbor."""

    device_type: _NeighborEnums.DeviceType
    rx_on_when_idle: _NeighborEnums.RxOnWhenIdle
    relationship: _NeighborEnums.Relationship
    extended_pan_id: ExtendedPanId
    ieee: EUI64
    nwk: NWK
    permit_joining: _NeighborEnums.PermitJoins
    depth: uint8_t
    lqi: uint8_t

    _convert_device_type = field_validator(
        "device_type", mode="before", check_fields=False
    )(convert_enum(_NeighborEnums.DeviceType))

    _convert_rx_on_when_idle = field_validator(
        "rx_on_when_idle", mode="before", check_fields=False
    )(convert_enum(_NeighborEnums.RxOnWhenIdle))

    _convert_relationship = field_validator(
        "relationship", mode="before", check_fields=False
    )(convert_enum(_NeighborEnums.Relationship))

    _convert_permit_joining = field_validator(
        "permit_joining", mode="before", check_fields=False
    )(convert_enum(_NeighborEnums.PermitJoins))

    _convert_depth = field_validator("depth", mode="before", check_fields=False)(
        convert_int(uint8_t)
    )
    _convert_lqi = field_validator("lqi", mode="before", check_fields=False)(
        convert_int(uint8_t)
    )

    @field_validator("extended_pan_id", mode="before", check_fields=False)
    @classmethod
    def convert_extended_pan_id(
        cls, extended_pan_id: Union[str, ExtendedPanId]
    ) -> ExtendedPanId:
        """Convert extended_pan_id to ExtendedPanId."""
        if isinstance(extended_pan_id, str):
            return ExtendedPanId.convert(extended_pan_id)
        return extended_pan_id

    @field_serializer("extended_pan_id", check_fields=False)
    def serialize_extended_pan_id(self, extended_pan_id: ExtendedPanId):
        """Customize how extended_pan_id is serialized."""
        return str(extended_pan_id)

    @field_serializer(
        "device_type",
        "rx_on_when_idle",
        "relationship",
        "permit_joining",
        check_fields=False,
    )
    def serialize_enums(self, enum_value: Enum):
        """Serialize enums by name."""
        return enum_value.name


class RouteInfo(BaseModel):
    """Describes a route."""

    dest_nwk: NWK
    route_status: RouteStatus
    memory_constrained: uint1_t
    many_to_one: uint1_t
    route_record_required: uint1_t
    next_hop: NWK

    _convert_route_status = field_validator(
        "route_status", mode="before", check_fields=False
    )(convert_enum(RouteStatus))

    _convert_memory_constrained = field_validator(
        "memory_constrained", mode="before", check_fields=False
    )(convert_int(uint1_t))

    _convert_many_to_one = field_validator(
        "many_to_one", mode="before", check_fields=False
    )(convert_int(uint1_t))

    _convert_route_record_required = field_validator(
        "route_record_required", mode="before", check_fields=False
    )(convert_int(uint1_t))

    @field_serializer(
        "route_status",
        check_fields=False,
    )
    def serialize_route_status(self, route_status: RouteStatus):
        """Serialize route_status as name."""
        return route_status.name


class EndpointNameInfo(BaseModel):
    """Describes an endpoint name."""

    name: str


EntityInfoUnion = (
    SirenEntityInfo
    | SelectEntityInfo
    | NumberEntityInfo
    | LightEntityInfo
    | FanEntityInfo
    | ButtonEntityInfo
    | CommandButtonEntityInfo
    | WriteAttributeButtonEntityInfo
    | AlarmControlPanelEntityInfo
    | FirmwareUpdateEntityInfo
    | SensorEntityInfo
    | BinarySensorEntityInfo
    | DeviceTrackerEntityInfo
    | ShadeEntityInfo
    | CoverEntityInfo
    | LockEntityInfo
    | SwitchEntityInfo
    | BatteryEntityInfo
    | ElectricalMeasurementEntityInfo
    | SmartEnergyMeteringEntityInfo
    | ThermostatEntityInfo
    | DeviceCounterSensorEntityInfo
    | SetpointChangeSourceTimestampSensorEntityInfo
    | NumberConfigurationEntityInfo
    | EnumSelectEntityInfo
    | ConfigurableAttributeSwitchEntityInfo
)

if not TYPE_CHECKING:
    EntityInfoUnion = as_tagged_union(EntityInfoUnion)


class ExtendedDeviceInfo(DeviceInfo):
    """Describes a ZHA device."""

    active_coordinator: bool
    entities: dict[tuple[Platform, str], EntityInfoUnion]
    neighbors: list[NeighborInfo]
    routes: list[RouteInfo]
    endpoint_names: list[EndpointNameInfo]
    device_automation_triggers: dict[tuple[str, str], dict[str, Any]]

    @field_validator(
        "device_automation_triggers", "entities", mode="before", check_fields=False
    )
    @classmethod
    def validate_tuple_keyed_dicts(
        cls,
        tuple_keyed_dict: dict[tuple[str, str], Any] | dict[str, dict[str, Any]],
    ) -> dict[tuple[str, str], Any] | dict[str, dict[str, Any]]:
        """Validate device_automation_triggers."""
        if all(isinstance(key, str) for key in tuple_keyed_dict):
            return {
                tuple(key.split(",")): item for key, item in tuple_keyed_dict.items()
            }
        return tuple_keyed_dict


class GroupMemberReference(BaseModel):
    """Describes a group member."""

    ieee: EUI64
    endpoint_id: int


class GroupEntityReference(BaseModel):
    """Reference to a group entity."""

    entity_id: str
    name: str | None = None
    original_name: str | None = None


class GroupMemberInfo(BaseModel):
    """Describes a group member."""

    ieee: EUI64
    endpoint_id: int
    device_info: ExtendedDeviceInfo
    entities: dict[str, EntityInfoUnion]


GroupEntityUnion = LightEntityInfo | FanEntityInfo | SwitchEntityInfo

if not TYPE_CHECKING:
    GroupEntityUnion = as_tagged_union(GroupEntityUnion)


class GroupInfo(BaseModel):
    """Describes a group."""

    group_id: int
    name: str
    members: list[GroupMemberInfo]
    entities: dict[str, GroupEntityUnion]

    @property
    def members_by_ieee(self) -> dict[EUI64, GroupMemberInfo]:
        """Return members by ieee."""
        return {member.ieee: member for member in self.members}
