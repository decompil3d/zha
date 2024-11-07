"""Models for the sensor platform."""

from __future__ import annotations

from datetime import datetime

from pydantic import ValidationInfo, field_validator
from zigpy.types.named import EUI64

from zha.application.platforms.model import (
    BaseEntityInfo,
    BaseIdentifiers,
    BasePlatformEntityInfo,
    EntityState,
)
from zha.application.platforms.sensor.const import SensorDeviceClass, SensorStateClass
from zha.model import BaseEventedModel, BaseModel, TypedBaseModel


class BatteryState(TypedBaseModel):
    """Battery state model."""

    state: str | float | int | None = None
    battery_size: str | None = None
    battery_quantity: int | None = None
    battery_voltage: float | None = None
    available: bool


class ElectricalMeasurementState(TypedBaseModel):
    """Electrical measurement state model."""

    state: str | float | int | None = None
    measurement_type: str | None = None
    active_power_max: float | None = None
    rms_current_max: float | None = None
    rms_voltage_max: float | None = None
    available: bool


class SmartEnergyMeteringState(TypedBaseModel):
    """Smare energy metering state model."""

    state: str | float | int | None = None
    device_type: str | None = None
    status: str | None = None
    available: bool


class DeviceCounterSensorState(TypedBaseModel):
    """Device counter sensor state model."""

    state: int
    available: bool


class SmartEnergyMeteringEntityDescription(BaseModel):
    """Model that describes a Zigbee smart energy metering entity."""

    key: str = "instantaneous_demand"
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT
    scale: int = 1
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None


class SmartEnergySummationEntityDescription(SmartEnergyMeteringEntityDescription):
    """Model that describes a Zigbee smart energy summation entity."""

    key: str = "summation_delivered"
    state_class: SensorStateClass | None = SensorStateClass.TOTAL_INCREASING


class BaseSensorEntityInfo(BasePlatformEntityInfo):
    """Sensor model."""

    attribute: str | None = None
    decimals: int
    divisor: int
    multiplier: int | float
    unit: int | str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    extra_state_attribute_names: set[str] | None = None


class SensorEntityInfo(BaseSensorEntityInfo):
    """Sensor entity model."""

    state: EntityState


class TimestampState(TypedBaseModel):
    """Default state model."""

    available: bool | None = None
    state: datetime | None = None


class SetpointChangeSourceTimestampSensorEntityInfo(BaseSensorEntityInfo):
    """Setpoint change source timestamp sensor model."""

    state: TimestampState


class DeviceCounterSensorEntityInfo(BaseEventedModel, BaseEntityInfo):
    """Device counter sensor model."""

    counter: str
    counter_value: int
    counter_groups: str
    counter_group: str
    state: DeviceCounterSensorState

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def convert_state(
        cls, state: dict | int | None, validation_info: ValidationInfo
    ) -> DeviceCounterSensorState:
        """Convert counter value to counter_value."""
        if state is not None:
            if isinstance(state, int):
                return DeviceCounterSensorState(state=state)
            if isinstance(state, dict):
                if "state" in state:
                    return DeviceCounterSensorState(
                        state=state["state"], available=state["available"]
                    )
                else:
                    return DeviceCounterSensorState(
                        state=validation_info.data["counter_value"],
                        available=state["available"],
                    )
        return DeviceCounterSensorState(
            state=validation_info.data["counter_value"],
            available=validation_info.data["available"],
        )


class BatteryEntityInfo(BaseSensorEntityInfo):
    """Battery entity model."""

    state: BatteryState


class ElectricalMeasurementEntityInfo(BaseSensorEntityInfo):
    """Electrical measurement entity model."""

    state: ElectricalMeasurementState


class SmartEnergyMeteringEntityInfo(BaseSensorEntityInfo):
    """Smare energy metering entity model."""

    state: SmartEnergyMeteringState
    entity_description: (
        SmartEnergySummationEntityDescription
        | SmartEnergyMeteringEntityDescription
        | None
    ) = None


class DeviceCounterSensorIdentifiers(BaseIdentifiers):
    """Device counter sensor identifiers."""

    device_ieee: EUI64
