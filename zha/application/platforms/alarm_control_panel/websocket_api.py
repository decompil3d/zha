"""WS api for the alarm control panel platform entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Union

from zha.application.discovery import Platform
from zha.application.platforms.websocket_api import (
    PlatformEntityCommand,
    execute_platform_entity_command,
)
from zha.websocket.const import APICommands
from zha.websocket.server.api import decorators, register_api_command

if TYPE_CHECKING:
    from zha.application.gateway import WebSocketServerGateway
    from zha.websocket.server.client import Client


class DisarmCommand(PlatformEntityCommand):
    """Disarm command."""

    command: Literal[APICommands.ALARM_CONTROL_PANEL_DISARM] = (
        APICommands.ALARM_CONTROL_PANEL_DISARM
    )
    platform: str = Platform.ALARM_CONTROL_PANEL
    code: Union[str, None] = None


@decorators.websocket_command(DisarmCommand)
@decorators.async_response
async def disarm(
    gateway: WebSocketServerGateway, client: Client, command: DisarmCommand
) -> None:
    """Disarm the alarm control panel."""
    await execute_platform_entity_command(
        gateway, client, command, "async_alarm_disarm"
    )


class ArmHomeCommand(PlatformEntityCommand):
    """Arm home command."""

    command: Literal[APICommands.ALARM_CONTROL_PANEL_ARM_HOME] = (
        APICommands.ALARM_CONTROL_PANEL_ARM_HOME
    )
    platform: str = Platform.ALARM_CONTROL_PANEL
    code: Union[str, None] = None


@decorators.websocket_command(ArmHomeCommand)
@decorators.async_response
async def arm_home(
    gateway: WebSocketServerGateway, client: Client, command: ArmHomeCommand
) -> None:
    """Arm the alarm control panel in home mode."""
    await execute_platform_entity_command(
        gateway, client, command, "async_alarm_arm_home"
    )


class ArmAwayCommand(PlatformEntityCommand):
    """Arm away command."""

    command: Literal[APICommands.ALARM_CONTROL_PANEL_ARM_AWAY] = (
        APICommands.ALARM_CONTROL_PANEL_ARM_AWAY
    )
    platform: str = Platform.ALARM_CONTROL_PANEL
    code: Union[str, None] = None


@decorators.websocket_command(ArmAwayCommand)
@decorators.async_response
async def arm_away(
    gateway: WebSocketServerGateway, client: Client, command: ArmAwayCommand
) -> None:
    """Arm the alarm control panel in away mode."""
    await execute_platform_entity_command(
        gateway, client, command, "async_alarm_arm_away"
    )


class ArmNightCommand(PlatformEntityCommand):
    """Arm night command."""

    command: Literal[APICommands.ALARM_CONTROL_PANEL_ARM_NIGHT] = (
        APICommands.ALARM_CONTROL_PANEL_ARM_NIGHT
    )
    platform: str = Platform.ALARM_CONTROL_PANEL
    code: Union[str, None] = None


@decorators.websocket_command(ArmNightCommand)
@decorators.async_response
async def arm_night(
    gateway: WebSocketServerGateway, client: Client, command: ArmNightCommand
) -> None:
    """Arm the alarm control panel in night mode."""
    await execute_platform_entity_command(
        gateway, client, command, "async_alarm_arm_night"
    )


class TriggerAlarmCommand(PlatformEntityCommand):
    """Trigger alarm command."""

    command: Literal[APICommands.ALARM_CONTROL_PANEL_TRIGGER] = (
        APICommands.ALARM_CONTROL_PANEL_TRIGGER
    )
    platform: str = Platform.ALARM_CONTROL_PANEL
    code: Union[str, None] = None


@decorators.websocket_command(TriggerAlarmCommand)
@decorators.async_response
async def trigger(
    gateway: WebSocketServerGateway, client: Client, command: TriggerAlarmCommand
) -> None:
    """Trigger the alarm control panel."""
    await execute_platform_entity_command(
        gateway, client, command, "async_alarm_trigger"
    )


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, disarm)
    register_api_command(gateway, arm_home)
    register_api_command(gateway, arm_away)
    register_api_command(gateway, arm_night)
    register_api_command(gateway, trigger)
