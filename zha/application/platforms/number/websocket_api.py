"""WS api for the number platform entity."""

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

ATTR_VALUE = "value"
COMMAND_SET_VALUE = "number_set_value"


class NumberSetValueCommand(PlatformEntityCommand):
    """Number set value command."""

    command: Literal[APICommands.NUMBER_SET_VALUE] = APICommands.NUMBER_SET_VALUE
    platform: str = Platform.NUMBER
    value: float


@decorators.websocket_command(NumberSetValueCommand)
@decorators.async_response
async def set_value(
    gateway: WebSocketServerGateway, client: Client, command: NumberSetValueCommand
) -> None:
    """Select an option."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_native_value"
    )


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, set_value)
