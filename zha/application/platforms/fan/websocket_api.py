"""WS API for the fan platform entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import Field

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


class FanTurnOnCommand(PlatformEntityCommand):
    """Fan turn on command."""

    command: Literal[APICommands.FAN_TURN_ON] = APICommands.FAN_TURN_ON
    platform: str = Platform.FAN
    speed: str | None = None
    percentage: Annotated[int, Field(ge=0, le=100)] | None = None
    preset_mode: str | None = None


@decorators.websocket_command(FanTurnOnCommand)
@decorators.async_response
async def turn_on(
    gateway: WebSocketServerGateway, client: Client, command: FanTurnOnCommand
) -> None:
    """Turn fan on."""
    await execute_platform_entity_command(gateway, client, command, "async_turn_on")


class FanTurnOffCommand(PlatformEntityCommand):
    """Fan turn off command."""

    command: Literal[APICommands.FAN_TURN_OFF] = APICommands.FAN_TURN_OFF
    platform: str = Platform.FAN


@decorators.websocket_command(FanTurnOffCommand)
@decorators.async_response
async def turn_off(
    gateway: WebSocketServerGateway, client: Client, command: FanTurnOffCommand
) -> None:
    """Turn fan off."""
    await execute_platform_entity_command(gateway, client, command, "async_turn_off")


class FanSetPercentageCommand(PlatformEntityCommand):
    """Fan set percentage command."""

    command: Literal[APICommands.FAN_SET_PERCENTAGE] = APICommands.FAN_SET_PERCENTAGE
    platform: str = Platform.FAN
    percentage: Annotated[int, Field(ge=0, le=100)]


@decorators.websocket_command(FanSetPercentageCommand)
@decorators.async_response
async def set_percentage(
    gateway: WebSocketServerGateway, client: Client, command: FanSetPercentageCommand
) -> None:
    """Set the fan speed percentage."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_percentage"
    )


class FanSetPresetModeCommand(PlatformEntityCommand):
    """Fan set preset mode command."""

    command: Literal[APICommands.FAN_SET_PRESET_MODE] = APICommands.FAN_SET_PRESET_MODE
    platform: str = Platform.FAN
    preset_mode: str


@decorators.websocket_command(FanSetPresetModeCommand)
@decorators.async_response
async def set_preset_mode(
    gateway: WebSocketServerGateway, client: Client, command: FanSetPresetModeCommand
) -> None:
    """Set the fan preset mode."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_preset_mode"
    )


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, turn_on)
    register_api_command(gateway, turn_off)
    register_api_command(gateway, set_percentage)
    register_api_command(gateway, set_preset_mode)
