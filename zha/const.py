"""Constants for Zigbee Home Automation."""

from enum import StrEnum
from typing import Final

STATE_CHANGED: Final[str] = "state_changed"
EVENT: Final[str] = "event"
EVENT_TYPE: Final[str] = "event_type"

MESSAGE_TYPE: Final[str] = "message_type"
MODEL_CLASS_NAME: Final[str] = "model_class_name"

COMMAND: Final[str] = "command"


class EventTypes(StrEnum):
    """WS event types."""

    CONTROLLER_EVENT = "zha_gateway_message"
    PLATFORM_ENTITY_EVENT = "platform_entity_event"
    RAW_ZCL_EVENT = "raw_zcl_event"
    DEVICE_EVENT = "device_event"
    ENTITY_EVENT = "entity"
    CLUSTER_HANDLER_EVENT = "cluster_handler_event"


class ClusterHandlerEvents(StrEnum):
    """Cluster handler events."""

    CLUSTER_HANDLER_STATE_CHANGED = "cluster_handler_state_changed"
    CLUSTER_HANDLER_ATTRIBUTE_UPDATED = "cluster_handler_attribute_updated"


class EntityEvents(StrEnum):
    """Entity events."""

    STATE_CHANGED = "state_changed"


class MessageTypes(StrEnum):
    """WS message types."""

    EVENT = "event"
    RESULT = "result"


class ControllerEvents(StrEnum):
    """WS controller events."""

    DEVICE_JOINED = "device_joined"
    RAW_DEVICE_INITIALIZED = "raw_device_initialized"
    DEVICE_REMOVED = "device_removed"
    DEVICE_LEFT = "device_left"
    DEVICE_FULLY_INITIALIZED = "device_fully_initialized"
    DEVICE_CONFIGURED = "device_configured"
    GROUP_MEMBER_ADDED = "group_member_added"
    GROUP_MEMBER_REMOVED = "group_member_removed"
    GROUP_ADDED = "group_added"
    GROUP_REMOVED = "group_removed"
    CONNECTION_LOST = "connection_lost"


class PlatformEntityEvents(StrEnum):
    """WS platform entity events."""

    PLATFORM_ENTITY_STATE_CHANGED = "platform_entity_state_changed"


class RawZCLEvents(StrEnum):
    """WS raw ZCL events."""

    ATTRIBUTE_UPDATED = "attribute_updated"


class DeviceEvents(StrEnum):
    """Events that devices can broadcast."""

    DEVICE_OFFLINE = "device_offline"
    DEVICE_ONLINE = "device_online"
    ZHA_EVENT = "zha_event"
