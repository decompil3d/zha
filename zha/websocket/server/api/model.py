"""Models for the websocket API."""

from typing import TYPE_CHECKING, Any, Literal, Optional

from pydantic import field_serializer, field_validator
from zigpy.state import CounterGroups, NetworkInfo, NodeInfo, State
from zigpy.types.named import EUI64

from zha.application.model import (
    ConnectionLostEvent,
    DeviceFullyInitializedEvent,
    DeviceJoinedEvent,
    DeviceLeftEvent,
    DeviceOfflineEvent,
    DeviceOnlineEvent,
    DeviceRemovedEvent,
    GroupAddedEvent,
    GroupMemberAddedEvent,
    GroupMemberRemovedEvent,
    GroupRemovedEvent,
    RawDeviceInitializedEvent,
)
from zha.application.platforms.events import EntityStateChangedEvent
from zha.model import BaseModel, TypedBaseModel, as_tagged_union
from zha.websocket.const import APICommands
from zha.zigbee.cluster_handlers.model import (
    ClusterAttributeUpdatedEvent,
    ClusterBindEvent,
    ClusterConfigureReportingEvent,
    ClusterInfo,
    LevelChangeEvent,
)
from zha.zigbee.cluster_handlers.security import ClusterHandlerStateChangedEvent
from zha.zigbee.model import (
    ClusterHandlerConfigurationComplete,
    ExtendedDeviceInfo,
    GroupInfo,
    ZHAEvent,
)


class WebSocketCommand(TypedBaseModel):
    """Command for the websocket API."""

    message_id: int = 1
    command: Literal[
        APICommands.STOP_SERVER,
        APICommands.CLIENT_LISTEN_RAW_ZCL,
        APICommands.CLIENT_DISCONNECT,
        APICommands.CLIENT_LISTEN,
        APICommands.BUTTON_PRESS,
        APICommands.PLATFORM_ENTITY_REFRESH_STATE,
        APICommands.PLATFORM_ENTITY_ENABLE,
        APICommands.PLATFORM_ENTITY_DISABLE,
        APICommands.ALARM_CONTROL_PANEL_DISARM,
        APICommands.ALARM_CONTROL_PANEL_ARM_HOME,
        APICommands.ALARM_CONTROL_PANEL_ARM_AWAY,
        APICommands.ALARM_CONTROL_PANEL_ARM_NIGHT,
        APICommands.ALARM_CONTROL_PANEL_TRIGGER,
        APICommands.START_NETWORK,
        APICommands.STOP_NETWORK,
        APICommands.UPDATE_NETWORK_TOPOLOGY,
        APICommands.RECONFIGURE_DEVICE,
        APICommands.GET_DEVICES,
        APICommands.GET_GROUPS,
        APICommands.PERMIT_JOINING,
        APICommands.ADD_GROUP_MEMBERS,
        APICommands.REMOVE_GROUP_MEMBERS,
        APICommands.CREATE_GROUP,
        APICommands.REMOVE_GROUPS,
        APICommands.REMOVE_DEVICE,
        APICommands.READ_CLUSTER_ATTRIBUTES,
        APICommands.WRITE_CLUSTER_ATTRIBUTE,
        APICommands.SIREN_TURN_ON,
        APICommands.SIREN_TURN_OFF,
        APICommands.SELECT_SELECT_OPTION,
        APICommands.SELECT_RESTORE_EXTERNAL_STATE_ATTRIBUTES,
        APICommands.NUMBER_SET_VALUE,
        APICommands.LOCK_CLEAR_USER_CODE,
        APICommands.LOCK_SET_USER_CODE,
        APICommands.LOCK_ENAABLE_USER_CODE,
        APICommands.LOCK_DISABLE_USER_CODE,
        APICommands.LOCK_LOCK,
        APICommands.LOCK_UNLOCK,
        APICommands.LOCK_RESTORE_EXTERNAL_STATE_ATTRIBUTES,
        APICommands.LIGHT_TURN_OFF,
        APICommands.LIGHT_TURN_ON,
        APICommands.LIGHT_RESTORE_EXTERNAL_STATE_ATTRIBUTES,
        APICommands.FAN_SET_PERCENTAGE,
        APICommands.FAN_SET_PRESET_MODE,
        APICommands.FAN_TURN_ON,
        APICommands.FAN_TURN_OFF,
        APICommands.COVER_STOP,
        APICommands.COVER_SET_POSITION,
        APICommands.COVER_OPEN,
        APICommands.COVER_CLOSE,
        APICommands.COVER_OPEN_TILT,
        APICommands.COVER_CLOSE_TILT,
        APICommands.COVER_SET_TILT_POSITION,
        APICommands.COVER_STOP_TILT,
        APICommands.COVER_RESTORE_EXTERNAL_STATE_ATTRIBUTES,
        APICommands.CLIMATE_SET_TEMPERATURE,
        APICommands.CLIMATE_SET_HVAC_MODE,
        APICommands.CLIMATE_SET_FAN_MODE,
        APICommands.CLIMATE_SET_PRESET_MODE,
        APICommands.SWITCH_TURN_ON,
        APICommands.SWITCH_TURN_OFF,
        APICommands.FIRMWARE_INSTALL,
        APICommands.GET_APPLICATION_STATE,
    ]


class WebSocketCommandResponse(WebSocketCommand):
    """Websocket command response."""

    message_type: Literal["result"] = "result"
    success: bool


class ErrorResponse(WebSocketCommandResponse):
    """Error response model."""

    success: bool = False
    error_code: str
    error_message: str
    zigbee_error_code: Optional[str] = None
    command: APICommands


class PermitJoiningResponse(WebSocketCommandResponse):
    """Get devices response."""

    command: Literal[APICommands.PERMIT_JOINING] = APICommands.PERMIT_JOINING
    duration: int | None = None
    ieee: EUI64 | None = None


class GetDevicesResponse(WebSocketCommandResponse):
    """Get devices response."""

    command: Literal[APICommands.GET_DEVICES] = APICommands.GET_DEVICES
    devices: dict[EUI64, ExtendedDeviceInfo]

    @field_serializer("devices", check_fields=False)
    def serialize_devices(self, devices: dict[EUI64, ExtendedDeviceInfo]) -> dict:
        """Serialize devices."""
        return {str(ieee): device for ieee, device in devices.items()}

    @field_validator("devices", mode="before", check_fields=False)
    @classmethod
    def convert_devices(
        cls, devices: dict[str, ExtendedDeviceInfo]
    ) -> dict[EUI64, ExtendedDeviceInfo]:
        """Convert devices."""
        if all(isinstance(ieee, str) for ieee in devices):
            return {EUI64.convert(ieee): device for ieee, device in devices.items()}
        return devices


class ReadClusterAttributesResponse(WebSocketCommandResponse):
    """Read cluster attributes response."""

    command: Literal[APICommands.READ_CLUSTER_ATTRIBUTES] = (
        APICommands.READ_CLUSTER_ATTRIBUTES
    )
    device: ExtendedDeviceInfo
    cluster: ClusterInfo
    manufacturer_code: Optional[int]
    succeeded: dict[str, Any]
    failed: dict[str, Any]


class AttributeStatus(BaseModel):
    """Attribute status."""

    attribute: str
    status: str


class WriteClusterAttributeResponse(WebSocketCommandResponse):
    """Write cluster attribute response."""

    command: Literal[APICommands.WRITE_CLUSTER_ATTRIBUTE] = (
        APICommands.WRITE_CLUSTER_ATTRIBUTE
    )
    device: ExtendedDeviceInfo
    cluster: ClusterInfo
    manufacturer_code: Optional[int]
    response: AttributeStatus


class GroupsResponse(WebSocketCommandResponse):
    """Get groups response."""

    command: Literal[APICommands.GET_GROUPS, APICommands.REMOVE_GROUPS]
    groups: dict[int, GroupInfo]


class UpdateGroupResponse(WebSocketCommandResponse):
    """Update group response."""

    command: Literal[
        APICommands.CREATE_GROUP,
        APICommands.ADD_GROUP_MEMBERS,
        APICommands.REMOVE_GROUP_MEMBERS,
    ]
    group: GroupInfo


class GetApplicationStateResponse(WebSocketCommandResponse):
    """Get devices response."""

    command: Literal[APICommands.GET_APPLICATION_STATE] = (
        APICommands.GET_APPLICATION_STATE
    )
    state: dict[str, Any]

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def validate_state(cls, value: State | dict[str, Any]) -> dict[str, Any]:
        """Validate the state."""
        if isinstance(value, State):
            return {
                "node_info": value.node_info.as_dict(),
                "network_info": value.network_info.as_dict(),
                "counters": value.counters,
                "broadcast_counters": value.broadcast_counters,
                "device_counters": value.device_counters,
                "group_counters": value.group_counters,
            }
        return value

    def get_converted_state(self) -> State:
        """Convert state."""
        state: State = State()
        state.network_info = NetworkInfo.from_dict(self.state["network_info"])
        state.node_info = NodeInfo.from_dict(self.state["node_info"])
        state.broadcast_counters = CounterGroups().update(
            **self.state["broadcast_counters"]
        )
        state.counters = CounterGroups().update(**self.state["counters"])
        state.device_counters = CounterGroups().update(**self.state["device_counters"])
        state.group_counters = CounterGroups().update(**self.state["group_counters"])
        return state


CommandResponses = (
    WebSocketCommandResponse
    | ErrorResponse
    | GetDevicesResponse
    | GroupsResponse
    | PermitJoiningResponse
    | UpdateGroupResponse
    | ReadClusterAttributesResponse
    | WriteClusterAttributeResponse
    | GetApplicationStateResponse
)


Events = (
    EntityStateChangedEvent
    | DeviceJoinedEvent
    | RawDeviceInitializedEvent
    | DeviceFullyInitializedEvent
    | DeviceLeftEvent
    | DeviceRemovedEvent
    | GroupRemovedEvent
    | GroupAddedEvent
    | GroupMemberAddedEvent
    | GroupMemberRemovedEvent
    | DeviceOfflineEvent
    | DeviceOnlineEvent
    | ZHAEvent
    | ConnectionLostEvent
    | ClusterAttributeUpdatedEvent
    | ClusterBindEvent
    | ClusterConfigureReportingEvent
    | LevelChangeEvent
    | ClusterHandlerStateChangedEvent
    | ClusterHandlerConfigurationComplete
)

Messages = CommandResponses | Events

if not TYPE_CHECKING:
    CommandResponses = as_tagged_union(CommandResponses)
    Events = as_tagged_union(Events)
    Messages = as_tagged_union(Messages)
