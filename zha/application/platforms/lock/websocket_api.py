"""WS api for the lock platform entity."""

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


class LockLockCommand(PlatformEntityCommand):
    """Lock lock command."""

    command: Literal[APICommands.LOCK_LOCK] = APICommands.LOCK_LOCK
    platform: str = Platform.LOCK


@decorators.websocket_command(LockLockCommand)
@decorators.async_response
async def lock(
    gateway: WebSocketServerGateway, client: Client, command: LockLockCommand
) -> None:
    """Lock the lock."""
    await execute_platform_entity_command(gateway, client, command, "async_lock")


class LockUnlockCommand(PlatformEntityCommand):
    """Lock unlock command."""

    command: Literal[APICommands.LOCK_UNLOCK] = APICommands.LOCK_UNLOCK
    platform: str = Platform.LOCK


@decorators.websocket_command(LockUnlockCommand)
@decorators.async_response
async def unlock(
    gateway: WebSocketServerGateway, client: Client, command: LockUnlockCommand
) -> None:
    """Unlock the lock."""
    await execute_platform_entity_command(gateway, client, command, "async_unlock")


class LockSetUserLockCodeCommand(PlatformEntityCommand):
    """Set user lock code command."""

    command: Literal[APICommands.LOCK_SET_USER_CODE] = APICommands.LOCK_SET_USER_CODE
    platform: str = Platform.LOCK
    code_slot: int
    user_code: str


@decorators.websocket_command(LockSetUserLockCodeCommand)
@decorators.async_response
async def set_user_lock_code(
    gateway: WebSocketServerGateway, client: Client, command: LockSetUserLockCodeCommand
) -> None:
    """Set a user lock code in the specified slot for the lock."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_lock_user_code"
    )


class LockEnableUserLockCodeCommand(PlatformEntityCommand):
    """Enable user lock code command."""

    command: Literal[APICommands.LOCK_ENAABLE_USER_CODE] = (
        APICommands.LOCK_ENAABLE_USER_CODE
    )
    platform: str = Platform.LOCK
    code_slot: int


@decorators.websocket_command(LockEnableUserLockCodeCommand)
@decorators.async_response
async def enable_user_lock_code(
    gateway: WebSocketServerGateway,
    client: Client,
    command: LockEnableUserLockCodeCommand,
) -> None:
    """Enable a user lock code for the lock."""
    await execute_platform_entity_command(
        gateway, client, command, "async_enable_lock_user_code"
    )


class LockDisableUserLockCodeCommand(PlatformEntityCommand):
    """Disable user lock code command."""

    command: Literal[APICommands.LOCK_DISABLE_USER_CODE] = (
        APICommands.LOCK_DISABLE_USER_CODE
    )
    platform: str = Platform.LOCK
    code_slot: int


@decorators.websocket_command(LockDisableUserLockCodeCommand)
@decorators.async_response
async def disable_user_lock_code(
    gateway: WebSocketServerGateway,
    client: Client,
    command: LockDisableUserLockCodeCommand,
) -> None:
    """Disable a user lock code for the lock."""
    await execute_platform_entity_command(
        gateway, client, command, "async_disable_lock_user_code"
    )


class LockClearUserLockCodeCommand(PlatformEntityCommand):
    """Clear user lock code command."""

    command: Literal[APICommands.LOCK_CLEAR_USER_CODE] = (
        APICommands.LOCK_CLEAR_USER_CODE
    )
    platform: str = Platform.LOCK
    code_slot: int


@decorators.websocket_command(LockClearUserLockCodeCommand)
@decorators.async_response
async def clear_user_lock_code(
    gateway: WebSocketServerGateway,
    client: Client,
    command: LockClearUserLockCodeCommand,
) -> None:
    """Clear a user lock code for the lock."""
    await execute_platform_entity_command(
        gateway, client, command, "async_clear_lock_user_code"
    )


class LockRestoreExternalStateAttributesCommand(PlatformEntityCommand):
    """Restore external state attributes command."""

    command: Literal[APICommands.LOCK_RESTORE_EXTERNAL_STATE_ATTRIBUTES] = (
        APICommands.LOCK_RESTORE_EXTERNAL_STATE_ATTRIBUTES
    )
    platform: str = Platform.LOCK
    state: Literal["locked", "unlocked"] | None


@decorators.websocket_command(LockRestoreExternalStateAttributesCommand)
@decorators.async_response
async def restore_lock_external_state_attributes(
    gateway: WebSocketServerGateway,
    client: Client,
    command: LockRestoreExternalStateAttributesCommand,
) -> None:
    """Restore externally preserved state for locks."""
    await execute_platform_entity_command(
        gateway, client, command, "restore_external_state_attributes"
    )


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, lock)
    register_api_command(gateway, unlock)
    register_api_command(gateway, set_user_lock_code)
    register_api_command(gateway, enable_user_lock_code)
    register_api_command(gateway, disable_user_lock_code)
    register_api_command(gateway, clear_user_lock_code)
    register_api_command(gateway, restore_lock_external_state_attributes)
