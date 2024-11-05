"""Support for ZHA button."""

from __future__ import annotations

from abc import ABC, abstractmethod
import functools
import logging
from typing import TYPE_CHECKING, Any, Self

from zigpy.quirks.v2 import WriteAttributeButtonMetadata, ZCLCommandButtonMetadata

from zha.application import Platform
from zha.application.const import ENTITY_METADATA
from zha.application.platforms import PlatformEntity, WebSocketClientEntity
from zha.application.platforms.button.const import DEFAULT_DURATION, ButtonDeviceClass
from zha.application.platforms.button.model import (
    ButtonEntityInfo,
    CommandButtonEntityInfo,
    WriteAttributeButtonEntityInfo,
)
from zha.application.platforms.const import EntityCategory
from zha.application.registries import PLATFORM_ENTITIES
from zha.zigbee.cluster_handlers.const import CLUSTER_HANDLER_IDENTIFY

if TYPE_CHECKING:
    from zha.zigbee.cluster_handlers import ClusterHandler
    from zha.zigbee.device import Device, WebSocketClientDevice
    from zha.zigbee.endpoint import Endpoint


MULTI_MATCH = functools.partial(PLATFORM_ENTITIES.multipass_match, Platform.BUTTON)
CONFIG_DIAGNOSTIC_MATCH = functools.partial(
    PLATFORM_ENTITIES.config_diagnostic_match, Platform.BUTTON
)

_LOGGER = logging.getLogger(__name__)


class ButtonEntityInterface(ABC):
    """Base class for ZHA button."""

    @abstractmethod
    async def async_press(self) -> None:
        """Press the button."""


class Button(PlatformEntity, ButtonEntityInterface):
    """Defines a ZHA button."""

    PLATFORM = Platform.BUTTON

    _command_name: str
    _args: list[Any]
    _kwargs: dict[str, Any]

    def __init__(
        self,
        unique_id: str,
        cluster_handlers: list[ClusterHandler],
        endpoint: Endpoint,
        device: Device,
        **kwargs: Any,
    ):
        """Initialize button."""
        self._cluster_handler: ClusterHandler = cluster_handlers[0]
        if ENTITY_METADATA in kwargs:
            self._init_from_quirks_metadata(kwargs[ENTITY_METADATA])
        super().__init__(unique_id, cluster_handlers, endpoint, device, **kwargs)

    def _init_from_quirks_metadata(
        self, entity_metadata: ZCLCommandButtonMetadata
    ) -> None:
        """Init this entity from the quirks metadata."""
        super()._init_from_quirks_metadata(entity_metadata)
        self._command_name = entity_metadata.command_name
        self._args = entity_metadata.args
        self._kwargs = entity_metadata.kwargs

    @property
    def info_object(self) -> CommandButtonEntityInfo:
        """Return a representation of the button."""
        return CommandButtonEntityInfo(
            **super().info_object.model_dump(),
            command=self._command_name,
            args=self._args,
            kwargs=self._kwargs,
        )

    @functools.cached_property
    def args(self) -> list[Any]:
        """Return the arguments to use in the command."""
        return list(self._args) if self._args else []

    @functools.cached_property
    def kwargs(self) -> dict[str, Any]:
        """Return the keyword arguments to use in the command."""
        return self._kwargs

    async def async_press(self) -> None:
        """Send out a update command."""
        command = getattr(self._cluster_handler, self._command_name)
        arguments = self.args or []
        kwargs = self.kwargs or {}
        await command(*arguments, **kwargs)


@MULTI_MATCH(cluster_handler_names=CLUSTER_HANDLER_IDENTIFY)
class IdentifyButton(Button):
    """Defines a ZHA identify button."""

    @classmethod
    def create_platform_entity(
        cls: type[Self],
        unique_id: str,
        cluster_handlers: list[ClusterHandler],
        endpoint: Endpoint,
        device: Device,
        **kwargs: Any,
    ) -> Self | None:
        """Entity Factory.

        Return entity if it is a supported configuration, otherwise return None
        """
        if PLATFORM_ENTITIES.prevent_entity_creation(
            Platform.BUTTON, device.ieee, CLUSTER_HANDLER_IDENTIFY
        ):
            return None
        return cls(unique_id, cluster_handlers, endpoint, device, **kwargs)

    _attr_device_class = ButtonDeviceClass.IDENTIFY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _command_name = "identify"
    _kwargs = {}
    _args = [DEFAULT_DURATION]


class WriteAttributeButton(PlatformEntity):
    """Defines a ZHA button, which writes a value to an attribute."""

    PLATFORM = Platform.BUTTON

    _attribute_name: str
    _attribute_value: Any = None

    def __init__(
        self,
        unique_id: str,
        cluster_handlers: list[ClusterHandler],
        endpoint: Endpoint,
        device: Device,
        **kwargs: Any,
    ) -> None:
        """Init this button."""
        self._cluster_handler: ClusterHandler = cluster_handlers[0]
        if ENTITY_METADATA in kwargs:
            self._init_from_quirks_metadata(kwargs[ENTITY_METADATA])
        super().__init__(unique_id, cluster_handlers, endpoint, device, **kwargs)

    def _init_from_quirks_metadata(
        self, entity_metadata: WriteAttributeButtonMetadata
    ) -> None:
        """Init this entity from the quirks metadata."""
        super()._init_from_quirks_metadata(entity_metadata)
        self._attribute_name = entity_metadata.attribute_name
        self._attribute_value = entity_metadata.attribute_value

    @property
    def info_object(self) -> WriteAttributeButtonEntityInfo:
        """Return a representation of the button."""
        return WriteAttributeButtonEntityInfo(
            **super().info_object.model_dump(),
            attribute_name=self._attribute_name,
            attribute_value=self._attribute_value,
        )

    async def async_press(self) -> None:
        """Write attribute with defined value."""
        await self._cluster_handler.write_attributes_safe(
            {self._attribute_name: self._attribute_value}
        )


@CONFIG_DIAGNOSTIC_MATCH(
    cluster_handler_names="tuya_manufacturer",
    manufacturers={
        "_TZE200_htnnfasr",
    },
)
class FrostLockResetButton(WriteAttributeButton):
    """Defines a ZHA frost lock reset button."""

    _unique_id_suffix = "reset_frost_lock"
    _attribute_name = "frost_lock_reset"
    _attribute_value = 0
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "reset_frost_lock"


@CONFIG_DIAGNOSTIC_MATCH(
    cluster_handler_names="opple_cluster", models={"lumi.motion.ac01"}
)
class NoPresenceStatusResetButton(WriteAttributeButton):
    """Defines a ZHA no presence status reset button."""

    _unique_id_suffix = "reset_no_presence_status"
    _attribute_name = "reset_no_presence_status"
    _attribute_value = 1
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "reset_no_presence_status"


@MULTI_MATCH(cluster_handler_names="opple_cluster", models={"aqara.feeder.acn001"})
class AqaraPetFeederFeedButton(WriteAttributeButton):
    """Defines a feed button for the aqara c1 pet feeder."""

    _unique_id_suffix = "feeding"
    _attribute_name = "feeding"
    _attribute_value = 1
    _attr_translation_key = "feed"


@CONFIG_DIAGNOSTIC_MATCH(
    cluster_handler_names="opple_cluster", models={"lumi.sensor_smoke.acn03"}
)
class AqaraSelfTestButton(WriteAttributeButton):
    """Defines a ZHA self-test button for Aqara smoke sensors."""

    _unique_id_suffix = "self_test"
    _attribute_name = "self_test"
    _attribute_value = 1
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "self_test"


class WebSocketClientButtonEntity(
    WebSocketClientEntity[ButtonEntityInfo], ButtonEntityInterface
):
    """Defines a ZHA button that is controlled via a websocket."""

    PLATFORM = Platform.BUTTON

    def __init__(
        self, entity_info: ButtonEntityInfo, device: WebSocketClientDevice
    ) -> None:
        """Initialize the ZHA alarm control device."""
        super().__init__(entity_info, device)

    @functools.cached_property
    def args(self) -> list[Any]:
        """Return the arguments to use in the command."""
        return self._entity_info.args or []

    @functools.cached_property
    def kwargs(self) -> dict[str, Any]:
        """Return the keyword arguments to use in the command."""
        return self._entity_info.kwargs or {}

    async def async_press(self) -> None:
        """Press the button."""
        await self._device.gateway.buttons.press(self._entity_info)
