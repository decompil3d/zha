"""Constants."""

from enum import StrEnum
from typing import Final


class APICommands(StrEnum):
    """WS API commands."""

    # Device commands
    GET_DEVICES = "get_devices"
    REMOVE_DEVICE = "remove_device"
    RECONFIGURE_DEVICE = "reconfigure_device"
    READ_CLUSTER_ATTRIBUTES = "read_cluster_attributes"
    WRITE_CLUSTER_ATTRIBUTE = "write_cluster_attribute"

    # Zigbee API commands
    PERMIT_JOINING = "permit_joining"
    START_NETWORK = "start_network"
    STOP_NETWORK = "stop_network"
    UPDATE_NETWORK_TOPOLOGY = "update_network_topology"

    # Group commands
    GET_GROUPS = "get_groups"
    CREATE_GROUP = "create_group"
    REMOVE_GROUPS = "remove_groups"
    ADD_GROUP_MEMBERS = "add_group_members"
    REMOVE_GROUP_MEMBERS = "remove_group_members"

    # Server API commands
    STOP_SERVER = "stop_server"
    GET_APPLICATION_STATE = "get_application_state"

    # Light API commands
    LIGHT_TURN_ON = "light_turn_on"
    LIGHT_TURN_OFF = "light_turn_off"
    LIGHT_RESTORE_EXTERNAL_STATE_ATTRIBUTES = "light_restore_external_state_attributes"

    # Switch API commands
    SWITCH_TURN_ON = "switch_turn_on"
    SWITCH_TURN_OFF = "switch_turn_off"

    SIREN_TURN_ON = "siren_turn_on"
    SIREN_TURN_OFF = "siren_turn_off"

    LOCK_UNLOCK = "lock_unlock"
    LOCK_LOCK = "lock_lock"
    LOCK_SET_USER_CODE = "lock_set_user_lock_code"
    LOCK_ENAABLE_USER_CODE = "lock_enable_user_lock_code"
    LOCK_DISABLE_USER_CODE = "lock_disable_user_lock_code"
    LOCK_CLEAR_USER_CODE = "lock_clear_user_lock_code"
    LOCK_RESTORE_EXTERNAL_STATE_ATTRIBUTES = "lock_restore_external_state_attributes"

    CLIMATE_SET_TEMPERATURE = "climate_set_temperature"
    CLIMATE_SET_HVAC_MODE = "climate_set_hvac_mode"
    CLIMATE_SET_FAN_MODE = "climate_set_fan_mode"
    CLIMATE_SET_PRESET_MODE = "climate_set_preset_mode"

    COVER_OPEN = "cover_open"
    COVER_OPEN_TILT = "cover_open_tilt"
    COVER_CLOSE = "cover_close"
    COVER_CLOSE_TILT = "cover_close_tilt"
    COVER_STOP = "cover_stop"
    COVER_SET_POSITION = "cover_set_position"
    COVER_SET_TILT_POSITION = "cover_set_tilt_position"
    COVER_STOP_TILT = "cover_stop_tilt"
    COVER_RESTORE_EXTERNAL_STATE_ATTRIBUTES = "cover_restore_external_state_attributes"

    FAN_TURN_ON = "fan_turn_on"
    FAN_TURN_OFF = "fan_turn_off"
    FAN_SET_PERCENTAGE = "fan_set_percentage"
    FAN_SET_PRESET_MODE = "fan_set_preset_mode"

    BUTTON_PRESS = "button_press"

    ALARM_CONTROL_PANEL_DISARM = "alarm_control_panel_disarm"
    ALARM_CONTROL_PANEL_ARM_HOME = "alarm_control_panel_arm_home"
    ALARM_CONTROL_PANEL_ARM_AWAY = "alarm_control_panel_arm_away"
    ALARM_CONTROL_PANEL_ARM_NIGHT = "alarm_control_panel_arm_night"
    ALARM_CONTROL_PANEL_TRIGGER = "alarm_control_panel_trigger"

    SELECT_SELECT_OPTION = "select_select_option"
    SELECT_RESTORE_EXTERNAL_STATE_ATTRIBUTES = (
        "select_restore_external_state_attributes"
    )

    NUMBER_SET_VALUE = "number_set_value"

    PLATFORM_ENTITY_REFRESH_STATE = "platform_entity_refresh_state"
    PLATFORM_ENTITY_ENABLE = "platform_entity_enable"
    PLATFORM_ENTITY_DISABLE = "platform_entity_disable"

    CLIENT_LISTEN = "client_listen"
    CLIENT_LISTEN_RAW_ZCL = "client_listen_raw_zcl"
    CLIENT_DISCONNECT = "client_disconnect"

    FIRMWARE_INSTALL = "firmware_install"


DEVICE: Final[str] = "device"
DEVICES: Final[str] = "devices"
GROUPS: Final[str] = "groups"
GROUP_ID: Final[str] = "group_id"
GROUP_IDS: Final[str] = "group_ids"
GROUP_NAME: Final[str] = "group_name"
ERROR_CODE: Final[str] = "error_code"
ERROR_MESSAGE: Final[str] = "error_message"
MESSAGE_ID: Final[str] = "message_id"
SUCCESS: Final[str] = "success"
WEBSOCKET_API: Final[str] = "websocket_api"
ZIGBEE_ERROR_CODE: Final[str] = "zigbee_error_code"
ZIGBEE_ERROR: Final[str] = "zigbee_error"
ZIGBEE_ERROR_MESSAGE: Final[str] = "zigbee_error_message"
