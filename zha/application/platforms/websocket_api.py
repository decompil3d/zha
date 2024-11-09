"""WS API for common platform entity functionality."""

from __future__ import annotations

import inspect
import logging
from typing import TYPE_CHECKING, Literal

from zigpy.types.named import EUI64

from zha.application import Platform
from zha.websocket.const import APICommands
from zha.websocket.server.api import decorators, register_api_command
from zha.websocket.server.api.model import WebSocketCommand

if TYPE_CHECKING:
    from zha.application.gateway import WebSocketServerGateway
    from zha.websocket.server.client import Client

_LOGGER = logging.getLogger(__name__)


class PlatformEntityCommand(WebSocketCommand):
    """Base class for platform entity commands."""

    ieee: EUI64 | None = None
    group_id: int | None = None
    unique_id: str
    platform: Platform


async def execute_platform_entity_command(
    gateway: WebSocketServerGateway,
    client: Client,
    command: PlatformEntityCommand,
    method_name: str,
) -> None:
    """Get the platform entity and execute a method based on the command."""

    _LOGGER.debug("attempting to execute platform entity command: %s", command)

    if command.group_id:
        group = gateway.get_group(command.group_id)
        platform_entity = group.group_entities[command.unique_id]
    else:
        device = gateway.get_device(command.ieee)
        platform_entity = device.get_platform_entity(
            command.platform, command.unique_id
        )

    if not platform_entity:
        client.send_result_error(
            command, "PLATFORM_ENTITY_COMMAND_ERROR", "platform entity not found"
        )
        return None

    try:
        action = getattr(platform_entity, method_name)
        arg_spec = inspect.getfullargspec(action)
        if arg_spec.varkw:
            if inspect.iscoroutinefunction(action):
                await action(**command.model_dump())
            else:
                action(**command.model_dump())
        elif inspect.iscoroutinefunction(action):
            await action()
        else:
            action()  # the only argument is self

    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.exception("Error executing command: %s", method_name, exc_info=err)
        client.send_result_error(command, "PLATFORM_ENTITY_ACTION_ERROR", str(err))
        return

    client.send_result_success(command)


class PlatformEntityRefreshStateCommand(PlatformEntityCommand):
    """Platform entity refresh state command."""

    command: Literal[APICommands.PLATFORM_ENTITY_REFRESH_STATE] = (
        APICommands.PLATFORM_ENTITY_REFRESH_STATE
    )


@decorators.websocket_command(PlatformEntityRefreshStateCommand)
@decorators.async_response
async def refresh_state(
    gateway: WebSocketServerGateway, client: Client, command: PlatformEntityCommand
) -> None:
    """Refresh the state of the platform entity."""
    await execute_platform_entity_command(gateway, client, command, "async_update")


class PlatformEntityEnableCommand(PlatformEntityCommand):
    """Platform entity enable command."""

    command: Literal[APICommands.PLATFORM_ENTITY_ENABLE] = (
        APICommands.PLATFORM_ENTITY_ENABLE
    )


@decorators.websocket_command(PlatformEntityEnableCommand)
@decorators.async_response
async def enable(
    gateway: WebSocketServerGateway,
    client: Client,
    command: PlatformEntityEnableCommand,
) -> None:
    """Enable the platform entity."""
    await execute_platform_entity_command(gateway, client, command, "enable")


class PlatformEntityDisableCommand(PlatformEntityCommand):
    """Platform entity disable command."""

    command: Literal[APICommands.PLATFORM_ENTITY_DISABLE] = (
        APICommands.PLATFORM_ENTITY_DISABLE
    )


@decorators.websocket_command(PlatformEntityDisableCommand)
@decorators.async_response
async def disable(
    gateway: WebSocketServerGateway,
    client: Client,
    command: PlatformEntityDisableCommand,
) -> None:
    """Disable the platform entity."""
    await execute_platform_entity_command(gateway, client, command, "disable")


# pylint: disable=import-outside-toplevel
def load_platform_entity_apis(gateway: WebSocketServerGateway) -> None:
    """Load the ws apis for all platform entities types."""
    from zha.application.platforms.alarm_control_panel.websocket_api import (
        load_api as load_alarm_control_panel_api,
    )
    from zha.application.platforms.button.websocket_api import (
        load_api as load_button_api,
    )
    from zha.application.platforms.climate.websocket_api import (
        load_api as load_climate_api,
    )
    from zha.application.platforms.cover.websocket_api import load_api as load_cover_api
    from zha.application.platforms.fan.websocket_api import load_api as load_fan_api
    from zha.application.platforms.light.websocket_api import load_api as load_light_api
    from zha.application.platforms.lock.websocket_api import load_api as load_lock_api
    from zha.application.platforms.number.websocket_api import (
        load_api as load_number_api,
    )
    from zha.application.platforms.select.websocket_api import (
        load_api as load_select_api,
    )
    from zha.application.platforms.siren.websocket_api import load_api as load_siren_api
    from zha.application.platforms.switch.websocket_api import (
        load_api as load_switch_api,
    )
    from zha.application.platforms.update.websocket_api import (
        load_api as load_update_api,
    )

    register_api_command(gateway, refresh_state)
    register_api_command(gateway, enable)
    register_api_command(gateway, disable)
    load_alarm_control_panel_api(gateway)
    load_button_api(gateway)
    load_climate_api(gateway)
    load_cover_api(gateway)
    load_fan_api(gateway)
    load_light_api(gateway)
    load_lock_api(gateway)
    load_number_api(gateway)
    load_select_api(gateway)
    load_siren_api(gateway)
    load_switch_api(gateway)
    load_update_api(gateway)
