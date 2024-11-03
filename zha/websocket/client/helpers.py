"""Helper classes for zha.client."""

from __future__ import annotations

from typing import Any, Literal, cast

from zigpy.types.named import EUI64

from zha.application.platforms.alarm_control_panel.model import (
    AlarmControlPanelEntityInfo,
)
from zha.application.platforms.alarm_control_panel.websocket_api import (
    ArmAwayCommand,
    ArmHomeCommand,
    ArmNightCommand,
    DisarmCommand,
    TriggerAlarmCommand,
)
from zha.application.platforms.button.model import ButtonEntityInfo
from zha.application.platforms.button.websocket_api import ButtonPressCommand
from zha.application.platforms.climate.model import ThermostatEntityInfo
from zha.application.platforms.climate.websocket_api import (
    ClimateSetFanModeCommand,
    ClimateSetHVACModeCommand,
    ClimateSetPresetModeCommand,
    ClimateSetTemperatureCommand,
)
from zha.application.platforms.cover.model import CoverEntityInfo
from zha.application.platforms.cover.websocket_api import (
    CoverCloseCommand,
    CoverCloseTiltCommand,
    CoverOpenCommand,
    CoverOpenTiltCommand,
    CoverRestoreExternalStateAttributesCommand,
    CoverSetPositionCommand,
    CoverSetTiltPositionCommand,
    CoverStopCommand,
)
from zha.application.platforms.fan.model import FanEntityInfo
from zha.application.platforms.fan.websocket_api import (
    FanSetPercentageCommand,
    FanSetPresetModeCommand,
    FanTurnOffCommand,
    FanTurnOnCommand,
)
from zha.application.platforms.light.const import ColorMode
from zha.application.platforms.light.model import LightEntityInfo
from zha.application.platforms.light.websocket_api import (
    LightRestoreExternalStateAttributesCommand,
    LightTurnOffCommand,
    LightTurnOnCommand,
)
from zha.application.platforms.lock.model import LockEntityInfo
from zha.application.platforms.lock.websocket_api import (
    LockClearUserLockCodeCommand,
    LockDisableUserLockCodeCommand,
    LockEnableUserLockCodeCommand,
    LockLockCommand,
    LockRestoreExternalStateAttributesCommand,
    LockSetUserLockCodeCommand,
    LockUnlockCommand,
)
from zha.application.platforms.model import BasePlatformEntityInfo
from zha.application.platforms.number.model import NumberEntityInfo
from zha.application.platforms.number.websocket_api import NumberSetValueCommand
from zha.application.platforms.select.model import SelectEntityInfo
from zha.application.platforms.select.websocket_api import (
    SelectRestoreExternalStateAttributesCommand,
    SelectSelectOptionCommand,
)
from zha.application.platforms.siren.model import SirenEntityInfo
from zha.application.platforms.siren.websocket_api import (
    SirenTurnOffCommand,
    SirenTurnOnCommand,
)
from zha.application.platforms.switch.websocket_api import (
    SwitchTurnOffCommand,
    SwitchTurnOnCommand,
)
from zha.application.platforms.update import WebSocketClientFirmwareUpdateEntity
from zha.application.platforms.update.websocket_api import InstallFirmwareCommand
from zha.application.platforms.websocket_api import (
    PlatformEntityDisableCommand,
    PlatformEntityEnableCommand,
    PlatformEntityRefreshStateCommand,
)
from zha.application.websocket_api import (
    AddGroupMembersCommand,
    CreateGroupCommand,
    GetApplicationStateCommand,
    GetApplicationStateResponse,
    GetDevicesCommand,
    GetGroupsCommand,
    PermitJoiningCommand,
    ReadClusterAttributesCommand,
    ReconfigureDeviceCommand,
    RemoveDeviceCommand,
    RemoveGroupMembersCommand,
    RemoveGroupsCommand,
    StartNetworkCommand,
    StopNetworkCommand,
    StopServerCommand,
    UpdateTopologyCommand,
    WriteClusterAttributeCommand,
)
from zha.websocket.client.client import Client
from zha.websocket.server.api.model import (
    GetDevicesResponse,
    GroupsResponse,
    PermitJoiningResponse,
    ReadClusterAttributesResponse,
    UpdateGroupResponse,
    WebSocketCommandResponse,
    WriteClusterAttributeResponse,
)
from zha.websocket.server.client import (
    ClientDisconnectCommand,
    ClientListenCommand,
    ClientListenRawZCLCommand,
)
from zha.zigbee.model import ExtendedDeviceInfo, GroupInfo, GroupMemberReference


class LightHelper:
    """Helper to issue light commands."""

    def __init__(self, client: Client):
        """Initialize the light helper."""
        self._client: Client = client

    async def turn_on(
        self,
        light_platform_entity: LightEntityInfo,
        brightness: int | None = None,
        transition: int | None = None,
        flash: str | None = None,
        effect: str | None = None,
        xy_color: tuple | None = None,
        color_temp: int | None = None,
    ) -> WebSocketCommandResponse:
        """Turn on a light."""
        command = LightTurnOnCommand(
            ieee=light_platform_entity.device_ieee,
            group_id=light_platform_entity.group_id,
            unique_id=light_platform_entity.unique_id,
            brightness=brightness,
            transition=transition,
            flash=flash,
            effect=effect,
            xy_color=xy_color,
            color_temp=color_temp,
        )
        return await self._client.async_send_command(command)

    async def turn_off(
        self,
        light_platform_entity: LightEntityInfo,
        transition: int | None = None,
        flash: bool | None = None,
    ) -> WebSocketCommandResponse:
        """Turn off a light."""
        command = LightTurnOffCommand(
            ieee=light_platform_entity.device_ieee,
            group_id=light_platform_entity.group_id,
            unique_id=light_platform_entity.unique_id,
            transition=transition,
            flash=flash,
        )
        return await self._client.async_send_command(command)

    async def restore_external_state_attributes(
        self,
        light_platform_entity: LightEntityInfo,
        state: bool | None,
        off_with_transition: bool | None,
        off_brightness: int | None,
        brightness: int | None,
        color_temp: int | None,
        xy_color: tuple[float, float] | None,
        color_mode: ColorMode | None,
        effect: str | None,
    ) -> None:
        """Restore extra state attributes that are stored outside of the ZCL cache."""
        command = LightRestoreExternalStateAttributesCommand(
            ieee=light_platform_entity.device_ieee,
            group_id=light_platform_entity.group_id,
            unique_id=light_platform_entity.unique_id,
            state=state,
            off_with_transition=off_with_transition,
            off_brightness=off_brightness,
            brightness=brightness,
            color_temp=color_temp,
            xy_color=xy_color,
            color_mode=color_mode,
            effect=effect,
        )
        await self._client.async_send_command(command)


class SwitchHelper:
    """Helper to issue switch commands."""

    def __init__(self, client: Client):
        """Initialize the switch helper."""
        self._client: Client = client

    async def turn_on(
        self,
        switch_platform_entity: LightEntityInfo,
    ) -> WebSocketCommandResponse:
        """Turn on a switch."""
        command = SwitchTurnOnCommand(
            ieee=switch_platform_entity.device_ieee,
            group_id=switch_platform_entity.group_id,
            unique_id=switch_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def turn_off(
        self,
        switch_platform_entity: LightEntityInfo,
    ) -> WebSocketCommandResponse:
        """Turn off a switch."""
        command = SwitchTurnOffCommand(
            ieee=switch_platform_entity.device_ieee,
            group_id=switch_platform_entity.group_id,
            unique_id=switch_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)


class SirenHelper:
    """Helper to issue siren commands."""

    def __init__(self, client: Client):
        """Initialize the siren helper."""
        self._client: Client = client

    async def turn_on(
        self,
        siren_platform_entity: SirenEntityInfo,
        duration: int | None = None,
        volume_level: int | None = None,
        tone: int | None = None,
    ) -> WebSocketCommandResponse:
        """Turn on a siren."""
        command = SirenTurnOnCommand(
            ieee=siren_platform_entity.device_ieee,
            unique_id=siren_platform_entity.unique_id,
            duration=duration,
            level=volume_level,
            tone=tone,
        )
        return await self._client.async_send_command(command)

    async def turn_off(
        self, siren_platform_entity: SirenEntityInfo
    ) -> WebSocketCommandResponse:
        """Turn off a siren."""
        command = SirenTurnOffCommand(
            ieee=siren_platform_entity.device_ieee,
            unique_id=siren_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)


class ButtonHelper:
    """Helper to issue button commands."""

    def __init__(self, client: Client):
        """Initialize the button helper."""
        self._client: Client = client

    async def press(
        self, button_platform_entity: ButtonEntityInfo
    ) -> WebSocketCommandResponse:
        """Press a button."""
        command = ButtonPressCommand(
            ieee=button_platform_entity.device_ieee,
            unique_id=button_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)


class CoverHelper:
    """helper to issue cover commands."""

    def __init__(self, client: Client):
        """Initialize the cover helper."""
        self._client: Client = client

    async def open_cover(
        self, cover_platform_entity: CoverEntityInfo
    ) -> WebSocketCommandResponse:
        """Open a cover."""
        command = CoverOpenCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def close_cover(
        self, cover_platform_entity: CoverEntityInfo
    ) -> WebSocketCommandResponse:
        """Close a cover."""
        command = CoverCloseCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def open_cover_tilt(
        self, cover_platform_entity: CoverEntityInfo
    ) -> WebSocketCommandResponse:
        """Open cover tilt."""
        command = CoverOpenTiltCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def close_cover_tilt(
        self, cover_platform_entity: CoverEntityInfo
    ) -> WebSocketCommandResponse:
        """Open cover tilt."""
        command = CoverCloseTiltCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def stop_cover(
        self, cover_platform_entity: CoverEntityInfo
    ) -> WebSocketCommandResponse:
        """Stop a cover."""
        command = CoverStopCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def set_cover_position(
        self,
        cover_platform_entity: CoverEntityInfo,
        position: int,
    ) -> WebSocketCommandResponse:
        """Set a cover position."""
        command = CoverSetPositionCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
            position=position,
        )
        return await self._client.async_send_command(command)

    async def set_cover_tilt_position(
        self,
        cover_platform_entity: CoverEntityInfo,
        tilt_position: int,
    ) -> WebSocketCommandResponse:
        """Set a cover tilt position."""
        command = CoverSetTiltPositionCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
            tilt_position=tilt_position,
        )
        return await self._client.async_send_command(command)

    async def stop_cover_tilt(
        self, cover_platform_entity: CoverEntityInfo
    ) -> WebSocketCommandResponse:
        """Stop a cover tilt."""
        command = CoverStopCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def restore_external_state_attributes(
        self,
        cover_platform_entity: CoverEntityInfo,
        state: Literal["open", "opening", "closed", "closing"],
        target_lift_position: int,
        target_tilt_position: int,
    ) -> WebSocketCommandResponse:
        """Stop a cover tilt."""
        command = CoverRestoreExternalStateAttributesCommand(
            ieee=cover_platform_entity.device_ieee,
            unique_id=cover_platform_entity.unique_id,
            state=state,
            target_lift_position=target_lift_position,
            target_tilt_position=target_tilt_position,
        )
        return await self._client.async_send_command(command)


class FanHelper:
    """Helper to issue fan commands."""

    def __init__(self, client: Client):
        """Initialize the fan helper."""
        self._client: Client = client

    async def turn_on(
        self,
        fan_platform_entity: FanEntityInfo,
        speed: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
    ) -> WebSocketCommandResponse:
        """Turn on a fan."""
        command = FanTurnOnCommand(
            ieee=fan_platform_entity.device_ieee,
            group_id=fan_platform_entity.group_id,
            unique_id=fan_platform_entity.unique_id,
            speed=speed,
            percentage=percentage,
            preset_mode=preset_mode,
        )
        return await self._client.async_send_command(command)

    async def turn_off(
        self,
        fan_platform_entity: FanEntityInfo,
    ) -> WebSocketCommandResponse:
        """Turn off a fan."""
        command = FanTurnOffCommand(
            ieee=fan_platform_entity.device_ieee,
            group_id=fan_platform_entity.group_id,
            unique_id=fan_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def set_fan_percentage(
        self,
        fan_platform_entity: FanEntityInfo,
        percentage: int,
    ) -> WebSocketCommandResponse:
        """Set a fan percentage."""
        command = FanSetPercentageCommand(
            ieee=fan_platform_entity.device_ieee,
            group_id=fan_platform_entity.group_id,
            unique_id=fan_platform_entity.unique_id,
            percentage=percentage,
        )
        return await self._client.async_send_command(command)

    async def set_fan_preset_mode(
        self,
        fan_platform_entity: FanEntityInfo,
        preset_mode: str,
    ) -> WebSocketCommandResponse:
        """Set a fan preset mode."""
        command = FanSetPresetModeCommand(
            ieee=fan_platform_entity.device_ieee,
            group_id=fan_platform_entity.group_id,
            unique_id=fan_platform_entity.unique_id,
            preset_mode=preset_mode,
        )
        return await self._client.async_send_command(command)


class LockHelper:
    """Helper to issue lock commands."""

    def __init__(self, client: Client):
        """Initialize the lock helper."""
        self._client: Client = client

    async def lock(
        self, lock_platform_entity: LockEntityInfo
    ) -> WebSocketCommandResponse:
        """Lock a lock."""
        command = LockLockCommand(
            ieee=lock_platform_entity.device_ieee,
            unique_id=lock_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def unlock(
        self, lock_platform_entity: LockEntityInfo
    ) -> WebSocketCommandResponse:
        """Unlock a lock."""
        command = LockUnlockCommand(
            ieee=lock_platform_entity.device_ieee,
            unique_id=lock_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)

    async def set_user_lock_code(
        self,
        lock_platform_entity: LockEntityInfo,
        code_slot: int,
        user_code: str,
    ) -> WebSocketCommandResponse:
        """Set a user lock code."""
        command = LockSetUserLockCodeCommand(
            ieee=lock_platform_entity.device_ieee,
            unique_id=lock_platform_entity.unique_id,
            code_slot=code_slot,
            user_code=user_code,
        )
        return await self._client.async_send_command(command)

    async def clear_user_lock_code(
        self,
        lock_platform_entity: LockEntityInfo,
        code_slot: int,
    ) -> WebSocketCommandResponse:
        """Clear a user lock code."""
        command = LockClearUserLockCodeCommand(
            ieee=lock_platform_entity.device_ieee,
            unique_id=lock_platform_entity.unique_id,
            code_slot=code_slot,
        )
        return await self._client.async_send_command(command)

    async def enable_user_lock_code(
        self,
        lock_platform_entity: LockEntityInfo,
        code_slot: int,
    ) -> WebSocketCommandResponse:
        """Enable a user lock code."""
        command = LockEnableUserLockCodeCommand(
            ieee=lock_platform_entity.device_ieee,
            unique_id=lock_platform_entity.unique_id,
            code_slot=code_slot,
        )
        return await self._client.async_send_command(command)

    async def disable_user_lock_code(
        self,
        lock_platform_entity: LockEntityInfo,
        code_slot: int,
    ) -> WebSocketCommandResponse:
        """Disable a user lock code."""
        command = LockDisableUserLockCodeCommand(
            ieee=lock_platform_entity.device_ieee,
            unique_id=lock_platform_entity.unique_id,
            code_slot=code_slot,
        )
        return await self._client.async_send_command(command)

    async def restore_external_state_attributes(
        self,
        lock_platform_entity: LockEntityInfo,
        state: Literal["locked", "unlocked"] | None,
    ) -> WebSocketCommandResponse:
        """Restore external state attributes."""
        command = LockRestoreExternalStateAttributesCommand(
            ieee=lock_platform_entity.device_ieee,
            unique_id=lock_platform_entity.unique_id,
            state=state,
        )
        return await self._client.async_send_command(command)


class NumberHelper:
    """Helper to issue number commands."""

    def __init__(self, client: Client):
        """Initialize the number helper."""
        self._client: Client = client

    async def set_value(
        self,
        number_platform_entity: NumberEntityInfo,
        value: int | float,
    ) -> WebSocketCommandResponse:
        """Set a number."""
        command = NumberSetValueCommand(
            ieee=number_platform_entity.device_ieee,
            unique_id=number_platform_entity.unique_id,
            value=value,
        )
        return await self._client.async_send_command(command)


class SelectHelper:
    """Helper to issue select commands."""

    def __init__(self, client: Client):
        """Initialize the select helper."""
        self._client: Client = client

    async def select_option(
        self,
        select_platform_entity: SelectEntityInfo,
        option: str | int,
    ) -> WebSocketCommandResponse:
        """Set a select."""
        command = SelectSelectOptionCommand(
            ieee=select_platform_entity.device_ieee,
            unique_id=select_platform_entity.unique_id,
            option=option,
        )
        return await self._client.async_send_command(command)

    async def restore_external_state_attributes(
        self,
        select_platform_entity: SelectEntityInfo,
        state: str | None,
    ) -> WebSocketCommandResponse:
        """Restore external state attributes."""
        command = SelectRestoreExternalStateAttributesCommand(
            ieee=select_platform_entity.device_ieee,
            unique_id=select_platform_entity.unique_id,
            state=state,
        )
        return await self._client.async_send_command(command)


class ClimateHelper:
    """Helper to issue climate commands."""

    def __init__(self, client: Client):
        """Initialize the climate helper."""
        self._client: Client = client

    async def set_hvac_mode(
        self,
        climate_platform_entity: ThermostatEntityInfo,
        hvac_mode: Literal[
            "heat_cool", "heat", "cool", "auto", "dry", "fan_only", "off"
        ],
    ) -> WebSocketCommandResponse:
        """Set a climate."""
        command = ClimateSetHVACModeCommand(
            ieee=climate_platform_entity.device_ieee,
            unique_id=climate_platform_entity.unique_id,
            hvac_mode=hvac_mode,
        )
        return await self._client.async_send_command(command)

    async def set_temperature(
        self,
        climate_platform_entity: ThermostatEntityInfo,
        hvac_mode: None
        | (
            Literal["heat_cool", "heat", "cool", "auto", "dry", "fan_only", "off"]
        ) = None,
        temperature: float | None = None,
        target_temp_high: float | None = None,
        target_temp_low: float | None = None,
    ) -> WebSocketCommandResponse:
        """Set a climate."""
        command = ClimateSetTemperatureCommand(
            ieee=climate_platform_entity.device_ieee,
            unique_id=climate_platform_entity.unique_id,
            temperature=temperature,
            target_temp_high=target_temp_high,
            target_temp_low=target_temp_low,
            hvac_mode=hvac_mode,
        )
        return await self._client.async_send_command(command)

    async def set_fan_mode(
        self,
        climate_platform_entity: ThermostatEntityInfo,
        fan_mode: str,
    ) -> WebSocketCommandResponse:
        """Set a climate."""
        command = ClimateSetFanModeCommand(
            ieee=climate_platform_entity.device_ieee,
            unique_id=climate_platform_entity.unique_id,
            fan_mode=fan_mode,
        )
        return await self._client.async_send_command(command)

    async def set_preset_mode(
        self,
        climate_platform_entity: ThermostatEntityInfo,
        preset_mode: str,
    ) -> WebSocketCommandResponse:
        """Set a climate."""
        command = ClimateSetPresetModeCommand(
            ieee=climate_platform_entity.device_ieee,
            unique_id=climate_platform_entity.unique_id,
            preset_mode=preset_mode,
        )
        return await self._client.async_send_command(command)


class AlarmControlPanelHelper:
    """Helper to issue alarm control panel commands."""

    def __init__(self, client: Client):
        """Initialize the alarm control panel helper."""
        self._client: Client = client

    async def disarm(
        self,
        alarm_control_panel_platform_entity: AlarmControlPanelEntityInfo,
        code: str,
    ) -> WebSocketCommandResponse:
        """Disarm an alarm control panel."""
        command = DisarmCommand(
            ieee=alarm_control_panel_platform_entity.device_ieee,
            unique_id=alarm_control_panel_platform_entity.unique_id,
            code=code,
        )
        return await self._client.async_send_command(command)

    async def arm_home(
        self,
        alarm_control_panel_platform_entity: AlarmControlPanelEntityInfo,
        code: str,
    ) -> WebSocketCommandResponse:
        """Arm an alarm control panel in home mode."""
        command = ArmHomeCommand(
            ieee=alarm_control_panel_platform_entity.device_ieee,
            unique_id=alarm_control_panel_platform_entity.unique_id,
            code=code,
        )
        return await self._client.async_send_command(command)

    async def arm_away(
        self,
        alarm_control_panel_platform_entity: AlarmControlPanelEntityInfo,
        code: str,
    ) -> WebSocketCommandResponse:
        """Arm an alarm control panel in away mode."""
        command = ArmAwayCommand(
            ieee=alarm_control_panel_platform_entity.device_ieee,
            unique_id=alarm_control_panel_platform_entity.unique_id,
            code=code,
        )
        return await self._client.async_send_command(command)

    async def arm_night(
        self,
        alarm_control_panel_platform_entity: AlarmControlPanelEntityInfo,
        code: str,
    ) -> WebSocketCommandResponse:
        """Arm an alarm control panel in night mode."""
        command = ArmNightCommand(
            ieee=alarm_control_panel_platform_entity.device_ieee,
            unique_id=alarm_control_panel_platform_entity.unique_id,
            code=code,
        )
        return await self._client.async_send_command(command)

    async def trigger(
        self,
        alarm_control_panel_platform_entity: AlarmControlPanelEntityInfo,
    ) -> WebSocketCommandResponse:
        """Trigger an alarm control panel alarm."""
        command = TriggerAlarmCommand(
            ieee=alarm_control_panel_platform_entity.device_ieee,
            unique_id=alarm_control_panel_platform_entity.unique_id,
        )
        return await self._client.async_send_command(command)


class PlatformEntityHelper:
    """Helper to send global platform entity commands."""

    def __init__(self, client: Client):
        """Initialize the platform entity helper."""
        self._client: Client = client

    async def refresh_state(
        self, platform_entity: BasePlatformEntityInfo
    ) -> WebSocketCommandResponse:
        """Refresh the state of a platform entity."""
        command = PlatformEntityRefreshStateCommand(
            ieee=platform_entity.device_ieee,
            unique_id=platform_entity.unique_id,
            platform=platform_entity.platform,
        )
        return await self._client.async_send_command(command)

    async def enable(
        self, platform_entity: BasePlatformEntityInfo
    ) -> WebSocketCommandResponse:
        """Enable a platform entity."""
        command = PlatformEntityEnableCommand(
            ieee=platform_entity.device_ieee,
            unique_id=platform_entity.unique_id,
            platform=platform_entity.platform,
        )
        return await self._client.async_send_command(command)

    async def disable(
        self, platform_entity: BasePlatformEntityInfo
    ) -> WebSocketCommandResponse:
        """Disable a platform entity."""
        command = PlatformEntityDisableCommand(
            ieee=platform_entity.device_ieee,
            unique_id=platform_entity.unique_id,
            platform=platform_entity.platform,
        )
        return await self._client.async_send_command(command)


class ClientHelper:
    """Helper to send client specific commands."""

    def __init__(self, client: Client):
        """Initialize the client helper."""
        self._client: Client = client

    async def listen(self) -> WebSocketCommandResponse:
        """Listen for incoming messages."""
        command = ClientListenCommand()
        return await self._client.async_send_command(command)

    async def listen_raw_zcl(self) -> WebSocketCommandResponse:
        """Listen for incoming raw ZCL messages."""
        command = ClientListenRawZCLCommand()
        return await self._client.async_send_command(command)

    async def disconnect(self) -> WebSocketCommandResponse:
        """Disconnect this client from the server."""
        command = ClientDisconnectCommand()
        return await self._client.async_send_command(command)


class GroupHelper:
    """Helper to send group commands."""

    def __init__(self, client: Client):
        """Initialize the group helper."""
        self._client: Client = client

    async def get_groups(self) -> dict[int, GroupInfo]:
        """Get the groups."""
        response = cast(
            GroupsResponse,
            await self._client.async_send_command(GetGroupsCommand()),
        )
        return response.groups

    async def create_group(
        self,
        name: str,
        group_id: int | None = None,
        members: list[GroupMemberReference] | None = None,
    ) -> GroupInfo:
        """Create a new group."""
        request_data: dict[str, Any] = {
            "group_name": name,
            "group_id": group_id,
        }
        if members is not None:
            request_data["members"] = [
                {"ieee": member.ieee, "endpoint_id": member.endpoint_id}
                for member in members
            ]

        command = CreateGroupCommand(**request_data)
        response = cast(
            UpdateGroupResponse,
            await self._client.async_send_command(command),
        )
        return response.group

    async def remove_groups(self, groups: list[GroupInfo]) -> dict[int, GroupInfo]:
        """Remove groups."""
        request: dict[str, Any] = {
            "group_ids": [group.group_id for group in groups],
        }
        command = RemoveGroupsCommand(**request)
        response = cast(
            GroupsResponse,
            await self._client.async_send_command(command),
        )
        return response.groups

    async def add_group_members(
        self, group: GroupInfo, members: list[GroupMemberReference]
    ) -> GroupInfo:
        """Add members to a group."""
        request_data: dict[str, Any] = {
            "group_id": group.group_id,
            "members": [
                {"ieee": member.ieee, "endpoint_id": member.endpoint_id}
                for member in members
            ],
        }

        command = AddGroupMembersCommand(**request_data)
        response = cast(
            UpdateGroupResponse,
            await self._client.async_send_command(command),
        )
        return response.group

    async def remove_group_members(
        self, group: GroupInfo, members: list[GroupMemberReference]
    ) -> GroupInfo:
        """Remove members from a group."""
        request_data: dict[str, Any] = {
            "group_id": group.group_id,
            "members": [
                {"ieee": member.ieee, "endpoint_id": member.endpoint_id}
                for member in members
            ],
        }

        command = RemoveGroupMembersCommand(**request_data)
        response = cast(
            UpdateGroupResponse,
            await self._client.async_send_command(command),
        )
        return response.group


class UpdateHelper:
    """Helper to send firmware update commands."""

    def __init__(self, client: Client):
        """Initialize the device helper."""
        self._client: Client = client

    async def install_firmware(
        self,
        firmware_update_entity: WebSocketClientFirmwareUpdateEntity,
        version: str | None = None,
    ) -> dict[EUI64, ExtendedDeviceInfo]:
        """Get the groups."""

        return await self._client.async_send_command(
            InstallFirmwareCommand(
                ieee=firmware_update_entity.info_object.device_ieee,
                unique_id=firmware_update_entity.info_object.unique_id,
                platform=firmware_update_entity.info_object.platform,
                version=version,
            )
        )


class DeviceHelper:
    """Helper to send device commands."""

    def __init__(self, client: Client):
        """Initialize the device helper."""
        self._client: Client = client

    async def get_devices(self) -> dict[EUI64, ExtendedDeviceInfo]:
        """Get the groups."""
        response = cast(
            GetDevicesResponse,
            await self._client.async_send_command(GetDevicesCommand()),
        )
        return response.devices

    async def reconfigure_device(self, device: ExtendedDeviceInfo) -> None:
        """Reconfigure a device."""
        await self._client.async_send_command(
            ReconfigureDeviceCommand(ieee=device.ieee)
        )

    async def remove_device(self, device: ExtendedDeviceInfo) -> None:
        """Remove a device."""
        await self._client.async_send_command(RemoveDeviceCommand(ieee=device.ieee))

    async def read_cluster_attributes(
        self,
        device: ExtendedDeviceInfo,
        cluster_id: int,
        cluster_type: str,
        endpoint_id: int,
        attributes: list[str],
        manufacturer_code: int | None = None,
    ) -> ReadClusterAttributesResponse:
        """Read cluster attributes."""
        response = cast(
            ReadClusterAttributesResponse,
            await self._client.async_send_command(
                ReadClusterAttributesCommand(
                    ieee=device.ieee,
                    endpoint_id=endpoint_id,
                    cluster_id=cluster_id,
                    cluster_type=cluster_type,
                    attributes=attributes,
                    manufacturer_code=manufacturer_code,
                )
            ),
        )
        return response

    async def write_cluster_attribute(
        self,
        device: ExtendedDeviceInfo,
        cluster_id: int,
        cluster_type: str,
        endpoint_id: int,
        attribute: str,
        value: Any,
        manufacturer_code: int | None = None,
    ) -> WriteClusterAttributeResponse:
        """Set the value for a cluster attribute."""
        response = cast(
            WriteClusterAttributeResponse,
            await self._client.async_send_command(
                WriteClusterAttributeCommand(
                    ieee=device.ieee,
                    endpoint_id=endpoint_id,
                    cluster_id=cluster_id,
                    cluster_type=cluster_type,
                    attribute=attribute,
                    value=value,
                    manufacturer_code=manufacturer_code,
                )
            ),
        )
        return response


class NetworkHelper:
    """Helper for network commands."""

    def __init__(self, client: Client):
        """Initialize the device helper."""
        self._client: Client = client

    async def permit_joining(
        self, duration: int = 255, device: ExtendedDeviceInfo | None = None
    ) -> bool:
        """Permit joining for a specified duration."""
        # TODO add permit with code support
        request_data: dict[str, Any] = {
            "duration": duration,
        }
        if device is not None:
            if device.device_type == "EndDevice":
                raise ValueError("Device is not a coordinator or router")
            request_data["ieee"] = device.ieee
        command = PermitJoiningCommand(**request_data)
        response = cast(
            PermitJoiningResponse,
            await self._client.async_send_command(command),
        )
        return response.success

    async def update_topology(self) -> None:
        """Update the network topology."""
        await self._client.async_send_command(UpdateTopologyCommand())

    async def start_network(self) -> bool:
        """Start the Zigbee network."""
        command = StartNetworkCommand()
        response = await self._client.async_send_command(command)
        return response.success

    async def stop_network(self) -> bool:
        """Stop the Zigbee network."""
        response = await self._client.async_send_command(StopNetworkCommand())
        return response.success

    async def get_application_state(self) -> GetApplicationStateResponse:
        """Get the application state."""
        return await self._client.async_send_command(GetApplicationStateCommand())


class ServerHelper:
    """Helper for server commands."""

    def __init__(self, client: Client):
        """Initialize the helper."""
        self._client: Client = client

    async def stop_server(self) -> bool:
        """Stop the websocket server."""
        response = await self._client.async_send_command(StopServerCommand())
        return response.success
