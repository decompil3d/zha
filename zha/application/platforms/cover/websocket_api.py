"""WS API for the cover platform entity."""

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


class CoverOpenCommand(PlatformEntityCommand):
    """Cover open command."""

    command: Literal[APICommands.COVER_OPEN] = APICommands.COVER_OPEN
    platform: str = Platform.COVER


@decorators.websocket_command(CoverOpenCommand)
@decorators.async_response
async def open_cover(
    gateway: WebSocketServerGateway, client: Client, command: CoverOpenCommand
) -> None:
    """Open the cover."""
    await execute_platform_entity_command(gateway, client, command, "async_open_cover")


class CoverOpenTiltCommand(PlatformEntityCommand):
    """Cover open tilt command."""

    command: Literal[APICommands.COVER_OPEN_TILT] = APICommands.COVER_OPEN_TILT
    platform: str = Platform.COVER


@decorators.websocket_command(CoverOpenTiltCommand)
@decorators.async_response
async def open_cover_tilt(
    gateway: WebSocketServerGateway, client: Client, command: CoverOpenTiltCommand
) -> None:
    """Open the cover tilt."""
    await execute_platform_entity_command(
        gateway, client, command, "async_open_cover_tilt"
    )


class CoverCloseCommand(PlatformEntityCommand):
    """Cover close command."""

    command: Literal[APICommands.COVER_CLOSE] = APICommands.COVER_CLOSE
    platform: str = Platform.COVER


@decorators.websocket_command(CoverCloseCommand)
@decorators.async_response
async def close_cover(
    gateway: WebSocketServerGateway, client: Client, command: CoverCloseCommand
) -> None:
    """Close the cover."""
    await execute_platform_entity_command(gateway, client, command, "async_close_cover")


class CoverCloseTiltCommand(PlatformEntityCommand):
    """Cover close tilt command."""

    command: Literal[APICommands.COVER_CLOSE_TILT] = APICommands.COVER_CLOSE_TILT
    platform: str = Platform.COVER


@decorators.websocket_command(CoverCloseTiltCommand)
@decorators.async_response
async def close_cover_tilt(
    gateway: WebSocketServerGateway, client: Client, command: CoverCloseTiltCommand
) -> None:
    """Close the cover tilt."""
    await execute_platform_entity_command(
        gateway, client, command, "async_close_cover_tilt"
    )


class CoverSetPositionCommand(PlatformEntityCommand):
    """Cover set position command."""

    command: Literal[APICommands.COVER_SET_POSITION] = APICommands.COVER_SET_POSITION
    platform: str = Platform.COVER
    position: int


@decorators.websocket_command(CoverSetPositionCommand)
@decorators.async_response
async def set_position(
    gateway: WebSocketServerGateway, client: Client, command: CoverSetPositionCommand
) -> None:
    """Set the cover position."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_cover_position"
    )


class CoverSetTiltPositionCommand(PlatformEntityCommand):
    """Cover set position command."""

    command: Literal[APICommands.COVER_SET_TILT_POSITION] = (
        APICommands.COVER_SET_TILT_POSITION
    )
    platform: str = Platform.COVER
    tilt_position: int


@decorators.websocket_command(CoverSetTiltPositionCommand)
@decorators.async_response
async def set_tilt_position(
    gateway: WebSocketServerGateway,
    client: Client,
    command: CoverSetTiltPositionCommand,
) -> None:
    """Set the cover tilt position."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_cover_tilt_position"
    )


class CoverStopCommand(PlatformEntityCommand):
    """Cover stop command."""

    command: Literal[APICommands.COVER_STOP] = APICommands.COVER_STOP
    platform: str = Platform.COVER


@decorators.websocket_command(CoverStopCommand)
@decorators.async_response
async def stop_cover(
    gateway: WebSocketServerGateway, client: Client, command: CoverStopCommand
) -> None:
    """Stop the cover."""
    await execute_platform_entity_command(gateway, client, command, "async_stop_cover")


class CoverStopTiltCommand(PlatformEntityCommand):
    """Cover stop tilt command."""

    command: Literal[APICommands.COVER_STOP_TILT] = APICommands.COVER_STOP_TILT
    platform: str = Platform.COVER


@decorators.websocket_command(CoverStopTiltCommand)
@decorators.async_response
async def stop_cover_tilt(
    gateway: WebSocketServerGateway, client: Client, command: CoverStopTiltCommand
) -> None:
    """Stop the cover tilt."""
    await execute_platform_entity_command(
        gateway, client, command, "async_stop_cover_tilt"
    )


class CoverRestoreExternalStateAttributesCommand(PlatformEntityCommand):
    """Cover restore external state attributes command."""

    command: Literal[APICommands.COVER_RESTORE_EXTERNAL_STATE_ATTRIBUTES] = (
        APICommands.COVER_RESTORE_EXTERNAL_STATE_ATTRIBUTES
    )
    platform: str = Platform.COVER
    state: Literal["open", "opening", "closed", "closing", "unavailable"]
    target_lift_position: int | None = None
    target_tilt_position: int | None = None


@decorators.websocket_command(CoverRestoreExternalStateAttributesCommand)
@decorators.async_response
async def restore_cover_external_state_attributes(
    gateway: WebSocketServerGateway,
    client: Client,
    command: CoverRestoreExternalStateAttributesCommand,
) -> None:
    """Stop the cover tilt."""
    await execute_platform_entity_command(
        gateway, client, command, "restore_external_state_attributes"
    )


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, open_cover)
    register_api_command(gateway, close_cover)
    register_api_command(gateway, set_position)
    register_api_command(gateway, stop_cover)
    register_api_command(gateway, open_cover_tilt)
    register_api_command(gateway, close_cover_tilt)
    register_api_command(gateway, set_tilt_position)
    register_api_command(gateway, stop_cover_tilt)
    register_api_command(gateway, restore_cover_external_state_attributes)
