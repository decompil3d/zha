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


class SelectSelectOptionCommand(PlatformEntityCommand):
    """Select select option command."""

    command: Literal[APICommands.SELECT_SELECT_OPTION] = (
        APICommands.SELECT_SELECT_OPTION
    )
    platform: str = Platform.SELECT
    option: str


@decorators.websocket_command(SelectSelectOptionCommand)
@decorators.async_response
async def select_option(
    server: Server, client: Client, command: SelectSelectOptionCommand
) -> None:
    """Select an option."""
    await execute_platform_entity_command(
        server, client, command, "async_select_option"
    )


class SelectRestoreExternalStateAttributesCommand(PlatformEntityCommand):
    """Select restore external state command."""

    command: Literal[APICommands.SELECT_RESTORE_EXTERNAL_STATE_ATTRIBUTES] = (
        APICommands.SELECT_RESTORE_EXTERNAL_STATE_ATTRIBUTES
    )
    platform: str = Platform.SELECT
    state: str


@decorators.websocket_command(SelectRestoreExternalStateAttributesCommand)
@decorators.async_response
async def restore_lock_external_state_attributes(
    server: Server, client: Client, command: SelectRestoreExternalStateAttributesCommand
) -> None:
    """Restore externally preserved state for selects."""
    await execute_platform_entity_command(
        server, client, command, "restore_external_state_attributes"
    )


def load_api(server: Server) -> None:
    """Load the api command handlers."""
    register_api_command(server, select_option)
    register_api_command(server, restore_lock_external_state_attributes)
