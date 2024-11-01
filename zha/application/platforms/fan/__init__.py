"""Fans on Zigbee Home Automation networks."""

from __future__ import annotations

from abc import ABC, abstractmethod
import functools
import math
from typing import TYPE_CHECKING, Any

from zigpy.zcl.clusters import hvac

from zha.application import Platform
from zha.application.platforms import (
    BaseEntity,
    GroupEntity,
    PlatformEntity,
    WebSocketClientEntity,
)
from zha.application.platforms.fan.const import (
    ATTR_PERCENTAGE,
    ATTR_PRESET_MODE,
    DEFAULT_ON_PERCENTAGE,
    LEGACY_SPEED_LIST,
    OFF_SPEED_VALUES,
    PRESET_MODE_AUTO,
    PRESET_MODE_SMART,
    PRESET_MODES_TO_NAME,
    SPEED_OFF,
    SPEED_RANGE,
    FanEntityFeature,
)
from zha.application.platforms.fan.helpers import (
    NotValidPresetModeError,
    int_states_in_range,
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)
from zha.application.platforms.fan.model import FanEntityInfo
from zha.application.registries import PLATFORM_ENTITIES
from zha.zigbee.cluster_handlers import wrap_zigpy_exceptions
from zha.zigbee.cluster_handlers.const import (
    CLUSTER_HANDLER_ATTRIBUTE_UPDATED,
    CLUSTER_HANDLER_FAN,
)

if TYPE_CHECKING:
    from zha.zigbee.cluster_handlers import ClusterAttributeUpdatedEvent, ClusterHandler
    from zha.zigbee.device import Device, WebSocketClientDevice
    from zha.zigbee.endpoint import Endpoint
    from zha.zigbee.group import Group

STRICT_MATCH = functools.partial(PLATFORM_ENTITIES.strict_match, Platform.FAN)
GROUP_MATCH = functools.partial(PLATFORM_ENTITIES.group_match, Platform.FAN)
MULTI_MATCH = functools.partial(PLATFORM_ENTITIES.multipass_match, Platform.FAN)


class FanEntityInterface(ABC):
    """Fan interface."""

    @property
    @abstractmethod
    def preset_modes(self) -> list[str]:
        """Return the available preset modes."""

    @property
    @abstractmethod
    def default_on_percentage(self) -> int:
        """Return the default on percentage."""

    @property
    @abstractmethod
    def speed_list(self) -> list[str]:
        """Get the list of available speeds."""

    @property
    @abstractmethod
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""

    @property
    @abstractmethod
    def supported_features(self) -> FanEntityFeature:
        """Flag supported features."""

    @property
    @abstractmethod
    def is_on(self) -> bool:
        """Return true if the entity is on."""

    @property
    @abstractmethod
    def percentage(self) -> int | None:
        """Return the current speed percentage."""

    @property
    @abstractmethod
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""

    @property
    @abstractmethod
    def speed(self) -> str | None:
        """Return the current speed."""

    @abstractmethod
    async def async_turn_on(
        self,
        speed: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the entity on."""

    @abstractmethod
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""

    @abstractmethod
    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""

    @abstractmethod
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode for the fan."""


class BaseFan(BaseEntity, FanEntityInterface):
    """Base representation of a ZHA fan."""

    PLATFORM = Platform.FAN

    _attr_supported_features: FanEntityFeature = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )
    _attr_translation_key: str = "fan"

    @functools.cached_property
    def preset_modes(self) -> list[str]:
        """Return the available preset modes."""
        return list(self.preset_modes_to_name.values())

    @functools.cached_property
    def preset_modes_to_name(self) -> dict[int, str]:
        """Return a dict from preset mode to name."""
        return PRESET_MODES_TO_NAME

    @functools.cached_property
    def preset_name_to_mode(self) -> dict[str, int]:
        """Return a dict from preset name to mode."""
        return {v: k for k, v in self.preset_modes_to_name.items()}

    @functools.cached_property
    def default_on_percentage(self) -> int:
        """Return the default on percentage."""
        return DEFAULT_ON_PERCENTAGE

    @functools.cached_property
    def speed_range(self) -> tuple[int, int]:
        """Return the range of speeds the fan supports. Off is not included."""
        return SPEED_RANGE

    @functools.cached_property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(self.speed_range)

    @functools.cached_property
    def supported_features(self) -> FanEntityFeature:
        """Flag supported features."""
        return self._attr_supported_features

    @property
    def is_on(self) -> bool:
        """Return true if the entity is on."""
        return self.speed not in [SPEED_OFF, None]  # pylint: disable=no-member

    @functools.cached_property
    def percentage_step(self) -> float:
        """Return the step size for percentage."""
        return 100 / self.speed_count

    @functools.cached_property
    def speed_list(self) -> list[str]:
        """Get the list of available speeds."""
        speeds = [SPEED_OFF, *LEGACY_SPEED_LIST]
        if preset_modes := self.preset_modes:
            speeds.extend(preset_modes)
        return speeds

    async def async_turn_on(  # pylint: disable=unused-argument
        self,
        speed: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the entity on."""
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
        elif speed is not None:
            await self.async_set_percentage(self.speed_to_percentage(speed))
        elif percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            percentage = self.default_on_percentage
            await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        """Turn the entity off."""
        await self.async_set_percentage(0)

    async def async_set_percentage(self, percentage: int, **kwargs) -> None:
        """Set the speed percentage of the fan."""
        fan_mode = math.ceil(percentage_to_ranged_value(self.speed_range, percentage))
        await self._async_set_fan_mode(fan_mode)

    async def async_set_preset_mode(self, preset_mode: str, **kwargs) -> None:
        """Set the preset mode for the fan."""
        try:
            mode = self.preset_name_to_mode[preset_mode]
        except KeyError as ex:
            raise NotValidPresetModeError(
                f"{preset_mode} is not a valid preset mode"
            ) from ex
        await self._async_set_fan_mode(mode)

    @abstractmethod
    async def _async_set_fan_mode(self, fan_mode: int, **kwargs) -> None:
        """Set the fan mode for the fan."""

    def handle_cluster_handler_attribute_updated(
        self,
        event: ClusterAttributeUpdatedEvent,  # pylint: disable=unused-argument
    ) -> None:
        """Handle state update from cluster handler."""
        self.maybe_emit_state_changed_event()

    def speed_to_percentage(self, speed: str) -> int:
        """Map a legacy speed to a percentage."""
        if speed in OFF_SPEED_VALUES:
            return 0
        if speed not in LEGACY_SPEED_LIST:
            raise ValueError(f"The speed {speed} is not a valid speed.")
        return ordered_list_item_to_percentage(LEGACY_SPEED_LIST, speed)

    def percentage_to_speed(self, percentage: int) -> str:
        """Map a percentage to a legacy speed."""
        if percentage == 0:
            return SPEED_OFF
        return percentage_to_ordered_list_item(LEGACY_SPEED_LIST, percentage)


@STRICT_MATCH(cluster_handler_names=CLUSTER_HANDLER_FAN)
class Fan(PlatformEntity, BaseFan):
    """Representation of a ZHA fan."""

    def __init__(
        self,
        unique_id: str,
        cluster_handlers: list[ClusterHandler],
        endpoint: Endpoint,
        device: Device,
        **kwargs,
    ) -> None:
        """Initialize the fan."""
        super().__init__(unique_id, cluster_handlers, endpoint, device, **kwargs)
        self._fan_cluster_handler: ClusterHandler = self.cluster_handlers.get(
            CLUSTER_HANDLER_FAN
        )
        if self._fan_cluster_handler:
            self._fan_cluster_handler.on_event(
                CLUSTER_HANDLER_ATTRIBUTE_UPDATED,
                self.handle_cluster_handler_attribute_updated,
            )

    @property
    def info_object(self) -> FanEntityInfo:
        """Return a representation of the binary sensor."""
        return FanEntityInfo(
            **super().info_object.__dict__,
            preset_modes=self.preset_modes,
            supported_features=self.supported_features,
            speed_count=self.speed_count,
            speed_list=self.speed_list,
            default_on_percentage=self.default_on_percentage,
            percentage_step=self.percentage_step,
        )

    @property
    def state(self) -> dict:
        """Return the state of the fan."""
        response = super().state
        response.update(
            {
                "preset_mode": self.preset_mode,
                "percentage": self.percentage,
                "is_on": self.is_on,
                "speed": self.speed,
            }
        )
        return response

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if (
            self._fan_cluster_handler.fan_mode is None
            or self._fan_cluster_handler.fan_mode > self.speed_range[1]
        ):
            return None
        if self._fan_cluster_handler.fan_mode == 0:
            return 0
        return ranged_value_to_percentage(
            self.speed_range, self._fan_cluster_handler.fan_mode
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return self.preset_modes_to_name.get(self._fan_cluster_handler.fan_mode)

    @property
    def speed(self) -> str | None:
        """Return the current speed."""
        if preset_mode := self.preset_mode:
            return preset_mode
        if (percentage := self.percentage) is None:
            return None
        return self.percentage_to_speed(percentage)

    async def _async_set_fan_mode(self, fan_mode: int, **kwargs) -> None:
        """Set the fan mode for the fan."""
        await self._fan_cluster_handler.async_set_speed(fan_mode)
        self.maybe_emit_state_changed_event()


@GROUP_MATCH()
class FanGroup(GroupEntity, BaseFan):
    """Representation of a fan group."""

    def __init__(self, group: Group):
        """Initialize a fan group."""
        self._fan_cluster_handler: ClusterHandler = group.endpoint[hvac.Fan.cluster_id]
        super().__init__(group)
        self._percentage = None
        self._preset_mode = None
        self.update()

    @property
    def info_object(self) -> FanEntityInfo:
        """Return a representation of the binary sensor."""
        return FanEntityInfo(
            **super().info_object.__dict__,
            preset_modes=self.preset_modes,
            supported_features=self.supported_features,
            speed_count=self.speed_count,
            speed_list=self.speed_list,
            default_on_percentage=self.default_on_percentage,
            percentage_step=self.percentage_step,
        )

    @property
    def state(self) -> dict[str, Any]:
        """Return the state of the fan."""
        response = super().state
        response.update(
            {
                "preset_mode": self.preset_mode,
                "percentage": self.percentage,
                "is_on": self.is_on,
                "speed": self.speed,
            }
        )
        return response

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return self._percentage

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return self._preset_mode

    @property
    def speed(self) -> str | None:
        """Return the current speed."""
        if preset_mode := self.preset_mode:
            return preset_mode
        if (percentage := self.percentage) is None:
            return None
        return self.percentage_to_speed(percentage)

    async def _async_set_fan_mode(self, fan_mode: int, **kwargs) -> None:
        """Set the fan mode for the group."""

        with wrap_zigpy_exceptions():
            await self._fan_cluster_handler.write_attributes({"fan_mode": fan_mode})

        self.maybe_emit_state_changed_event()

    def update(self, _: Any = None) -> None:
        """Query all members and determine the fan group state."""
        self.debug("Updating fan group entity state")
        platform_entities = self._group.get_platform_entities(self.PLATFORM)
        all_states = [entity.state for entity in platform_entities]
        self.debug(
            "All platform entity states for group entity members: %s", all_states
        )

        percentage_states: list[dict] = [
            state for state in all_states if state.get(ATTR_PERCENTAGE)
        ]
        preset_mode_states: list[dict] = [
            state for state in all_states if state.get(ATTR_PRESET_MODE)
        ]

        if percentage_states:
            self._percentage = percentage_states[0][ATTR_PERCENTAGE]
            self._preset_mode = None
        elif preset_mode_states:
            self._preset_mode = preset_mode_states[0][ATTR_PRESET_MODE]
            self._percentage = None
        else:
            self._percentage = None
            self._preset_mode = None

        self.maybe_emit_state_changed_event()


@MULTI_MATCH(
    cluster_handler_names="ikea_airpurifier",
    models={"STARKVIND Air purifier", "STARKVIND Air purifier table"},
)
class IkeaFan(Fan):
    """Representation of an Ikea fan."""

    _attr_supported_features: FanEntityFeature = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )

    def __init__(
        self,
        unique_id: str,
        cluster_handlers: list[ClusterHandler],
        endpoint: Endpoint,
        device: Device,
        **kwargs,
    ):
        """Initialize the fan."""
        super().__init__(unique_id, cluster_handlers, endpoint, device, **kwargs)
        self._fan_cluster_handler: ClusterHandler = self.cluster_handlers.get(
            "ikea_airpurifier"
        )
        self._fan_cluster_handler.on_event(
            CLUSTER_HANDLER_ATTRIBUTE_UPDATED,
            self.handle_cluster_handler_attribute_updated,
        )

    @functools.cached_property
    def preset_modes_to_name(self) -> dict[int, str]:
        """Return a dict from preset mode to name."""
        return {1: PRESET_MODE_AUTO}

    @functools.cached_property
    def speed_range(self) -> tuple[int, int]:
        """Return the range of speeds the fan supports. Off is not included."""

        # 1 is not a speed, but auto mode and is filtered out in async_set_percentage
        return 1, 10

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self._fan_cluster_handler.fan_speed is None:
            return None
        if self._fan_cluster_handler.fan_speed == 0:
            return 0
        return ranged_value_to_percentage(
            # Starkvind has an additional fan_speed attribute that we can use to
            # get the speed even if fan_mode is set to auto.
            self.speed_range,
            self._fan_cluster_handler.fan_speed,
        )

    async def async_turn_on(
        self,
        speed: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the entity on."""
        # Starkvind turns on in auto mode by default.
        if speed is None and percentage is None and preset_mode is None:
            await self.async_set_preset_mode("auto")
        else:
            await super().async_turn_on(speed, percentage, preset_mode)

    async def async_set_percentage(self, percentage: int, **kwargs) -> None:
        """Set the speed percentage of the fan."""
        fan_mode = math.ceil(percentage_to_ranged_value(self.speed_range, percentage))
        # 1 is a mode, not a speed, so we skip to 2 instead.
        if fan_mode == 1:
            fan_mode = 2
        await self._async_set_fan_mode(fan_mode)


@MULTI_MATCH(
    cluster_handler_names=CLUSTER_HANDLER_FAN,
    models={"HBUniversalCFRemote", "HDC52EastwindFan"},
)
class KofFan(Fan):
    """Representation of a fan made by King Of Fans."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )

    @functools.cached_property
    def speed_range(self) -> tuple[int, int]:
        """Return the range of speeds the fan supports. Off is not included."""
        return (1, 4)

    @functools.cached_property
    def preset_modes_to_name(self) -> dict[int, str]:
        """Return a dict from preset mode to name."""
        return {6: PRESET_MODE_SMART}


class WebSocketClientFanEntity(
    WebSocketClientEntity[FanEntityInfo], FanEntityInterface
):
    """Representation of a ZHA fan over WebSocket."""

    PLATFORM: Platform = Platform.FAN

    def __init__(
        self, entity_info: FanEntityInfo, device: WebSocketClientDevice
    ) -> None:
        """Initialize the ZHA fan entity."""
        super().__init__(entity_info, device)

    @property
    def preset_modes(self) -> list[str]:
        """Return the available preset modes."""
        return self.info_object.preset_modes

    @property
    def default_on_percentage(self) -> int:
        """Return the default on percentage."""
        return self.info_object.default_on_percentage

    @property
    def speed_list(self) -> list[str]:
        """Get the list of available speeds."""
        return self.info_object.speed_list

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return self.info_object.speed_count

    @property
    def supported_features(self) -> FanEntityFeature:
        """Flag supported features."""
        return self.info_object.supported_features

    @property
    def is_on(self) -> bool:
        """Return true if the entity is on."""
        return self.info_object.state.is_on

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return self.info_object.state.percentage

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return self.info_object.state.preset_mode

    @property
    def speed(self) -> str | None:
        """Return the current speed."""
        return self.info_object.state.speed

    @property
    def percentage_step(self) -> float:
        """Return the step size for percentage."""
        return self.info_object.percentage_step

    async def async_turn_on(
        self,
        speed: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the entity on."""
        await self._device.gateway.fans.turn_on(
            self.info_object, speed, percentage, preset_mode
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._device.gateway.fans.turn_off(self.info_object)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        await self._device.gateway.fans.set_fan_percentage(self.info_object, percentage)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode for the fan."""
        await self._device.gateway.fans.set_fan_preset_mode(
            self.info_object, preset_mode
        )
