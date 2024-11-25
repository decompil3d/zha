"""Group for Zigbee Home Automation."""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Any, Generic

import zigpy.exceptions
from zigpy.types.named import EUI64

from zha.application import discovery
from zha.application.platforms import PlatformEntity, T, WebSocketClientEntity
from zha.const import STATE_CHANGED
from zha.event import EventBase
from zha.mixins import LogMixin
from zha.zigbee.model import GroupInfo, GroupMemberInfo, GroupMemberReference

if TYPE_CHECKING:
    from zigpy.group import Group as ZigpyGroup, GroupEndpoint

    from zha.application.gateway import Gateway, WebSocketClientGateway
    from zha.application.platforms import GroupEntity
    from zha.application.platforms.events import EntityStateChangedEvent
    from zha.zigbee.device import Device, WebSocketClientDevice

_LOGGER = logging.getLogger(__name__)


class BaseGroupMember(LogMixin, ABC):
    """Composite object that represents a device endpoint in a Zigbee group."""

    def __init__(self, zha_group, device, endpoint_id: int) -> None:
        """Initialize the group member."""
        self._group = zha_group
        self._device = device
        self._endpoint_id: int = endpoint_id

    @property
    @abstractmethod
    def group(self):
        """Return the group this member belongs to."""

    @property
    def endpoint_id(self) -> int:
        """Return the endpoint id for this group member."""
        return self._endpoint_id

    @property
    @abstractmethod
    def device(self):
        """Return the ZHA device for this group member."""

    @property
    @abstractmethod
    def member_info(self) -> GroupMemberInfo:
        """Get ZHA group info."""

    @property
    @abstractmethod
    def associated_entities(self) -> list[PlatformEntity]:
        """Return the list of entities that were derived from this endpoint."""

    @abstractmethod
    async def async_remove_from_group(self) -> None:
        """Remove the device endpoint from the provided zigbee group."""

    def log(self, level: int, msg: str, *args: Any, **kwargs) -> None:
        """Log a message."""
        msg = f"[%s](%s): {msg}"
        args = (f"0x{self._group.group_id:04x}", self.endpoint_id) + args
        _LOGGER.log(level, msg, *args, **kwargs)


class GroupMember(BaseGroupMember):
    """Composite object that represents a device endpoint in a Zigbee group."""

    def __init__(self, zha_group: Group, device: Device, endpoint_id: int) -> None:
        """Initialize the group member."""
        super().__init__(zha_group, device, endpoint_id)

    @property
    def group(self) -> Group:
        """Return the group this member belongs to."""
        return self._group

    @property
    def endpoint(self) -> GroupEndpoint:
        """Return the endpoint for this group member."""
        return self._device.device.endpoints.get(self.endpoint_id)

    @property
    def device(self) -> Device:
        """Return the ZHA device for this group member."""
        return self._device

    @property
    def member_info(self) -> GroupMemberInfo:
        """Get ZHA group info."""
        return GroupMemberInfo(
            ieee=self.device.ieee,
            endpoint_id=self.endpoint_id,
            device_info=self.device.extended_device_info,
            entities={
                entity.unique_id: entity.info_object.model_dump()
                for entity in self.associated_entities
            },
        )

    @property
    def associated_entities(self) -> list[PlatformEntity]:
        """Return the list of entities that were derived from this endpoint."""
        return [
            platform_entity
            for platform_entity in self._device.platform_entities.values()
            if hasattr(platform_entity, "endpoint")
            and platform_entity.endpoint.id == self.endpoint_id
        ]

    async def async_remove_from_group(self) -> None:
        """Remove the device endpoint from the provided zigbee group."""
        try:
            await self._device.device.endpoints[self._endpoint_id].remove_from_group(
                self._group.group_id
            )
        except (zigpy.exceptions.ZigbeeException, TimeoutError) as ex:
            self.debug(
                (
                    "Failed to remove endpoint: %s for device '%s' from group: 0x%04x"
                    " ex: %s"
                ),
                self._endpoint_id,
                self._device.ieee,
                self._group.group_id,
                str(ex),
            )


class WebSocketClientGroupMember(BaseGroupMember):
    """Composite object that represents a device endpoint in a Zigbee group."""

    def __init__(
        self,
        zha_group: WebSocketClientGroup,
        device: WebSocketClientDevice,
        endpoint_id: int,
        member_info: GroupMemberInfo,
    ) -> None:
        """Initialize the group member."""
        super().__init__(zha_group, device, endpoint_id)
        self._member_info = member_info

    @property
    def group(self) -> WebSocketClientGroup:
        """Return the group this member belongs to."""
        return self._group

    @property
    def device(self) -> WebSocketClientDevice:
        """Return the ZHA device for this group member."""
        return self._device

    @property
    def member_info(self) -> GroupMemberInfo:
        """Get ZHA group info."""
        return self._member_info

    @property
    def associated_entities(self) -> list[PlatformEntity]:
        """Return the list of entities that were derived from this endpoint."""
        return [
            platform_entity
            for platform_entity in self._device.platform_entities.values()
            if platform_entity.info_object.endpoint_id == self.endpoint_id
        ]

    async def async_remove_from_group(self) -> None:
        """Remove the device endpoint from the provided zigbee group."""
        await self.group.gateway.groups_helper.remove_group_members(
            self.group.info_object, [self.member_info]
        )


class BaseGroup(LogMixin, EventBase, ABC, Generic[T]):
    """Base class for Zigbee groups."""

    def __init__(
        self,
        gateway: Gateway,
    ) -> None:
        """Initialize the group."""
        super().__init__()
        self._gateway = gateway

    @property
    def gateway(self) -> Gateway:
        """Return the gateway for this group."""
        return self._gateway

    @property
    @abstractmethod
    def name(self) -> str:
        """Return group name."""

    @property
    @abstractmethod
    def group_id(self) -> int:
        """Return group name."""

    @property
    @abstractmethod
    def group_entities(self) -> dict[str, T]:
        """Return the platform entities of the group."""

    @property
    @abstractmethod
    def members(self):
        """Return the ZHA devices that are members of this group."""

    @property
    @abstractmethod
    def info_object(self) -> GroupInfo:
        """Get ZHA group info."""


class Group(BaseGroup):
    """ZHA Zigbee group object."""

    def __init__(
        self,
        gateway: Gateway,
        zigpy_group: zigpy.group.Group,
    ) -> None:
        """Initialize the group."""
        super().__init__(gateway)
        self._zigpy_group = zigpy_group
        self._group_entities: dict[str, GroupEntity] = {}
        self._entity_unsubs: dict[str, Callable] = {}

    @property
    def name(self) -> str:
        """Return group name."""
        return self._zigpy_group.name

    @property
    def group_id(self) -> int:
        """Return group name."""
        return self._zigpy_group.group_id

    @property
    def endpoint(self) -> zigpy.endpoint.Endpoint:
        """Return the endpoint for this group."""
        return self._zigpy_group.endpoint

    @property
    def group_entities(self) -> dict[str, GroupEntity]:
        """Return the platform entities of the group."""
        return self._group_entities

    @property
    def zigpy_group(self) -> ZigpyGroup:
        """Return the zigpy group."""
        return self._zigpy_group

    @property
    def gateway(self) -> Gateway:
        """Return the gateway for this group."""
        return self._gateway

    @property
    def members(self) -> list[GroupMember]:
        """Return the ZHA devices that are members of this group."""
        return [
            GroupMember(self, self._gateway.devices[member_ieee], endpoint_id)
            for (member_ieee, endpoint_id) in self._zigpy_group.members
            if member_ieee in self._gateway.devices
        ]

    @property
    def info_object(self) -> GroupInfo:
        """Get ZHA group info."""
        return GroupInfo(
            group_id=self.group_id,
            name=self.name,
            members=[member.member_info for member in self.members],
            entities={
                unique_id: entity.info_object.model_dump()
                for unique_id, entity in self._group_entities.items()
            },
        )

    @property
    def all_member_entity_unique_ids(self) -> list[str]:
        """Return all platform entities unique ids for the members of this group."""
        all_entity_unique_ids: list[str] = []
        for member in self.members:
            entities = member.associated_entities
            for entity in entities:
                all_entity_unique_ids.append(entity.unique_id)
        return all_entity_unique_ids

    def register_group_entity(self, group_entity: GroupEntity) -> None:
        """Register a group entity."""
        if group_entity.unique_id not in self._group_entities:
            self._group_entities[group_entity.unique_id] = group_entity
            self._entity_unsubs[group_entity.unique_id] = group_entity.on_event(
                STATE_CHANGED,
                self._handle_maybe_update_group_members,
            )
        self.update_entity_subscriptions()

    def _handle_maybe_update_group_members(self, event: EntityStateChangedEvent):
        """Handle the maybe update group members event."""
        self.gateway.async_create_task(self._maybe_update_group_members(event))

    async def _maybe_update_group_members(self, event: EntityStateChangedEvent) -> None:
        """Update the state of the entities that make up the group if they are marked as should poll."""
        tasks = []
        platform_entities = self.get_platform_entities(event.platform)
        for platform_entity in platform_entities:
            if platform_entity.should_poll:
                tasks.append(platform_entity.async_update())
        if tasks:
            await asyncio.gather(*tasks)

    def update_entity_subscriptions(self) -> None:
        """Update the entity event subscriptions.

        Loop over all the entities in the group and update the event subscriptions. Get all of the unique ids
        for both the group entities and the entities that they are compositions of. As we loop through the member
        entities we establish subscriptions for their events if they do not exist. We also add the entity unique id
        to a list for future processing. Once we have processed all group entities we combine the list of unique ids
        for group entities and the platrom entities that we processed. Then we loop over all of the unsub ids and we
        execute the unsubscribe method for each one that isn't in the combined list.
        """

        group_entity_ids = list(self._group_entities.keys())
        processed_platform_entity_ids = []
        for group_entity in self._group_entities.values():
            for platform_entity in self.get_platform_entities(group_entity.PLATFORM):
                processed_platform_entity_ids.append(platform_entity.unique_id)
                if platform_entity.unique_id not in self._entity_unsubs:
                    self._entity_unsubs[platform_entity.unique_id] = (
                        platform_entity.on_event(
                            STATE_CHANGED,
                            group_entity.debounced_update,
                        )
                    )
        all_ids = group_entity_ids + processed_platform_entity_ids
        existing_unsub_ids = self._entity_unsubs.keys()
        processed_unsubs = []
        for unsub_id in existing_unsub_ids:
            if unsub_id not in all_ids:
                self._entity_unsubs[unsub_id]()
                processed_unsubs.append(unsub_id)

        for unsub_id in processed_unsubs:
            self._entity_unsubs.pop(unsub_id)

    async def async_add_members(self, members: list[GroupMemberReference]) -> None:
        """Add members to this group."""
        devices: dict[EUI64, Device] = self._gateway.devices
        if len(members) > 1:
            tasks = []
            for member in members:
                tasks.append(
                    devices[member.ieee].async_add_endpoint_to_group(
                        member.endpoint_id, self.group_id
                    )
                )
            await asyncio.gather(*tasks)
        else:
            member = members[0]
            await devices[member.ieee].async_add_endpoint_to_group(
                member.endpoint_id, self.group_id
            )
        self.update_entity_subscriptions()

    async def async_remove_members(self, members: list[GroupMemberReference]) -> None:
        """Remove members from this group."""
        devices: dict[EUI64, Device] = self._gateway.devices
        if len(members) > 1:
            tasks = []
            for member in members:
                tasks.append(
                    devices[member.ieee].async_remove_endpoint_from_group(
                        member.endpoint_id, self.group_id
                    )
                )
            await asyncio.gather(*tasks)
        else:
            member = members[0]
            await devices[member.ieee].async_remove_endpoint_from_group(
                member.endpoint_id, self.group_id
            )
        self.update_entity_subscriptions()

    def get_platform_entities(self, platform: str) -> list[PlatformEntity]:
        """Return entities belonging to the specified platform for this group."""
        platform_entities: list[PlatformEntity] = []
        for member in self.members:
            if member.device.is_coordinator:
                continue
            for entity in member.associated_entities:
                if platform == entity.PLATFORM:
                    platform_entities.append(entity)

        return platform_entities

    def log(self, level: int, msg: str, *args: Any, **kwargs) -> None:
        """Log a message."""
        msg = f"[%s](%s): {msg}"
        args = (self.name, self.group_id) + args
        _LOGGER.log(level, msg, *args, **kwargs)

    async def on_remove(self) -> None:
        """Cancel tasks this group owns."""
        for group_entity in self._group_entities.values():
            await group_entity.on_remove()


class WebSocketClientGroup(BaseGroup):
    """ZHA Zigbee group object for the websocket client."""

    def __init__(
        self,
        group_info: GroupInfo,
        gateway: WebSocketClientGateway,
    ) -> None:
        """Initialize the group."""
        super().__init__(gateway)
        self._group_info = group_info
        self._entities: dict[str, WebSocketClientEntity] = {}
        if self._group_info.entities:
            self._build_or_update_entities()

    @property
    def name(self) -> str:
        """Return group name."""
        return self._group_info.name

    @property
    def group_id(self) -> int:
        """Return group name."""
        return self._group_info.group_id

    @property
    def group_entities(self) -> dict[str, WebSocketClientEntity]:
        """Return the platform entities of the group."""
        return self._entities

    @property
    def members(self) -> list[WebSocketClientGroupMember]:
        """Return the ZHA devices that are members of this group."""
        return [
            WebSocketClientGroupMember(
                self, self._gateway.devices[member.ieee], member.endpoint_id, member
            )
            for member in self._group_info.members
        ]

    @property
    def all_member_entity_unique_ids(self) -> list[str]:
        """Return all platform entities unique ids for the members of this group."""
        all_entity_unique_ids: list[str] = []
        for member in self.members:
            entities = member.associated_entities
            for entity in entities:
                all_entity_unique_ids.append(entity.unique_id)
        return all_entity_unique_ids

    @property
    def info_object(self) -> GroupInfo:
        """Get ZHA group info."""
        return self._group_info

    @info_object.setter
    def info_object(self, group_info: GroupInfo) -> None:
        """Set ZHA group info."""
        self._group_info = group_info
        self._build_or_update_entities()

    def _build_or_update_entities(self):
        """Build the entities for this device or rebuild them from extended device info."""
        current_entity_ids = set(self._entities.keys())
        for unique_id, entity_info in self._group_info.entities.items():
            if unique_id in self._entities:
                self._entities[unique_id].entity_info = entity_info
                current_entity_ids.remove(unique_id)
            else:
                self._entities[unique_id] = (
                    discovery.ENTITY_INFO_CLASS_TO_WEBSOCKET_CLIENT_ENTITY_CLASS[
                        entity_info.__class__
                    ](entity_info, self)
                )
        for entity_id in current_entity_ids:
            self._entities.pop(entity_id, None)

    def emit_platform_entity_event(self, event: EntityStateChangedEvent) -> None:
        """Proxy the firing of an entity event."""
        entity = self.group_entities.get(event.unique_id)
        if entity is not None:
            entity.state = event.state

    async def async_add_members(self, members: list[GroupMemberReference]) -> None:
        """Add members to this group."""
        await self._gateway.groups_helper.add_group_members(self.info_object, members)

    async def async_remove_members(self, members: list[GroupMemberReference]) -> None:
        """Remove members from this group."""
        await self._gateway.groups_helper.remove_group_members(
            self.info_object, members
        )
