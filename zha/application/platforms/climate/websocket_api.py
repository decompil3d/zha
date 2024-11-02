"""WS api for the climate platform entity."""

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


class ClimateSetFanModeCommand(PlatformEntityCommand):
    """Set fan mode command."""

    command: Literal[APICommands.CLIMATE_SET_FAN_MODE] = (
        APICommands.CLIMATE_SET_FAN_MODE
    )
    platform: str = Platform.CLIMATE
    fan_mode: str


@decorators.websocket_command(ClimateSetFanModeCommand)
@decorators.async_response
async def set_fan_mode(
    gateway: WebSocketServerGateway, client: Client, command: ClimateSetFanModeCommand
) -> None:
    """Set the fan mode for the climate platform entity."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_fan_mode"
    )


class ClimateSetHVACModeCommand(PlatformEntityCommand):
    """Set HVAC mode command."""

    command: Literal[APICommands.CLIMATE_SET_HVAC_MODE] = (
        APICommands.CLIMATE_SET_HVAC_MODE
    )
    platform: str = Platform.CLIMATE
    hvac_mode: Literal[
        "off",  # All activity disabled / Device is off/standby
        "heat",  # Heating
        "cool",  # Cooling
        "heat_cool",  # The device supports heating/cooling to a range
        "auto",  # The temperature is set based on a schedule, learned behavior, AI or some other related mechanism. User is not able to adjust the temperature
        "dry",  # Device is in Dry/Humidity mode
        "fan_only",  # Only the fan is on, not fan and another mode like cool
    ]


@decorators.websocket_command(ClimateSetHVACModeCommand)
@decorators.async_response
async def set_hvac_mode(
    gateway: WebSocketServerGateway, client: Client, command: ClimateSetHVACModeCommand
) -> None:
    """Set the hvac mode for the climate platform entity."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_hvac_mode"
    )


class ClimateSetPresetModeCommand(PlatformEntityCommand):
    """Set preset mode command."""

    command: Literal[APICommands.CLIMATE_SET_PRESET_MODE] = (
        APICommands.CLIMATE_SET_PRESET_MODE
    )
    platform: str = Platform.CLIMATE
    preset_mode: str


@decorators.websocket_command(ClimateSetPresetModeCommand)
@decorators.async_response
async def set_preset_mode(
    gateway: WebSocketServerGateway,
    client: Client,
    command: ClimateSetPresetModeCommand,
) -> None:
    """Set the preset mode for the climate platform entity."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_preset_mode"
    )


class ClimateSetTemperatureCommand(PlatformEntityCommand):
    """Set temperature command."""

    command: Literal[APICommands.CLIMATE_SET_TEMPERATURE] = (
        APICommands.CLIMATE_SET_TEMPERATURE
    )
    platform: str = Platform.CLIMATE
    temperature: float | None = None
    target_temp_high: float | None = None
    target_temp_low: float | None = None
    hvac_mode: (
        (
            Literal[
                "off",  # All activity disabled / Device is off/standby
                "heat",  # Heating
                "cool",  # Cooling
                "heat_cool",  # The device supports heating/cooling to a range
                "auto",  # The temperature is set based on a schedule, learned behavior, AI or some other related mechanism. User is not able to adjust the temperature
                "dry",  # Device is in Dry/Humidity mode
                "fan_only",  # Only the fan is on, not fan and another mode like cool
            ]
        )
        | None
    ) = None


@decorators.websocket_command(ClimateSetTemperatureCommand)
@decorators.async_response
async def set_temperature(
    gateway: WebSocketServerGateway,
    client: Client,
    command: ClimateSetTemperatureCommand,
) -> None:
    """Set the temperature and hvac mode for the climate platform entity."""
    await execute_platform_entity_command(
        gateway, client, command, "async_set_temperature"
    )


def load_api(gateway: WebSocketServerGateway) -> None:
    """Load the api command handlers."""
    register_api_command(gateway, set_fan_mode)
    register_api_command(gateway, set_hvac_mode)
    register_api_command(gateway, set_preset_mode)
    register_api_command(gateway, set_temperature)
