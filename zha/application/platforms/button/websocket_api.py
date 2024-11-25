"""WS API for the button platform entity."""

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


class ButtonPressCommand(PlatformEntityCommand):
    """Button press command."""

    command: Literal[APICommands.BUTTON_PRESS] = APICommands.BUTTON_PRESS
    platform: str = Platform.BUTTON


@decorators.websocket_command(ButtonPressCommand)
@decorators.async_response
async def press(
    gateway: WebSocketServerGateway, client: Client, command: PlatformEntityCommand
) -> None:
    """Turn on the button."""
    await execute_platform_entity_command(gateway, client, command, "async_press")


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, press)
