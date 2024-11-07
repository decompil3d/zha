"""Models for the climate platform."""

from __future__ import annotations

from zha.application.platforms.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from zha.application.platforms.model import BasePlatformEntityInfo
from zha.model import TypedBaseModel


class ThermostatState(TypedBaseModel):
    """Thermostat state model."""

    current_temperature: float | None = None
    outdoor_temperature: float | None = None
    target_temperature: float | None = None
    target_temperature_low: float | None = None
    target_temperature_high: float | None = None
    hvac_action: HVACAction | None = None
    hvac_mode: HVACMode | None = None
    preset_mode: str
    fan_mode: str | None = None
    system_mode: str | None = None
    occupancy: int | None = None
    occupied_cooling_setpoint: int | None = None
    occupied_heating_setpoint: int | None = None
    unoccupied_heating_setpoint: int | None = None
    unoccupied_cooling_setpoint: int | None = None
    pi_cooling_demand: int | None = None
    pi_heating_demand: int | None = None
    available: bool


class ThermostatEntityInfo(BasePlatformEntityInfo):
    """Thermostat entity model."""

    state: ThermostatState
    supported_features: ClimateEntityFeature
    hvac_modes: list[HVACMode]
    fan_modes: list[str] | None = None
    preset_modes: list[str] | None = None
    max_temp: float
    min_temp: float
