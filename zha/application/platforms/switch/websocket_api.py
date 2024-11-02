"""WS api for the switch platform entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

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


class SwitchTurnOnCommand(PlatformEntityCommand):
    """Switch turn on command."""

    command: Literal[APICommands.SWITCH_TURN_ON] = APICommands.SWITCH_TURN_ON
    platform: str = Platform.SWITCH


@decorators.websocket_command(SwitchTurnOnCommand)
@decorators.async_response
async def turn_on(
    gateway: WebSocketServerGateway, client: Client, command: SwitchTurnOnCommand
) -> None:
    """Turn on the switch."""
    await execute_platform_entity_command(gateway, client, command, "async_turn_on")


class SwitchTurnOffCommand(PlatformEntityCommand):
    """Switch turn off command."""

    command: Literal[APICommands.SWITCH_TURN_OFF] = APICommands.SWITCH_TURN_OFF
    platform: str = Platform.SWITCH


@decorators.websocket_command(SwitchTurnOffCommand)
@decorators.async_response
async def turn_off(
    gateway: WebSocketServerGateway, client: Client, command: SwitchTurnOffCommand
) -> None:
    """Turn on the switch."""
    await execute_platform_entity_command(gateway, client, command, "async_turn_off")


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, turn_on)
    register_api_command(gateway, turn_off)
