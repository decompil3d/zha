"""WS api for the select platform entity."""

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
    from zha.application.gateway import WebSocketServerGateway as Server
    from zha.websocket.server.client import Client


class InstallFirmwareCommand(PlatformEntityCommand):
    """Install firmware command."""

    command: Literal[APICommands.SELECT_SELECT_OPTION] = (
        APICommands.SELECT_SELECT_OPTION
    )
    platform: str = Platform.UPDATE
    version: str | None = None


@decorators.websocket_command(InstallFirmwareCommand)
@decorators.async_response
async def install_firmware(
    server: Server, client: Client, command: InstallFirmwareCommand
) -> None:
    """Select an option."""
    await execute_platform_entity_command(server, client, command, "async_install")


def load_api(server: Server) -> None:
    """Load the api command handlers."""
    register_api_command(server, install_firmware)
